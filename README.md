# Miku Mini：Codex 原生步态版

直接作为 Codex 自定义宠物使用。成品只需 `pet.json` 和 `spritesheet.webp`，播放时无需 Python、Node、独立桌宠程序或 AI 模型。

![新版向右移动](docs/native-previews/running-right.gif)
![新版向左移动](docs/native-previews/running-left.gif)

## 本次修复

旧移动素材长期由同一只脚领步，缺少另一半步态。此前动画 WebP 还把同一姿势复制到一行全部八列，图片内部的1.28秒周期与 Codex 的1.06秒周期独立，切换动作时可能截断脚步。

本版复用原画的身体和腿部纹理，用两个独立的腿部控制器补齐前伸、承重、回收和换脚，烘焙为左右各八格。腿部采用连续网格变形，减少分段图块的连接缝；左移按格镜像，不反转动作顺序。制作方式由用户明确选择，不使用付费图像生成。

图集改为普通静态 v2 WebP：1536×2288、8×11、每格192×208。图片本身不再包含第二个播放时钟，动作由 Codex 换格推进。文件约2.65 MB，之前为44.3 MB。九种标准动作行保留；待机、工作、等待和审阅使用此前静态微动作备用版的关键帧；16个注视方向保留原画。

## 安装与显示更新

Windows：解压安装包，双击 `Install-Codex.cmd`。安装会备份旧文件，再写入 `$CODEX_HOME/pets/miku-mini`；未配置时为 `%USERPROFILE%\.codex\pets\miku-mini`。

手动安装：在该目录放入 `pet.json` 和 `spritesheet.webp`。仓库中的成品图集位于 `assets/spritesheet.webp`。

安装后，在 Codex 的宠物设置中刷新并选择 **Miku Mini · 原生步态版**。如果应用仍持有旧图片，请保存任务后完整退出并重新打开 Codex。替换本地文件或更新 GitHub 不保证正在运行的窗口立即重载。

安装脚本只写文件，不操作或重启 Codex。备份位于脚本旁边的 `backups/`；Python 安装器可指定备份目录。恢复时将备份的两个文件复制回宠物目录，然后重新加载。

本版默认已是静态图集，旧 `-Static` 参数保留兼容。图片无独立动画时间轴，宿主的减少动态效果设置可以让显示保持单格。

## 效果与边界

文件检查确认左右脚有完整交替，首尾没有大幅位置或比例跳变。隔离 headless Edge 验证了最终图集的 CSS/data-URL 显示、左右八格、1.06秒周期、起停、反向、减少动态效果和16个注视格。

仍有轻微屈膝折线感，首尾附近两脚重叠较多。当前检查过的 Codex 26.930.4958.0 默认把移动播三遍后转待机，松手或反向可立即切换状态，末格固定停留220ms。仅更换图集无法保证任意时刻停止都走完最后一步，也不能提高宿主写死的换格频率。

真实 Codex 窗口内的观感尚未在本次制作中确认；浏览器预览和文件检查不等于用户窗口实测。

## 验证与重建

- [图集验证](docs/native-validation.json)：静态图集、透明空格、保留原画、独立八格与文件哈希。
- [播放验证](docs/native-browser-validation.json)：最终资产的隔离浏览器渲染与本机宿主时序模型。
- [步态视觉 QA](docs/gait-visual-qa.json)：独立检查结果、接受的轻微问题与批准素材的哈希。
- [修复记录](docs/gait-repair-progress.md)：现成资源对照、缺陷及制作过程。

已批准的八格行在 `assets/walk-gait/`，静态微动作基础图集在 `assets/native-micro-base.webp`。普通重建运行 `tools/build_native.py`，需要 Pillow 和 NumPy。

重新烘焙步态：`tools/bake_walk_rig.py --mirror-left --outdir assets/walk-gait`。修改参数或原画后，必须重新进行独立视觉检查并更新批准哈希，才能组装发布。

预览：运行 `tools/serve_preview.py --port 8766`，访问 `/native-preview.html`。运行 `tools/verify_native.cjs` 需要 Node、Playwright 和 headless Edge，且预览服务已经启动。

历史独立桌宠代码仍在仓库中，属于较早版本；本安装包只提供 Codex 内置素材。来源与许可证见 [THIRD-PARTY.md](THIRD-PARTY.md)，角色原画继续沿用项目原有作品集条款。
