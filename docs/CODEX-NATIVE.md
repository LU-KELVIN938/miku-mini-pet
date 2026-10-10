# Miku Mini：Codex 内置流畅版

此版本直接作为 Codex 自定义宠物使用。运行时仅加载 `pet.json` 与 `spritesheet.webp`，无需 Python、Node、桌宠程序或 AI 模型。

## 安装与重新加载

Windows：解压安装包后双击 `Install-Codex.cmd`。它先备份旧文件，再安装到 `$CODEX_HOME/pets/miku-mini`；未设置该环境变量时使用 `%USERPROFILE%\.codex\pets\miku-mini`。

也可以手动创建上述目录，把 `pet.json` 和 `spritesheet.webp` 放进去。仓库里的图集位于 `assets/spritesheet.webp`；安装包的两个文件就在根目录。

**安装后完整退出并重新打开 Codex，在宠物选择菜单中选择「Miku Mini · 内置流畅版」。** 正在运行的应用可能继续持有此前加载的图片；更新 GitHub 或替换文件不会自动刷新它。请先确保正在运行的任务已保存。

没有自动操作 Codex 窗口或重启应用。截图和本地素材播放测试来自隔离的浏览器；未在用户当前 Codex 窗口中读取或检查画面。

## 实际改动

- 从原来的 Codex 待机帧拆出头部、身体、双马尾与眼睛，保留原来的角色样子；离线烘焙呼吸、眨眼与小幅状态姿势。
- 使用通过视觉检查的左右移动、挥手、跳跃补帧。两个有瑕疵的补帧继续保留原姿势。
- 保留原失败反应；16 个注视方向沿用原画，加入脚部固定的轻微呼吸，未使用的格子保持透明。
- 自包含动画 WebP：1536×2288、8×11、192×208，32 个图集画面，每画面 80 毫秒，循环 2.56 秒；图像动画目标为 12.5 帧/秒，不是 60 帧承诺。

## 为什么能在内置宠物里播放

安装的 Codex 26.930.4958.0 通过图片 data URL 和 CSS 背景显示自定义宠物。静态图集的动作帧数与间隔写在程序里，待机会放慢六倍。本版本让 WebP 图片自身包含连续画面，同一动作行的已使用格子在每个时刻显示同一姿势，避免应用切换列时打断连续动画。

保留九种标准动作行、16 个方向及 `spriteVersionNumber: 2`，无需修改 Codex 程序。浏览器测试覆盖相同 data URL、背景位置和播放间隔；不是对用户当前窗口的实测，也不能保证未来版本继续支持相同显示方式。

运行状态的呼吸等画面循环为 2.56 秒；左右移动循环 1.28 秒，挥手 0.64 秒，跳跃 1.28 秒。宿主动作切换时间保持由 Codex 控制，图片内部动作节奏与旧素材略有不同。

## 普通静态备用版

如果应用版本不播放动画 WebP，或希望静止/更低资源占用，可以使用 `static-spritesheet.webp`：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Codex.ps1 -Static
```

该文件在四个常用动作行中保留不同的烘焙关键帧，受 Codex 固定播放间隔限制。Codex 的减少动态效果设置会固定格子，但不一定暂停图片内部动画；需要完全静止时使用静态备用版并启用该设置。

旧版备份在安装脚本旁边的 `backups/`，Python 安装脚本的备份在 `outputs/`（可指定路径）。恢复时把备份中的 `pet.json` 与 `spritesheet.webp` 复制回宠物目录并重新加载。

## 验证与制作

[图集验证](native-validation.json) 验证全部 32 个解码画面、透明格子、方向首帧原画和旧素材差异；[CSS 播放验证](native-browser-validation.json) 验证图片通过 Codex 使用的 data URL 显示并持续变化，也检查固定注视方向时继续呼吸；[视觉 QA](native-visual-qa.md) 检查睁眼、闭眼和动作预览。

重建步骤：`tools/prepare_native_layers.py` → `node tools/write_psd.cjs --native` → `node tools/bake_native.cjs` → `tools/build_native.py`。制作时需要 Pillow、NumPy、Node.js 和可运行的隔离 Playwright 浏览器，且本地预览服务需启动。成品播放不需要这些制作工具。

动画来自原画与现有开源工具，来源与许可证见仓库的 `THIRD-PARTY.md`。原画沿用项目原有作品集条款。
