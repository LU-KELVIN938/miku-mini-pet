# Third-party components

Character artwork remains under the project's existing personal-portfolio terms.
Those terms do not replace the licenses of the following components.

The full repository retains the earlier standalone renderer and its dependencies. The native Codex pet ZIP contains only artwork, baked image animation, a static fallback, installation scripts and notices. It does not ship the Python vendor directory or require an external renderer during playback. Anime2.5DRig and RIFE were used offline to produce the native animation assets.

- **Anime2.5DRig**, https://github.com/852wa/Anime2.5DRig, MIT. Pinned source commit: `7ddbd9943ea3152561b3dc8348fd752c850f3e95`. The original license is included at `web/rig/LICENSE`. The retained ag-psd bundle and generic eyelid/mouth fixtures originate from that distribution. Local changes: a bounded player bridge, 30/60 fps target, disabled device input and viewer color-scheme fix. Animation, mesh generation, springs and WebGL drawing reuse upstream code.
- **Codex-desktop-pet**, https://github.com/shicheng5589-oss/Codex-desktop-pet. Only its read-only `codex_state.py` from the 2026-10-04 inspected snapshot is included. The upstream MIT notice is preserved verbatim in `desktop/Codex-desktop-pet-LICENSE`, including its original copyright placeholder. Other model assets from that project are not included.
- **RIFE ncnn Vulkan**, https://github.com/nihui/rife-ncnn-vulkan, release `20221029`, MIT. Used offline with the included `rife-v4.6` model; the executable and model download are not required for playback and are not bundled. Generated intermediate frames are source-art-derived animation assets, not performance claims. Rebuilding requires obtaining the executable and model from the upstream release under their terms.
- **pywebview 6.2.1**, BSD-3-Clause, https://github.com/r0x0r/pywebview. Used for the transparent Windows host. Its vendored package retains its distribution metadata and bundled runtime notices.
- Bundled Python dependencies include pythonnet 3.2.1 (MIT), clr-loader 0.3.1 (MIT), cffi 2.1.1 (MIT), pycparser 3.11 (BSD), bottle 0.13.4 (MIT), proxy-tools 0.1.0 (BSD) and typing_extensions 4.16.0 (PSF). Their installed distribution notices are included with `desktop/vendor`.
- Microsoft Edge WebView2 and .NET are platform/runtime dependencies governed by their own terms. The desktop bundle does not include the operating system, a Python installation or a WebView2 installer.
- Pillow and NumPy are build-only dependencies, not needed for the already-built pet playback. Their respective licenses apply when installing them.

No camera or microphone assets/weights are bundled. Device input is disabled in the pet viewer. Upstream editor files retain optional device code, but the pet does not request those permissions or expose those controls.
