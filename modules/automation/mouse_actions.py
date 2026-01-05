import pyautogui
import time

pyautogui.FAILSAFE = True

def double_click(x, y, delay=0.1):
    pyautogui.moveTo(x, y)
    pyautogui.doubleClick()
    time.sleep(delay)
