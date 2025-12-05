# 通知总结助手

该程序可以帮助总结通知，转化为简洁的代办，并生成html。
能获取当前时间；超过两千token时自动删除前文，只保留最近一次，但是因为之前对话的代办事项已经在最近一次的助手回答里，所以之前的代办事项仍未丢失。
==程序基于openai0.28.1，不兼容openai新版本。==

下载依赖库：
`pip install openai==0.28.1 tiktoken`

然后在`openai.api_key = "your api key of deepseek"`这一行中将your api key of deepseek改成自己的api后即可开始使用（保留双引号）