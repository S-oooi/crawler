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

def get_notes_content(max_notes=3):
    """提取博主主页的笔记标题和正文（适配动态弹窗并关闭）"""
    try:
        # 打印当前窗口句柄，确认上下文
        print(f"当前窗口句柄: {wd.current_window_handle}")
        print(f"窗口总数: {len(wd.window_handles)}")

        # 等待笔记列表加载，使用正确的 section 标签
        print("尝试定位笔记列表...")
        notes = WebDriverWait(wd, 15).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//section[contains(@class, 'note-item')]")
            )
        )
        print(f"找到 {len(notes)} 篇笔记，将提取前 {max_notes} 篇")

        # 存储所有笔记内容
        notes_content = []
        
        for i, note in enumerate(notes[:max_notes], 1):
            try:
                # 找到可点击的封面链接
                cover_link = note.find_element(By.XPATH, ".//a[contains(@class, 'cover')]")
                cover_link.click()
                print(f"正在打开第 {i} 篇笔记")

                # 等待弹窗中的标题加载
                note_title = WebDriverWait(wd, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@id='detail-title' and contains(@class, 'title')]")
                    )
                )
                
                # 等待弹窗中的正文加载
                note_body = WebDriverWait(wd, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@id='detail-desc' and contains(@class, 'desc')]//span[contains(@class, 'note-text')]")
                    )
                )

                title_text = note_title.text.strip()
                body_text = note_body.text.strip()
                
                notes_content.append({
                    'note_number': i,
                    'title': title_text,
                    'body': body_text
                })
                print(f"第 {i} 篇笔记标题: {title_text}")
                print(f"第 {i} 篇笔记正文预览: {body_text[:100]}...")

                # 关闭弹窗
                try:
                    close_button = WebDriverWait(wd, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//div[contains(@class, 'close') and contains(@class, 'close-mask-dark')]")
                        )
                    )
                    close_button.click()
                    print(f"已关闭第 {i} 篇笔记弹窗")
                except Exception as e:
                    print(f"关闭弹窗失败: {e}，尝试继续下一条")

                # 等待页面恢复
                time.sleep(2)

            except Exception as e:
                print(f"提取第 {i} 篇笔记出错: {e}")
                continue

        return notes_content

    except Exception as e:
        print(f"获取笔记列表出错: {e}")
        print("当前页面部分源代码:")
        print(wd.page_source[:500])  # 打印前500字符
        return []
def main():
    try:
        login_xiaohongshu()
        blogger_name = "吃西瓜的夏天"
        search_and_get_profile(blogger_name)
        
        # 获取笔记内容
        notes = get_notes_content(max_notes=3)
        
        # 分类打印笔记内容
        print("\n=== 提取的笔记内容 ===")
        for note in notes:
            print(f"\n笔记 {note['note_number']}:")
            print(f"标题: {note['title']}")
            print(f"正文: {note['body']}")
            
    finally:
        wd.quit()

if __name__ == "__main__":
    main()