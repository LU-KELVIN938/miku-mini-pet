# Codex 原动作轻量版

当前版本恢复原画移动姿势与顺序，使用无损静态v2图集。运行时只需 `pet.json` 与 `spritesheet.webp`；安装和制作步骤见 [仓库说明](../README.md)。

选择名称：**Miku Mini · 原动作轻量版**。替换文件后在宠物设置刷新并重新选择；如果仍显示旧图，请保存任务后完整退出并重新打开 Codex。

本次通过文件和隔离浏览器验证，真实 Codex 窗口观感尚待确认。脚步停止、快速反向和末格220ms停留仍受宿主控制。

验证：[图集](native-validation.json)、[最终资产播放](native-browser-validation.json)、[原动作视觉 QA](original-action-visual-qa.json)。

此前32帧动画 WebP 的方案已被替换；历史记录见 [CHANGELOG](CHANGELOG.md)。
