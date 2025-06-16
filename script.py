import pyautogui
import pyperclip
import time
class script():
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.duration = 0.2
    def move_and_click(self):
        self.reset()
        pyautogui.click()
    def up_sliding(self):
        self.reset()
        pyautogui.scroll(-1000)
    def down_sliding(self):
        self.reset()
        pyautogui.scroll(1000)
    def zoom_in(self):
        self.reset()
        pyautogui.hotkey('ctrl','+')
    def zoom_out(self):
        self.reset()
        pyautogui.hotkey('ctrl','-')
    def Left_sliding(self):
        self.reset()
        pyautogui.press('left')
    def Right_sliding(self):       
        self.reset()
        pyautogui.press('right')
    def reset(self):
        pyautogui.moveTo(self.screen_width/2, self.screen_height/2, duration=self.duration)
   