import threading

from modules.automation.browser import open_brave
from modules.automation.mouse_actions import double_click
from modules.automation.ocr_watcher import OCRWatcher


class OCRAutomationRunner:
    def __init__(self):
        self.watcher = None
        self.thread = None

    def start(self):
        if self.watcher:
            return False

        open_brave("https://www.tiktok.com/@mobot.sg")

        def on_ocr(text, conf):
            if "CONFIRM" in text.upper():
                double_click(1200, 720)

        self.watcher = OCRWatcher(
            region=(900, 600, 1400, 800),
            interval=3,
            min_conf=65,
            cooldown=15,
            trigger_fn=on_ocr,
        )

        self.thread = threading.Thread(
            target=self.watcher.start,
            daemon=True,
        )
        self.thread.start()

        return True

    def stop(self):
        if not self.watcher:
            return False

        self.watcher.stop()
        self.thread.join(timeout=2)

        self.watcher = None
        self.thread = None
        return True
