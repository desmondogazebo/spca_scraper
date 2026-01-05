import time
import threading
import hashlib

from modules.automation.ocr import grab_region, run_ocr_with_fallback


class OCRWatcher:
    def __init__(
        self,
        region,
        interval,
        min_conf,
        trigger_fn,
        cooldown=10,
    ):
        self.region = region
        self.interval = interval
        self.min_conf = min_conf
        self.trigger_fn = trigger_fn
        self.cooldown = cooldown

        self._last_hash = None
        self._last_trigger_time = 0
        self._stop_event = threading.Event()

    def _hash(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def start(self):
        self._stop_event.clear()

        while not self._stop_event.is_set():
            image = grab_region(*self.region)
            text, conf = run_ocr_with_fallback(image)

            now = time.time()

            if text and conf >= self.min_conf:
                h = self._hash(text)

                if (
                    h != self._last_hash
                    and now - self._last_trigger_time >= self.cooldown
                ):
                    self._last_hash = h
                    self._last_trigger_time = now
                    self.trigger_fn(text, conf)

            self._stop_event.wait(self.interval)

    def stop(self):
        self._stop_event.set()
