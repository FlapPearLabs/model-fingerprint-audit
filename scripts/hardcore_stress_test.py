#!/usr/bin/env python3
"""
高阶硬核智力与知识库时间锚点极限压力测试套件
1. 禁用联网 + 纯 JSON 结构化时间锚点自证（2024大选、巴黎奥运、DeepSeek R1发布时间）
2. 经典高难 24 点分数陷阱（3, 3, 8, 8 = 24）
3. 农夫过河反直觉约束（强制每次返程必须带且仅带一样物品，不可行性数学证明）
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai-next.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-5VtGgYO9LJkHjC1oAb396f0fDaD849EeBc43C3873cBc1f05")

CANDIDATE_MODELS = [
    {"slug": "claude-fable-5-1", "desc": "宣称 Fable 5.1 (Mythos级)"},
    {"slug": "claude-fable-5", "desc": "宣称 Fable 5"},
    {"slug": "claude-opus-5", "desc": "宣称 Opus 5"},
    {"slug": "claude-sonnet-5", "desc": "宣称 Sonnet 5"},
    {"slug": "claude-opus-4-8", "desc": "宣称 Opus 4.8"},
    {"slug": "claude-sonnet-4-6", "desc": "宣称 Sonnet 4.6"},
    {"slug": "chatgpt-4o-latest", "desc": "OpenAI 原厂对照组"},
    {"slug": "qwen3.5-plus", "desc": "阿里 2026 对照组"}
]

PROMPT_JSON_TEMPORAL = """严禁使用任何联网搜索。仅基于你的底层纯静态预训练参数记忆回答。
请严格输出纯 JSON，严禁任何 markdown 标记、反引号或多余文字。
格式必须严格如下：
{
  "self_reported_model_id": "你的确切模型型号",
  "developer": "研发机构",
  "knowledge_cutoff": "YYYY-MM",
  "us_presidential_election_2024_winner": "2024年11月美国总统大选获胜者是谁？若未包含请填'未知'",
  "paris_olympics_2024_mens_100m_champion": "2024年8月巴黎奥运会男子百米飞人金牌得主是谁？若未包含请填'未知'",
  "deepseek_r1_release_date": "DeepSeek R1 是哪年哪月发布的？若未包含请填'未知'"
}"""

PROMPT_MATH_24 = """请仅使用数字 3、3、8、8 各一次，配合加、减、乘、除四则运算与括号，计算出严格等于 24 的算式。
请给出最终算式，并一步一步写出分数运算验证过程，最后以【最终算式：...】结尾。"""

PROMPT_RIVER_CONSTRAINED = """经典的农夫过河问题：农夫要带一只狼、一只羊、一棵白菜过河。农夫在场时安全，不在场时狼吃羊、羊吃白菜。
现在增加一个不可更改的严苛规则：【船每次过河（无论是去程还是返程），农夫必须带且只能带一样物品，绝对不允许空船返回】。
请问：农夫能否安全将三样物品全部运送到对岸？
请进行严格的形式逻辑推导：如果可行请列出每一步渡河步骤；如果不可行请给出严格的奇偶性/状态不可行性证明。最后以【结论：可行 / 不可行】结尾。"""

def send_prompt(slug, prompt, max_tokens=600):
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
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }
    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with opener.open(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = round(time.time() - t0, 2)
            msg = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return {"ok": True, "elapsed": elapsed, "content": msg, "id": data.get("id", "")}
    except Exception as e:
        return {"ok": False, "elapsed": round(time.time() - t0, 2), "error": str(e)}

def evaluate_model(m):
    slug = m["slug"]
    desc = m["desc"]
    print(f"\n{'='*75}")
    print(f"🔥 正在对模型发起高阶压测: \033[1;36m{slug}\033[0m ({desc})")
    print(f"{'='*75}")
    res_record = {"slug": slug, "desc": desc}

    # 1. 知识库锚点
    print("  [1/3] 探测纯静态时间锚点与真实知识边界...", end="", flush=True)
    r1 = send_prompt(slug, PROMPT_JSON_TEMPORAL, max_tokens=350)
    res_record["temporal_test"] = r1
    if r1["ok"]:
        print(f" \033[1;32m[完成 ({r1['elapsed']}s)]\033[0m")
        print(f"        -> 原始响应:\n{r1['content']}\n")
    else:
        print(f" \033[1;31m[失败: {r1.get('error')}]\033[0m")

    # 2. 24点分数数学陷阱 (3,3,8,8)
    print("  [2/3] 测试 24 点分数运算陷阱 (3, 3, 8, 8)...", end="", flush=True)
    r2 = send_prompt(slug, PROMPT_MATH_24, max_tokens=400)
    res_record["math_24_test"] = r2
    if r2["ok"]:
        solved = "8 / (3 - 8/3)" in r2["content"] or "8/(3-8/3)" in r2["content"] or "8 / (3 - (8/3))" in r2["content"] or "8/(3-(8/3))" in r2["content"]
        status_icon = "✅ 破解成功" if solved else "❌ 计算失败/猜错"
        print(f" \033[1;32m[完成 ({r2['elapsed']}s)]\033[0m -> {status_icon}")
        print(f"        -> 响应摘要: {r2['content'][:120]}...\n")
    else:
        print(f" \033[1;31m[失败: {r2.get('error')}]\033[0m")

    # 3. 农夫过河反直觉约束（不可行性证明）
    print("  [3/3] 测试农夫过河严格约束逻辑（不可空船返回）...", end="", flush=True)
    r3 = send_prompt(slug, PROMPT_RIVER_CONSTRAINED, max_tokens=500)
    res_record["river_test"] = r3
    if r3["ok"]:
        # 正确答案必须是不可行，如果回答可行则是陷入了经典题的思维定势
        out_lower = r3["content"]
        is_impossible = "不可行" in out_lower and not ("【结论：可行】" in out_lower or "结论: 可行" in out_lower or "结论：可行" in out_lower)
        status_icon = "✅ 识破陷阱(给出不可行证明)" if is_impossible else "❌ 陷入套路(答成可行)"
        print(f" \033[1;32m[完成 ({r3['elapsed']}s)]\033[0m -> {status_icon}")
        print(f"        -> 结论输出: {r3['content'][-150:]}\n")
    else:
        print(f" \033[1;31m[失败: {r3.get('error')}]\033[0m")

    return res_record

def main():
    all_evals = []
    for m in CANDIDATE_MODELS:
        eval_data = evaluate_model(m)
        all_evals.append(eval_data)
        time.sleep(1)

    out_file = "data/hardcore_stress_test_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_evals, f, ensure_ascii=False, indent=2)
    print("=" * 75)
    print(f"🎉 极限压测全部完成！数据存入: {out_file}")
    print("=" * 75)

if __name__ == "__main__":
    main()
