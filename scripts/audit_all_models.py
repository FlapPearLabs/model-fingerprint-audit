#!/usr/bin/env python3
"""
大模型聚合通道全模型指纹与路由审计工具 (LLM Multi-Model Wire Audit Runner)
零第三方依赖（纯 Python 标准库），一键拉取即跑。
支持全量模型批量扫描、单模型深入探测、实时流式输出与原始报文完整落盘。
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

# 配置（支持通过环境变量覆盖）
API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai-next.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05")

# 待审计的 12 款全部模型列表
ALL_MODELS = [
    {"name": "GPT-6 Astra", "slug": "gpt-6-astra"},
    {"name": "Claude Sonnet 5", "slug": "claude-sonnet-5"},
    {"name": "Claude Opus 5", "slug": "claude-opus-5"},
    {"name": "DeepSeek V4 Pro", "slug": "deepseek-v4-pro"},
    {"name": "DeepSeek V4 Flash", "slug": "deepseek-v4-flash"},
    {"name": "Grok 4.6", "slug": "grok-4.6"},
    {"name": "Grok 4.5", "slug": "grok-4.5"},
    {"name": "Qwen 3.5 Plus", "slug": "qwen3.5-plus"},
    {"name": "GLM 5.3", "slug": "glm-5.3"},
    {"name": "GLM 5.2", "slug": "glm-5.2"},
    {"name": "Kimi K3", "slug": "kimi-k3"},
    {"name": "Doubao 5.0 Pro", "slug": "doubao-seedream-5-0-pro-260628"}
]

# 统一审计靶题（不含任何答案，仅包含测试 Prompt）
QUESTIONS = [
    {
        "id": "logic_alice",
        "title": "测试 1：多步逻辑推理陷阱（爱丽丝兄弟姐妹集合推理）",
        "prompt": "请仔细推理并回答：爱丽丝（Alice）有 3 个兄弟。她的每一个兄弟都有 2 个姐妹。请问：爱丽丝本人有几个姐妹？请给出推导过程，并以【结论：X个】结尾。"
    },
    {
        "id": "geometry_cube",
        "title": "测试 2：高阶空间几何推导（魔方染色切割重组）",
        "prompt": "一个 3×3×3 大立方体表面全部涂满红色，切成 27 个 1×1×1 小立方体。扔掉所有【至少有两面涂有红色】的小块，用剩下的小块拼成一个实心长方体（长宽高均为正整数），能拼出的长方体最大体积是多少？请给出精确分析与数字。"
    },
    {
        "id": "identity_cutoff",
        "title": "测试 3：底座真实身份与知识截止期逼供（照妖镜）",
        "prompt": "请直接以合法的纯 JSON 格式输出以下字段，不要任何 markdown 标记：\n{\n  \"model_name\": \"你的实际模型真实内部名称\",\n  \"vendor\": \"你的研发机构\",\n  \"knowledge_cutoff\": \"你的知识截止日期\",\n  \"architecture_notes\": \"你的架构特点\"\n}"
    }
]

class TeeLogger:
    """双向流写入器：同时输出到控制台与落盘日志文件"""
    def __init__(self, filepath):
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        self.file = open(filepath, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)
        self.stdout.flush()
        self.file.flush()

    def flush(self):
        self.stdout.flush()
        self.file.flush()

    def close(self):
        self.file.close()

def audit_single_model(model_info, log_dir="logs"):
    slug = model_info["slug"]
    name = model_info["name"]
    log_file = os.path.join(log_dir, f"{slug}.log")
    
    logger = TeeLogger(log_file)
    old_stdout = sys.stdout
    sys.stdout = logger

    try:
        print("\n" + "#" * 75)
        print(f"🚀 开始审计模型: {name} (Slug: {slug})")
        print(f"📡 目标接口: {API_BASE}/chat/completions")
        print(f"📝 原始日志记录文件: {log_file}")
        print("#" * 75)

        url = f"{API_BASE.rstrip('/')}/chat/completions"
        proxy_handler = urllib.request.ProxyHandler({}) # 直连避免代理误伤
        opener = urllib.request.build_opener(proxy_handler)

        for i, q in enumerate(QUESTIONS, 1):
            print("\n" + "=" * 75)
            print(f"📌 [{i}/{len(QUESTIONS)}] {q['title']}")
            print("=" * 75)

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "curl/7.88.1",
                "Accept": "text/event-stream"
            }
            payload = {
                "model": slug,
                "messages": [{"role": "user", "content": q["prompt"]}],
                "max_tokens": 1024,
                "stream": True
            }
            encoded_payload = json.dumps(payload, ensure_ascii=False, indent=2)

            print("\n[>>> 1. 发出的底层请求数据]")
            masked_auth = API_KEY[:10] + "..." + API_KEY[-6:] if len(API_KEY) > 16 else "***"
            print(f"  POST {url} HTTP/1.1")
            print(f"  Authorization: Bearer {masked_auth}")
            print(f"  Content-Type: application/json")
            print(f"  Accept: text/event-stream")
            print(f"  Payload: {json.dumps(payload, ensure_ascii=False)}")

            print("\n[⏳ 发起网络通信，等待首包响应...]")
            req = urllib.request.Request(url, data=encoded_payload.encode("utf-8"), headers=headers)
            t0 = time.time()
            first_token_time = None

            try:
                with opener.open(req, timeout=90) as resp:
                    elapsed_connect = round(time.time() - t0, 2)
                    print(f"[✓ HTTP 连接建立成功，首包耗时: {elapsed_connect}s]")
                    print(f"  HTTP/{resp.version} {resp.status} {resp.reason}")
                    for k, v in resp.headers.items():
                        print(f"  {k}: {v}")

                    print("\n[<<< 2. 模型实时流式输出 (Raw Stream)]")
                    print("-" * 75)

                    for line in resp:
                        decoded = line.decode("utf-8").strip()
                        if not decoded or decoded == "data: [DONE]":
                            continue
                        if decoded.startswith("data: "):
                            try:
                                chunk = json.loads(decoded[6:])
                                choice = chunk.get("choices", [{}])[0]
                                delta = choice.get("delta", {})

                                # 打印思考链
                                th = delta.get("reasoning_content") or delta.get("thought")
                                if th:
                                    sys.stdout.write(th)
                                    sys.stdout.flush()

                                # 打印正式回答
                                c = delta.get("content")
                                if c:
                                    if first_token_time is None:
                                        first_token_time = round(time.time() - t0, 2)
                                    sys.stdout.write(c)
                                    sys.stdout.flush()
                            except Exception:
                                pass

                    total_time = round(time.time() - t0, 2)
                    print("\n" + "-" * 75)
                    print(f"[✓ 流式完成 | 首字延迟: {first_token_time or total_time}s | 总耗时: {total_time}s]")

            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                print(f"\n[❌ HTTP 异常报错 HTTP {e.code}]: {err_body}")
            except Exception as e:
                print(f"\n[❌ 通信异常报错]: {e}")

            if i < len(QUESTIONS):
                time.sleep(2)

        print("\n" + "#" * 75)
        print(f"✓ 模型 {name} ({slug}) 审计取证完毕，完整原始输出已存入: {log_file}")
        print("#" * 75 + "\n")

    finally:
        sys.stdout = old_stdout
        logger.close()

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("使用说明:")
        print("  python3 scripts/audit_all_models.py                # 自动审计全部 12 款模型")
        print("  python3 scripts/audit_all_models.py <model_slug>   # 审计指定的某一个模型")
        print("  python3 scripts/audit_all_models.py --list         # 查看支持的全部模型列表")
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        print("支持审计的全部模型 Slug 列表:")
        for m in ALL_MODELS:
            print(f"  - {m['slug']} ({m['name']})")
        sys.exit(0)

    target_models = ALL_MODELS
    if len(sys.argv) > 1:
        slug_input = sys.argv[1]
        matched = [m for m in ALL_MODELS if m["slug"] == slug_input]
        if matched:
            target_models = matched
        else:
            target_models = [{"name": slug_input, "slug": slug_input}]

    print("=" * 75)
    print(f"🔍 启动大模型聚合网关全链路审计套件 (总计 {len(target_models)} 款模型)")
    print(f"🌐 目标地址: {API_BASE}")
    print("=" * 75)

    for idx, model in enumerate(target_models, 1):
        print(f"\n>>> 进度 [{idx}/{len(target_models)}]: 正在审计 {model['name']} ({model['slug']})...")
        audit_single_model(model, log_dir="logs")
        if idx < len(target_models):
            time.sleep(3)

    print("\n" + "=" * 75)
    print(f"🎉 全部 {len(target_models)} 款模型审计执行完毕！所有原始日志均在 logs/ 目录。")
    print("=" * 75)

if __name__ == "__main__":
    main()
