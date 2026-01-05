import subprocess
import time

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

def open_brave(url, wait=5):
    subprocess.Popen(
        [BRAVE_PATH, "--new-window", url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(wait)  # let page load
