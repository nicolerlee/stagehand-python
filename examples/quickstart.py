import asyncio
import os
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# 添加项目根目录到Python路径，以便导入stagehand和配置
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from stagehand import Stagehand
from stagehand_config import *

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Define Pydantic models for structured data extraction
class Company(BaseModel):
    name: str = Field(..., description="Company name")
    description: str = Field(..., description="Brief company description")

class Companies(BaseModel):
    companies: list[Company] = Field(..., description="List of companies")
    
async def main():
    # Create configuration
    # config = StagehandConfig(
    #   local_gemini  # 本地Gemini
    #   #  local_openai  # 本地OpenAI
    #   #  local_claude  # 本地Claude
    # )

    config = StagehandConfig(
        model_name="google/gemini-2.5-flash-preview-05-20",
        model_client_options={"apiKey": os.getenv("GOOGLE_API_KEY")},
    )
    stagehand = Stagehand(config)
    
    try:
        print("\nInitializing 🤘 Stagehand...")
        # Initialize Stagehand
        await stagehand.init()

        if stagehand.env == "BROWSERBASE":    
            print(f"🌐 View your live browser: https://www.browserbase.com/sessions/{stagehand.session_id}")

        page = stagehand.page

        await page.goto("https://www.aigrant.com")
        
        # Extract companies using structured schema        
        companies_data = await page.extract(
          "Extract names and descriptions of 5 companies in batch 3",
          schema=Companies
        )
        
        # Display results
        print("\nExtracted Companies:")
        for idx, company in enumerate(companies_data.companies, 1):
            print(f"{idx}. {company.name}: {company.description}")

        observe = await page.observe("the link to the company Browserbase")
        print("\nObserve result:", observe)
        act = await page.act("click the link to the company Browserbase")
        print("\nAct result:", act)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        # Close the client
        print("\nClosing 🤘 Stagehand...")
        await stagehand.close()

if __name__ == "__main__":
    asyncio.run(main())