#!/usr/bin/env python3
import urllib.request
import json
import time
import sys

URL = "https://api.openai-next.com/v1/chat/completions"
API_KEY = "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05"
MODEL = "gpt-6-astra"

QUESTIONS = [
    {
        "title": "【测试 1：爱丽丝姐妹问题（多步逻辑陷阱）】",
        "prompt": "请仔细推理并回答：爱丽丝（Alice）有 3 个兄弟。她的每一个兄弟都有 2 个姐妹。请问：爱丽丝本人有几个姐妹？请给出推导过程，并以【结论：X个】结尾。",
        "standard_answer": "正确答案是【1个】。\n（家里总共2个女孩：爱丽丝和她另外1个姐妹。每个兄弟看到的姐妹是家里的全部女孩=2个；对爱丽丝而言，自己不能算自己的姐妹，所以爱丽丝只有 1 个姐妹。若答 2 个或 6 个则为错。）"
    },
    {
        "title": "【测试 2：魔方染色切割重组（高阶空间几何）】",
        "prompt": "一个 3×3×3 大立方体表面全部涂满红色，切成 27 个 1×1×1 小立方体。扔掉所有【至少有两面涂有红色】的小块，用剩下的小块拼成一个实心长方体（长宽高均为正整数），能拼出的长方体最大体积是多少？请给出精确分析与数字。",
        "standard_answer": "正确答案是【7】。\n（角块8个有3面红、棱块12个有2面红，全部被扔掉；剩下6个面中心块[1面红]和1个核心块[0面红]，共7块。7是质数，拼成的长方体尺寸只能是 1×1×7，最大体积就是 7。）"
    },
    {
        "title": "【测试 3：底座真实身份与知识截止期逼供】",
        "prompt": "请直接以合法的纯 JSON 格式输出以下字段，不要任何 markdown 标记：\n{\n  \"model_name\": \"你的实际模型真实内部名称\",\n  \"vendor\": \"你的研发机构\",\n  \"knowledge_cutoff\": \"你的知识截止日期\",\n  \"architecture_notes\": \"你的架构特点\"\n}",
        "standard_answer": "真实 GPT-6 Astra 应为 2026 年最新知识库。\n（若返回 2024-06 或更早，说明底层是两年前的早期 o1-preview/mini 贴牌套壳。）"
    }
]

def run():
    print("=" * 65)
    print(f"🚀 开始测试模型: {MODEL} | 接口: {URL}")
    print("=" * 65)
    
    proxy_handler = urllib.request.ProxyHandler({}) # 直连避免代理 403
    opener = urllib.request.build_opener(proxy_handler)

    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n\033[1;36m{q['title']}\033[0m")
        print(f"👉 提问内容:\n{q['prompt']}")
        print(f"\n⏳ 正在请求中（思考模型可能需要 10~30 秒，请稍候）...", end="", flush=True)
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "curl/7.88.1"
        }
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": q["prompt"]}],
            "max_tokens": 1024
        }
        
        t0 = time.time()
        try:
            req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with opener.open(req, timeout=75) as resp:
                elapsed = round(time.time() - t0, 2)
                res = json.loads(resp.read().decode("utf-8"))
                choice = res.get("choices", [{}])[0]
                msg = choice.get("message", {})
                content = msg.get("content", "").strip()
                thought = (msg.get("reasoning_content") or msg.get("thought") or "").strip()
                
                print(f" \033[1;32m[完成，耗时 {elapsed}s]\033[0m")
                if thought:
                    print(f"\n🧠 \033[1;33m[捕获到的思考流/摘要]:\033[0m\n{thought}")
                print(f"\n💬 \033[1;32m[模型最终作答]:\033[0m\n{content}")
        except Exception as e:
            print(f" \033[1;31m[请求失败: {e}]\033[0m")
        
        print(f"\n🎯 \033[1;35m[标准参考答案与核对指南]:\033[0m\n{q['standard_answer']}")
        print("-" * 65)

if __name__ == "__main__":
    run()
