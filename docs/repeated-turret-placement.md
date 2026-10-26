# Repeated turret placement

The 1.5.4 client now keeps purchase placement active for buildings with the
`tower` property, just as it does for buildings with the `wall` property.
Each successful placement still uses the normal purchase command and cost.
The existing tutorial, stored-item, energy, affordability, and placement
checks are unchanged. Other buildings still leave purchase placement after
one purchase.

The change is in `core.Base.mouseUsed`, method body 79, inside
`assets/flash/Basesec_1.5.4.swf`. No turret is reclassified as a wall.

## Reproduction

Use Java, JPEXS FFDec 26.4.0, and an original client from Git:

```powershell
.\.venv\Scripts\python.exe tools/patch_turret_placement.py ORIGINAL.swf PATCHED.swf build/runtime/ffdec/ffdec.jar
```

The tool verifies the original SHA-256 and exports the patched class again.
It refuses the result unless the complete decompiled Base class matches the
original with only the placement condition extended to include towers.
Copy the verified output to the client asset and rebuild with `build-local.ps1`.

The original client is backed up locally at
`build/runtime/client-backups/Basesec_1.5.4.original.swf`.

## In-game acceptance check

After restarting Flash Browser, buy a turret and place it on two valid tiles
without reopening the shop. Confirm that two turrets are added and their
normal cost is charged twice. Confirm that wall placement still repeats,
an ordinary house purchase ends placement, and canceling placement works.
Also check that insufficient resources stop further purchases. These visual
checks remain to be performed in the game.
