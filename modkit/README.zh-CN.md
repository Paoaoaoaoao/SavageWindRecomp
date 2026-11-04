# Savage Wind MOD 控制台

[English](README.md) · **简体中文**

一个给 [Savage Wind Recomp](https://github.com/Revivedx/SavageWindRecomp)
用的 **RomFS overlay MOD 分组开关**。

> 本仓库**不含任何游戏文件，也不含任何 MOD 文件**，只有开关本身。
> 授权说明见[最后一节](#授权与署名)。

## 为什么需要这层东西

Savage Wind 读 MOD 只认一个环境变量：

```bat
set SAVAGEWIND_ROMFS_OVERLAY=<文件夹>
```

这个文件夹的目录结构和游戏的 RomFS 一样：里面有的文件就替换游戏的文件，游戏
没有的文件会加进它的文件表。这套机制是能用的，但它只接受**一个**目录，也没有
"开/关"的概念。于是每换一种 MOD 组合都要手工拼一次，想对比"装 MOD / 不装
MOD"就得来回搬几百个文件。

这个工具把你的 MOD 分成组，那个唯一目录由它来拼：

```
  mods/
    01_主角/        ┐
    02_服装/        │  你的分组，一组一个文件夹，内容就是 RomFS 的目录结构
    03_新增套装/    │
    ...            │
    10_核心数据/    ┘
  _enabled/        <- 拼装结果（硬链接），每次启动都重建
```

它不修改游戏，只做两件事：写出那一个文件夹，然后带着两个环境变量把游戏拉起来。

## 环境要求

| | |
|---|---|
| 游戏 | **《旷野之息》1.9.0** —— Savage Wind 只认这个版本 |
| 构建 | 支持 `SAVAGEWIND_ROMFS_OVERLAY` 的构建；上游 `main` 和 `test` 都有 |
| 系统 | Windows（启动器是 `.bat`；`modtool.py` 本身是纯 Python，放哪都能跑）|
| Python | `PATH` 里要有 Python 3。**两个启动器每次运行都需要它**，因为启动前都要重建 `_enabled/`。`mod_console.bat` 也接受放在 `_tools\python\python.exe` 的便携版 |

## 上手

1. 把这个文件夹放哪都行，它不关心游戏装在哪里。
2. 把 MOD 放进 `mods/`，一组一个文件夹，命名 `NN_名字`。
   里面的目录结构必须和 RomFS 对应 —— 见[一个组里放什么](#一个组里放什么)。
3. 告诉它游戏在哪，两种办法：

   ```bat
   set SAVAGEWIND_HOME=D:\Games\SavageWind
   ```

   或者把这个文件夹放在 `savagewind.exe` 旁边，或者放在包含
   `build\savagewind.exe` 的那层目录旁边。这两种位置它会自己探测。
4. 双击 `mod_console.bat`，用数字开关，按 `S` 启动。

`launch_game.bat` 把后两步合成一步，按 `mods_config.ini` 里**当前**的开关状态
启动 —— 它不是"全部打开"。

从桌面快捷方式直接启动游戏会绕过环境变量和工作目录，游戏会原样启动，看起来
就像 MOD 坏了。这就是下面的 **坑 5**。

## 控制台

| 按键 | 作用 |
|---|---|
| `1`..`N` | 切换该组开关 |
| `A` | 全部打开 |
| `N` | 全部关闭 |
| `S` | 重建 `_enabled/` 并启动 |
| `E` | 用记事本打开 `mods_config.ini` |
| `Q` | 退出 |

也可以直接调用引擎：

| 命令 | |
|---|---|
| `python modtool.py list` | 列出所有组和状态 |
| `python modtool.py toggle <n>` / `on <n>` / `off <n>` | 单个组 |
| `python modtool.py setall <1\|0>` | 全部 |
| `python modtool.py build` | 重建 `_enabled/` |
| `python modtool.py status` | 当前实际生效的数量 |
| `python modtool.py init` | 写一份初始的 `mods_config.ini` |

## 一个组里放什么

组内的相对路径要和 RomFS 根一一对应。下表是这套控制台开发时用的分组（编号就是
`mods_config.ini` 里那份，内容你自己填）：

| # | 分组 | 放什么 |
|---|---|---|
| 1 | 主角模型 | `Pack/TitleBG.pack`（外加 `Model/Link.Tex1.sbfres`）。注意主角**在 pack 里面**，不在松散层 |
| 2 | 服装体型适配 | `Actor/Pack/*.sbactorpack`、`Model/*.sbfres`，让女性服装不穿模 |
| 3 | 新增服装套装 | 新增的 `Armor_*` actor、模型和 `UI/` 图标 |
| 4 | 林可儿 NPC | `Actor/`、`Model/`、`Event/`，NPC 替换 |
| 5 | 武器 | `Actor/Pack`、`Model/`、`UI/` |
| 6 | 敌人 | `Actor/Pack` |
| 7 | 物品与场景 | `Actor/Pack`、`Model/` |
| 8 | 音效 | `Sound/Resource/**`（`.bfstm`、`.bars`） |
| 9 | 演出事件 | `Event/**` |
| 10 | **核心数据** | `Actor/ActorInfo.product.sbyml`、`System/Resource/ResourceSizeTable.product.srsizetable`、`Pack/Bootup_<语言>.pack` |

第 10 组不是可选项。见 **坑 1**。

引擎的几条规则，全是踩出来的：

* 编号取文件夹名里第一个 `_` 之前的那段：`01_主角` → 1，`10_核心数据` → 10，
  `10` → 10。
* **`mods_config.ini` 里的编号不要写前导零。** 写成 `MOD|01|...` 之后按 `1` 会
  回答 `no group numbered 1`，只有输入 `01` 才行 —— 开关是**按字符串**比编号的，
  而找文件夹是按数值比的。
* 两个文件夹用同一个编号：按名字排序取第一个，另一个**静默不用**。
* 两个组里有同一个路径：先启用的组赢，另一个文件被跳过。构建时会列出这些冲突，
  每次都要看一眼。
* `mods_config.ini` 是 UTF-8。改 `1`/`0` 就行，`|` 分隔符别动，一组一行，整行
  删掉就是隐藏该组。名字随便写，只是给你自己看的。
* 某组的文件夹不存在时，`build` 会提示，但不算失败。

## 装一个下载来的 MOD

1. **先拿到松散文件。** 这个工具读的是文件夹，不读 `.bnp`（见
   [BNP / BCML](#bnp--bcml)）。
2. **确认 RomFS 相对路径。** 打开包，里面会看到 `Actor/`、`Model/`、`Pack/`、
   `Sound/` …… 和上表一样的名字。那一层就是 RomFS 根，它下面的结构原样保留。
3. **放进 `mods/NN_名字/`**，目录结构一丝不改。
4. **在 `mods_config.ini` 里加一行**，或者把文件夹名改成已有编号直接复用。
5. **检查两个登记表。** 如果这个 MOD 加了新 actor（服装、武器、敌人），它必须
   自带、或者被合并进核心组的 `ActorInfo.product.sbyml`；如果它的文件比原版大，
   核心组的 ResourceSizeTable 必须能覆盖到。**大多数完整 MOD 包会自带这两个文件，
   但不要让第二个组再带一份**（见 **坑 1**、**坑 8**）。

这两个登记表**不能手工合并**。用生成它们的工具去合（BCML 会替你合 `ActorInfo`
和 RSTB），把合好的结果放进第 10 组。

## 会踩的坑

按"浪费时间的程度"排序。前四条是崩溃，后面都是"静悄悄不生效"。

### 坑 1. 载入时 `c0000005`：ResourceSizeTable 缺失或不对

`System/Resource/ResourceSizeTable.product.srsizetable` 是**每一个** RomFS 文件的
尺寸登记表，游戏按它分配内存。MOD 的文件比原版大，如果 overlay 没有一起替换这张
表，游戏按旧尺寸分配、把新内容拷进去、再读就越界了 —— `c0000005`，通常死在读盘
画面。

* 只要开着别的组，核心数据组就必须开着。违反这条时控制台会打一大段警告，那不是
  装饰。
* **这张表只能有一个组携带。** 两个组各带一份，先启用的赢，另一组登记的尺寸全部
  作废 —— 同样崩，而且更难查，因为 `build` 只把它当成普通的路径冲突报出来。
* 表必须和周围的文件来自同一个游戏版本（1.9.0）。旧版本的表比没有更糟：格式对、
  数字全错。

### 坑 2. 载入时 `c0000005`：HUD 图标字补丁撞上被替换的表

这条不是你的问题，但它解释了启动器里那行看起来莫名其妙的设置。

Savage Wind 会改写 `Pack/Bootup.pack`，把屏幕上的按键提示换成手柄图标字体，并把
这个包变大了多少登记进 ResourceSizeTable。而当 overlay 替换了那张表时，这条登记
会被跳过：

```c
// runtime/services/fs.c, hud_letters_patch()
R->grown[R->ngrown++] = (GrownFile){"Layout/Common.blarc", nn - an};   // 第 849 行

// runtime/services/fs.c, rstb_patch()
if (overlay_file(rstb_path, host, sizeof host)) {
    LOG("[fs] voices: the overlay folder replaces the ResourceSizeTable: ...");
    return;                                    // 第 999 行：上面那条永远写不进表
}
```

*（行号按上游 `test` 分支 `60f0b68` 计；万一漂了，按函数名去搜。）*

包在内存里被改大并直接从内存提供，而表里写的还是旧尺寸 → 和坑 1 一样的越界。
所以两个启动器都设了：

```bat
set SAVAGEWIND_NO_HUD_LETTERS=1
```

代价是：HUD 的按键提示保留游戏自带的 A/B/X/Y 字母，不用图标字体。这是目前唯一
的取舍；上游哪天把登记挪到提前返回之前，这行就可以删。

触发条件要说准：需要 overlay 替换了**那张表**、但**没有**替换
`Pack/Bootup.pack`。如果 MOD 连 `Bootup.pack` 一起替换，根本走不到登记那一步
（同时也拿不到图标提示，因为包被换掉了）。

### 坑 3. 该用硬链接的地方别用符号链接

`_enabled/` 里全是**硬链接**。不要换成符号链接、`mklink /D` 目录联接，或者
`subst` 虚拟盘。运行时是按路径打开 overlay 文件的，遇到符号链接会跟过去，实测
直接 `c0000005`。只有硬链接和真实拷贝是安全的，文件系统不给链接时引擎会自动
退化成拷贝。

（这条只约束**你自己的** overlay。游戏自己的 `extracted/aoc1` 那类链接是游戏
的事，不受影响。）

### 坑 4. `c0000005` 来自没写完的 pack

手工拷一个 140 MiB 的 `.pack`，中途打断，再挂上去，就是个截断的包：游戏读到
文件头，信任一张指向文件末尾之外的表，然后崩。`_enabled/` 只做链接，不会截断；
但如果你手工往 `mods/` 里拷文件，等它拷完再启动。

### 坑 5. 启动方式不对，所以什么都没生效

游戏启动的那一刻，**两件事同时成立**才会读到 MOD：

1. `SAVAGEWIND_ROMFS_OVERLAY` 指向 `_enabled/`；
2. 进程的工作目录是游戏的数据目录。

桌面快捷方式、Steam、在资源管理器里双击 `savagewind.exe`，这两条都不成立，游戏
就是原版。"MOD 又坏了"之前先查这一条，别急着动文件。两个启动器都做了这两件事
（`set` 之后再 `cd /d "%GAME%"`）。

### 坑 6. 能进游戏但毫无变化：把松散文件塞进 pack 里

RomFS 文件表登记的是 pack，不是 pack 里面的东西。所以这种写法永远读不到：

```
mods/01_主角/Pack/TitleBG.pack/Model/Link.sbfres      <- 被忽略
```

要改 pack 里面的东西，必须**整个替换这个 pack**：

```
mods/01_主角/Pack/TitleBG.pack                        <- 正确
```

`Bootup.pack`、`AocMainField.pack`、所有 `.pack` 和 `.sarc` 都一样。这也正是
主角模型要占 140 MiB 的原因：它只在 `TitleBG.pack` 里，改一个文件就是整包。

### 坑 7. 新增文件只能放进游戏已有的目录

游戏 RomFS 里没有的文件，会在启动时被加进文件表（`add_new_files()`），但
**父目录必须已经在游戏 RomFS 里存在**。否则文件被跳过，只留一行很不起眼的日志，
不报错：

```
[fs] overlay file Actor/Pack/MyNew/Armor_999.sbactorpack: directory not in the game's RomFS, skipped
```

可以往 `Actor/Pack/`、`Model/`、`Sound/Resource/Stream/`、`Event/` 里加文件，
但不能凭空造出 `Actor/Pack/MyNew/`。

相关的一条：**新增文件区分大小写。** 游戏是按名字字节算哈希去查的，
`Model/link.sbfres` 和 `Model/Link.sbfres` 是两个不同的条目，大小写错了就是
查不到。而"替换"反而宽容 —— Windows 自己解析路径。于是会出现很迷惑的现象：
替换生效，新增不生效。

### 坑 8. 两个组有同一路径：先启用的赢，而且不报错

构建时遇到某个路径已被占用就跳过。它会列出这些冲突：

```
  [!] 3 files are claimed by more than one group (the first one won):
        Actor/Pack/Armor_200.sbactorpack
```

看到这个就说明分组有重叠，其中一组没完全生效。把重叠部分并进一个组，别依赖顺序。
真正致命的是那两个登记表：`Actor/ActorInfo.product.sbyml` 和
ResourceSizeTable。对它们来说，"先启用的赢"意味着另一个 MOD 的 actor 或尺寸
根本不存在，然后游戏会在一个它知道名字、却查不到尺寸的文件上出事。

### 坑 9. 会静悄悄失效的游戏设置

如果 overlay 替换了某个内置补丁要改的 pack，那个补丁会直接跳过自己。不报错、
不打日志，设置就是没反应：

| overlay 替换了 | 丢掉的 |
|---|---|
| `Pack/TitleBG.pack` | **视频 → 雾气（Haze）** 滑块失效（`haze_patch()` 改的是这个包里的 `WorldMgr/normal.bwinfo`）|
| `Pack/Bootup.pack` | HUD 图标字体补丁（预期内，坑 2 就是为了避开它）|
| `System/Version.txt` | 标题界面的 `Savage Wind 1.9` 版本字样 |
| `System/AocVersion.txt` 或 `Pack/AocMainField.pack` | 你什么都没丢 —— 但游戏会**以为**你的 RomFS 已经合并了 DLC，转而按 `Aoc/0010/...` 的条目去放大尺寸。这两个文件千万别误打包进来。|

第一行会命中所有主角模型 MOD，因为模型就在 `TitleBG.pack` 里。绕不过去：pack 是
替换的最小单位。要么模型，要么雾气滑块，二选一。

### 坑 10. DLC 内容在 overlay 里只有一处固定位置

如果你的构建挂载了 DLC（`extracted/aoc1`、`aoc2`……），追加内容的文件放这里：

```
_enabled/aoc/0010/<DLC RomFS 里的路径>
```

不论第几个 DLC，`0010` 都是**写死的**，不是索引值 —— 这是 Wii U 的目录习惯，
运行时就是这么读的（`fs.c`：`ov_sub = "aoc/0010/"`）。另外要注意：上游的
**正式版根本不挂 DLC**，`main` 里没有任何追加内容代码（`misc.c` 写着
`aoc:u (no DLC)`），只有 `test` 有，最多 8 个。

### 坑 11. 硬链接 = 一份数据两个名字

* 通过 `_enabled/` 编辑文件，等于改 `mods/` 里的原文件 —— 同一份字节。别在
  `_enabled/` 里"修东西"。
* 删 `_enabled/` 永远不动 `mods/`，链接只是少了个名字。
* 在 `mods/` 里**替换**文件（覆盖保存、解压新版本）会断开链接，`_enabled/` 还
  留着旧字节。重建。
* 文件系统不支持硬链接时引擎改成拷贝，那 `_enabled/` 就实打实占一份空间 ——
  450 MB 变 900 MB。
* `_enabled/` 是一次性的。别往里放自己的东西，每次启动都会被删掉重建。

### 坑 12. Windows 和启动器

* `.bat` 必须**纯 ASCII + CRLF 换行**。`cmd` 按系统 ANSI 代码页读脚本，含中文的
  `.bat` 换台机器就变乱码。所有界面文字都从 `modtool.py` 出。你要改 bat，请守住
  这条。仓库根目录写的是 `* text=auto eol=lf`，所以 `modkit/.gitattributes`
  专门把 `eol=crlf` 拉回来。
* Python 的找法依次是 `where python`、`where py -3`、
  `_tools\python\python.exe`，没有写死任何用户路径。
* 控制台文字**没有**走 `print()`。CP936 控制台下 Python 3.13 仍然报
  `sys.stdout.encoding == "utf-8"`，写出去的是 UTF-8 字节，而 `cmd` 按 CP936
  解码 —— 满屏乱码。引擎改用 `WriteConsoleW` 绕过代码页。别"顺手简化"回 `print`。
* **崩溃时窗口会先关掉，你看不到报错。** 要看结尾就从一个已经开着的 `cmd` 里
  启动 `mod_console.bat`。日志去哪了取决于构建：
  * 控制台构建 → 直接打到终端，不落文件；
  * GUI 构建（正式版）→ 写在 exe 旁边的 `savagewind.log`。

### 坑 13. 重建时清不掉 `_enabled`

Windows 不肯删正在被打开的文件。上一次运行还没退干净时，`_enabled` 挪不走，
构建会告诉你多少个文件被占用。关掉游戏再重建。

引擎之所以先逐个 `unlink` 再删目录，就是为了这个：直接递归删除可能在 Windows 上
留下整整 796 个文件的树，而 `shutil.rmtree(ignore_errors=True)` 还照样返回成功，
下一次构建就悄悄沿用了旧文件。

## 怎么确认真的挂上了

日志会按顺序说：

| 日志行 | 含义 |
|---|---|
| `[fs] overlay: 622 romfs files replaced` | 这么多个游戏文件改成从你的文件夹读（数字来自一套 796 文件的 MOD）|
| `[fs] overlay: 175 new romfs files` | 游戏本来没有、被加进文件表的文件数 |
| `[fs] overlay file X: directory not in the game's RomFS, skipped` | 有新增文件没落地 —— **坑 7** |
| `[fs] voices: the overlay folder replaces the ResourceSizeTable: N bigger banks left to it` | MOD 替换了尺寸表；带 RSTB 的 MOD 出这行是正常且必然的 |
| `[fs] romfs index: N files` | 最终文件表的大小 |

完全没有 `overlay:` 开头的行，说明环境变量没生效 —— **坑 5**，或者 `_enabled/`
是空的。

## BNP / BCML

这个工具要的是**松散文件**，目录结构得和 RomFS 一致。它不读 `.bnp`（BCML）包，
Savage Wind 也不读 —— 上游那个 BNP 管线至今还是一个没合的 PR（#430）。手上只有
`.bnp` 的话，先用做它的工具解开，再把结果按 RomFS 结构放进 `mods/NN_名字/`。

## 授权与署名

**本仓库不含任何游戏资源，也不含任何 MOD 资源。** 只有开关：`modtool.py`、两个
`.bat`、一份配置示例、这些文档。

开发这套东西时使用的 MOD 是 **lynard killer** 与 Linkle Project 制作的
**林可儿（Linkle）** 模组，发布在 GameBanana：

* <https://gamebanana.com/mods/168235> —— Linkle Mod（原版）
* <https://gamebanana.com/mods/406768> —— The Linkle Mod 3.0

该作品使用 **CC BY-NC-ND 4.0**（署名-非商业性使用-禁止演绎）授权。这里的关键是
**ND（禁止演绎）**：它不允许分发修改过的副本，而把一份下载包拆成若干组，**就是**
修改过的副本。所以本仓库不以任何形式转载这些 MOD 文件 —— 整包不转，拆开也不转。
请自行到作者页面下载，在本地自己整理。

这些文件里同时含有任天堂的原始素材，任何地方都不要转载从游戏里提取出来的文件。

Savage Wind Recomp 本身是 MIT 授权，版权归 Revivedx 与 Savage Wind Recomp 贡献者、
以及 Peiikai（LAS Recomp）。详见仓库的 `LICENSE`。

## 目录结构

```
  mod_console.bat        开关界面
  launch_game.bat        重建 + 启动，无界面
  _tools/modtool.py      引擎
  mods_config.ini        分组清单与开关状态
  mods/                  你的分组（这里是空的，见 mods/README.md）
  _enabled/              拼装出来的 overlay（自动生成）
```

`modtool.py` 用自己的路径反推根目录，整个文件夹可以整体搬走 —— 但它必须待在
`_tools/` 里，和 `mods/`、`mods_config.ini` 保持同级。
