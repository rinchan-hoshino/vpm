# K-NECO VPM

猫尾草工作室的 VRChat Creator Companion 软件源。

- 软件源页面：<https://vpm.k-neco.com/>
- 软件源地址：<https://vpm.k-neco.com/index.json>
- 当前 Package：[AFK Motion Patcher](https://github.com/k-neco-lab/afk-motion-patcher)

页面沿用 VRChat Community 的 [`template-package-listing`](https://github.com/vrchat-community/template-package-listing) 标准结构，并通过 GitHub Pages 发布 `Website/` 中经过验证的静态文件。

## 发布检查

更新 `Website/` 后，至少确认：

1. `Website/index.json` 中的软件源 URL、Package URL、版本与 SHA-256 正确；
2. `Website/index.html` 和 `Website/app.js` 使用相同的软件源 URL 与 Package 信息；
3. 本地静态预览中的 Add to VCC、复制和 Package Info 可用；
4. GitHub Pages 部署成功，公网 `index.json` 与 Package ZIP 可下载。
