from playwright.sync_api import sync_playwright, Error as PlaywrightError
import threading
import time


class DOMAutomationRunner:
    def __init__(self):
        self._thread = None
        self._stop_flag = False

        self._playwright = None
        self._browser = None
        self._page = None

    # ----------------------------
    # Internal worker
    # ----------------------------

    def _run(self):
        self._playwright = sync_playwright().start()
        USER_AGENT = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        self._browser = self._playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = self._browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="Asia/Singapore",
        )

        self._page = context.new_page()
        self._page.goto("https://www.tiktok.com/@mobot.sg/live")

        print("[DOM] Browser opened")

        try:
            while not self._stop_flag:
                try:
                    # -------- STOP CONDITION --------
                    stop_locator = self._page.locator(
                        "div.H2-Medium.text-center"
                    ).filter(has_text="STOP")

                    if stop_locator.count() > 0:
                        print("[DOM] STOP detected — shutting down automation")
                        break

                    # -------- PRIMARY TARGET --------
                    target = self._page.locator(
                        "p.truncate.P3-Semibold.text-UIText1"
                    ).filter(has_text="MobotSG")

                    if target.count() > 0:
                        print("[DOM] Target detected")
                        target.first.click()
                        print("[DOM] Clicked target")

                        time.sleep(10)

                    time.sleep(1)

                except PlaywrightError:
                    # Browser / page was closed externally
                    print("[DOM] Browser or page closed externally — stopping runner")
                    break

        finally:
            self._cleanup()

    # ----------------------------
    # Lifecycle
    # ----------------------------

    def start(self):
        if self._thread:
            return False

        self._stop_flag = False
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self._thread.start()

        return True

    def stop(self):
        if not self._thread:
            return False

        print("[DOM] Stop requested manually")
        self._stop_flag = True
        self._thread.join(timeout=5)

        self._thread = None
        return True

    # ----------------------------
    # Cleanup
    # ----------------------------

    def _cleanup(self):
        print("[DOM] Cleaning up browser")

        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass

        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass

        self._browser = None
        self._playwright = None
        self._page = None
