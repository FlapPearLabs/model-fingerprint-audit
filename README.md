# 🔍 LLM Model Fingerprinting & Routing Audit (大模型中转路由与真实底模指纹审计)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Audit Status](https://img.shields.io/badge/Audit-Completed-success.svg)]()
[![Date](https://img.shields.io/badge/Date-2026--09--15-orange.svg)]()

一个用于对第三方大模型聚合 API（API Resellers / 中转网关）进行**模型验真、底模指纹探测、版本虚标审计与降配路由追踪**的完整工具包与实测证据库。

---

## 🎯 为什么需要这个项目？

当前许多开发者在使用各类第三方聚合中转 API 时，常常遇到类似困惑：
- *“为什么我切到了标称的最新顶尖模型，开到最高思考模式还是错漏百出？”*
- *“为什么接口里的响应极慢，思考流看起来很像模板或者开源小模型？”*

中转服务商往往通过定制 System Prompt、挂接廉价思考前缀等方式，将两三年前的老旧模型或低成本开源权重重新包装为最新的超大模型对外售卖。

本项目利用**大模型物理级指纹特征（特殊控制 Token、知识截止边界、Tokenizer 细节行为、推理复杂度分界）**，彻底剥除包装，扒出背后的真实底模。

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

> 完整审计取证记录详见：[`reports/audit_report.md`](reports/audit_report.md)

---

## 🛠️ 指纹探测核心方法 (Forensic Probes)

1. **特殊控制符诱捕法（Special Token Leak）**：
   - 探查 `<｜begin of sentence｜>` 或 `<|im_start|>` 等厂商硬编码控制符。开源底座遇到自身特殊标记时会产生不可掩盖的截断或崩溃现象。
2. **底层元数据与知识截止期逼供（Identity & Cutoff Probe）**：
   - 绕过表层角色扮演提示词，诱导模型从底层权重参数库中输出真实的 `knowledge_cutoff` 和架构规格。
3. **思考链心理语言学特征（Thought Trace Stylometry）**：
   - 分析思考流是 OpenAI Responses 原生摘要，还是 DeepSeek-R1 风格中英混杂碎碎念，或是中转站前端硬拼接的假思考。
4. **高阶逻辑与注意力穿透力靶题（Reasoning Shibboleths）**：
   - 爱丽丝姐妹逻辑陷阱（秒杀误读女孩总数的小模型）。
   - Strawberry 倒序与辅音编码（测试注意力是否在长序列字符上串行）。
   - 染色立方体切割重组（测试复杂多步空间几何推导）。

---

## 🚀 本地快速复现 (Quick Start)

### 1. 配置环境变量
```bash
export OPENAI_API_BASE="https://api.openai-next.com/v1"
export OPENAI_API_KEY="your-api-key-here"
```

### 2. 运行自动化探针
```bash
# 测试指定模型
python3 scripts/probe_benchmark.py gpt-6-astra deepseek-v4-pro grok-4.6

# 批量测试全部默认模型
python3 scripts/probe_benchmark.py
```

测试结果将自动生成格式化 JSON 并保存在 `data/raw/` 目录下。

---

## 📂 仓库目录结构

```text
├── README.md                      # 项目总览与核心结论速查
├── LICENSE                        # MIT License
├── scripts/
│   └── probe_benchmark.py         # 自动化指纹探测与靶向测试主脚本
├── reports/
│   └── audit_report.md            # 详尽的取证日志与逐个模型深度剖析
└── data/
    └── raw/                       # 原始第一手 JSON 响应证据
        ├── round1_gpt6_deepseek.json
        └── round2_batch_models.json
```

---

## 🔒 隐私与安全性申明
本项目开源的所有测试原始日志及测试脚本中，已严格剥离所有个人 API Token 及敏感认证信息。测试数据均来源于标准接口返回。
