# F117 Academy

The F117 Academy is a new building, item **500**, available from level **6** in
**Build → Army/Attack → Aircrafts** for **35 cash**. It trains the existing F-117
unit (1096), using the normal academy training panel, queue and population rules.
The regular F-117 price remains **2 cash**, with its existing combat statistics.
Construction and training each take 5 seconds; the footprint is 6 × 6 tiles,
health is 1,000, and it has no upgrade chain or individual quantity limit.

## Custom artwork

- `assets/artwork/0500_f117_academy.png`: original generated transparent artwork.
- `assets/sprites/0500_f117_academy.swf`: new Flash sprite with a unique exported
  MovieClip class, compatible with the game's sprite loader.
- `assets/thumbs/0500_f117_academy.jpg`: matching 90 × 90 shop/portrait thumbnail.

The custom stealth hangar artwork includes an F-117 on its apron and an integrated
control tower. It is a static sprite, with two mirrored orientation frames. It
uses the stock Hangar III's MovieClip structure, with its bitmap replaced, class
linkage renamed and original beacon overlay removed. The original hangar remains
unchanged. No changes to the main game SWF are required.

Rebuild the sprite and thumbnail with Java, Pillow and JPEXS FFDec 26.4.0:

```powershell
.\.venv\Scripts\python.exe tools/build_f117_academy_assets.py build/runtime/ffdec/ffdec.jar
```

The configuration adds one item and retains the earlier tower/wall limit changes.
Item 500 was checked against the configuration, config patches and the recovered
client's reserved building constants. Item 302 is reserved for Atom Fusion and
must not be used for this academy.

## Verification

The bundled server serves the new item and both new assets. The shop and map
render the custom artwork in FlashBrowser. An isolated copy of the account was
used for construction and training checks. A purchase command for item 500 and
completed F-117 training commands were observed, and the resulting building and
aircraft were verified in the test save. The test account is removed after QA.
