import subprocess
import time
import sys
import os
import httpx
from playwright.sync_api import sync_playwright

def is_server_running(url="http://127.0.0.1:8000/health"):
    try:
        r = httpx.get(url, timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False

def main():
    print("Checking backend server status...")
    if not is_server_running():
        print("Starting FastAPI backend on http://127.0.0.1:8000...")
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        for i in range(15):
            time.sleep(1)
            if is_server_running():
                print("Server is up and healthy!")
                break
            print(f"Waiting for server... ({i+1}/15)")
    else:
        print("Backend server is already running on http://127.0.0.1:8000!")

    print("\nLaunching Playwright browser to open AI Job Search Agent...")
    with sync_playwright() as p:
        # Launch headed browser so user sees the application window directly!
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        
        print("Navigating to http://127.0.0.1:8000...")
        page.goto("http://127.0.0.1:8000", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        
        # Take a screenshot to verify and save
        screenshot_path = "data/dashboard_preview.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        print("\nApp is open in your browser window!")
        print("You can explore the Dashboard, Job Discovery, Job Matching, Resume Manager, and Q&A Knowledge Base.")
        print("Keeping browser open for your session (close the browser window when done)...")
        
        # Wait until user closes browser or page
        try:
            page.wait_for_close(timeout=0)
        except Exception:
            pass

if __name__ == "__main__":
    main()
