# Miku Mini：Codex 原动作轻量版

直接作为 Codex 自定义宠物使用。成品只需 `pet.json` 和 `spritesheet.webp`，播放时无需 Python、Node、独立桌宠程序或 AI 模型。

![新版向右移动](docs/native-previews/running-right.gif)
![新版向左移动](docs/native-previews/running-left.gif)

## 本次修复

用户要求保留此前原画动作，撤回程序生成的腿部步态。当前左右移动两行直接使用原画八格与原来的列顺序；可见RGBA逐像素相同，没有重画、腿部变形、缩放或光流补帧。

此前32帧动画WebP把同一移动姿势复制到全部八列，图片内部的1.28秒周期与Codex的1.06秒周期独立。恢复原动作时继续保留静态图集，避免重新引入额外图片动画时钟和大型动画文件的解码负担。移动中不再使用RIFE合成帧，保留原画自身的清晰度。

图集为无损静态v2 WebP：1536×2288、8×11、每格192×208。文件约3.15 MB，之前动画版为44.3 MB。九种标准动作行保留；待机、工作、等待和审阅保留此前静态微动作备用版，16个注视方向保留原画。没有调用付费绘图。

## 安装与显示更新

Windows：解压安装包，双击 `Install-Codex.cmd`。安装会备份旧文件，再写入 `$CODEX_HOME/pets/miku-mini`；未配置时为 `%USERPROFILE%\.codex\pets\miku-mini`。

手动安装：在该目录放入 `pet.json` 和 `spritesheet.webp`。仓库中的成品图集位于 `assets/spritesheet.webp`。

安装后，在 Codex 的宠物设置中刷新并选择 **Miku Mini · 原动作轻量版**。如果应用仍持有旧图片，请保存任务后完整退出并重新打开 Codex。替换本地文件或更新 GitHub 不保证正在运行的窗口立即重载。

安装脚本只写文件，不操作或重启 Codex。备份位于脚本旁边的 `backups/`；Python 安装器可指定备份目录。恢复时将备份的两个文件复制回宠物目录，然后重新加载。

本版默认已是静态图集，旧 `-Static` 参数保留兼容。图片无独立动画时间轴，宿主的减少动态效果设置可以让显示保持单格。

## 效果与边界

文件检查确认原始移动姿势、列顺序和可见像素保留，无程序腿部动作残留。隔离headless Edge验证最终图集的CSS/data-URL显示、左右八格、1.06秒周期、起停、反向、减少动态效果和16个注视格。

当前检查过的Codex 26.930.4958.0每格通常停留120ms，末格220ms，移动默认三遍后转待机；松手或反向可立即切换状态。这种低换格频率本身会有顿感。轻量图集和去掉合成帧可降低额外负担、去除合成帧的变形，但不能把宿主播放提高到30/60fps，也不能保证任意时刻停止都走完一步。原动作的领步特点按用户要求保留。

真实 Codex 窗口内的观感尚未在本次制作中确认；浏览器预览和文件检查不等于用户窗口实测。

## 验证与重建

- [图集验证](docs/native-validation.json)：静态图集、透明空格、保留原画、独立八格与文件哈希。
- [播放验证](docs/native-browser-validation.json)：最终资产的隔离浏览器渲染与本机宿主时序模型。
- [原动作恢复视觉 QA](docs/original-action-visual-qa.json)：当前独立检查结果及素材哈希。
- [历史程序步态记录](docs/gait-repair-progress.md)：已撤回的动作方案，供历史追溯。

原始移动行在`assets/source-spritesheet.webp`，静态微动作基础图集在`assets/native-micro-base.webp`。普通重建运行`tools/build_native.py`，需要Pillow和NumPy；构建会验证移动行可见像素与原图相同。安装和打包检查最终文件、浏览器验证及原动作视觉QA的哈希一致。

`tools/bake_walk_rig.py`及`assets/walk-gait/`只保留为历史实验，当前构建不使用程序腿部动作。重新发布时应重新运行文件验证、隔离浏览器验证和原动作视觉QA。

预览：运行 `tools/serve_preview.py --port 8766`，访问 `/native-preview.html`。运行 `tools/verify_native.cjs` 需要 Node、Playwright 和 headless Edge，且预览服务已经启动。

历史独立桌宠代码仍在仓库中，属于较早版本；本安装包只提供 Codex 内置素材。来源与许可证见 [THIRD-PARTY.md](THIRD-PARTY.md)，角色原画继续沿用项目原有作品集条款。
