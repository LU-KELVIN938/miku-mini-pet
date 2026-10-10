# 最终文件视觉 QA

日期：2026-10-10

范围：检查 docs/interpolation-preview.png、docs/previews/running-right.gif、docs/previews/jumping.gif，以及修复后的 web/interpolated/running-right/09.png 和 web/interpolated/jumping/05.png。仅检查文件，未操作屏幕或浏览器。

- **running-right：通过。** 回退后的 09.png 保留连续的深色靴子与腿部轮廓，此前白色楔形瑕疵已消失；相关 GIF 文件所检查的帧无该瑕疵。
- **jumping：通过。** 回退后的 05.png 保留原帧的完整手臂、袖口与手掌，此前两侧袖口的白色楔形瑕疵已消失；相关 GIF 文件所检查的帧无该瑕疵。
- **插值预览静态图：通过。** 角色身份、比例、方向和完整轮廓正常，未见明显裁切或白色楔形瑕疵。

接受的轻微限制：两处回退会短暂重复原姿势；其他过渡帧的轻微软化沿用此前接受结论。本次未重新检查已通过的所有素材，也未测试桌面运行、实际播放流畅度或动画性能。
