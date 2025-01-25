import os
import uuid
import eel
import json
import psutil
import requests
import datetime
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from tkinter import filedialog, Tk

# 初始化eel，指定web文件目录
eel.init('web')

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROME_DATA_DIR = os.path.join(SCRIPT_DIR, "chrome_data")
CHROME_DRIVER_PATH = os.path.join(SCRIPT_DIR, "chromedriver.exe")

# 确保Chrome数据目录存在
if not os.path.exists(CHROME_DATA_DIR):
    os.makedirs(CHROME_DATA_DIR)

# 全局导出器实例
exporter = None

@eel.expose
def select_directory():
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes('-topmost', True)  # 保持在最前
    directory = filedialog.askdirectory()
    root.destroy()
    return directory if directory else None

@eel.expose
def start_export(base_dir):
    global exporter
    if exporter:
        exporter.start_export(base_dir)

@eel.expose
def confirm_login():
    global exporter
    if exporter:
        exporter.confirm_login()

class XHSExporter:
    def __init__(self):
        self.browser = None
        self.should_stop = False
        self.export_dir = None
        self.login_confirmed = False
    
    def confirm_login(self):
        self.login_confirmed = True
    
    def start_export(self, base_dir):
        try:
            # 创建导出目录
            self.export_dir = os.path.join(base_dir, f"export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(os.path.join(self.export_dir, "img"), exist_ok=True)
            
            # 启动浏览器
            eel.updateStatus("正在启动浏览器...")()
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={CHROME_DATA_DIR}")
            chrome_options.add_argument("--profile-directory=Default")
            # 添加其他必要的参数
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-features=TranslateUI')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-component-extensions-with-background-pages')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-client-side-phishing-detection')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-hang-monitor')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--disable-prompt-on-repost')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--remote-debugging-port=0')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--password-store=basic')
            chrome_options.add_argument('--use-mock-keychain')
            # 设置窗口大小和位置 (x,y,width,height)
            chrome_options.add_argument('--window-position=900,0')
            chrome_options.add_argument('--window-size=800,900')
            
            service = Service(CHROME_DRIVER_PATH)
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            
            # 打开小红书
            eel.updateStatus("请在浏览器中登录小红书...")()
            self.browser.get('https://www.xiaohongshu.com/user/profile/563eaf6d9eb578045ba942b7')
            
            # 等待用户确认登录
            eel.showLoginModal()()
            while not self.login_confirmed and not self.should_stop:
                eel.sleep(0.1)
            
            if self.should_stop:
                return
            
            # 等待页面加载
            try:
                WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.ID, "userPostedFeeds")))
            except:
                eel.showError("等待页面加载超时，请检查网络连接")()
                return
            
            # 获取文章列表
            links = set()
            total_scrolls = 40
            eel.updateStatus("正在获取文章列表...")()
            
            for i in range(total_scrolls):
                if self.should_stop:
                    return
                
                eel.updateProgress(i + 1, total_scrolls)()
                
                for link in WebDriverWait(self.browser, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "a.cover.ld.mask[href*='/user/profile/'][target='_self']")
                    )
                ):
                    if href := link.get_attribute("href"):
                        links.add(href)
                
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                eel.sleep(1.0)
                
                if self.browser.execute_script("return window.pageYOffset + window.innerHeight >= document.body.scrollHeight;"):
                    break
            
            if not links:
                eel.showError("未找到任何文章")()
                return
            
            # 下载文章
            eel.updateStatus("开始下载文章...")()
            success = 0
            total = len(links)
            
            for i, url in enumerate(links, 1):
                if self.should_stop:
                    return
                
                eel.updateArticleProgress(i, total)()
                
                try:
                    self.browser.get(url)
                    note_content = WebDriverWait(self.browser, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.note-content'))
                    )
                    
                    title = note_content.find_element(By.CSS_SELECTOR, ".title").text
                    desc = note_content.find_element(By.CSS_SELECTOR, ".desc").text
                    images = self.browser.find_elements(By.CSS_SELECTOR, "img[src*='sns-webpic-qc.xhscdn.com']")
                    
                    eel.updateStatus(f"正在下载: {title[:30]}{'...' if len(title) > 30 else ''}")()
                    
                    image_markdown = ""
                    for j, img in enumerate(images, 1):
                        if self.should_stop:
                            return
                        
                        if img_url := img.get_attribute("src"):
                            try:
                                response = requests.get(img_url)
                                if response.status_code == 200:
                                    image = Image.open(BytesIO(response.content))
                                    file_name = f"{uuid.uuid4()}.jpg"
                                    image.save(os.path.join(self.export_dir, "img", file_name))
                                    image_markdown += f"![](img/{file_name})\n"
                                    eel.updateStatus(f"正在下载: {title[:20]}... (图片 {j}/{len(images)})")()
                            except Exception as e:
                                eel.updateStatus(f"图片下载失败: {str(e)}")()
                    
                    safe_title = "".join(x for x in title if x.isalnum() or x in (' ', '-', '_'))[:50]
                    with open(os.path.join(self.export_dir, f"{safe_title}.md"), "w", encoding="utf-8") as f:
                        f.write(f"# {title}\n\n{image_markdown}\n{desc}")
                    
                    success += 1
                except Exception as e:
                    eel.updateStatus(f"文章下载失败: {str(e)}")()
            
            eel.showSuccess(f"完成！成功导出 {success}/{total} 篇文章\n保存在: {self.export_dir}")()
            
        except Exception as e:
            eel.showError(f"程序出错: {str(e)}")()
        finally:
            if self.browser:
                self.browser.quit()
    
    def stop_export(self):
        self.should_stop = True
        if self.browser:
            self.browser.quit()

@eel.expose
def stop_export():
    global exporter
    if exporter:
        exporter.stop_export()

def main():
    global exporter
    exporter = XHSExporter()
    # 设置窗口大小和位置 (width, height, x, y)
    eel.start('index.html', size=(800, 600), position=(50, 50))

if __name__ == "__main__":
    main()
