<div align="center">

<img src="https://raw.githubusercontent.com/RiverFlowsInUUU/Surfboard/main/icons/Surfboard.png" height="64" alt="Surfboard">&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://raw.githubusercontent.com/RiverFlowsInUUU/Surfboard/main/icons/Brand-Cross.png" height="64" alt="">&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://raw.githubusercontent.com/RiverFlowsInUUU/Self-Configuration/main/icons/Surge.png" height="64" alt="Surge">

# Surfboard 配置模板

借壳上车 · 实测为准

[![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=flat-square)](#-两版任选)
[![Profile](https://img.shields.io/badge/Profile-2%20%E4%BB%BD-8250df?style=flat-square)](#-两版任选)
[![Source](https://img.shields.io/badge/Source-Surge%20%E8%BD%AC%E6%8D%A2-1f6feb?style=flat-square)](tools/build_surfboard.py)
[![License](https://img.shields.io/badge/License-MIT-dfb317?style=flat-square)](LICENSE)

</div>

> 🩺 **导入报 connection closed？先看这里** → [`docs/01-兼容性排查.md`](docs/01-兼容性排查.md)：多半不是配置的错，是订阅地址。

---

## 📥 两版任选

| <div align="center">内核</div> | 🪶 懒人版 · 至简 · 省心 | 🧭 分流版 · 可控 · 随心 |
|:--|:--|:--|
| <img src="https://raw.githubusercontent.com/RiverFlowsInUUU/Surfboard/main/icons/Surfboard.png" height="20" alt=""> **Surfboard** | [`sb-lazy.conf`](profiles/sb-lazy.conf) | [`sb-routing.conf`](profiles/sb-routing.conf) |

两份都从 [Self-Configuration](https://github.com/RiverFlowsInUUU/Self-Configuration) 的 Surge 配置转换而来 —— 已去掉 Surfboard 不认的语法，导入前**只需改一处**：把 `Airport` 那行的 `policy-path` 换成你自己的订阅地址。

```
Airport = select, policy-path=<换成你的 Surge 格式订阅地址>, update-interval=86400, hidden=true
```

> ⚠️ 订阅必须是 **Surge 格式**（纯节点行），Clash/YAML 或 base64 会报
> `fetched policy-path content is invalid`。很多机场不提供独立 Surge 链接，
> 同一账号下逐个试，记住能用的那个。

---

## 🧭 实测为凭

官方 manual 停更约四年，其「支持的协议」「不支持的功能」两节已严重过时 —— 本仓只登记**实测结论**。

| | <div align="center">Surfboard</div> | 说明 |
|:--|:--|:--|
| ⚡ `smart` 策略组 | ✅ 降级为 auto | 官方 release notes：`Support Smart proxy group type(fallback to auto)` |
| 🛰️ `policy-path` 订阅槽 | ✅ | **导入时真去拉取**，失败即中断（本仓一半篇幅在讲这个） |
| 📜 `RULE-SET` + `update-interval` | ✅ | 支持后台自动刷新 |
| 🔗 `underlying-proxy` 链式代理 | ✅ | — |
| 🚀 Hysteria2 / AnyTLS / Snell / SS2022 / TUIC v5 | ✅ | 新版均已支持 |
| 🖼️ `icon-url` | ❌ 静默忽略 | 写了不报错，但没图标 |
| 🔀 `[URL Rewrite]` 段 | ❌ 不支持 | 官方明示 |
| 📶 `[SSID Setting]` 段 | ❌ 无此概念 | 它有自研 `subnet` 组类型，语法不同 |
| 🛡️ Surge 4/5 的 DNS 加固键 | ❌ 无对应实现 | `encrypted-dns-server` / `block-quic` 等 |
| 🎭 `USER-AGENT` · `URL-REGEX` 规则 | ❌ 不支持 | 官方明示 |

---

## 🔁 重新生成

上游 Surge 配置更新后：

```bash
python tools/build_surfboard.py --all <Self-Configuration 仓库根> profiles
```

转换做六件事：

| 处理 | 原因 |
|:--|:--|
| 首行 `#! version=` → 普通注释 | Surfboard 把 `#!` 当特殊指令头解析 |
| 删 `[URL Rewrite]` 段 | 官方明示不支持 |
| 删 `[SSID Setting]` 段 | Android 无此概念 |
| 删规则行 `pre-matching` / `extended-matching` | Surge 专有参数 |
| 删全部 `icon-url` | 不认，写了会被忽略 |
| 删 `[General]` 新式键 | 无对应实现 |

⚠️ **不动 `policy-path`** —— 它能跑，但导入时会真去拉取。这是订阅侧的事，脚本无法也不应代劳。

---

## 📖 按需查阅

| 路径 | 内容 |
|:--|:--|
| [`docs/01-兼容性排查.md`](docs/01-兼容性排查.md) | 一次导入失败的完整排查：控制变量二分法 · 七个被证伪的猜想 · 订阅格式三种失败形态 · 导入前自检清单 |
| [`tools/build_surfboard.py`](tools/build_surfboard.py) | 转换脚本 |
| [`probe/`](probe/) | 排查用的控制变量样本，可复用为回归样本 |

---

<div align="center">

🩺 官方手册靠不住 · 实测才算数 · MIT License

</div>
