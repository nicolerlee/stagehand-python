# Stagehand Python 项目技术分析文档

## 目录
- [项目概述](#项目概述)
- [配置文件分析](#配置文件分析)
- [环境变量优化](#环境变量优化)
- [代码转换实践](#代码转换实践)
- [大模型调用架构](#大模型调用架构)
- [LiteLLM 统一接口](#litellm-统一接口)

---

## 项目概述

**Stagehand** 是一个AI驱动的浏览器自动化框架，提供自然语言与代码结合的方式来自动化Web操作。

### 核心功能
- **act** — 使用自然语言指示AI执行操作（如点击按钮或滚动）
- **extract** — 使用Pydantic模式从页面提取和验证数据
- **observe** — 获取自然语言解释来识别页面选择器或元素
- **agent** — 执行多步自主任务（OpenAI、Anthropic等）

---

## 配置文件分析

### pyproject.toml 详解

`pyproject.toml` 是Python项目的现代化统一配置文件，包含：

#### 1. 项目元数据
```toml
[project]
name = "stagehand"
version = "0.4.0"
description = "Python SDK for Stagehand"
requires-python = ">=3.9"
```

#### 2. 依赖管理
```toml
dependencies = [
    "httpx>=0.24.0", 
    "python-dotenv>=1.0.0", 
    "pydantic>=1.10.0",
    "playwright>=1.42.1",
    "openai>=1.83.0",
    "anthropic>=0.51.0",
    "litellm>=1.72.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.1",
    "black>=23.3.0", 
    "ruff",
    "mypy>=1.3.0"
]
```

#### 3. 开发工具配置
- **Black**（代码格式化）
- **Ruff**（代码检查）
- **pytest**（测试框架）
- **MyPy**（类型检查）

### .egg-info 目录

`stagehand.egg-info` 是Python包安装时自动生成的元数据目录：

#### 文件结构
- `PKG-INFO` - 包的完整元数据和依赖信息
- `requires.txt` - 依赖清单（核心依赖 + [dev]开发依赖）
- `top_level.txt` - 顶级包名（`stagehand`）
- `SOURCES.txt` - 源文件清单
- `dependency_links.txt` - 依赖链接（通常为空）

#### 作用
- 让 `pip list` 能看到已安装的包
- 管理包的依赖关系
- 支持 `import stagehand` 正常工作
- 允许 `pip uninstall stagehand` 正确卸载

---

## 环境变量优化

### load_dotenv() 路径修复

**问题**：原代码使用 `load_dotenv()` 无参数调用，可能因工作目录不同导致 `.env` 文件加载失败。

**解决方案**：为所有文件添加基于 `__file__` 的绝对路径参数：

#### 修改示例
```python
# 修改前
load_dotenv()

# 修改后 - 不同目录层级
# 主目录文件
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 子目录文件  
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
```

#### 修改的文件
- `stagehand/main.py`
- `examples/quickstart.py`
- `examples/agent_example.py` 
- `examples/example.py`
- `stagehand/agent/openai_cua.py`
- `stagehand/agent/anthropic_cua.py`

---

## 代码转换实践

### TypeScript → Python 转换

将 `h5_novel_act.ts` 转换为 `h5_novel_act.py`：

#### 主要转换内容

1. **导入和配置**
```typescript
// TypeScript
import { Stagehand } from "../dist";
import StagehandConfig from "@/stagehand.config";

// Python
from stagehand import Stagehand, StagehandConfig
```

2. **配置对象**
```python
config = StagehandConfig(
    env="LOCAL",
    model_name="google/gemini-2.5-flash-preview-05-20",
    model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
    verbose=1,
    headless=False,
    dom_settle_timeout_ms=3000,
)
```

3. **文件操作**
```typescript
// TypeScript
const logDir = path.join(__dirname, "log");
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
}

// Python
log_dir = Path(__file__).parent / "log"
if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)
```

4. **异步等待**
```typescript
// TypeScript
await page.waitForTimeout(2000);

// Python  
await asyncio.sleep(2)
```

---

## 大模型调用架构

### 三个核心调用位置

#### 1. 主要入口：`stagehand/llm/client.py` (第123行)
```python
# 最重要的调用位置 - 处理所有基础操作
response = litellm.completion(**filtered_params)
```
**用途**：
- 处理 `page.act()` - 页面操作
- 处理 `page.observe()` - 页面观察  
- 处理 `page.extract()` - 数据提取

#### 2. OpenAI代理：`stagehand/agent/openai_cua.py` (第384行)
```python
# OpenAI 计算机使用代理的直接调用
response = self.openai_sdk_client.responses.create(
    model=self.model,
    input=current_input_items,
    tools=self.tools,
    reasoning={"summary": "concise"},
    truncation="auto",
)
```

#### 3. Anthropic代理：`stagehand/agent/anthropic_cua.py` (第164行)
```python
# Anthropic 计算机使用代理的直接调用
response = self.anthropic_sdk_client.beta.messages.create(
    model=self.model,
    max_tokens=self.max_tokens,
    system=self.instructions + "Remember to call the computer tools...",
    messages=current_messages,
    tools=self.tools,
    betas=self.beta_flag,
)
```

### 调用流程图
```
用户调用
├── page.act/observe/extract → stagehand/llm/client.py → litellm.completion
└── stagehand.agent.execute
    ├── OpenAI Agent → openai_sdk_client.responses.create  
    └── Anthropic Agent → anthropic_sdk_client.beta.messages.create
```

---

## LiteLLM 统一接口

### 什么是 LiteLLM？

**LiteLLM** 是一个**统一多个AI模型提供商API的中间层**，提供标准化接口来调用各种不同的AI模型。

### 核心优势

#### 1. 统一API接口
```python
import litellm

# 调用不同模型，代码格式完全相同
# OpenAI
response = litellm.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Anthropic  
response = litellm.completion(
    model="claude-3-opus-20240229", 
    messages=[{"role": "user", "content": "Hello"}]
)

# Google Gemini
response = litellm.completion(
    model="gemini/gemini-pro",
    messages=[{"role": "user", "content": "Hello"}]
)
```

#### 2. 支持的模型提供商
- **OpenAI**: GPT-4, GPT-3.5
- **Anthropic**: Claude-3, Claude-2
- **Google**: Gemini, PaLM
- **Azure OpenAI**: Azure版GPT模型
- **AWS Bedrock**: Amazon模型服务
- **Cohere**: Command系列模型
- **Hugging Face**: 开源模型
- **Ollama**: 本地部署模型
- **100+其他提供商**

#### 3. 统一的响应格式
```python
{
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "响应内容"
            }
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
}
```

### 在 Stagehand 中的应用

#### 模型切换灵活性
```python
# 用户可以轻松切换模型
config = StagehandConfig(
    model_name="gpt-4o",                    # OpenAI
    # model_name="claude-3-opus-20240229",  # Anthropic  
    # model_name="gemini/gemini-pro",       # Google
    model_client_options={"apiKey": "your_api_key"}
)
```

#### 智能模型名称处理
```python
# Stagehand 中的自动映射
if completion_model.startswith("google/"):
    completion_model = completion_model.replace("google/", "gemini/")
```

#### 统一错误处理和监控
```python
try:
    response = litellm.completion(**filtered_params)
    # 统一的使用统计
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
except Exception as e:
    # 统一处理所有提供商的错误
    self.logger.error(f"Error calling litellm.completion: {e}")
```

### 关键特性

1. **🔄 统一接口**：一套代码调用所有AI模型
2. **🔧 简化集成**：不需要学习每个提供商的API  
3. **📊 标准化响应**：所有模型返回相同格式的数据
4. **💰 成本透明**：统一的使用量统计和成本计算
5. **🚀 快速切换**：更换AI提供商只需改一行配置

---

## 总结

Stagehand 通过以下技术架构实现了强大的AI浏览器自动化能力：

1. **现代化配置管理**：使用 `pyproject.toml` 统一管理项目配置
2. **环境变量最佳实践**：确保 `.env` 文件正确加载
3. **多语言支持**：支持 TypeScript 和 Python 实现
4. **统一模型接口**：通过 LiteLLM 支持多种AI模型提供商
5. **分层架构设计**：基础操作与高级Agent分离

这种设计让开发者可以：
- 自由选择AI模型提供商
- 在自然语言和代码之间灵活切换
- 快速构建复杂的浏览器自动化任务
