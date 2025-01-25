import os
import uuid
import requests
import psutil
import time
import datetime
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

def check_and_wait_chrome():
    while any(proc.info['name'].lower() in ['chrome.exe', 'google chrome'] 
             for proc in psutil.process_iter(['name'])):
        print("\n请先关闭所有的Chrome浏览器窗口！")
        time.sleep(2)

def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data")
    chrome_options.add_argument("--profile-directory=Default")
    service = Service("D:\\my\\xhs-export\\chromedriver.exe")
    return webdriver.Chrome(service=service, options=chrome_options)

def get_articles(browser):
    print("\n请在打开的浏览器中登录小红书账号（已登录可直接按回车）...")
    input()
    
    browser.get('https://www.xiaohongshu.com/user/profile/563eaf6d9eb578045ba942b7')
    links = set()
    
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, "userPostedFeeds")))
    
    for _ in range(40):
        for link in WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a.cover.ld.mask[href*='/user/profile/'][target='_self']")
            )
        ):
            if href := link.get_attribute("href"):
                links.add(href)
        
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        if browser.execute_script("return window.pageYOffset + window.innerHeight >= document.body.scrollHeight;"):
            break
    
    print(f"\n共获取到 {len(links)} 篇文章")
    return links

def save_article(browser, url, export_dir):
    browser.get(url)
    note_content = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.note-content')))
    
    title = note_content.find_element(By.CSS_SELECTOR, ".title").text
    desc = note_content.find_element(By.CSS_SELECTOR, ".desc").text
    images = browser.find_elements(By.CSS_SELECTOR, "img[src*='sns-webpic-qc.xhscdn.com']")
    
    image_markdown = ""
    for img in images:
        if img_url := img.get_attribute("src"):
            try:
                response = requests.get(img_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    file_name = f"{uuid.uuid4()}.jpg"
                    image.save(os.path.join(export_dir, "img", file_name))
                    image_markdown += f"![](img/{file_name})\n"
            except Exception as e:
                print(f"图片下载失败: {str(e)}")
    
    safe_title = "".join(x for x in title if x.isalnum() or x in (' ', '-', '_'))[:50]
    with open(os.path.join(export_dir, f"{safe_title}.md"), "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{image_markdown}\n{desc}")
    
    print(f"已保存: {title}")

def main():
    try:
        print("\n=== 小红书文章导出工具 ===")
        check_and_wait_chrome()
        
        export_dir = f"export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(os.path.join(export_dir, "img"))
        print(f"\n文章将保存在 {export_dir} 目录")
        
        browser = setup_browser()
        try:
            for url in get_articles(browser):
                try:
                    save_article(browser, url, export_dir)
                except Exception as e:
                    print(f"文章处理失败: {str(e)}")
        finally:
            browser.quit()
            
        print(f"\n完成！所有文章已保存到 {export_dir}")
    except Exception as e:
        print(f"\n程序出错: {str(e)}")
    finally:
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()
