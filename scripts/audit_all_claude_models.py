#!/usr/bin/env python3
"""
全量 47 款 Claude 系列模型可用性与真伪地毯式排查
验证 openainext 端点上所有带 claude 前缀的模型，探查哪些是真实的、哪些可请求。
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai-next.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05")

def check_model(slug):
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
        "messages": [{"role": "user", "content": "请用一句话回答：你的具体型号名称是什么？知识截止到哪年几月？"}],
        "max_tokens": 150
    }
    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with opener.open(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = round(time.time() - t0, 2)
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            req_id = data.get("id", "")
            return {
                "slug": slug,
                "status": "ONLINE",
                "elapsed": elapsed,
                "req_id": req_id,
                "is_anthropic_msg": req_id.startswith("msg_"),
                "reply": content
            }
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")[:100]
        except Exception:
            pass
        return {"slug": slug, "status": f"HTTP_{e.code}", "elapsed": round(time.time() - t0, 2), "error": body}
    except Exception as e:
        return {"slug": slug, "status": "TIMEOUT_OR_ERR", "elapsed": round(time.time() - t0, 2), "error": str(e)}

def main():
    with open("data/all_models_catalog.json") as f:
        all_models = json.load(f)
    
    claude_slugs = sorted([m for m in all_models if "claude" in m.lower()])
    print(f"🚀 开始地毯式测试全部 {len(claude_slugs)} 款 Claude 模型...")
    
    results = []
    for idx, slug in enumerate(claude_slugs, 1):
        print(f"[{idx:02d}/{len(claude_slugs):02d}] 测试 {slug:35s} ...", end="", flush=True)
        res = check_model(slug)
        results.append(res)
        if res["status"] == "ONLINE":
            is_anth = "✅ Anthropic原生(msg_)" if res["is_anthropic_msg"] else "⚠️ 非标准msg_ID"
            print(f" \033[1;32m[可用]\033[0m {res['elapsed']}s | {is_anth} | 回复: {res['reply'][:60]}")
        else:
            print(f" \033[1;31m[{res['status']}]\033[0m {res.get('error', '')[:40]}")
        time.sleep(0.5)

    out_file = "data/all_claude_models_audit.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 测试完成！结果已存入: {out_file}")

if __name__ == "__main__":
    main()
