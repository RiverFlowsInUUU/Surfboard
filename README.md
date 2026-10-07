# Surfboard

Android 客户端 **Surfboard** 的配置模板与兼容性笔记。

Surfboard 自称「兼容 Surge 配置」，实际是**兼容子集** —— 语法的确大量重叠，
但 Surge 4/5 新增的一批能力它没有对应实现，且**官方 manual 已停更约四年**，
能力边界只能靠实测与 release notes 判定。本仓就是把这些实测结论沉淀下来。

---

## 目录

| 路径 | 内容 |
|:--|:--|
| [`profiles/`](profiles/) | **现役配置**：`sb-lazy.conf`（懒人版）· `sb-routing.conf`（分流版） |
| [`docs/01-兼容性排查.md`](docs/01-兼容性排查.md) | 一次完整导入失败的排查全过程：控制变量方法、七个被证伪的猜想、真因与自检清单 |
| [`tools/build_surfboard.py`](tools/build_surfboard.py) | 从 Surge 配置生成 Surfboard 兼容版的转换脚本 |
| [`probe/`](probe/) | 排查期间构建的控制变量样本，可直接复用为回归样本 |

---

## 怎么用

### 直接用现役配置

两份 `profiles/*.conf` 是从 Surge 正式版转换而来，已去掉 Surfboard 不支持的语法。
**导入前只需改一处**：把 `[Proxy Group]` 里 `Airport` 那行的 `policy-path`
换成你自己的真实订阅地址（且必须是 Surge 格式的订阅）。

```
Airport = select, policy-path=<换成你的 Surge 格式订阅地址>, update-interval=86400, hidden=true
```

### 自己重新生成

仓库更新后想重新转换：

```bash
python tools/build_surfboard.py --all <Surge 仓库根> profiles
```

### 转换做了什么

| 处理 | 原因 |
|:--|:--|
| 首行 `#! version=` → 普通注释 | Surfboard 把 `#!` 当特殊指令头解析 |
| 删 `[URL Rewrite]` 段 | 官方明示不支持 |
| 删 `[SSID Setting]` 段 | Android 无此概念 |
| 删规则行的 `pre-matching` / `extended-matching` | Surge 专有参数 |
| 删全部 `icon-url` | Surfboard 不认，写了会被忽略 |
| 删 `[General]` 新式键 | Surfboard 无对应实现（如 `encrypted-dns-server`、`block-quic`） |

⚠️ **不动 `policy-path`** —— Surfboard 支持它，但导入时会真去拉取，
地址无效即报 `connection closed`。这是订阅侧的事，脚本无法也**不应**代劳。

---

## 三个最常踩的坑

**① 报错只有 `connection closed` 两个词。**
优先怀疑订阅地址拉取失败，不要去翻配置语法。Surfboard 导入时会**真去请求**
`policy-path` 指向的地址，失败即中断且不给原因。

**② `fetched policy-path content is invalid`。**
拉到了，但内容不是 Surge 格式。Surge 的 policy-path 要的是纯节点行：

```
ProxyHTTPS = https, 1.2.3.4, 443, username, password, sni=www.google.com
```

Clash / mihomo YAML、base64 节点串都会触发这个错。很多机场不提供独立的
Surge 订阅链接 —— 同一账号下逐个试，记住能用的那个。

**③ 导入成功但一个节点都没有。**
机场识别出客户端后返回了空响应（常伴随「不支持你使用的客户端」）。同样是换订阅地址。

---

## 与 Surge 的能力差（何时该换客户端）

Surfboard **不建议**用于：

- 需要 `[URL Rewrite]` 做重定向；
- 需要 `[SSID Setting]` 做网络自动切换；
- 需要 Surge 4/5 那套 DNS 加固键（`encrypted-dns-server`、`block-quic` 等）；
- 需要 `icon-url` 图标（不报错，但会被忽略）。

Surfboard **可以正常用**：

- `smart` / `select` / `url-test` / `fallback` 策略组（`smart` 自动降级为 auto 语义）；
- `policy-path` 订阅槽 + `update-interval` 后台刷新；
- `RULE-SET` + `update-interval`；
- Hysteria2 / AnyTLS / Snell / SS2022 / WireGuard / TUIC v5；
- `underlying-proxy` 链式代理。

若目标是安卓端完整体验，mihomo 系（Clash Meta 内核）在协议覆盖与配置自由度上
明显更宽；若已有 Surge 配置资产、只求复用，Surfboard 是可行的折中。

---

## 维护说明

本仓记录的是**实测结论**，不是官方文档的转述。官方 manual
（<https://manual.getsurfboard.com/>）自约 2022 年起未再更新，其「支持的协议」
「受限不支持的功能」两节已严重过时 —— 判断能力边界请查
[GitHub Releases](https://github.com/getsurfboard/surfboard/releases)。

新增结论时请附**证据**（实测步骤、或 release notes 原文），不要只写「支持/不支持」。
