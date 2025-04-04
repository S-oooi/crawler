from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os
COOKIES_PATH = r'E:\anaconda\pachong\cookies.pkl'

wd = webdriver.Chrome()
wd.implicitly_wait(10)

def save_cookies():

    with open(COOKIES_PATH, 'wb') as f:
        pickle.dump(wd.get_cookies(), f)
def load_cookies():
  
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, 'rb') as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                wd.add_cookie(cookie)
        return True
    return False
def login_xiaohongshu():
    """处理小红书扫码登录"""
    wd.get('https://www.xiaohongshu.com')
    
    # 如果已有 Cookies，尝试加载
    if load_cookies():
        wd.refresh()
        time.sleep(3)
        # 检查是否已登录（检查页面是否有用户我的类）
        try:
            WebDriverWait(wd, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'channel'))  # 类名
            )
            print("已通过 Cookies 登录")
            return
        except:
            print("Cookies 无效，需重新扫码登录")
    
    # 等待二维码出现
    try:
        qr_code = WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'qrcode-img'))  # 类名
        )
        print("请使用小红书 App 扫描二维码登录...")
        # 等待手动扫码，假设 60 秒足够
        time.sleep(60)
        
        # 检查是否登录成功
        WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'channel'))  #类名
        )
        print("登录成功")
        # 保存 Cookies
        save_cookies()
    except Exception as e:
        print(f"登录出错: {e}")
        raise
def main():
    try:
        login_xiaohongshu()
        
    finally:
        wd.quit()
if __name__ == "__main__":
    main()