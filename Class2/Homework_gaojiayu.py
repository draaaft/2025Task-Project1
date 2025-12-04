#一份迟交的作业（）其实我一直记得它的，离布置到现在其实也就过了...一个多月（惊叹
# 可获知当前时间的对话助手
# 思路：通过datetime库来获取当前时间，并通过提示词告知大模型，使得大模型始终知道当下的时间。

import openai
import datetime

openai.api_key = "api-key"  #设置api
history = []  #初始化对话历史

#无限循环对话，直到用户输入为空
while True:
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #获取时间
    prompt = f"现在的时间是 {current_time}，你可以作为参考。{input('You: ')}" #自动将时间添加添加到引导词
    if not prompt:
        break  

    history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  #设置模型
        messages=history,       #将对话历史传给模型
        max_tokens=1000
    )

    answer = response['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": answer})#将模型的回答添加到历史
    print(f"Assistant: {answer}")