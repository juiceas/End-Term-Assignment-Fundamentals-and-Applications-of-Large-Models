# 红楼梦问答系统 - 快速开始指南

## 第一步: 安装依赖
 如果有报错，按照提示安装所需依赖包即可。
## 第二步: 配置API密钥



编辑`.env`文件
   API密钥从https://cloud.siliconflow.cn/i/wmhVdICz获取即可，可有免费的14元额度。
   填入硅基流动API密钥:
```
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxx
```

## 第三步: 准备数据

将PDF文档放入`PDF/`文件夹(如果有的话)

## 第四步: 构建知识库

运行数据处理管道:

```bash
python main.py --mode full
```

此命令将:
- 爬取红楼梦相关网站
- 处理PDF文档
- OCR识别扫描版PDF
- 构建向量知识库

## 第五步: 启动Web应用

```bash
python api.py
```

浏览器会打开应用(http://localhost:5000)

## 开始使用!

在输入框中输入问题,例如:
- "贾宝玉到底更爱黛玉还是宝钗?"
- "林黛玉和薛宝钗谁更有钱？"
- "红楼梦中最好看的女孩儿是谁？"

