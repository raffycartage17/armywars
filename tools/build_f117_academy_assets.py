"""Package the custom F117 Academy artwork using JPEXS FFDec 26.4.0.

Usage: python tools/build_f117_academy_assets.py PATH/TO/ffdec.jar
Requires Java and Pillow. Reuses the stock hangar's two orientation frames and
MovieClip linkage, with a new bitmap, new linkage name, and no stock beacon.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSET = '0500_f117_academy'


def main():
    jar = Path(sys.argv[1]).resolve()
    artwork = ROOT / 'assets/artwork' / (ASSET + '.png')
    source = ROOT / 'assets/sprites/0077_hangar_3_m.swf'
    output = ROOT / 'assets/sprites' / (ASSET + '.swf')

    def ff(*args):
        subprocess.run(['java', '-jar', str(jar), *map(str, args)], check=True)

    with tempfile.TemporaryDirectory() as folder:
        work = Path(folder)
        image = Image.open(artwork).convert('RGBA')
        assert image.getchannel('A').getextrema()[0] == 0, 'Transparent artwork required'
        # Match the stock bitmap canvas: the game positions buildings from its
        # bounds, while the two existing frames provide mirrored orientations.
        sprite = ImageOps.contain(image, (648, 482), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (648, 482))
        canvas.alpha_composite(sprite, ((648 - sprite.width) // 2, 482 - sprite.height))
        canvas.save(work / 'sprite.png')
        thumb = Image.new('RGB', (90, 90), 'white')
        small = ImageOps.contain(image, (88, 88), Image.Resampling.LANCZOS)
        thumb.paste(small, ((90 - small.width) // 2, (90 - small.height) // 2), small)
        thumb.save(ROOT / 'assets/thumbs' / (ASSET + '.jpg'), quality=95)
        ff('-replace', source, work / 'bitmap.swf', '1', work / 'sprite.png')
        ff('-swf2xml', work / 'bitmap.swf', work / 'sprite.xml')
        tree = ET.parse(work / 'sprite.xml')
        links = 0
        for node in tree.iter():
            if node.text == '0077_hangar_3_m':
                node.text = ASSET
                links += 1
        assert links == 2, 'Expected class name and SymbolClass linkage'
        # The old animated red dot belongs to the old artwork. The new sprite
        # already contains its own lights, so remove the old overlay placements.
        sprite_tag = next(t for t in tree.findall('.//*[@type="DefineSpriteTag"]') if t.get('spriteId') == '5')
        tags = sprite_tag.find('subTags')
        for child in list(tags):
            if child.get('depth') == '2':
                tags.remove(child)
        tree.write(work / 'sprite.xml', encoding='utf-8', xml_declaration=True)
        ff('-xml2swf', work / 'sprite.xml', output)
        ff('-swf2xml', output, work / 'verify.xml')
        verified = ET.parse(work / 'verify.xml')
        assert verified.find('.//*[@type="SymbolClassTag"]/names/item').text == ASSET
        assert next(t for t in verified.findall('.//*[@type="DefineSpriteTag"]') if t.get('spriteId') == '5').get('frameCount') == '2'
        print('Created custom academy sprite and thumbnail:', output)


if __name__ == '__main__':
    main()
