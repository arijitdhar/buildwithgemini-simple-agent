import asyncio
import os
import shutil
import glob
from playwright.async_api import async_playwright

async def record():
    os.makedirs("demo_output", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir="demo_output",
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print("Navigating to http://localhost:8080...")
        await page.goto("http://localhost:8080")
        await page.wait_for_timeout(2000)
        
        # --- Prompt 1: What app does best (Explore catalog) ---
        print("Sending Prompt 1...")
        await page.fill("#input", "What destinations do you have in the catalog?")
        await page.wait_for_timeout(1000)
        await page.click("button:has-text('Send')")
        
        # Wait for reply bubble to finish updating
        await page.wait_for_timeout(8000)
        
        # --- Prompt 2: Richer prompt (Tool call, database lookup, generated AI postcard image) ---
        print("Sending Prompt 2...")
        await page.fill("#input", "Use generate_destination_postcard to create a scenic postcard for Paris")
        await page.wait_for_timeout(1000)
        await page.click("button:has-text('Send')")
        
        # Wait for image generation tool & card rendering
        await page.wait_for_timeout(14000)
        
        await context.close()
        await browser.close()
        print("Recording finished.")

if __name__ == "__main__":
    asyncio.run(record())
