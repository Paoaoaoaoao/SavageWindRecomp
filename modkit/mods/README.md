# Put your mod groups here

Each subfolder is one switchable group, named `NN_something` where `NN`
matches the number in `mods_config.ini`:

```
  01_linkle_player/
    Pack/TitleBG.pack
  02_armour_fit/
    Model/...
  10_core_data/
    System/Resource/ResourceSizeTable.product.srsizetable
    Actor/ActorInfo.product.sbyml
```

The folder contents must mirror the RomFS layout — the same paths the game
would read, relative to the RomFS root. The console hard-links them into
`_enabled/`, which becomes `SAVAGEWIND_ROMFS_OVERLAY`.

No mod files are included in this repository. See the licence section in
`../README.md`: the Linkle mod is CC BY-NC-ND 4.0, which does not allow
redistributing modified copies, so these folders are yours to assemble from
the authors' own downloads.

Two things worth knowing before you fill this in:

* **The `ResourceSizeTable` group is not optional.** It is the size registry
  for every RomFS file. Mount bigger mod files without it and the game
  allocates from stale sizes and crashes on load with `c0000005`. Keep it on
  whenever anything else is on. The console warns you if you forget.
* **A file claimed by two groups is taken from the first one only.** The
  console lists such conflicts after every build; if you see them, the groups
  overlap and one of them is being partly ignored.
