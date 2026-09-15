#!/usr/bin/env python3
"""
底层 API 原生流量检查器 (Raw Wire-Level API Inspector)
实时打印 HTTP 请求头、请求体、响应头、流式 Token 与标准答案比对。
"""

import urllib.request
import json
import time
import sys

URL = "https://api.openai-next.com/v1/chat/completions"
API_KEY = "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05"
MODEL = "gpt-6-astra"

QUESTIONS = [
    {
        "id": 1,
        "title": "测试 1：爱丽丝姐妹逻辑陷阱（多步逻辑推理）",
        "prompt": "请仔细推理并回答：爱丽丝（Alice）有 3 个兄弟。她的每一个兄弟都有 2 个姐妹。请问：爱丽丝本人有几个姐妹？请给出推导过程，并以【结论：X个】结尾。",
        "standard_answer": "【1个】（全家女孩总数是2个，爱丽丝除外只有1个姐妹；若答2个或6个则为错）"
    },
    {
        "id": 2,
        "title": "测试 2：魔方染色切割重组（高阶空间几何推导）",
        "prompt": "一个 3×3×3 大立方体表面全部涂满红色，切成 27 个 1×1×1 小立方体。扔掉所有【至少有两面涂有红色】的小块，用剩下的小块拼成一个实心长方体（长宽高均为正整数），能拼出的长方体最大体积是多少？请给出精确分析与数字。",
        "standard_answer": "【7】（只剩6个面中心块+1个内部核心块共7块，7是质数，只能拼成 1×1×7，体积为7）"
    },
    {
        "id": 3,
        "title": "测试 3：底座真实身份与知识截止期逼供（照妖镜）",
        "prompt": "请直接以合法的纯 JSON 格式输出以下字段，不要任何 markdown 标记：\n{\n  \"model_name\": \"你的实际模型真实内部名称\",\n  \"vendor\": \"你的研发机构\",\n  \"knowledge_cutoff\": \"你的知识截止日期\",\n  \"architecture_notes\": \"你的架构特点\"\n}",
        "standard_answer": "真实 GPT-6 Astra 应为 2025 年末至 2026 年最新知识库；若返回 2024-06 则实锤为早期 o1-preview/mini 贴牌。"
    }
]

def inspect_call(q_idx=0):
    q = QUESTIONS[q_idx]
    
    print("\n" + "=" * 70)
    print(f"\033[1;35m📌 当前运行测试项: {q['title']}\033[0m")
    print("=" * 70)

    # 1. 组装底层请求数据
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "curl/7.88.1",
        "Accept": "text/event-stream"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": q["prompt"]}],
        "max_tokens": 1024,
        "stream": True
    }
    encoded_payload = json.dumps(payload, ensure_ascii=False, indent=2)

    # 2. 打印请求底层细节
    print("\n\033[1;34m[>>> 1. 底层请求行与目标 URL]\033[0m")
    print(f"POST {URL} HTTP/1.1")
    print(f"Host: api.openai-next.com")
    
    print("\n\033[1;34m[>>> 2. 实际发出的完整请求头 (Request Headers)]\033[0m")
    for k, v in headers.items():
        if k.lower() == "authorization":
            # 显示首尾保留中间脱敏，也可直接查验
            masked = v[:17] + "..." + v[-8:]
            print(f"  {k}: {masked}")
        else:
            print(f"  {k}: {v}")

    print("\n\033[1;34m[>>> 3. 实际发出的请求体 Payload (JSON)]\033[0m")
    print(encoded_payload)

    # 3. 发起请求并捕获响应头
    print("\n\033[1;33m[⏳ 正在建立 TCP/TLS 连接并发送请求...]\033[0m")
    proxy_handler = urllib.request.ProxyHandler({}) # 直连
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(URL, data=encoded_payload.encode("utf-8"), headers=headers)
    
    t0 = time.time()
    try:
        with opener.open(req, timeout=90) as resp:
            elapsed_connect = round(time.time() - t0, 2)
            print(f"\033[1;32m[✓ 连接建立成功，首包耗时: {elapsed_connect}s]\033[0m")
            
            print("\n\033[1;32m[<<< 4. 服务端返回的 HTTP 状态与响应头 (Response Headers)]\033[0m")
            print(f"  HTTP/{resp.version} {resp.status} {resp.reason}")
            for k, v in resp.headers.items():
                print(f"  {k}: {v}")

            print("\n\033[1;36m[<<< 5. 模型实时流式输出 (Real-time Token Stream)]\033[0m")
            print("----------------------------------------------------------------------")
            
            full_content = []
            full_thought = []
            first_token_time = None
            
            for line in resp:
                decoded_line = line.decode("utf-8").strip()
                if not decoded_line:
                    continue
                if decoded_line == "data: [DONE]":
                    break
                if decoded_line.startswith("data: "):
                    raw_data = decoded_line[6:]
                    try:
                        chunk = json.loads(raw_data)
                        choice = chunk.get("choices", [{}])[0]
                        delta = choice.get("delta", {})
                        
                        # 捕获思考流
                        th = delta.get("reasoning_content") or delta.get("thought")
                        if th:
                            full_thought.append(th)
                            sys.stdout.write(f"\033[33m{th}\033[0m")
                            sys.stdout.flush()
                        
                        # 捕获正文流
                        c = delta.get("content")
                        if c:
                            if first_token_time is None:
                                first_token_time = round(time.time() - t0, 2)
                            full_content.append(c)
                            sys.stdout.write(c)
                            sys.stdout.flush()
                    except Exception:
                        pass
            
            total_elapsed = round(time.time() - t0, 2)
            print("\n----------------------------------------------------------------------")
            print(f"\033[1;32m[✓ 流式接收完成 | 首字延迟: {first_token_time or total_elapsed}s | 总耗时: {total_elapsed}s]\033[0m")

    except Exception as e:
        print(f"\n\033[1;31m[❌ 请求报错: {e}]\033[0m")

    print("\n\033[1;35m[🎯 标准答案与核对指南]\033[0m")
    print(f"标准答案：{q['standard_answer']}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    choice = 0
    if len(sys.argv) > 1:
        try:
            choice = int(sys.argv[1]) - 1
            if choice not in [0, 1, 2]:
                choice = 0
        except ValueError:
            choice = 0
    inspect_call(choice)
