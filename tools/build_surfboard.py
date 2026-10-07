#!/usr/bin/env python3
"""从 Surge 配置生成 Surfboard 兼容版。

用法：
    python tools/build_surfboard.py <surge-profile.conf> <out.conf> [--title "..."]
    python tools/build_surfboard.py --all <surge-repo-root> <out-dir>

做四件事（Surfboard 不支持或会被忽略的，一律删掉）：
  1. 首行 `#! version=` → 普通注释（Surfboard 把 `#!` 当特殊指令头解析）
  2. 删 [URL Rewrite] / [SSID Setting] 两段（前者官方明示不支持，后者无对应概念）
  3. 删规则行上的 pre-matching / extended-matching（Surge 专有参数）
  4. 删全部 icon-url、以及 [General] 里 Surfboard 无对应实现的新式键

⚠️ 不改的：policy-path（Surfboard 支持，但**导入时会真去拉取**，
   地址无效即报 connection closed / HTTP 400 —— 这是配置之外的事，见 docs/01）。
"""

import io
import os
import re
import sys

DROP_SECTIONS = ("[URL Rewrite]", "[SSID Setting]")

# Surfboard 无对应实现的 Surge 4/5 [General] 键（被忽略或报错，一律去掉）
DROP_GENERAL = (
    "show-error-page-for-reject", "encrypted-dns-server",
    "encrypted-dns-follow-outbound-mode", "allow-dns-svcb", "ipv6-vif",
    "disable-geoip-db-auto-update", "proxy-test-udp", "udp-priority",
    "block-quic", "allow-wifi-access", "allow-hotspot-access",
    "proxy-restricted-to-lan", "gateway-restricted-to-lan", "all-hybrid",
    "wifi-assist", "use-local-host-item-for-proxy", "read-etc-hosts",
    "exclude-simple-hostnames", "geoip-maxmind-url",
)

HEADER = """# ============================================================================
# {title} · Surfboard 兼容版
# ============================================================================
# ⚠️ 导入前必须改一处：把 [Proxy Group] 里 `Airport` 那行的 policy-path
#    换成你自己的真实订阅地址 —— 且必须是 **Surge 格式**的订阅（不是 Clash/YAML）。
#    改之前导入会报 connection closed / HTTP 400：Surfboard 在导入时会真去
#    拉这个地址，拉不到就直接断，不给友好提示。
#
# 与 Surge 正式版的差异（为兼容 Surfboard 刻意去掉）：
#   · 首行 `#! version=` → 普通注释（Surfboard 把它当特殊指令头解析）
#   · 删 [URL Rewrite] 段        · 删 [SSID Setting] 段
#   · 删规则行上的 pre-matching / extended-matching（Surge 专有参数）
#   · 删全部 icon-url（Surfboard 不认，写了会被忽略）
#   · 删 [General] 里 Surfboard 无对应实现的新式键
# ============================================================================

"""


def convert(src_path, title="Surge 配置"):
    s = io.open(src_path, encoding="utf-8").read()

    # 1) 首行特殊指令 → 普通注释
    s = re.sub(r"^#! version=(\S+)\n", r"# 版本 \1\n", s, count=1)

    # 2) 删不支持的段
    lines, out, skip = s.split("\n"), [], False
    for ln in lines:
        if ln.startswith("["):
            if ln.strip() in DROP_SECTIONS:
                skip = True
                continue
            skip = False
        if skip:
            continue
        out.append(ln)
    s = "\n".join(out)

    # 3) 规则参数
    s = re.sub(r",pre-matching,extended-matching", "", s)
    s = re.sub(r",extended-matching", "", s)
    s = re.sub(r",pre-matching", "", s)

    # 4) icon-url
    s = re.sub(r", ?icon-url=\S+", "", s)
    s = re.sub(r"icon-url=\S+, ?", "", s)

    # 5) [General] 新式键
    out = []
    for ln in s.split("\n"):
        if any(ln.strip().startswith(k + " =") for k in DROP_GENERAL):
            continue
        out.append(ln)
    s = "\n".join(out)

    return HEADER.format(title=title) + s.lstrip("\n")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv:
        root, outdir = args[0], args[1]
        os.makedirs(outdir, exist_ok=True)
        jobs = [
            ("surge/profiles/lazy.conf", "sb-lazy.conf", "Surge 懒人配置"),
            ("surge/profiles/routing.conf", "sb-routing.conf", "Surge 分流配置"),
        ]
        for rel, name, title in jobs:
            src = os.path.join(root, rel)
            if not os.path.exists(src):
                print(f"⏭  跳过（不存在）：{rel}")
                continue
            out = convert(src, title)
            dst = os.path.join(outdir, name)
            io.open(dst, "w", encoding="utf-8", newline="\n").write(out)
            print(f"✅ {name}  ({len(out.splitlines())} 行)")
        return 0

    if len(args) < 2:
        print(__doc__)
        return 2
    title = "Surge 配置"
    if "--title" in sys.argv:
        title = sys.argv[sys.argv.index("--title") + 1]
    out = convert(args[0], title)
    io.open(args[1], "w", encoding="utf-8", newline="\n").write(out)
    print(f"✅ {args[1]}  ({len(out.splitlines())} 行)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
