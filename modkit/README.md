# Savage Wind MOD console

A group on/off switch for **RomFS overlay mods** on
[Savage Wind Recomp](https://github.com/Revivedx/SavageWindRecomp).

Savage Wind already supports modding through
`SAVAGEWIND_ROMFS_OVERLAY`, which replaces or *adds* RomFS files. What it does
not have is any way to **manage** a pile of mods: no groups, no on/off
switches, no way to combine several mods that need to be mounted together
(the overlay variable takes exactly one directory).

This is that layer. Nothing here changes the game — it only assembles the
overlay folder for you and starts the game with it.

```
  mods/
    01_linkle_player/     ┐
    02_armour_fit/        │  your own mod folders, grouped however you like
    03_added_armours/     │  (folder name starts with the group number)
    ...                   │
    10_core_data/         ┘
  _enabled/               <- assembled here: hard links, not copies
```

## What it does

* **Groups.** Each folder in `mods/` named `NN_something` is one switchable
  group. `mods_config.ini` lists them; flip a digit to enable or disable.
* **One overlay folder.** Only enabled groups are assembled into `_enabled/`,
  which becomes `SAVAGEWIND_ROMFS_OVERLAY`. Combining several mods is the
  whole point, because the game takes one directory.
* **Hard links, not copies.** Assembly uses `os.link`, so a 450 MB mod set
  costs almost nothing on disk and is instant. It falls back to a real copy
  only when the target filesystem cannot hard link.
* **Crash guard.** The `ResourceSizeTable` is the size registry for every
  RomFS file. Mount a mod that ships bigger files without also mounting its
  RSTB and the game allocates from the stale sizes and dies with
  `c0000005`. The console warns loudly when group 10 is off while others are
  on.

## Requirements

* Windows (the launcher is a `.bat`; `modtool.py` itself is plain Python).
* Python 3 — for the console. `launch_game.bat` works without it once
  `_enabled/` exists, but rebuilding needs it.
* A Savage Wind build that supports `SAVAGEWIND_ROMFS_OVERLAY`. Both `main`
  and `test` do.

## Setup

1. Put this folder anywhere. It does not care where the game is.
2. Put your mod folders in `mods/`, named with a leading group number:
   `01_linkle_player`, `02_armour_fit`, ...
3. Point it at the game — either set `SAVAGEWIND_HOME`, or keep this folder
   next to `savagewind.exe` (both `savagewind.exe` at the top and
   `build\savagewind.exe` are found):

   ```bat
   set SAVAGEWIND_HOME=D:\Games\SavageWind
   ```

4. Double-click `mod_console.bat`, toggle what you want, press `S`.

`launch_game.bat` builds and launches in one step using whatever
`mods_config.ini` currently says.

## Keys

| Key | Action |
|---|---|
| `1`..`N` | toggle that group |
| `A` | all on |
| `N` | all off |
| `S` | rebuild `_enabled/` and launch |
| `E` | open `mods_config.ini` in Notepad |
| `Q` | quit |

## About the HUD-button-letters patch

Savage Wind rewrites `Pack/Bootup.pack` so the on-screen button prompts use
the icon font, and it records that archive's growth in the
`ResourceSizeTable`. When an overlay **replaces** the RSTB — which any mod
set with a size table does — that registration is skipped:

```c
// runtime/services/fs.c, hud_letters_patch()
R->grown[R->ngrown++] = (GrownFile){"Layout/Common.blarc", nn - an};

// runtime/services/fs.c, rstb_patch()
if (overlay_file(rstb_path, host, sizeof host)) {
    LOG("[fs] voices: the overlay folder replaces the ResourceSizeTable: ...");
    return;   // <- those entries are never written
}
```

The game then reads a pack bigger than its entry and crashes. This console
sets `SAVAGEWIND_NO_HUD_LETTERS=1` for that reason: it is the only way to
have a mod overlay and the HUD patch coexist on current builds. If upstream
fixes the ordering, that line can go.

## Licensing and credits

**This repository ships no game assets and no mod assets.** It is the switch
only.

The Linkle mod used while developing this came from **lynard killer** and the
Linkle Project team, published on GameBanana:

* <https://gamebanana.com/mods/168235> — Linkle Mod (original)
* <https://gamebanana.com/mods/406768> — The Linkle Mod 3.0

That work is licensed **CC BY-NC-ND 4.0** (Attribution-NonCommercial-NoDerivatives).
The NoDerivatives term matters: it does not permit distributing modified
copies. So the mod files are **not** redistributed here in any form, not
whole and not split into groups. Download them from the authors' pages
yourself, then arrange them into `mods/NN_...` folders locally.

The mods also contain Nintendo's original assets. Do not republish extracted
game files.

Savage Wind Recomp itself is MIT licensed, © Revivedx and the Savage Wind
Recomp contributors, and © Peiikai (LAS Recomp). See `LICENSE`.

## Layout

```
  mod_console.bat        the switch UI
  launch_game.bat        build + launch, no UI
  modtool.py             the engine (put under _tools/)
  mods_config.ini        group list and state
  mods/                  your groups (empty here)
  _enabled/              assembled overlay, rebuilt every launch
```

`modtool.py` finds its root from its own path, so the whole folder is
relocatable. It must sit in `_tools/` next to `mods/`.

## Notes on the console output

`modtool.py` does not use `print` for console text. On a non-UTF-8 Windows
code page, Python 3.13 still reports `sys.stdout.encoding == "utf-8"` and
writes UTF-8 bytes that `cmd` decodes as CP936 — mojibake. The engine writes
through `WriteConsoleW` instead, which ignores the code page. The UI is
English, so this is belt and braces, but it means translated text will not
break.
