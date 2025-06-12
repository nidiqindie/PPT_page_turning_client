import pyautogui
import pyperclip
import time
class script():
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.duration = 0.2
    def move_and_click(self):
        pyautogui.move(self.screen_width/2, self.screen_height/2, duration=self.duration)
        pyautogui.click()
    def upward_sliding(self):
        pyautogui.scroll(-1000)
    def down_sliding(self):
        pyautogui.scroll(1000)
    # def moveTo_click_inputCHinese(self,x, y,duration,text):
    #     self.moveTo_click(x, y, duration)
    #     pyperclip.copy(text)
    #     pyautogui.hotkey('ctrl', 'v')