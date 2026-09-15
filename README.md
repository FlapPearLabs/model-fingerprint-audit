# 🔍 LLM Model Fingerprinting & Routing Audit (大模型中转路由与真实底模指纹全量审计)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Audit Status](https://img.shields.io/badge/Audit-12_Models_Completed-success.svg)]()
[![Date](https://img.shields.io/badge/Date-2026--09--15-orange.svg)]()

一个用于对第三方大模型聚合 API（API Resellers / 中转网关）进行**模型验真、底模指纹探测、版本虚标审计与跨厂商降配路由追踪**的完整开源工具包与第一手实测证据库。

---

## 🎯 为什么需要这个项目？

在使用第三方聚合中转 API 时，开发者常常遇到类似问题：
- *“为什么我切到了标称的最新顶尖模型，开到最高思考模式还是错漏百出？”*
- *“为什么不同名称的模型，输出语气和思维习惯惊人一致？”*

中转服务商往往通过修改 System Prompt、增加伪思维链包装、甚至跨厂商偷换底座（如拿谷歌 Gemini 充当国产智谱模型）等手段，将老旧廉价模型伪装为顶尖旗舰对外售卖。

本项目利用**大模型物理级指纹特征（原生控制 Token 崩溃、真实知识截止边界、架构自白、推理复杂度分界）**，彻底剥除包装，扒出背后的真实底模。

---

## 📊 12 款模型全量实测审计总表 (Full Audit Results)

针对聚合网关（`api.openai-next.com`）全量 12 款模型的实测结论与证据对应表如下：

| 客户端展示名称 (Slug) | 网关宣称等级 | 探针扒出的真实底模 | 真实知识截止期 | 真实研发机构 | 核心定性诊断 | 完整原始日志 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`gpt-6-astra`** | SOTA 旗舰 (2026.09) | **OpenAI o1-preview / o1-mini** | **2024-06** | OpenAI | ❌ **假冒新旗舰**：两年前早期 o1 贴牌冒充 | [`logs/gpt-6-astra.log`](logs/gpt-6-astra.log) |
| **`claude-sonnet-5`**| 5 代旗舰 | **Claude Base (拒绝背书 5 代)** | 官方未披露 | Anthropic | ⚠️ **外挂虚标**：底模对齐机制直接拆穿包装 Prompt | [`logs/claude-sonnet-5.log`](logs/claude-sonnet-5.log) |
| **`claude-opus-5`** | 5 代超旗舰 | **Claude 4.5 / 3.5 Checkpoint** | **2025-01** | Anthropic | ⚠️ **原厂降代**：确为原厂高阶，但版本号虚标 | [`logs/claude-opus-5.log`](logs/claude-opus-5.log) |
| **`deepseek-v4-pro`**| V4 旗舰 | **DeepSeek-R1 (思维链推理模型)** | **2025-05** | 深度求索 | ⚠️ **模型代换**：拿 R1 充当 V4-Pro 售卖 | [`logs/deepseek-v4-pro.log`](logs/deepseek-v4-pro.log) |
| **`deepseek-v4-flash`**| V4 极速版 | **DeepSeek-V3 (`deepseek-chat`)** | **2025-05** | 深度求索 | ❌ **版本虚标**：拿 671B V3 假冒 V4-Flash | [`logs/deepseek-v4-flash.log`](logs/deepseek-v4-flash.log) |
| **`glm-5.2`** | 智谱 5.2 | **Gemini 1.5 Pro（实锤跨厂！）** | **2024-01** | **Google DeepMind** | 🚨 **跨厂商大换皮**：直接拿谷歌 Gemini 充当智谱模型 | [`logs/glm-5.2.log`](logs/glm-5.2.log) |
| **`glm-5.3`** | 智谱 5.3 | **GLM-4** | **约 2024 年** | Z.ai（智谱） | ❌ **严重换皮**：拿两年前的 GLM-4 假冒 5.3 代 | [`logs/glm-5.3.log`](logs/glm-5.3.log) |
| **`grok-4.6`** | xAI 4.6 | **Grok-2 (MoE)** | **2024-07** | xAI | ❌ **版本虚标**：拿两年前的 Grok-2 假冒 4.6 代 | [`logs/grok-4.6.log`](logs/grok-4.6.log) |
| **`grok-4.5`** | xAI 4.5 | **Grok 4** | 未设固定截止期 | xAI | ⚠️ **底座正常**：确实接入 Grok 体系 | [`logs/grok-4.5.log`](logs/grok-4.5.log) |
| **`qwen3.5-plus`** | 阿里通义 3.5 | **Qwen3.5** | **2026** | 阿里通义实验室 | ✅ **正品在列**：真实 Qwen3.5 权重与 MoE 架构 | [`logs/qwen3.5-plus.log`](logs/qwen3.5-plus.log) |
| **`kimi-k3`** | Moonshot 思考版 | **Kimi 系列编码助手** | 未披露 | Moonshot AI | ⚠️ **底座正常**：月之暗面原生模型 | [`logs/kimi-k3.log`](logs/kimi-k3.log) |
| **`doubao-seedream...`**| 字节跳动 5.0 | **SeaDream 绘图/生图 API** | N/A | 字节跳动 | ❌ **类型错配**：将火山引擎生图接口误挂到对话（HTTP 400） | [`logs/doubao-seedream-5-0-pro-260628.log`](logs/doubao-seedream-5-0-pro-260628.log) |

> 详细深度取证分析请参阅：[`reports/audit_report.md`](reports/audit_report.md)

---

## 🚀 极简本地复现指南 (随便拉到本地跑)

本项目主脚本 `scripts/audit_all_models.py` **完全采用 Python 3 标准库（内置 `urllib`），零第三方依赖（无需 `pip install` 任何包）**，任何环境拉下来就能直接跑！

### 1. 克隆仓库
```bash
git clone https://github.com/FlapPearLabs/model-fingerprint-audit.git
cd model-fingerprint-audit
```

### 2. 运行测试（开箱即用）

#### 一键审计全量 12 款模型：
```bash
python3 scripts/audit_all_models.py
```

#### 单独审计某一款感兴趣的模型：
```bash
# 测试谷歌偷梁换柱智谱的 glm-5.2
python3 scripts/audit_all_models.py glm-5.2

# 测试贴牌早期 o1 的 gpt-6-astra
python3 scripts/audit_all_models.py gpt-6-astra

# 测试 DeepSeek 系列
python3 scripts/audit_all_models.py deepseek-v4-pro
```

#### 查看支持的所有模型名称：
```bash
python3 scripts/audit_all_models.py --list
```

---

## 📂 仓库目录结构

```text
├── README.md                           # 全模型实测总表与快速复现
├── LICENSE                             # MIT License
├── docs/
│   └── GROUND_TRUTH.md                 # 靶题唯一标准答案、数学推导与判题依据
├── scripts/
│   ├── audit_all_models.py             # 【推荐】零依赖全量模型自动化流式审计主程序
│   ├── openai_sdk_stream_test.py      # 官方 OpenAI SDK 原生流式测试脚本
│   ├── raw_api_inspector.py            # 底层 Wire-Level 报文与请求头检查器
│   └── probe_benchmark.py              # 批量多模型自动化指纹探针
├── logs/                               # 12 款模型全部第一手未经删改的真实终端日志
│   ├── gpt-6-astra.log
│   ├── glm-5.2.log                     # （惊现 Google Gemini 1.5 Pro 底模！）
│   ├── glm-5.3.log
│   ├── deepseek-v4-pro.log
│   ├── deepseek-v4-flash.log
│   ├── claude-opus-5.log
│   ├── claude-sonnet-5.log
│   ├── grok-4.6.log
│   ├── grok-4.5.log
│   ├── qwen3.5-plus.log
│   ├── kimi-k3.log
│   └── doubao-seedream-5-0-pro-260628.log
├── reports/
│   └── audit_report.md                 # 12 款模型深度技术剖析与跨厂证据链
└── data/
    └── raw/                            # 批处理原始 JSON 数据
```

---

## 🔒 客观性与可信度申明
为了保证 100% 的客观性与公信力：
1. **终端绝不输出预设答案**：脚本运行时只负责将底层报文和模型流式 Token 实时打到屏幕并落盘，绝不输出任何先入为主的提示；所有参考答案均放在 [`docs/GROUND_TRUTH.md`](docs/GROUND_TRUTH.md) 供事后交叉比对。
2. **日志完全未删改**：`logs/` 下的 12 份模型日志均为实机运行真实捕获，保留了毫秒级时间戳、首字延迟与服务端的真实错误响应。
