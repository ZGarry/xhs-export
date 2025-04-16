# xhs-export

导出小红书笔记到 Markdown 文件，方便本地备份和管理。

## 特性

-   导出笔记的文字内容
-   下载笔记中的图片并保存到本地
-   将笔记内容格式化为 Markdown 文件

## 准备工作

1.  **安装 Python**: 确保你的系统中安装了 Python 3.x。
2.  **下载项目**: 使用 Git 克隆本仓库：
    ```bash
    git clone <仓库地址>
    cd xhs-export
    ```
3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
    *(注意: 你可能需要先创建 `requirements.txt` 文件并列出项目依赖)*

## 如何使用

  **运行脚本**:
    ```bash
    python main.py 
    ```
    *(注意: 假设你的主脚本是 `main.py`)*


**查看结果**: 脚本执行完毕后，导出的 Markdown 文件和图片将保存在指定的输出目录中 (默认为 `output/`，可在代码中修改)。

## 效果示例

*(这里可以添加导出的 Markdown 文件截图或示例)*

```markdown
---
title: 我的小红书笔记标题
create_time: 2023-10-27 10:00:00
---

这是笔记的第一段内容...

![图片描述1](./images/图片1.jpg)

这是笔记的第二段内容...

![图片描述2](./images/图片2.jpg)
```


## 依赖

*(需要根据 `requirements.txt` 文件的内容填写，例如)*
-   requests
-   beautifulsoup4
-   ...

## 贡献

欢迎提交 Pull Request 或提出 Issue。


