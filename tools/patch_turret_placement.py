"""Enable repeated turret purchases in the original 1.5.4 Flash client.

Usage: python tools/patch_turret_placement.py ORIGINAL.swf OUTPUT.swf FFDEC.jar
Requires Java and JPEXS FFDec 26.4.0. The input hash deliberately pins the
supported client so body 79 cannot accidentally refer to another method.
"""

import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile


ORIGINAL_SHA256 = "e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77"
OLD_CONDITION = "this.selectedBuilding != null && !Base.Properties.elementHasProperty(this.selectedBuilding.id,PropertyManager.WALL)"
NEW_CONDITION = "this.selectedBuilding != null && (!Base.Properties.elementHasProperty(this.selectedBuilding.id,PropertyManager.WALL) && !Base.Properties.elementHasProperty(this.selectedBuilding.id,PropertyManager.TOWER))"


def main():
    source, output, jar = (Path(arg).resolve() for arg in sys.argv[1:])
    if source == output:
        raise ValueError("Use a separate output file; retain the original client.")
    if hashlib.sha256(source.read_bytes()).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("Unsupported input: expected the original Basesec_1.5.4.swf.")

    def ffdec(*args):
        subprocess.run(["java", "-jar", str(jar), *map(str, args)], check=True)

    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        ffdec("-selectclass", "core.Base", "-format", "script:pcode",
              "-export", "script", work / "pcode", source)
        assembly = (work / "pcode/scripts/core/Base.pcode").read_text(encoding="utf-8")
        start = assembly.index("public function mouseUsed(")
        start = assembly.index("\n", assembly.index("method\n", start)) + 1
        end = assembly.index("end ; method", start)
        method = "\n".join(line.strip() for line in assembly[start:end].splitlines())
        needle = 'callproperty QName(PackageNamespace(""),"elementHasProperty"), 2\nnot\nofs0aba:'
        replacement = '''callproperty QName(PackageNamespace(""),"elementHasProperty"), 2
not
dup
iffalse ofs0aba
pop
getlex QName(PackageNamespace("core"),"Base")
getproperty QName(PackageNamespace(""),"Properties")
getlocal0
getproperty QName(PackageNamespace(""),"selectedBuilding")
getproperty QName(PackageNamespace(""),"id")
getlex QName(PackageNamespace("core.isoengine"),"PropertyManager")
getproperty QName(PackageNamespace(""),"TOWER")
callproperty QName(PackageNamespace(""),"elementHasProperty"), 2
not
ofs0aba:'''
        if method.count(needle) != 1:
            raise ValueError("Placement instruction sequence did not match.")
        patch = work / "mouseUsed.pcode"
        patch.write_text(method.replace(needle, replacement), encoding="utf-8")
        candidate = work / "patched.swf"
        ffdec("-replace", source, candidate, "core.Base", patch, "79")

        # Check the complete Base class, not just the changed instruction block.
        for folder, client in [("before", source), ("after", candidate)]:
            ffdec("-selectclass", "core.Base", "-export", "script", work / folder, client)
        before = (work / "before/scripts/core/Base.as").read_text(encoding="utf-8")
        after = (work / "after/scripts/core/Base.as").read_text(encoding="utf-8")
        if before.count(OLD_CONDITION) != 1 or after != before.replace(OLD_CONDITION, NEW_CONDITION):
            raise ValueError("Unexpected decompiled differences; refusing to publish the patch.")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(candidate.read_bytes())
        print("Verified repeated turret placement:", output)


if __name__ == "__main__":
    main()
