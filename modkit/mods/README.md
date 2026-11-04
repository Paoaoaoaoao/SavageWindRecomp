# Put your mod groups here · 把你的 MOD 分组放在这里

**English** — each subfolder is one switchable group, named `NN_something`
where `NN` matches `mods_config.ini`. The contents mirror the RomFS root: same
paths the game reads, relative to it. Nothing else in this folder is committed;
`mods/*` is gitignored on purpose so nobody pushes 450 MB of someone else's
assets by accident.

**中文** —— 每个子文件夹是一组，命名 `NN_名字`，`NN` 和 `mods_config.ini`
对应。里面的目录结构和 RomFS 根一致（路径就是游戏读取时的相对路径）。
除本文件外，这个目录整个被 `.gitignore` 挡掉，避免有人顺手把别人的 450 MB
素材提交上来。

## Read this first · 先看这几条

Full details in [`../README.md`](../README.md) (English) or
[`../README.zh-CN.md`](../README.zh-CN.md) (中文)。最容易崩的四条：

1. **The core-data group is mandatory.** `ResourceSizeTable.product.srsizetable`
   is the size registry for every RomFS file. Without it the game allocates from
   the old sizes and dies with `c0000005`. Only **one** group may ship it.
   **核心数据组必开**，而且只能有一个组带这张表，否则载入时 `c0000005`。
2. **A pack is replaced whole.** `Pack/TitleBG.pack/Model/…` is never read; ship
   the entire `.pack`. **pack 只能整包替换**，塞在 pack 里的松散文件永远读不到。
3. **Added files need an existing parent directory.** `Actor/Pack/NewThing/` is
   silently skipped unless the game already has that directory, and the name is
   matched case-sensitively. **新增文件的父目录必须是游戏里已有的**，且大小写敏感。
4. **Two groups, same path: the first wins, silently.** Especially for
   `Actor/ActorInfo.product.sbyml` and the RSTB — merge those, don't stack them.
   **同一路径两组都给，先启用的赢**，两个登记表要合并而不是叠加。
