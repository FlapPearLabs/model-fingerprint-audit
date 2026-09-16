#!/usr/bin/env python3
"""
针对 openainext 网关上的 Fable 5 / Fable 5.1 模型进行深度底层指纹与能力评测
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai-next.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05")

PROBE_SLUGS = [
    "claude-fable-5-1",
    "claude-fable-5",
    "fable-5.1",
    "claude-fable-5.1"
]

def request_model(slug, messages, max_tokens=600):
    url = f"{API_BASE.rstrip('/')}/chat/completions"
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "curl/7.88.1"
    }
    payload = {
        "model": slug,
        "messages": messages,
        "max_tokens": max_tokens
    }
    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with opener.open(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = round(time.time() - t0, 2)
            return {"ok": True, "elapsed": elapsed, "data": data}
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        return {"ok": False, "elapsed": round(time.time() - t0, 2), "error": f"HTTP {e.code}", "detail": body}
    except Exception as e:
        return {"ok": False, "elapsed": round(time.time() - t0, 2), "error": str(e)}

def test_slug(slug):
    print(f"\n{'='*70}")
    print(f"🔍 正在测试 Slug: \033[1;36m{slug}\033[0m")
    print(f"{'='*70}")

    # 1. 基础连通性与身份自证
    prompt_id = [
        {"role": "user", "content": "请如实回答：你的底层具体是哪个模型？哪家公司研发的？你的知识库截止到哪一年几月？如果是Claude系列，你的具体型号是Fable、Opus还是Sonnet？"}
    ]
    res1 = request_model(slug, prompt_id, max_tokens=400)
    if not res1["ok"]:
        print(f"❌ 连通失败: {res1.get('error')} | 详情: {res1.get('detail')}")
        return

    print(f"✅ 成功连通! 响应耗时: {res1['elapsed']}s")
    raw_data = res1["data"]
    print(f"📌 返回底层 ID: {raw_data.get('id')}")
    print(f"📌 返回 Model 标识: {raw_data.get('model')}")
    msg = raw_data.get("choices", [{}])[0].get("message", {})
    content = msg.get("content", "")
    reasoning = msg.get("reasoning_content", "")
    print(f"💬 模型回答:\n{content}")
    if reasoning:
        print(f"🧠 思维链摘要:\n{reasoning[:200]}...")

    # 2. 逻辑陷阱测试（爱丽丝姐妹）
    prompt_logic = [
        {"role": "user", "content": "爱丽丝有3个兄弟，每个兄弟都有2个姐妹。请问爱丽丝本人有几个姐妹？给出简明推导和最终数字结论。"}
    ]
    res2 = request_model(slug, prompt_logic, max_tokens=400)
    if res2["ok"]:
        ans2 = res2["data"].get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"\n🧩 爱丽丝姐妹推导 (耗时 {res2['elapsed']}s):\n{ans2.strip()}")

    # 3. 浮点数陷阱（9.11 vs 9.9）
    prompt_float = [
        {"role": "user", "content": "9.11 和 9.9 哪个大？"}
    ]
    res3 = request_model(slug, prompt_float, max_tokens=150)
    if res3["ok"]:
        ans3 = res3["data"].get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"\n🔢 9.11 vs 9.9 比较 (耗时 {res3['elapsed']}s):\n{ans3.strip()}")

def main():
    print("🚀 开始探测 openainext 上的 Fable 5 / Fable 5.1 模型...")
    for slug in PROBE_SLUGS:
        test_slug(slug)
        time.sleep(1)

if __name__ == "__main__":
    main()
