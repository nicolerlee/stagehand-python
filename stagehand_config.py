"""
Stagehand Python 配置文件 - 简化版
提供直观易用的配置管理
"""

import os
from dotenv import load_dotenv
from stagehand import StagehandConfig

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# 基础配置参数
BASE_CONFIG = {
    "verbose": 2,
    "dom_settle_timeout_ms": 30000,
    "experimental": False,
}

# 浏览器配置
BROWSER_CONFIG = {
    "local": {
        "env": "LOCAL",
        "local_browser_launch_options": {
            "headless": False,
            "viewport": {"width": 1024, "height": 768},
        }
    },
    "local_headless": {
        "env": "LOCAL", 
        "local_browser_launch_options": {
            "headless": True,
            "viewport": {"width": 1024, "height": 768},
        }
    },
    "browserbase": {
        "env": "BROWSERBASE",
        "api_key": os.getenv("BROWSERBASE_API_KEY"),
        "project_id": os.getenv("BROWSERBASE_PROJECT_ID"),
        "browserbase_session_create_params": {
            "projectId": os.getenv("BROWSERBASE_PROJECT_ID"),
            "browserSettings": {
                "blockAds": True,
                "viewport": {"width": 1024, "height": 768},
            },
        } if os.getenv("BROWSERBASE_PROJECT_ID") else None,
    }
}

# LLM配置
LLM_CONFIG = {
    "deepseek": {
        "model_name": "deepseek/deepseek-chat",
        "model_client_options": {"apiKey": os.getenv("DEEPSEEK_API_KEY")},
    },
    "gemini": {
        "model_name": "gemini-2.5-flash-preview-04-17", 
        "model_client_options": {"apiKey": os.getenv("GOOGLE_API_KEY")},
    },
    "claude": {
        "model_name": "claude-3-7-sonnet-latest",
        "model_client_options": {
            "apiKey": os.getenv("AIHUBMIX_API_KEY"),
            "base_url": "https://aihubmix.com",
        }
    },
    "openai": {
        "model_name": "gpt-4o",
        "model_client_options": {
            "apiKey": os.getenv("AIHUBMIX_API_KEY"),
            "base_url": "https://aihubmix.com/v1",
        }
    }
}


def make_config(llm_name="deepseek", browser_type="local", **overrides):
    """
    创建配置对象
    
    Args:
        llm_name: LLM名称 ("deepseek", "gemini", "claude", "openai")
        browser_type: 浏览器类型 ("local", "local_headless", "browserbase")
        **overrides: 其他要覆盖的参数
    
    Returns:
        StagehandConfig: 配置对象
    """
    config = {}
    config.update(BASE_CONFIG)
    config.update(LLM_CONFIG.get(llm_name, LLM_CONFIG["deepseek"]))
    config.update(BROWSER_CONFIG.get(browser_type, BROWSER_CONFIG["local"]))
    config.update(overrides)
    
    return StagehandConfig(**config)


# 预定义的常用配置实例
local_deepseek = make_config("deepseek", "local")
local_gemini = make_config("gemini", "local") 
local_claude = make_config("claude", "local")
local_openai = make_config("openai", "local")

headless_deepseek = make_config("deepseek", "local_headless")
headless_gemini = make_config("gemini", "local_headless")

browserbase_claude = make_config("claude", "browserbase")
browserbase_gemini = make_config("gemini", "browserbase")

# 默认配置 - 自动选择环境
auto_env = "browserbase" if (
    os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")
) else "local"
default_config = make_config("deepseek", auto_env)


if __name__ == "__main__":
    # 测试配置
    print("=== 配置测试 ===")
    print(f"默认配置: {default_config.model_name} ({default_config.env})")
    print(f"本地DeepSeek: {local_deepseek.model_name} ({local_deepseek.env})")
    print(f"本地Gemini: {local_gemini.model_name} ({local_gemini.env})")
    print(f"无头模式: {headless_deepseek.local_browser_launch_options['headless']}")
    
    # 自定义配置示例
    custom = make_config("openai", "local", verbose=1, dom_settle_timeout_ms=5000)
    print(f"自定义配置: {custom.model_name}, verbose={custom.verbose}")
    
    print("✅ 配置文件工作正常！") 