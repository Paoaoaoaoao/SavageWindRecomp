# -*- coding: utf-8 -*-
"""
Savage Wind MOD console -- the engine.

Usage:
    python modtool.py screen               main screen (list + keys)
    python modtool.py list                 list every mod group and its state
    python modtool.py toggle <n>           flip one group on or off
    python modtool.py on <n> / off <n>     set one group
    python modtool.py setall <1|0>         every group on / off
    python modtool.py build                rebuild the _enabled overlay folder
    python modtool.py status               count what is live right now
    python modtool.py init                 write a starter mods_config.ini
    python modtool.py msg <key>            one line of UI text, for the .bat

Why the output layer looks like this
------------------------------------
This is a Windows console tool for people whose code page is not UTF-8.
Python 3.13 on a CP936 console still reports sys.stdout.encoding == "utf-8",
so printing Chinese writes UTF-8 bytes that cmd decodes as CP936 -- mojibake.
The fix is to bypass sys.stdout entirely:

    real console (GetFileType == FILE_TYPE_CHAR) -> WriteConsoleW, UTF-16,
                                                    which ignores the code page
    redirected / piped                            -> raw bytes in the console's
                                                    own code page

Do not "simplify" this back to print().  sys.stdout.reconfigure(encoding='gbk')
does nothing on a real tty; it only looks right when the output is redirected,
which is exactly the case you are NOT testing.
"""
import os
import sys
import shutil
import unicodedata

# ==========================================================================
#  output layer: do not route Chinese text through sys.stdout
# ==========================================================================
import ctypes
from ctypes import wintypes

_k32 = ctypes.WinDLL('kernel32', use_last_error=True) if sys.platform == 'win32' else None

_STD_OUT = -11
_HANDLE = None
_IS_CONSOLE = False

if _k32 is not None:
    _HANDLE = _k32.GetStdHandle(_STD_OUT)
    try:
        _IS_CONSOLE = _k32.GetFileType(_HANDLE) == 2  # FILE_TYPE_CHAR
    except Exception:
        _IS_CONSOLE = False


def _console_cp():
    if _k32 is None:
        return 936
    try:
        return _k32.GetConsoleOutputCP() or 936
    except Exception:
        return 936


def _fallback_enc():
    cp = _console_cp()
    if cp == 65001:
        return 'utf-8'
    if cp == 936:
        return 'gbk'
    if cp:
        return 'cp%d' % cp
    return 'gbk'


def emit(s):
    """Write one string to the console, whatever the code page is."""
    if not s:
        return
    if _IS_CONSOLE:
        # UTF-16 straight to the console buffer: the code page never applies
        for i in range(0, len(s), 8192):
            chunk = s[i:i + 8192]
            buf = ctypes.create_unicode_buffer(chunk)
            written = wintypes.DWORD(0)
            _k32.WriteConsoleW(_HANDLE, buf, len(chunk),
                               ctypes.byref(written), None)
    else:
        data = s.replace('\r\n', '\n').encode(_fallback_enc(), 'replace')
        try:
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        except Exception:
            pass


def print(*args, sep=' ', end='\n', **_kw):
    """Shadow the builtin so every Chinese string goes through emit()."""
    emit(sep.join(str(a) for a in args) + end)


def text_width(s):
    """Display columns, not characters: CJK takes two."""
    w = 0
    for ch in s:
        w += 2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1
    return w


def pad(s, width):
    return s + ' ' * max(0, width - text_width(s))


def center(s, width):
    fill = max(0, width - text_width(s))
    left = fill // 2
    return ' ' * left + s + ' ' * (fill - left)


def set_title(title):
    if _k32 is None:
        return
    try:
        _k32.SetConsoleTitleW(title)
    except Exception:
        pass


# ==========================================================================
#  paths -- everything hangs off _tools/ so the tree is relocatable
# ==========================================================================
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODS = os.path.join(ROOT, 'mods')
INI = os.path.join(ROOT, 'mods_config.ini')
STAGE = os.path.join(ROOT, '_enabled')

# (number, name).  Groups are folders named "NN_something" inside mods/.
# Ship these as an example: the user drops their own mod folders in and
# renames them to match, or edits mods_config.ini to describe their own.
DEFAULT_MODS = [
    ('1', 'Linkle player model (Pack/TitleBG.pack)'),
    ('2', 'Armour body-fit (no clipping in the female armours)'),
    ('3', 'Added armour sets (A280/A300/VLG/VTS1...)'),
    ('4', 'Linkle NPCs'),
    ('5', 'Weapons'),
    ('6', 'Enemies'),
    ('7', 'Items and scenery'),
    ('8', 'Audio'),
    ('9', 'Cutscene events'),
    ('10', 'Core data (ActorInfo + RSTB + language packs) -- required'),
]

MESSAGES = {
    'build_head': '  rebuilding the overlay folder from mods_config.ini ...',
    'build_done': '  overlay folder is ready.',
    'launching': '  starting the game ...',
    'game_exit': '  the game has exited, back to the console.',
    'no_python': '  [!] Python not found, the console cannot run.',
    'no_python_tip': '      Either: double-click launch_game.bat (all groups on),',
    'no_python_tip2': '      or: install Python 3 and try again.',
    'no_game': '  [!] savagewind.exe not found:',
    'ask_input': '  number or letter > ',
}


def say(key):
    msg = MESSAGES.get(key, key)
    if key == 'ask_input':
        emit(msg)
    else:
        print(msg)


# ==========================================================================
#  config
# ==========================================================================
HEADER_LINES = [
    '# Savage Wind MOD groups',
    '#',
    '#  One line per group:   MOD|<number>|1 or 0|<name>',
    '#      1 = on   0 = off',
    '#',
    '#  Edit the digits and save; the console rebuilds on launch (S).',
    '#  Delete a whole line to hide it.',
    '#',
]


def write_ini(rows):
    lines = list(HEADER_LINES)
    for num, name in rows:
        lines.append('MOD|%s|1|%s' % (num, name))
    lines.append('')
    with open(INI, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def save(rows):
    lines = list(HEADER_LINES)
    for num, on, name in rows:
        lines.append('MOD|%s|%s|%s' % (num, on, name))
    lines.append('')
    with open(INI, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def read_ini():
    if not os.path.exists(INI):
        write_ini(DEFAULT_MODS)
    out = []
    try:
        with open(INI, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('MOD|'):
                    continue
                parts = line.split('|')
                if len(parts) < 4:
                    continue
                out.append((parts[1].strip(), parts[2].strip(), parts[3].strip()))
    except OSError:
        pass
    return out


def group_dir(num):
    """Folder inside mods/ whose name starts with the group number."""
    if not os.path.isdir(MODS):
        return None
    for d in sorted(os.listdir(MODS)):
        full = os.path.join(MODS, d)
        if not os.path.isdir(full):
            continue
        head = d.split('_', 1)[0]
        if head.isdigit() and head.lstrip('0') == num.lstrip('0'):
            return full
    return None


def count_files(d):
    if not d:
        return 0
    return sum(len(fs) for _, _, fs in os.walk(d))


# ==========================================================================
#  subcommands
# ==========================================================================
RULE = '  ' + '=' * 60
THIN = '  ' + '-' * 60


def cmd_list():
    rows = read_ini()
    items = []
    wmax = text_width('group')
    for num, on, name in rows:
        st = '[ on  ]' if on == '1' else '[ off ]'
        n = count_files(group_dir(num))
        items.append((num, st, name, n))
        wmax = max(wmax, text_width(name))

    print(RULE)
    print(center('Savage Wind MOD console', 60))
    print(RULE)
    print('')
    print('  %s  %s  %s  %s' % (pad('#', 4), pad('state', 8),
                                pad('group', wmax), 'files'.rjust(6)))
    print('  %s  %s  %s  %s' % ('-' * 4, '-' * 8, '-' * wmax, '-' * 6))
    for num, st, name, n in items:
        print('  %s  %s  %s  %s' % (pad(num, 4), pad(st, 8),
                                    pad(name, wmax), str(n).rjust(6)))
    print('')


def cmd_screen():
    cmd_list()
    print('')
    print(THIN)
    print('   1-N   toggle a group        A  all on        N  all off')
    print('   S     rebuild and launch     E  edit the config')
    print('   Q     quit')
    print(THIN)
    print('')
    say('ask_input')


def cmd_toggle(num):
    rows = read_ini()
    for i, (n, on, name) in enumerate(rows):
        if n == num:
            new = '0' if on == '1' else '1'
            rows[i] = (n, new, name)
            print('  %s -> %s : %s' % (name,
                                       'on' if new == '1' else 'off',
                                       'enabled' if new == '1' else 'disabled'))
            save(rows)
            return 0
    print('  [!] no group numbered %s' % num)
    return 1


def cmd_setall(v):
    rows = read_ini()
    save([(n, v, name) for n, on, name in rows])
    print('  all %s' % ('on' if v == '1' else 'off'))
    return 0


def cmd_status():
    rows = read_ini()
    on = [r for r in rows if r[1] == '1']
    tot = 0
    for num, _, _name in on:
        tot += count_files(group_dir(num))
    print('  enabled %d / %d groups, %d files' % (len(on), len(rows), tot))
    if not os.path.isdir(STAGE):
        print('  (the overlay folder has not been built yet)')
        return 0
    print('  _enabled now holds %d files' % count_files(STAGE))
    return 0


def _rmtree_hard(path):
    """
    Remove a tree that is made of hard links.

    shutil.rmtree(ignore_errors=True) can leave the whole tree behind on
    Windows; each leftover link still costs a directory entry, and on this
    project that was 796 files pretending to be 446 MB.  Unlink them one by
    one first (that only drops the link count, the mods/ originals are fine),
    then remove the empty directories.
    """
    if not os.path.isdir(path):
        return True
    failed = 0
    for r, _dirs, fs in os.walk(path):
        for f in fs:
            try:
                os.unlink(os.path.join(r, f))
            except OSError:
                failed += 1
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass
    if os.path.isdir(path):
        for r, _dirs, _fs in os.walk(path, topdown=False):
            try:
                os.rmdir(r)
            except OSError:
                pass
    gone = not os.path.isdir(path)
    if not gone or failed:
        print('  [ i ] could not clear the old overlay folder completely '
              '(%d files busy). Delete it by hand: %s' % (failed, path))
    return gone


def cmd_build():
    rows = read_ini()
    enabled = [num for num, on, _ in rows if on == '1']

    print(MESSAGES['build_head'])

    if not enabled:
        print('  [!] nothing is enabled -- the game will be vanilla.')

    # Move it aside first (that nearly always succeeds), then unlink the links.
    if os.path.isdir(STAGE):
        old = STAGE + '_old'
        _rmtree_hard(old)
        if os.path.isdir(old):
            old = STAGE + '_old_' + str(os.getpid())
        try:
            os.rename(STAGE, old)
        except OSError as e:
            print('  [!] cannot move the old folder aside: %s' % e)
            return 1
        _rmtree_hard(old)

    os.makedirs(STAGE, exist_ok=True)

    linked = 0
    copied = 0
    conflict = []
    missing = []

    for num in enabled:
        d = group_dir(num)
        if not d:
            missing.append(num)
            continue
        for r, _dirs, fs in os.walk(d):
            for f in fs:
                src = os.path.join(r, f)
                rel = os.path.relpath(src, d)
                dst = os.path.join(STAGE, rel)
                if os.path.exists(dst):
                    conflict.append(rel)
                    continue
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                try:
                    os.link(src, dst)
                    linked += 1
                except OSError:
                    try:
                        shutil.copy2(src, dst)
                        copied += 1
                    except OSError as e:
                        print('  [!] copy failed %s : %s' % (rel, e))

    print('  overlay rebuilt: %d files (hard links %d, copies %d)'
          % (linked + copied, linked, copied))
    if missing:
        print('  [!] no folder for group(s): %s' % ', '.join(missing))
    if conflict:
        print('  [!] %d files are claimed by more than one group '
              '(the first one won):' % len(conflict))
        for c in conflict[:5]:
            print('        %s' % c)

    tl = os.path.join(STAGE, 'Pack', 'TitleBG.pack')
    if os.path.exists(tl):
        print('  [OK] Pack/TitleBG.pack is mounted (the player model lives in it)')
    else:
        print('  [ i ] TitleBG.pack not mounted -- the player model will not apply.')

    others = [n for n in enabled if n != '10']
    if others and '10' not in enabled:
        print('')
        print('  [!!] DANGER: the core-data group is off but %d other groups are on.'
              % len(others))
        print('       The ResourceSizeTable in it is the size registry for every')
        print('       mod file. Without it the game allocates from the file sizes')
        print('       and crashes on load (c0000005).')
        print('       Put group 10 back on.')
    elif not enabled:
        print('')
        print('  [ i ] nothing enabled -- this launch is vanilla.')

    return 0


def main():
    set_title('The Legend of Zelda: Breath of the Wild -- MOD console')

    if len(sys.argv) < 2:
        cmd_screen()
        return 0
    a = sys.argv[1].lower()

    if a == 'screen':
        cmd_screen()
    elif a == 'list':
        cmd_list()
    elif a == 'status':
        return cmd_status()
    elif a == 'msg' and len(sys.argv) > 2:
        say(sys.argv[2])
    elif a == 'toggle' and len(sys.argv) > 2:
        return cmd_toggle(sys.argv[2])
    elif a == 'on' and len(sys.argv) > 2:
        rows = read_ini()
        save([(n, '1' if n == sys.argv[2] else on, name) for n, on, name in rows])
        print('  group %s on' % sys.argv[2])
    elif a == 'off' and len(sys.argv) > 2:
        rows = read_ini()
        save([(n, '0' if n == sys.argv[2] else on, name) for n, on, name in rows])
        print('  group %s off' % sys.argv[2])
    elif a == 'setall' and len(sys.argv) > 2:
        return cmd_setall(sys.argv[2])
    elif a == 'build':
        return cmd_build()
    elif a == 'init':
        write_ini(DEFAULT_MODS)
        print('  wrote %s' % INI)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
