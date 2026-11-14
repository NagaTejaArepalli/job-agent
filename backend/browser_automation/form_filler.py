import os
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from playwright.async_api import async_playwright
from config.settings import settings

class BrowserFormFiller:
    """
    Automates filling job application forms on career portals (Greenhouse, Lever, etc.)
    CRITICAL SAFETY GUARANTEE:
    This agent fills fields, attaches the tailored resume, and STOPS.
    It NEVER clicks the final "Submit Application" button.
    The browser can remain open or provide a review screenshot for the human to complete.
    """
    
    @classmethod
    async def fill_application(
        cls,
        application_url: str,
        form_data: Dict[str, Any],
        resume_file_path: Optional[str] = None,
        headed: bool = False
    ) -> Dict[str, Any]:
        """
        Navigates to the application URL, maps inputs, fills fields, attaches resume,
        and pauses before submission.
        """
        filled_fields = []
        errors = []
        screenshot_path = None
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=not headed,
                slow_mo=50 if headed else 0
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                await page.goto(application_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000) # Give dynamic widgets time to render
                
                # Helper to try filling common input selectors
                async def try_fill(selectors, value, field_name):
                    if not value:
                        return False
                    for sel in selectors:
                        try:
                            loc = page.locator(sel).first
                            if await loc.count() > 0 and await loc.is_visible():
                                await loc.fill(str(value))
                                filled_fields.append({"field": field_name, "selector": sel, "value": str(value)})
                                return True
                        except Exception:
                            continue
                    return False

                # 1. First Name
                await try_fill(
                    ['input[name*="first_name" i]', 'input[id*="first_name" i]', 'input[autocomplete="given-name"]', '#first_name'],
                    form_data.get("first_name", {}).get("value") or form_data.get("first_name"),
                    "first_name"
                )

                # 2. Last Name
                await try_fill(
                    ['input[name*="last_name" i]', 'input[id*="last_name" i]', 'input[autocomplete="family-name"]', '#last_name'],
                    form_data.get("last_name", {}).get("value") or form_data.get("last_name"),
                    "last_name"
                )

                # Full Name fallback
                if "first_name" not in [f["field"] for f in filled_fields]:
                    full_name = f"{form_data.get('first_name', {}).get('value', '')} {form_data.get('last_name', {}).get('value', '')}".strip()
                    await try_fill(
                        ['input[name*="name" i]', 'input[id*="name" i]', 'input[autocomplete="name"]'],
                        full_name,
                        "full_name"
                    )

                # 3. Email
                await try_fill(
                    ['input[name*="email" i]', 'input[type="email"]', 'input[id*="email" i]'],
                    form_data.get("email", {}).get("value") or form_data.get("email"),
                    "email"
                )

                # 4. Phone
                await try_fill(
                    ['input[name*="phone" i]', 'input[type="tel"]', 'input[id*="phone" i]'],
                    form_data.get("phone", {}).get("value") or form_data.get("phone"),
                    "phone"
                )

                # 5. LinkedIn
                await try_fill(
                    ['input[name*="linkedin" i]', 'input[id*="linkedin" i]', 'input[placeholder*="linkedin" i]'],
                    form_data.get("linkedin", {}).get("value") or form_data.get("linkedin"),
                    "linkedin"
                )

                # 6. GitHub
                await try_fill(
                    ['input[name*="github" i]', 'input[id*="github" i]', 'input[placeholder*="github" i]'],
                    form_data.get("github", {}).get("value") or form_data.get("github"),
                    "github"
                )

                # 7. Portfolio / Website
                await try_fill(
                    ['input[name*="portfolio" i]', 'input[name*="website" i]', 'input[id*="portfolio" i]', 'input[placeholder*="portfolio" i]'],
                    form_data.get("portfolio", {}).get("value") or form_data.get("portfolio") or "https://nagatejaarepalli.github.io/PortfolioPage/",
                    "portfolio"
                )

                # 8. Current Company
                await try_fill(
                    ['input[name*="current_company" i]', 'input[name*="company" i]', 'input[id*="employer" i]'],
                    form_data.get("current_company", {}).get("value") or "Infor",
                    "current_company"
                )

                # 9. Current Title
                await try_fill(
                    ['input[name*="current_title" i]', 'input[name*="title" i]', 'input[id*="title" i]'],
                    form_data.get("current_title", {}).get("value") or "QA Engineer (SDET)",
                    "current_title"
                )

                # 10. Notice Period
                await try_fill(
                    ['input[name*="notice" i]', 'input[id*="notice" i]'],
                    "60 days",
                    "notice_period"
                )

                # 11. Current CTC
                await try_fill(
                    ['input[name*="current_ctc" i]', 'input[id*="current_ctc" i]', 'input[placeholder*="ctc" i]'],
                    "9.75 LPA",
                    "current_ctc"
                )

                # 12. Expected CTC
                await try_fill(
                    ['input[name*="expected_ctc" i]', 'input[id*="expected_ctc" i]'],
                    "14-15 LPA",
                    "expected_ctc"
                )

                # 13. Resume Attachment
                if resume_file_path and os.path.exists(resume_file_path):
                    file_input = page.locator('input[type="file"][name*="resume" i], input[type="file"]').first
                    if await file_input.count() > 0:
                        try:
                            await file_input.set_input_files(resume_file_path)
                            filled_fields.append({"field": "resume_file", "selector": 'input[type="file"]', "file": resume_file_path})
                        except Exception as e:
                            errors.append(f"Failed to attach resume file: {str(e)[:80]}")

                # 8. Capture review screenshot
                screenshots_dir = settings.DATA_DIR / "screenshots"
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                shot_file = screenshots_dir / f"review_{os.urandom(4).hex()}.png"
                await page.screenshot(path=str(shot_file), full_page=True)
                screenshot_path = str(shot_file)

                # If headed, give human user time to see it before closing
                if headed:
                    # Keep browser open for user review
                    await page.wait_for_timeout(10000)
                    
            except Exception as e:
                errors.append(f"Automation execution error: {str(e)[:120]}")
            finally:
                await browser.close()
                
        return {
            "status": "ready_for_review",
            "filled_fields": filled_fields,
            "errors": errors,
            "screenshot_path": screenshot_path,
            "human_action_required": "Please open application URL, review prefilled entries, verify legal checkboxes, and click Submit.",
            "url": application_url
        }
