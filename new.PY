from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 指定 ChromeDriver 的路径
chrome_driver_path = r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data'

# 配置 ChromeOptions
# 提前登录小红书 + 提前关闭你的谷歌浏览器
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={chrome_driver_path}")  # 替换为你的用户数据目录路径
chrome_options.add_argument("--profile-directory=Default")  # 使用默认配置文件，如果需要其他配置文件可以修改

# 创建 Chrome 浏览器实例
service = Service(r"D:\my\xhs-export\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# 打开网页
driver.get("https://www.google.com")

# 关闭浏览器
driver.quit()
