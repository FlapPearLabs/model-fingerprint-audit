#!/usr/bin/env python3
"""
2025-2026 跨年时间线与无联网知识截止深度审讯套件
通过精心挑选的“事前已知计划” vs “事后才确定的真实结果/突发科技事件”
逼迫模型通过纯 JSON 结构自爆其底层真实的静态知识物理边界。
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai-next.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05")

MODELS_TO_PROBE = [
    {"slug": "claude-fable-5-1", "desc": "宣称 Fable 5.1 (曾自称 2026-06)"},
    {"slug": "claude-fable-5", "desc": "宣称 Fable 5 (曾自爆 Sonnet 4.5)"},
    {"slug": "claude-opus-5", "desc": "宣称 Opus 5"},
    {"slug": "claude-sonnet-5", "desc": "宣称 Sonnet 5"},
    {"slug": "claude-sonnet-4-6", "desc": "宣称 Sonnet 4.6 (自称 2025-04)"},
    {"slug": "deepseek-v4-pro", "desc": "宣称 DeepSeek V4 (自称 2025-05)"},
    {"slug": "qwen3.5-plus", "desc": "阿里千问 3.5 Plus (自称 2026)"},
    {"slug": "chatgpt-4o-latest", "desc": "OpenAI 官方原版 4o"}
]

PROMPT_TIMELINE_AUDIT = """【严格指令：禁止使用任何联网工具，禁止猜测，纯靠你的预训练静态底层参数作答】
请严格以合法纯 JSON 格式输出，不要输出任何代码块标记（不要写 ```json）、反引号或任何前言后语。

我们需要严格测定你的物理知识截止点到底是 2024、2025 还是 2026。
对于在你知识截止日期之后发生的事件，必须严格填写 "知识库未包含" 或 "未知"，严禁幻觉脑补。

JSON 结构必须严格按以下字段：
{
  "model_claimed_identity": "你的真实模型名与研发商",
  "strict_knowledge_cutoff": "YYYY-MM",
  "timeline_probes": {
    "probe_2024_11_us_election": "2024年11月美国总统大选获胜者及所获选举人票大概范围",
    "probe_2025_01_trump_inauguration": "2025年1月20日宣誓就职的美国第47任总统与其副总统搭档是谁？",
    "probe_2025_01_deepseek_r1": "2025年1月引爆全球AI圈的DeepSeek-R1模型的发布日期与其核心训练范式（SFT还是纯RL强化学习）？",
    "probe_2025_02_claude_3_7_sonnet": "Anthropic在2025年2月发布的Claude 3.7 Sonnet的核心技术特征是什么（例如是否具备混合推理思维模式）？",
    "probe_2025_late_or_2026_real_event": "列举一项发生在2025年下半年或2026年的具体真实世界大事件（若你的知识截止早于此时，必须填'知识库未包含，无法确认'）"
  },
  "self_audit_conclusion": "基于上述问答，你自认真实的知识截止年月究竟是哪一年哪一月？"
}"""

def request_json_audit(slug):
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
        "messages": [{"role": "user", "content": PROMPT_TIMELINE_AUDIT}],
        "max_tokens": 600
    }
    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with opener.open(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = round(time.time() - t0, 2)
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return {"ok": True, "elapsed": elapsed, "content": content, "id": data.get("id", "")}
    except Exception as e:
        return {"ok": False, "elapsed": round(time.time() - t0, 2), "error": str(e)}

def main():
    print("=" * 80)
    print("🕰️ 启动 2025-2026 时间线穿透审讯 (无联网纯静态参数知识边界自爆测试)")
    print("=" * 80)

    results = []
    for item in MODELS_TO_PROBE:
        slug = item["slug"]
        desc = item["desc"]
        print(f"\n👉 正在审讯: \033[1;36m{slug}\033[0m ({desc}) ...", end="", flush=True)
        res = request_json_audit(slug)
        res["slug"] = slug
        res["desc"] = desc
        results.append(res)

        if not res["ok"]:
            print(f" \033[1;31m[报错: {res.get('error')}]\033[0m")
        else:
            print(f" \033[1;32m[成功 ({res['elapsed']}s)]\033[0m")
            raw_text = res["content"]
            # 尝试截取输出关键字段
            try:
                s = raw_text.find("{")
                e = raw_text.rfind("}")
                if s != -1 and e != -1:
                    parsed = json.loads(raw_text[s:e+1])
                    cutoff = parsed.get("strict_knowledge_cutoff", "未知")
                    concl = parsed.get("self_audit_conclusion", "未知")
                    probe_2026 = parsed.get("timeline_probes", {}).get("probe_2025_late_or_2026_real_event", "未知")
                    print(f"   📋 自爆真实截止: \033[1;33m{cutoff}\033[0m")
                    print(f"   🔎 2025下半年/2026真事件考查: {probe_2026[:60]}...")
                    print(f"   🎯 审讯结论: {concl[:80]}")
                else:
                    print(f"   ⚠️ 未解析到标准JSON:\n{raw_text[:200]}")
            except Exception:
                print(f"   ⚠️ JSON解析异常，原始摘要: {raw_text[:150]}")
        time.sleep(1)

    out_file = "data/chronological_cutoff_audit.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n" + "=" * 80)
    print(f"🎉 2025-2026 时间线知识边界自爆测试全部完成！数据落盘: {out_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
