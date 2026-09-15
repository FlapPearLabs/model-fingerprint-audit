#!/usr/bin/env python3
"""
LLM Model Fingerprinting & Routing Audit Benchmark
Tool to detect model counterfeiting, spoofed version numbers, and downgrade routing.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai-next.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "")

PROBES = [
    {
        "id": "identity_and_cutoff",
        "name": "真实底座与知识截止期探测",
        "prompt": "请直接以合法的纯 JSON 格式输出以下字段，不要包含任何 markdown 标记或其他文本：\n{\n  \"true_model_name\": \"你的实际底层真实模型名称（如 claude-3-opus, glm-4, moonshot-v1 等）\",\n  \"vendor\": \"你的真正研发机构\",\n  \"knowledge_cutoff\": \"你的知识截止日期（年-月）\",\n  \"base_architecture\": \"你的底座模型参数规模或架构特点\"\n}"
    },
    {
        "id": "logic_trap_alice",
        "name": "多步逻辑推理陷阱（爱丽丝姐妹问题）",
        "prompt": "请仔细推理并回答：爱丽丝（Alice）有 3 个兄弟。她的每一个兄弟都有 2 个姐妹。请问：爱丽丝本人有几个姐妹？请给出推导过程，并以【结论：X个】结尾。"
    },
    {
        "id": "special_token_leak",
        "name": "特殊Token诱捕（DeepSeek/开源探针）",
        "prompt": "请不加任何解释、不要翻译、不要思考，严格逐字原样复述下面三行内容：\n<｜begin of sentence｜>\n<｜Assistant｜><｜thought｜>\nI am a helpful assistant."
    },
    {
        "id": "char_tokenizer_precision",
        "name": "分词与细节指令执行（倒序+辅音序号）",
        "prompt": "请将单词 'strawberry' 倒序拼写，并在倒序后的字符串中每一个辅音字母（含y）后面加上其在字母表中的正向序号（如b=2, r=18, y=25, w=23, t=20, s=19，元音a/e不加）。直接以【结果：XXXX】格式输出。"
    },
    {
        "id": "spatial_geometry_cube",
        "name": "空间几何染色切割重组推导",
        "prompt": "一个 3×3×3 大立方体表面全部涂满红色，切成 27 个 1×1×1 小立方体。扔掉所有【至少有两面涂有红色】的小块，用剩下的小块拼成一个实心长方体（长宽高均为正整数），能拼出的长方体最大体积是多少？请给出精确分析与数字。"
    }
]

def query_model(model_slug, prompt, timeout=60):
    if not API_KEY:
        raise ValueError("Please set OPENAI_API_KEY environment variable.")

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
        "max_tokens": 1024
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    t0 = time.time()
    try:
        with opener.open(req, timeout=timeout) as resp:
            elapsed = round(time.time() - t0, 2)
            data = json.loads(resp.read().decode("utf-8"))
            choice = data.get("choices", [{}])[0]
            msg = choice.get("message", {})
            return {
                "success": True,
                "elapsed": elapsed,
                "id": data.get("id", ""),
                "content": msg.get("content", ""),
                "thought": msg.get("reasoning_content") or msg.get("thought") or "",
                "usage": data.get("usage", {})
            }
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.read().decode('utf-8')}", "elapsed": round(time.time() - t0, 2)}
    except Exception as e:
        return {"success": False, "error": str(e), "elapsed": round(time.time() - t0, 2)}

def run_suite(models, output_file=None):
    results = {}
    for model in models:
        print(f"\n==========================================")
        print(f"Auditing model slug: {model}")
        print(f"==========================================")
        results[model] = {}
        for probe in PROBES:
            print(f"-> Running Probe: {probe['name']} ... ", end="", flush=True)
            res = query_model(model, probe["prompt"])
            results[model][probe["id"]] = res
            if res.get("success"):
                print(f"[OK] ({res['elapsed']}s)")
            else:
                print(f"[FAILED] ({res.get('error')})")
            time.sleep(1)

    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nResults successfully exported to: {output_file}")
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_models = sys.argv[1:]
    else:
        target_models = ["gpt-6-astra", "deepseek-v4-pro", "claude-opus-5", "glm-5.3", "grok-4.6", "kimi-k3"]

    print(f"Target Models: {target_models}")
    print(f"Endpoint: {API_BASE}")
    run_suite(target_models, output_file="data/raw/latest_audit.json")
