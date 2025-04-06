from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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
def search_and_get_profile(blogger_name):
    """搜索博主并提取主页简介"""
    try:
        # 找到搜索框并输入博主名称
        search_box = WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'search-input'))
        )
        search_box.clear()
        search_box.send_keys(blogger_name)
        search_box.send_keys(Keys.RETURN)  # 使用回车键触发搜索
        print(f"已搜索博主: {blogger_name}")
       
        # 记录当前窗口句柄
        original_window = wd.current_window_handle

        # 等待搜索结果加载，找到博主头像并点击
        avatar = WebDriverWait(wd, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'user-item')]//img"))  # 搜索结果中的头像
        )
        avatar.click()
        print("已进入博主主页")

        # 检查是否打开了新窗口，如果有则切换
        try:
            WebDriverWait(wd, 10).until(EC.number_of_windows_to_be(2))
            for window_handle in wd.window_handles:
                if window_handle != original_window:
                    wd.switch_to.window(window_handle)
                    print(f"已切换到新窗口: {window_handle}")
                    break
        except:
            print("未检测到新窗口，仍在当前窗口操作")

        # 等待主页加载，提取简介
        profile_intro = WebDriverWait(wd, 10).until(
           EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'user-desc')]"))
                )
        print(profile_intro.text)
        intro_text = profile_intro.text
        print(f"博主简介: {intro_text}")
        return intro_text

    except Exception as e:
        print(f"搜索或提取简介出错: {e}")
        return None

def main():
    try:
        login_xiaohongshu()
        #搜索某个博主并提取简介
        blogger_name = "AI车库中的老李"  # 替换为你想搜索的博主名称
        search_and_get_profile(blogger_name)
    finally:
        wd.quit()

if __name__ == "__main__":
    main()