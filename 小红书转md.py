import os
import uuid
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# 获取当前文件的路径和目录
current_file = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file)
os.chdir(current_directory)

# 确保img目录存在
if not os.path.exists('img'):
    os.makedirs('img')

# 浏览器配置
chrome_driver_path = r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data'
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={chrome_driver_path}")
chrome_options.add_argument("--profile-directory=Default")

# 创建Chrome浏览器实例
service = Service(r"D:\my\xhs-export\chromedriver.exe")
browser = webdriver.Chrome(service=service, options=chrome_options)

def getAllArticle():
    browser.get('https://www.xiaohongshu.com/user/profile/563eaf6d9eb578045ba942b7')
    links_set = set()
    
    try:
        # 等待用户Feed加载
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.ID, "userPostedFeeds"))
        )
        
        # 滚动加载更多内容
        for i in range(40):
            # 等待链接加载
            wait = WebDriverWait(browser, 10)
            # 使用精确的选择器匹配文章链接
            links = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a.cover.ld.mask[href*='/user/profile/'][target='_self']")
            ))
            
            # 收集链接
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and '/user/profile/' in href:
                        links_set.add(href)
                except Exception as e:
                    print(f"处理链接时出错: {str(e)}")
                    continue
            
            # 滚动到底部
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            browser.implicitly_wait(2)
            
            # 检查是否到达底部
            if browser.execute_script("return window.pageYOffset + window.innerHeight >= document.body.scrollHeight;"):
                break
                
    except Exception as e:
        print(f"获取文章列表时出错: {str(e)}")
    
    # 输出所有获取到的链接
    print("\n获取到的所有文章链接:")
    for link in sorted(links_set):
        print(f"- {link}")
    
    print(f"\n共获取到 {len(links_set)} 篇文章")
    return links_set

def downForArticle(url):
    try:
        browser.get(url)
        
        # 等待内容加载
        wait = WebDriverWait(browser, 20)
        note_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.note-content')))
        
        # 获取标题和描述
        title = note_content.find_element(By.CSS_SELECTOR, ".title").text
        desc = note_content.find_element(By.CSS_SELECTOR, ".desc").text
        
        # 获取图片
        images = browser.find_elements(By.CSS_SELECTOR, "img[src*='sns-webpic-qc.xhscdn.com']")
        image_markdown = ""
        
        # 下载并保存图片
        for img in images:
            try:
                img_url = img.get_attribute("src")
                if not img_url:
                    continue
                    
                response = requests.get(img_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    image = image.convert("RGB")
                    file_name = f'img/{uuid.uuid4()}.jpg'
                    image.save(file_name)
                    image_markdown += f"![]({file_name})\n"
                    print(f"图片保存成功: {file_name}")
            except Exception as e:
                print(f"处理图片时出错: {str(e)}")
                continue
        
        # 生成markdown内容
        markdown = f"# {title}\n\n{image_markdown}\n{desc}"
        
        # 保存markdown文件
        safe_title = "".join(x for x in title if x.isalnum() or x in (' ', '-', '_'))[:50]
        with open(f"{safe_title}.md", "w", encoding="utf-8") as f:
            f.write(markdown)
            
        print(f"文章《{title}》保存成功")
        
    except Exception as e:
        print(f"处理文章时出错: {str(e)}")

def main():
    try:
        articles = getAllArticle()
        print("开始下载文章...")
        for url in articles:
            try:
                downForArticle(url)
            except Exception as e:
                print(f"处理文章 {url} 时出错: {str(e)}")
                continue
    finally:
        browser.quit()

if __name__ == "__main__":
    main()
