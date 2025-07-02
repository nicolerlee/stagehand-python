import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径，以便导入stagehand
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from stagehand import Stagehand, StagehandConfig

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

async def open_h5_novel_page():
    """打开H5小说页面并自动化操作"""
    # 创建配置
    config = StagehandConfig(
        env="LOCAL",  # 或者 "BROWSERBASE"
        # api_key=os.getenv("BROWSERBASE_API_KEY"),
        # project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="google/gemini-2.5-flash-preview-05-20",
        model_client_options={"apiKey": os.getenv("GOOGLE_API_KEY")},
        verbose=1,
        headless=False,  # 设置为 False 以便观察浏览器操作
        dom_settle_timeout_ms=3000,
    )
    
    stagehand = Stagehand(config)

    try:
        await stagehand.init()
        print("Stagehand initialized successfully")

        page = stagehand.page
        target_url = (
            "https://novetest.fun.tv/tt/xingchen/pages/readerPage/readerPage?"
            "cartoon_id=649371&num=10&coopCode=ad&popularizeId=funtv&"
            "microapp_id=aw7xho2to223zyp5&source=fix&clickid=testclickidwx01&"
            "promotionid=testpromotionidwx01&promotion_ad_id=2204300841111&"
            "promotion_code=jlgg&si=13022864&&promotion_pt=88752"
        )

        # 检查并创建log文件夹
        log_dir = Path(__file__).parent / "log"
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            print("Created log directory")

        # 打开页面
        print("Opening webpage:", target_url)
        await page.goto(target_url, timeout=30000, wait_until="networkidle")
        
        # 等待页面加载
        await asyncio.sleep(2)
        print("Page ready for interaction")

        # 截图并识别套餐
        await page.screenshot(path=str(log_dir / "debug_popup.png"))

        observations = await page.observe(
            "Find all elements whose data-e2e attribute starts with 'payment-pop-item'"
        )

        print(f"Found {len(observations)} payment items")

        # 依次点击每个套餐
        for idx, observation in enumerate(observations):
            print(f"Clicking package {idx + 1}/{len(observations)}")

            await page.act(observation)
            await asyncio.sleep(1)
            await page.screenshot(path=str(log_dir / f"package_{idx + 1}.png"))

        print("All packages clicked successfully!")
        print(f"Screenshots saved to: {log_dir}")
        
    except Exception as error:
        print(f"Error: {error}")
        raise
    finally:
        await stagehand.close()


async def main():
    """主函数"""
    try:
        await open_h5_novel_page()
    except Exception as e:
        print(f"Script failed: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 