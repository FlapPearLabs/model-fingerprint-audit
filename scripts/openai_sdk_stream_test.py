#!/usr/bin/env python3
"""
OpenAI SDK 官方客户端原生流式测试脚本 (OpenAI SDK Native Streaming Test)
使用官方 openai Python SDK，直连聚合接口，逐字流式输出模型思考过程与生成内容。
"""

import os
import sys
import time
import httpx
from openai import OpenAI

BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai-next.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05")
MODEL = "gpt-6-astra"

QUESTIONS = [
    {
        "id": 1,
        "title": "测试 1/3：多步逻辑推理（爱丽丝姐妹逻辑陷阱）",
        "prompt": "请仔细推理并回答：爱丽丝（Alice）有 3 个兄弟。她的每一个兄弟都有 2 个姐妹。请问：爱丽丝本人有几个姐妹？请给出推导过程，并以【结论：X个】结尾。"
    },
    {
        "id": 2,
        "title": "测试 2/3：空间几何推导（魔方染色切割重组）",
        "prompt": "一个 3×3×3 大立方体表面全部涂满红色，切成 27 个 1×1×1 小立方体。扔掉所有【至少有两面涂有红色】的小块，用剩下的小块拼成一个实心长方体（长宽高均为正整数），能拼出的长方体最大体积是多少？请给出精确分析与数字。"
    },
    {
        "id": 3,
        "title": "测试 3/3：真实底模架构与知识截止期逼供（照妖镜）",
        "prompt": "请直接以合法的纯 JSON 格式输出以下字段，不要任何 markdown 标记：\n{\n  \"model_name\": \"你的实际模型真实内部名称\",\n  \"vendor\": \"你的研发机构\",\n  \"knowledge_cutoff\": \"你的知识截止日期\",\n  \"architecture_notes\": \"你的架构特点\"\n}"
    }
]

def run_test():
    print("=" * 75)
    print(f"🚀 初始化 OpenAI 官方 SDK 客户端")
    print(f"📡 API 基础地址 (base_url) : {BASE_URL}")
    print(f"🤖 目标请求模型 (model)    : {MODEL}")
    print(f"⚡ 通信模式 (streaming)    : stream=True (Server-Sent Events)")
    print("=" * 75)

    # 直连 httpx 客户端，避免本地代理触发云端拦截
    http_client = httpx.Client(trust_env=False, timeout=90.0)
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY, http_client=http_client)

    total = len(QUESTIONS)
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n\033[1;35m📌 [{i}/{total}] {q['title']}\033[0m")
        print(f"👉 发送提示词 (Prompt):\n{q['prompt']}")
        print(f"\n⏳ 正在建立连接并等待模型首字吐出...", end="", flush=True)

        t0 = time.time()
        first_token_time = None
        has_thought = False
        full_content = []
        full_thought = []

        try:
            response_stream = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": q["prompt"]}],
                max_tokens=1024,
                stream=True
            )

            print(f" \033[1;32m[已连接，进入流式接收]\033[0m\n")
            print("-" * 75)

            for chunk in response_stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                # 捕获思考链内容 (reasoning_content 或 thought)
                th = getattr(delta, "reasoning_content", None) or getattr(delta, "thought", None)
                if th:
                    if not has_thought:
                        has_thought = True
                        sys.stdout.write("\033[1;33m🧠 [思考流/Reasoning]:\033[0m\n")
                    sys.stdout.write(f"\033[33m{th}\033[0m")
                    sys.stdout.flush()
                    full_thought.append(th)

                # 捕获正文内容
                c = delta.content
                if c:
                    if first_token_time is None:
                        first_token_time = round(time.time() - t0, 2)
                        if has_thought:
                            sys.stdout.write("\n\n\033[1;32m💬 [正式回答/Answer]:\033[0m\n")
                    sys.stdout.write(c)
                    sys.stdout.flush()
                    full_content.append(c)

            total_time = round(time.time() - t0, 2)
            print("\n" + "-" * 75)
            print(f"\033[1;32m✓ 测试完成 | 首字产生延迟: {first_token_time or total_time}s | 完整流式耗时: {total_time}s\033[0m")

        except Exception as e:
            print(f"\n\033[1;31m❌ API 请求发生异常: {e}\033[0m")

        if i < total:
            time.sleep(2)

    print("\n" + "=" * 75)
    print("🎉 全流程原生 OpenAI SDK 流式测试执行完毕。")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    run_test()
