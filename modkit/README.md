# Savage Wind MOD console

**English** · [简体中文](README.zh-CN.md)

A group switch for RomFS overlay mods on
[Savage Wind Recomp](https://github.com/Revivedx/SavageWindRecomp).

> This repository ships **no game files and no mod files**. It is the switch
> only — see [Licensing and credits](#licensing-and-credits).

## Why this exists

Savage Wind reads mods through one environment variable:

```bat
set SAVAGEWIND_ROMFS_OVERLAY=<folder>
```

That folder is laid out like the game's RomFS: files in it replace the game's
files, and files the game does not have are added to its table. It works — but
it takes exactly **one** directory, and there is no notion of "on" and "off".
Every combination of mods has to be assembled by hand, and comparing "with mod"
against "without mod" means moving hundreds of files around.

This tool keeps mods in groups and assembles that one folder for you:

```
  mods/
    01_player/         ┐
    02_armour/         │  your groups: one folder each, contents = RomFS layout
    03_extra_armours/  │
    ...                │
    10_core/           ┘
  _enabled/            <- assembled here as hard links, rebuilt on every launch
```

Nothing here patches the game. It writes one folder and starts the game with
two environment variables set.

## Requirements

| | |
|---|---|
| Game | *Breath of the Wild* **1.9.0** — the only version Savage Wind reads |
| Build | any build with `SAVAGEWIND_ROMFS_OVERLAY`; upstream `main` and `test` both have it |
| OS | Windows (the launchers are `.bat`; `modtool.py` itself is plain Python) |
| Python | Python 3 on `PATH`. **Both launchers need it on every run**, because both rebuild `_enabled/` before starting the game. `mod_console.bat` also accepts a portable copy at `_tools\python\python.exe` |

## Quick start

1. Put this folder anywhere. It does not care where the game is.
2. Put your mods into `mods/`, one folder per group, named `NN_something`.
   The contents must mirror the RomFS — see
   [What a group looks like](#what-a-group-looks-like).
3. Point it at the game, either by setting a variable:

   ```bat
   set SAVAGEWIND_HOME=D:\Games\SavageWind
   ```

   or by keeping this folder next to `savagewind.exe`, or next to the folder
   that contains `build\savagewind.exe`. Both are probed.
4. Double-click `mod_console.bat`, toggle with the numbers, press `S`.

`launch_game.bat` does the last two steps in one go, honouring whatever
`mods_config.ini` currently says — it does not "turn everything on".

Starting the game from a desktop shortcut bypasses the environment variables
and the working directory, so the game boots vanilla and the mod looks broken.
That is **P5** below.

## The console

| Key | Action |
|---|---|
| `1`..`N` | toggle that group |
| `A` | all on |
| `N` | all off |
| `S` | rebuild `_enabled/` and launch |
| `E` | open `mods_config.ini` in Notepad |
| `Q` | quit |

The engine can also be driven directly:

| Command | |
|---|---|
| `python modtool.py list` | groups and their state |
| `python modtool.py toggle <n>` / `on <n>` / `off <n>` | one group |
| `python modtool.py setall <1\|0>` | every group |
| `python modtool.py build` | rebuild `_enabled/` |
| `python modtool.py status` | what is live right now |
| `python modtool.py init` | write a starter `mods_config.ini` |

## What a group looks like

Paths inside a group mirror the RomFS root exactly. This is the set the console
was developed against — the numbering is what `mods_config.ini` ships with, the
contents are yours:

| # | Group | Holds |
|---|---|---|
| 1 | Player model | `Pack/TitleBG.pack` (+ `Model/Link.Tex1.sbfres`) — the protagonist lives **inside** that pack |
| 2 | Armour body-fit | `Actor/Pack/*.sbactorpack`, `Model/*.sbfres` — female armours without clipping |
| 3 | Added armour sets | new `Armor_*` actors, their `Model/` meshes and `UI/` icons |
| 4 | NPCs | `Actor/`, `Model/`, `Event/` — the NPC swap |
| 5 | Weapons | `Actor/Pack`, `Model/`, `UI/` |
| 6 | Enemies | `Actor/Pack` |
| 7 | Items and scenery | `Actor/Pack`, `Model/` |
| 8 | Audio | `Sound/Resource/**` (`.bfstm`, `.bars`) |
| 9 | Cutscene events | `Event/**` |
| 10 | **Core data** | `Actor/ActorInfo.product.sbyml`, `System/Resource/ResourceSizeTable.product.srsizetable`, `Pack/Bootup_<lang>.pack` |

Group 10 is not optional. See **P1**.

Rules the engine follows, all of them learned the hard way:

* The number is the text before the first `_` in the folder name: `01_player`
  → 1, `10_core` → 10, `10` → 10.
* **Do not zero-pad the number in `mods_config.ini`.** With `MOD|01|...`
  pressing `1` answers `no group numbered 1`; only `01` works. The console
  compares the number as text (`toggle`), while the folder lookup compares it
  numerically.
* Two folders with the same number: the first in name order wins and the other
  is used never, silently.
* Two groups shipping the same path: the first enabled group wins, the second
  file is skipped, and the build lists them. Read that list every time.
* `mods_config.ini` is UTF-8. Edit the `1`/`0` digits, keep the `|` separators,
  one line per group, delete a whole line to hide it. The name is for you.
* A group whose folder is missing is reported by `build`, not fatal.

## Adding a mod you downloaded

1. **Get loose files.** This tool reads folders, not archives — no `.bnp`
   support (see [BNP / BCML](#bnp--bcml-mods)).
2. **Find the RomFS-relative paths.** Open the archive: inside it you will see
   `Actor/`, `Model/`, `Pack/`, `Sound/` … , the same names as in the table
   above. That top level is the RomFS root; keep everything below it.
3. **Drop them into `mods/NN_name/`** preserving the structure exactly.
4. **Add a line to `mods_config.ini`** — or reuse an existing number by naming
   the folder to match.
5. **Check the two registries.** If the mod adds actors (armour, weapons,
   enemies) it must come with, or be merged into, the core group's
   `ActorInfo.product.sbyml`; if it ships files bigger than the originals, the
   core group's ResourceSizeTable must cover them. Most complete mod packages
   bring both files with them — **do not let a second group bring its own
   copies** (**P1**, **P8**).

Merging two registry files by hand does not work. Use the tool that produced
them (BCML merges `ActorInfo` and the RSTB for you) and put the merged result
into group 10.

## Pitfalls

Ordered by how much time they cost. The first four crash the game; the rest are
silent.

### P1. `c0000005` on load: the ResourceSizeTable is missing or wrong

`System/Resource/ResourceSizeTable.product.srsizetable` is the size registry for
**every** RomFS file. The game sizes its allocations from it. A mod ships files
that are bigger than the originals; if the overlay does not also replace the
table, the game allocates the old size, copies the new bytes in, and the read
runs past the end — `c0000005`, usually on the loading screen.

* Whenever anything else is on, the core-data group must be on too. The console
  prints a large warning when you break that rule; it is not decorative.
* **Exactly one group may carry the table.** If two groups ship one, the first
  wins and the second group's sizes are stale — same crash, harder to see,
  because `build` also reports the overlap as an ordinary conflict.
* The table must come from the same game version as the files around it
  (1.9.0). A table from an older patch is worse than none: right shape, wrong
  numbers.

### P2. `c0000005` on load: the HUD-letters patch versus a replaced table

Not your fault, but it explains a line in both launchers.

Savage Wind rewrites `Pack/Bootup.pack` so the on-screen button prompts use the
icon font, and records that archive's growth in the ResourceSizeTable. When an
overlay replaces the table, the registration is skipped:

```c
// runtime/services/fs.c, hud_letters_patch()
R->grown[R->ngrown++] = (GrownFile){"Layout/Common.blarc", nn - an};   // line 849

// runtime/services/fs.c, rstb_patch()
if (overlay_file(rstb_path, host, sizeof host)) {
    LOG("[fs] voices: the overlay folder replaces the ResourceSizeTable: ...");
    return;                                    // line 999: those entries never land
}
```

*Line numbers as of upstream `test` at `60f0b68`; the function names are what to
grep for if they drift.*

The pack is patched in memory and served from there, bigger than the size the
table claims → same overflow as P1. This is why both launchers set:

```bat
set SAVAGEWIND_NO_HUD_LETTERS=1
```

The cost: the HUD's prompts keep the game's own A/B/X/Y letters instead of the
icon font. That is the only trade available on current builds; if upstream ever
writes those entries before the early return, the line can go.

The exact condition matters: it needs an overlay that replaces the **table** but
**not** `Pack/Bootup.pack`. A mod set that replaces `Bootup.pack` as well never
reaches the registration (and loses the icon prompts anyway, being replaced).

### P3. Symlinks where hard links are needed

`_enabled/` is made of **hard links**. Do not replace them with symbolic links,
`mklink /D` junctions, or a `subst` drive. The runtime opens overlay files by
path and follows whatever is there; through a symlink it has crashed with
`c0000005` in testing. Hard links and real copies are the only two safe options,
and the engine already falls back to a copy when the filesystem refuses a link.

(That restriction is about **your** overlay. The game's own `extracted/aoc1`-style
links are the game's business.)

### P4. `c0000005` from a half-written pack

Copying a 140 MiB `.pack` by hand, interrupting it, and mounting it gives a
truncated archive: the game reads the header, trusts a table that points past
the end, and dies. `_enabled/` only ever links, so it cannot truncate — but if
you copy files into `mods/` manually, let the copy finish before launching.

### P5. You launched it the wrong way, so nothing applies

The mods exist only if **both** of these are true when the game starts:

1. `SAVAGEWIND_ROMFS_OVERLAY` points at `_enabled/`;
2. the process starts with the game's data folder as its working directory.

A desktop shortcut, Steam, or a file-manager double-click on `savagewind.exe`
gives you neither: the game boots vanilla. If the mod "stopped working", check
this before touching anything else. The launchers do both (`set` then
`cd /d "%GAME%"`).

### P6. It loads and nothing changes: loose files inside a pack

The RomFS file table lists packs, not their contents. So this is never read:

```
mods/01_player/Pack/TitleBG.pack/Model/Link.sbfres      <- ignored
```

To change something inside a pack you must replace **the whole pack**:

```
mods/01_player/Pack/TitleBG.pack                        <- correct
```

Same for `Bootup.pack`, `AocMainField.pack`, every `.pack` and `.sarc`. This is
why the player model costs a 140 MiB file: it lives inside `TitleBG.pack` and
nowhere else, and a one-file change costs the whole archive.

### P7. New files only land in directories the game already has

Overlay files that the game's RomFS does not have are added to its file table at
boot (`add_new_files()`), but the **parent directory must already exist** in the
game's RomFS. Otherwise the file is skipped with one quiet log line and no
error:

```
[fs] overlay file Actor/Pack/MyNew/Armor_999.sbactorpack: directory not in the game's RomFS, skipped
```

You can add files to `Actor/Pack/`, `Model/`, `Sound/Resource/Stream/`,
`Event/` — you cannot invent `Actor/Pack/MyNew/`.

Related: **case matters for added files.** The game looks a file up by a hash of
its name bytes, so `Model/link.sbfres` and `Model/Link.sbfres` are different
entries; the wrong case is simply not found. Replacement is more forgiving,
because Windows resolves that path itself — which makes the failure confusing:
replacements work, additions do not.

### P8. Same path in two groups: the first one wins, silently

The build stops at the first group that claims a path and skips the rest. It
does print the list:

```
  [!] 3 files are claimed by more than one group (the first one won):
        Actor/Pack/Armor_200.sbactorpack
```

If you see that, your groups overlap and one of them is not fully applied.
Merge the overlap into one group instead of relying on order. The two files
where this really bites are `Actor/ActorInfo.product.sbyml` and the
ResourceSizeTable: for those, "first wins" means the other mod's actors or
sizes simply do not exist, and the game then fails on a file it was told about
but cannot size.

### P9. Game settings that quietly stop working

Replacing the pack that a built-in patch edits makes that patch skip itself. No
error, no log line, the setting just does nothing:

| Overlay replaces | Loses |
|---|---|
| `Pack/TitleBG.pack` | **Video → Haze** — the atmospheric-haze slider (`haze_patch()`); it patches `WorldMgr/normal.bwinfo` inside that pack |
| `Pack/Bootup.pack` | the HUD icon-font patch (expected, and the reason P2 avoids it) |
| `System/Version.txt` | the title screen's `Savage Wind 1.9` text |
| `System/AocVersion.txt` or `Pack/AocMainField.pack` | nothing of yours — but the game now *thinks* your RomFS has the DLC merged into it and grows RSTB entries from `Aoc/0010/...`. Never ship these two by accident. |

The first row hits every player-model mod, because the model lives in
`TitleBG.pack`. There is no way around it: the pack is the unit of replacement.
Choose the model or the haze slider.

### P10. DLC content has one fixed place in the overlay

If your build mounts the DLC (`extracted/aoc1`, `aoc2`, …), add-on content files
go here:

```
_enabled/aoc/0010/<paths inside the DLC's RomFS>
```

`0010` is literal for **every** add-on content index, not the index itself —
that is the Wii U layout and what the runtime reads (`fs.c`: `ov_sub =
"aoc/0010/"`). Note also that upstream's **official release does not mount DLC
at all**: `main` has no add-on code (`misc.c` says `aoc:u (no DLC)`), only
`test` does, up to 8 contents.

### P11. Hard links mean one file with two names

* Editing a file through `_enabled/` edits `mods/` — same bytes, two paths.
  Never "fix" something under `_enabled/`.
* Deleting `_enabled/` never touches `mods/`; the links only lose a name.
* **Replacing** a file in `mods/` (extracting over it, saving a new copy) breaks
  the link: `_enabled/` keeps the old bytes. Rebuild.
* On a filesystem that cannot hard link, the engine copies instead. Then
  `_enabled/` costs as much disk as `mods/` — 450 MB becomes 900 MB.
* `_enabled/` is disposable. Never put anything of your own in it; it is
  deleted and rebuilt on every launch.

### P12. Windows and the launchers

* `.bat` files must be **CRLF and pure ASCII**. `cmd` reads them in the system
  ANSI code page, so Chinese inside a `.bat` becomes mojibake on a machine with
  a different one. Every piece of UI text comes from `modtool.py`. If you edit
  the bats, keep that rule. `modkit/.gitattributes` exists to keep `eol=crlf`
  even though the repository root sets `* text=auto eol=lf`.
* Python is found with `where python`, then `where py -3`, then
  `_tools\python\python.exe`. No user path is hard-coded.
* Console text does **not** go through `print()`. On a CP936 console Python
  3.13 still reports `sys.stdout.encoding == "utf-8"` and writes UTF-8 bytes
  that `cmd` decodes as CP936 — mojibake. The engine writes through
  `WriteConsoleW`, which bypasses the code page. Do not "simplify" it back.
* **A crash closes the window before you can read it.** Start
  `mod_console.bat` from an already-open `cmd` if you need the tail. Where the
  log goes depends on the build:
  * console build → stdout/stderr in the terminal, no file;
  * GUI build (official release) → `savagewind.log` next to the exe.

### P13. The rebuild cannot clear `_enabled`

Windows will not delete a file that is open. If a previous run is still
shutting down, `_enabled` cannot be renamed away and the build says how many
files were busy. Close the game and rebuild.

The engine unlinks the links one by one before removing the directory for
exactly this reason: a plain recursive delete can leave a 796-file tree behind
while `shutil.rmtree(ignore_errors=True)` reports success, and the next build
then quietly reuses stale files.

## Did it actually load?

The log says so, in this order:

| Line | Means |
|---|---|
| `[fs] overlay: 622 romfs files replaced` | that many of the game's files are served from your folder (numbers from one 796-file mod set) |
| `[fs] overlay: 175 new romfs files` | files the game did not have were added to its table |
| `[fs] overlay file X: directory not in the game's RomFS, skipped` | a new file went nowhere — **P7** |
| `[fs] voices: the overlay folder replaces the ResourceSizeTable: N bigger banks left to it` | your mod set replaced the table; for any set that ships an RSTB this is the normal, wanted line |
| `[fs] romfs index: N files` | the final table size |

No `overlay:` line at all means the variable was not seen — **P5**, or
`_enabled/` is empty.

## BNP / BCML mods

This tool needs **loose files** laid out like the RomFS. It does not read `.bnp`
(BCML) archives, and neither does Savage Wind: the BNP pipeline is still an
unmerged pull request upstream (#430). If all you have is a `.bnp`, unpack it
with the tool that made it, then place the result into `mods/NN_.../` following
the RomFS layout.

## Licensing and credits

**This repository ships no game assets and no mod assets.** It is the switch
only: `modtool.py`, two `.bat` files, a config sample, these docs.

The mod set this was developed against is the **Linkle** mod by **lynard killer**
and the Linkle Project, published on GameBanana:

* <https://gamebanana.com/mods/168235> — Linkle Mod (original)
* <https://gamebanana.com/mods/406768> — The Linkle Mod 3.0

That work is licensed **CC BY-NC-ND 4.0**
(Attribution-NonCommercial-NoDerivatives). The NoDerivatives term is the one
that matters here: it does not permit distributing modified copies, and
splitting a download into groups *is* a modified copy. So the mod files are not
redistributed in this repository in any form — not whole, not split. Download
them from the authors' pages and arrange them locally.

Those files also contain Nintendo's original assets. Do not republish extracted
game files anywhere.

Savage Wind Recomp itself is MIT licensed, © Revivedx and the Savage Wind Recomp
contributors, and © Peiikai (LAS Recomp). See the repository's `LICENSE`.

## Layout

```
  mod_console.bat        the switch UI
  launch_game.bat        rebuild + launch, no UI
  _tools/modtool.py      the engine
  mods_config.ini        group list and state
  mods/                  your groups (empty here, see mods/README.md)
  _enabled/              the assembled overlay (generated)
```

`modtool.py` finds its root from its own path, so the whole folder is
relocatable — but it must stay in `_tools/`, next to `mods/` and
`mods_config.ini`.
