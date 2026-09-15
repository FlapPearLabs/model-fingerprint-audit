# 🔍 LLM Model Fingerprinting & Routing Audit (大模型中转路由与真实底模指纹审计)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Audit Status](https://img.shields.io/badge/Audit-Completed-success.svg)]()
[![Date](https://img.shields.io/badge/Date-2026--09--15-orange.svg)]()

一个用于对第三方大模型聚合 API（API Resellers / 中转网关）进行**模型验真、底模指纹探测、版本虚标审计与降配路由追踪**的完整工具包与实测取证库。

---

## 🎯 为什么需要这个项目？

当前许多开发者在使用各类第三方聚合中转 API 时，常常遇到类似困惑：
- *“为什么我切到了标称的最新顶尖模型，开到最高思考模式还是错漏百出？”*
- *“为什么接口里的响应极慢，思考流看起来很像模板或者开源小模型？”*

中转服务商往往通过定制 System Prompt、挂接廉价思考前缀等方式，将两三年前的老旧模型或低成本开源权重重新包装为最新的超大模型对外售卖。

本项目利用**大模型物理级指纹特征（特殊控制 Token、知识截止边界、Tokenizer 细节行为、推理复杂度分界）**，彻底剥除包装，扒出背后的真实底模，并提供**全链路底层报文与实时流式输出**进行公开取证。

---

## 📊 实测审计总表 (Test Results Summary)

针对某主流聚合中转服务（`api.openai-next.com`）的 7 款高知名度模型实测结论如下：

| 客户端展示名称 (Slug) | 网关宣称等级 | 探针扒出的真实底模 | 真实知识截止期 | 实际情况诊断 |
| :--- | :--- | :--- | :--- | :--- |
| **`gpt-6-astra`** | SOTA 旗舰 (2026.09) | **OpenAI o1-preview / o1-mini** | **2024-06** | ❌ **假冒新旗舰**：两年前早期思考模型贴牌，思考慢且水 |
| **`deepseek-v4-pro`**| SOTA 旗舰 (2026.08) | **DeepSeek-V3 (`deepseek-chat`)** | **2025-05** | ❌ **版本虚标**：拿 671B V3 假冒新一代 V4 |
| **`claude-opus-5`** | 超旗舰 (5 代) | **Claude 4.5 / 3.5 Checkpoint** | **2025-01** | ⚠️ **原厂降代**：确为 Anthropic 原厂通道，但版本虚标 |
| **`claude-sonnet-5`**| 旗舰 (5 代) | **Claude Base (拒绝背书 5 代)**| 未披露 | ⚠️ **外挂伪装**：底模防御机制直接拆穿包装 Prompt |
| **`glm-5.3`** | 智谱 5 代旗舰 | **GLM-4** | **2024-07** | ❌ **严重换皮**：拿两年前的 GLM-4 假冒 5.3 |
| **`grok-4.6`** | xAI 4.6 代 | **Grok-1 (初代开源 314B)** | **2023-12** | ❌ **严重注水**：3 年前初代开源权重外挂假思考流 |
| **`kimi-k3`** | Moonshot 思考版 | **Kimi 早期底模** | **2024-06** | ❌ **套壳挂思维**：知识截止停在 2024 年中 |
| **`doubao-seedream...`**| 字节跳动 5.0 | **SeaDream 图像生成 API** | N/A | ❌ **类型错配**：将火山引擎生图接口误挂到对话列表（400 错误） |

---

## 📂 仓库目录结构

```text
├── README.md                           # 项目总览与全模型对比总表
├── LICENSE                             # MIT License
├── docs/
│   └── GROUND_TRUTH.md                 # 靶题标准参考答案、数学推导与判准指南
├── scripts/
│   ├── openai_sdk_stream_test.py      # 官方 OpenAI SDK 原生流式测试脚本 (最简最直观)
│   ├── raw_api_inspector.py            # 底层 HTTP 请求头/响应头/流式 SSE 全报文检查器
│   └── probe_benchmark.py              # 批量多模型自动化指纹探针套件
├── logs/                               # 未经任何删改的第一手真实终端运行日志
│   ├── openai_sdk_stream_run.log       # 官方 OpenAI SDK 流式运行全量终端日志
│   └── user_terminal_wire_inspector_run.log  # Wire-Level 检查器运行全量底层报文日志
├── reports/
│   └── audit_report.md                 # 详尽取证分析报告（逐个模型技术剖析）
└── data/
    └── raw/                            # 自动化批处理原始 JSON 响应数据
        ├── round1_gpt6_deepseek.json
        └── round2_batch_models.json
```

---

## 🚀 终端复现测试指南

### 方法 1：使用官方 OpenAI SDK 原生流式测试（最简推荐）
直接调用 `openai` Python SDK，实时查看思考过程（Reasoning）与流式作答：

```bash
# 使用 uv 一键拉起 SDK 并运行（无需污染系统环境）
uv run --with openai --with httpx python3 scripts/openai_sdk_stream_test.py
```

### 方法 2：使用 Wire-Level 底层报文检查器
查看完整的底层网络协议传输（`POST` 请求行、完整的 `Request Headers`、`Payload JSON`、服务端返回的全部 `Response Headers`、以及逐字接收的 SSE 流）：

```bash
python3 scripts/raw_api_inspector.py
```

### 🎯 验证与判准说明
为了保证测试终端的纯净性与可信度，**终端执行时绝不打印答案干扰**。所有测试题目的标准推导及判题规则已统一归档于文档：
👉 **[docs/GROUND_TRUTH.md](docs/GROUND_TRUTH.md)**

---

## 🔒 真实性与可信度申明
本项目所有在 `logs/` 下存放的日志均为现场真实执行捕获，保留了 Cloudflare `CF-RAY` 标识、上游聚合调度头（`x-shellapi-request-id`）、首包延迟与真实首字吐出时间戳，保证取证链条 100% 真实、客观、可复现。
