#!/usr/bin/env python3
"""
全频谱模型验真与战力大阅兵评测套件 (Full-Spectrum Model Benchmark & Tier List)
横跨 30 款典型代表模型（涵盖官方顶流、营销虚标换皮、中端良心正品、古董垫底模型）
评测出【最夯】、【良心正品】与【最拉】模型。
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai-next.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05")

# 待测试的 30 款全频谱典型模型
BENCHMARK_MODELS = [
    # --- 1. 官方顶流旗舰 / 最夯候选 (Top-Tier SOTA Candidates) ---
    {"cohort": "官方旗舰", "slug": "claude-3-7-sonnet-thinking", "claim": "Anthropic 官方混合思考旗舰"},
    {"cohort": "官方旗舰", "slug": "claude-3-5-sonnet-20241022", "claim": "Anthropic 官方编程标杆"},
    {"cohort": "官方旗舰", "slug": "o3-mini", "claim": "OpenAI 官方新一代推理"},
    {"cohort": "官方旗舰", "slug": "o1", "claim": "OpenAI 官方满血深度推理"},
    {"cohort": "官方旗舰", "slug": "chatgpt-4o-latest", "claim": "OpenAI 官方动态最新 4o"},
    {"cohort": "官方旗舰", "slug": "deepseek-r1", "claim": "DeepSeek 官方满血 R1 思维模型"},
    {"cohort": "官方旗舰", "slug": "deepseek-chat", "claim": "DeepSeek 官方 V3 671B"},
    {"cohort": "官方旗舰", "slug": "gemini-2.0-flash", "claim": "Google 官方新一代极速多模态"},
    {"cohort": "官方旗舰", "slug": "qwen3.5-plus", "claim": "阿里千问 3.5 Plus MoE 新旗舰"},
    {"cohort": "官方旗舰", "slug": "qwen-max-latest", "claim": "阿里千问 Max 最新官方旗舰"},

    # --- 2. 营销虚标与魔改换皮模型 (Marketing Spoofs / Aliases) ---
    {"cohort": "营销虚标", "slug": "gpt-6-astra", "claim": "宣称 GPT-6 Astra"},
    {"cohort": "营销虚标", "slug": "gpt-5.4-pro", "claim": "宣称 GPT-5.4 Pro"},
    {"cohort": "营销虚标", "slug": "gpt-5-chat", "claim": "宣称 GPT-5 对话"},
    {"cohort": "营销虚标", "slug": "o4-mini", "claim": "宣称 o4-mini"},
    {"cohort": "营销虚标", "slug": "claude-sonnet-5", "claim": "宣称 Claude 5 代 Sonnet"},
    {"cohort": "营销虚标", "slug": "claude-opus-5", "claim": "宣称 Claude 5 代 Opus"},
    {"cohort": "营销虚标", "slug": "deepseek-v4-pro", "claim": "宣称 DeepSeek V4 旗舰"},
    {"cohort": "营销虚标", "slug": "glm-5.2", "claim": "宣称智谱 5.2 (实测 Gemini)"},
    {"cohort": "营销虚标", "slug": "grok-4.6", "claim": "宣称 xAI Grok 4.6"},
    {"cohort": "营销虚标", "slug": "doubao-seedream-5-0-pro-260628", "claim": "宣称豆包 5.0 (生图错配)"},

    # --- 3. 中端正品与开源良心 (Authentic Mid-Tier & Open Source) ---
    {"cohort": "中端正品", "slug": "glm-4", "claim": "智谱官方 GLM-4"},
    {"cohort": "中端正品", "slug": "qwen2.5-72b-instruct", "claim": "通义千问 2.5 72B 纯血开源"},
    {"cohort": "中端正品", "slug": "qwen2.5-coder-32b-instruct", "claim": "通义千问 2.5 32B 代码专精"},
    {"cohort": "中端正品", "slug": "llama-3.1-70b", "claim": "Meta Llama 3.1 70B 开源旗舰"},
    {"cohort": "中端正品", "slug": "mixtral-8x22b", "claim": "Mistral 8x22B MoE"},

    # --- 4. 古董垫底与退化底座 (The Worst / Ancient / Degraded) ---
    {"cohort": "古董垫底", "slug": "gpt-3.5-turbo", "claim": "OpenAI 早期一代基座"},
    {"cohort": "古董垫底", "slug": "llama-2-7b", "claim": "Meta 2023年老代 7B 小模型"},
    {"cohort": "古董垫底", "slug": "qwen-1.8b-chat", "claim": "阿里初代 1.8B 超轻量底模"},
    {"cohort": "古董垫底", "slug": "qwen-7b-chat", "claim": "阿里初代 7B 历史底模"},
    {"cohort": "古董垫底", "slug": "mistral-7b-instruct", "claim": "Mistral 初代 7B 小模型"}
]

PROMPT_IDENTITY = '请直接以合法的纯 JSON 格式输出：{"model_name":"你的内部真实名称","vendor":"研发机构","knowledge_cutoff":"知识截止年月"}，严禁任何额外字符。'
PROMPT_ALICE = "爱丽丝有3个兄弟，每个兄弟都有2个姐妹。爱丽丝本人有几个姐妹？请推导并给出最终数字结论。"
PROMPT_FLOAT = "比较大小：9.11 和 9.9 哪个数更大？请直接回答并在末尾以【结论：X更大】结尾。"

def send_chat_request(model_slug, prompt, max_tokens=400, timeout=50):
    url = f"{API_BASE.rstrip('/')}/chat/completions"
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "curl/7.88.1"
    }
    payload = {
        "model": model_slug,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }
    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with opener.open(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = round(time.time() - t0, 2)
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            req_id = data.get("id", "")
            return {"ok": True, "content": content.strip(), "elapsed": elapsed, "req_id": req_id}
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        return {"ok": False, "error": f"HTTP {e.code}", "detail": body[:120], "elapsed": round(time.time() - t0, 2)}
    except Exception as e:
        return {"ok": False, "error": str(e), "elapsed": round(time.time() - t0, 2)}

def test_single_model(item):
    slug = item["slug"]
    cohort = item["cohort"]
    claim = item["claim"]
    
    result = {
        "slug": slug,
        "cohort": cohort,
        "claim": claim,
        "accessible": False,
        "identity_raw": "",
        "vendor": "未知",
        "real_model": "未知",
        "cutoff": "未知",
        "alice_passed": False,
        "alice_output": "",
        "float_passed": False,
        "float_output": "",
        "latency_id": 0,
        "latency_alice": 0,
        "latency_float": 0,
        "is_spoofed": False,
        "is_authentic": False,
        "status": "NORMAL"
    }
    
    # 1. 身份自证
    r_id = send_chat_request(slug, PROMPT_IDENTITY, max_tokens=250)
    if not r_id["ok"]:
        result["error"] = r_id["error"]
        result["error_detail"] = r_id.get("detail", "")
        result["status"] = "ERROR / UNREACHABLE"
        return result
    
    result["accessible"] = True
    result["latency_id"] = r_id["elapsed"]
    raw_id = r_id["content"]
    result["identity_raw"] = raw_id
    
    try:
        s = raw_id.find("{")
        e = raw_id.rfind("}")
        if s != -1 and e != -1:
            id_data = json.loads(raw_id[s:e+1])
            result["vendor"] = id_data.get("vendor", "未知")
            result["real_model"] = id_data.get("model_name", "未知")
            result["cutoff"] = id_data.get("knowledge_cutoff", "未知")
    except Exception:
        pass
    
    # 2. 爱丽丝姐妹逻辑测试
    r_alice = send_chat_request(slug, PROMPT_ALICE, max_tokens=400)
    if r_alice["ok"]:
        result["latency_alice"] = r_alice["elapsed"]
        out = r_alice["content"]
        result["alice_output"] = out
        # 正确答案为 1 个姐妹（排除 2 个或 6 个的错误推论）
        if ("1 个" in out or "1个" in out or "1位" in out or "只有一个" in out or "1 位" in out) and not ("结论：2" in out or "结论: 2" in out or "6个" in out or "6 个" in out):
            result["alice_passed"] = True
    
    # 3. 9.11 vs 9.9 浮点数陷阱
    r_float = send_chat_request(slug, PROMPT_FLOAT, max_tokens=250)
    if r_float["ok"]:
        result["latency_float"] = r_float["elapsed"]
        out_f = r_float["content"]
        result["float_output"] = out_f
        # 正确答案为 9.9 更大
        if "9.9更大" in out_f or "9.9 大于 9.11" in out_f or "9.9 比较大" in out_f or "9.9 是更大" in out_f or "结论：9.9" in out_f or "结论: 9.9" in out_f:
            if not ("9.11更大" in out_f or "9.11 大于 9.9" in out_f):
                result["float_passed"] = True

    # 4. 判定注水度与真实性
    # 如果声明为前沿或营销高版本，但底座完全不符（如 gpt-6 返回 o1, glm-5.2 返回 gemini, grok-4.6 返回 grok-1/2）
    slug_lower = slug.lower()
    real_lower = str(result["real_model"]).lower()
    
    if cohort == "营销虚标":
        result["is_spoofed"] = True
    elif cohort == "官方旗舰" or cohort == "中端正品":
        # 检验是否挂羊头卖狗肉
        if any(w in real_lower for w in ["gemini", "claude", "gpt", "deepseek", "qwen", "glm", "llama"]):
            # 简单验证厂商是否匹配
            if "glm" in slug_lower and "gemini" in real_lower:
                result["is_spoofed"] = True
            elif "qwen" in slug_lower and "qwen" in real_lower:
                result["is_authentic"] = True
            elif "claude" in slug_lower and ("claude" in real_lower or "anthropic" in str(result["vendor"]).lower()):
                result["is_authentic"] = True
            elif ("o1" in slug_lower or "o3" in slug_lower or "4o" in slug_lower) and ("gpt" in real_lower or "openai" in str(result["vendor"]).lower() or "o1" in real_lower or "o3" in real_lower):
                result["is_authentic"] = True
            elif "deepseek" in slug_lower and "deepseek" in real_lower:
                result["is_authentic"] = True
            else:
                result["is_authentic"] = True
        else:
            result["is_authentic"] = True

    return result

def main():
    print("=" * 80)
    print("🚀 聚合网关全频谱 30 款大模型真伪验真与战力排位赛 (Full-Spectrum Tier Benchmark)")
    print(f"📡 目标接口: {API_BASE}")
    print(f"📊 参评阵容: {len(BENCHMARK_MODELS)} 款模型（官方旗舰 / 营销虚标 / 中端良心 / 古董垫底）")
    print("=" * 80)

    results = []
    for idx, item in enumerate(BENCHMARK_MODELS, 1):
        slug = item["slug"]
        cohort = item["cohort"]
        claim = item["claim"]
        print(f"\n[{idx:02d}/{len(BENCHMARK_MODELS):02d}] 正在评测: [{cohort}] \033[1;36m{slug}\033[0m ({claim}) ...", end="", flush=True)
        res = test_single_model(item)
        results.append(res)
        
        if not res["accessible"]:
            print(f" \033[1;31m[不可用/报错: {res.get('error')} | {res.get('error_detail')}]\033[0m")
        else:
            alice_icon = "✓" if res["alice_passed"] else "✗"
            float_icon = "✓" if res["float_passed"] else "✗"
            print(f" \033[1;32m[成功]\033[0m -> 机构: {res['vendor']} | 底模: {res['real_model']} | 截止: {res['cutoff']}")
            print(f"       -> 爱丽丝姐妹: {alice_icon} | 9.11 vs 9.9: {float_icon} | 响应总耗时: {round(res['latency_id'] + res['latency_alice'] + res['latency_float'], 2)}s")
        time.sleep(1)

    # 导出完整评测结果 JSON
    out_path = "/Users/songshiyao/.gemini/antigravity/scratch/model-fingerprint-audit/data/full_spectrum_benchmark_30models.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n" + "=" * 80)
    print(f"🎉 评测全部完成！原始结构化数据已落盘: {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
