import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 获取当前文件的路径
current_file = os.path.abspath(__file__)

# 获取当前文件所在的目录
current_directory = os.path.dirname(current_file)

# 设置当前工作目录
os.chdir(current_directory)

# 打印当前工作目录
print("当前工作目录:", os.getcwd())

chrome_options = Options()
chrome_options.add_argument("--user-data-dir=D:\my")
browser = webdriver.Chrome(chrome_options)


def getAllArticle():

    # option.binary_location = r"C:\Program Files\Google\Chrome\Application/google.exe"  # binary_location属性指定Chrome启动文件
    # browser = webdriver.Chrome(option)
    browser.get(
        'https://www.xiaohongshu.com/user/profile/60460e150000000001001ed4')

    # 人工进行登录

# 定义一个集合用来存储链接
# 未登录，只能看到过去30篇笔记
    links_set = set()

    # 找到 id 为 "userPostedFeeds" 的元素
    user_posted_feeds = browser.find_element(By.ID, "userPostedFeeds")

 # 等待页面加载完成
    browser.implicitly_wait(100)

    # 滚动到页面底部，并获取链接
    for i in range(40):
        # 找到所有以 "/explore" 开头的链接
        wait = WebDriverWait(browser, 10)
        links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href^='/user/profile']")))

        # 将链接添加到集合中
        for link in links:
            try:
                links_set.add(link.get_attribute("href"))
            except:
                pass

        # 执行滚动操作
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # 等待页面加载完成
        browser.implicitly_wait(10)

        # 如果已经滚动到了页面底部，退出循环
        if browser.execute_script("return window.pageYOffset + window.innerHeight >= document.body.scrollHeight;"):
            break

        # 重新获取 id 为 "userPostedFeeds" 的元素
        user_posted_feeds = browser.find_element(By.ID, "userPostedFeeds")

    # https://www.xiaohongshu.com/explore/652b48b7000000001f03bed6?xsec_token=ABmeeILZLA2Kz4cDESXC3P9reVGrRWwE1cDWzrkuQmb-M=&xsec_source=pc_user
    # 输出去重后的链接
    for link in links_set:
        print(link)

    return links_set


def downForArticle(url):
    # 创建Chrome浏览器对象
    # 加载指定的页面
    # 打开页面
    browser.get(url)

    # 设置隐式等待时间为10秒(第一次时等待10s)
    browser.implicitly_wait(10)

    # 找到 class 为 "note-content" 的元素
    note_content = browser.find_elements(By.CSS_SELECTOR, '.note-content')[0]

    # 找到 class 为 "title" 和 "desc" 的子元素
    titles = note_content.find_elements(By.CSS_SELECTOR, ".title")
    descs = note_content.find_elements(By.CSS_SELECTOR, ".desc")

    import requests
    from PIL import Image
    from io import BytesIO

    # 找到 class 为 "note-content" 的元素
    # 使用 CSS 选择器查找所有包含 'xhscdn' 的 img 元素
    images = browser.find_elements(By.CSS_SELECTOR, "img[src*='sns-webpic-qc.xhscdn.com']")

    # 使用正则表达式提取内容
    # 打印每个图片的 src 属性
    result = []
    for img in images:
        result.append(img.get_attribute("src"))

    # 输出提取的内容
    s = ""
    result = set(result)
    for url in result:
        # 发送 GET 请求获取图片数据
        response = requests.get(url)

        # 检查响应状态码
        if response.status_code == 200:
            # 创建 Image 对象
            image = Image.open(BytesIO(response.content))

            # 转换为 JPG 格式
            image = image.convert("RGB")

            # 获取文件名
            import uuid
            file_name = 'img/' + str(uuid.uuid4()) + ".jpg"

            s += f"![]({file_name})\n"
            # 保存图片到本地
            image.save(file_name)
            print("图片保存成功！")
        else:
            print("图片下载失败！")

    # 构造 Markdown 格式的字符串
    markdown = f"# {titles[0].text}\n\n {s} \n{descs[0].text}"
    # 将字符串写入同目录下的 Markdown 文件
    with open(f"{titles[0].text}.md", "w", encoding="utf-8") as f:
        f.write(markdown)


li = getAllArticle()
# pass
for i in list(li):
    try:
        downForArticle(i)
    except:
        pass
