#能自动将输入的通知转化为代办事项的ai助手
#本来是想基于itchat做能自动获取聊天记录然后总结通知的，但是现在禁用网页版微信，用起来有点麻烦
#听说即使解决了这个问题使用微信bot也有封号风险，遂放弃
import openai
import datetime
import tiktoken
import os
import tkinter as tk

openai.api_key = "your api key"
openai.api_base = "https://api.deepseek.com"

def get_user_input_gui():   #获取用户输入
    """
    通过图形界面获取用户输入
    返回用户输入的字符串，或None表示退出
    """
    # 创建极简深色对话框
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建输入对话框
    dialog = tk.Toplevel(root)
    dialog.title("通知转代办")
    dialog.geometry("500x400")
    
    # 深色主题
    bg_color = "#1a1a1a"
    fg_color = "#ffffff"
    accent_color = "#0078d4"
    dialog.configure(bg=bg_color)
    
    # 输入框标签
    tk.Label(
        dialog,
        text="请输入要总结的通知：",
        font=("Segoe UI", 11),
        bg=bg_color,
        fg=fg_color
    ).pack(pady=(20, 5), padx=20, anchor="w")
    
    # 输入文本框（带滚动条）
    text_input = tk.Text(
        dialog,
        height=12,
        font=("Segoe UI", 11),
        bg="#2d2d2d",
        fg=fg_color,
        insertbackground=fg_color,
        relief="flat"
    )
    text_input.pack(padx=20, pady=5, fill="both", expand=True)
    text_input.focus_set()
    
    # 用于存储结果的变量
    user_input_result = None
    dialog_closed = False
    
    def on_confirm():
        nonlocal user_input_result
        user_input_result = text_input.get("1.0", "end-1c").strip()
        if user_input_result:
            dialog.destroy()
    
    def on_cancel():
        dialog.destroy()
    
    # 按钮区域
    button_frame = tk.Frame(dialog, bg=bg_color)
    button_frame.pack(pady=(0, 20), padx=20)
    
    tk.Button(
        button_frame,
        text="确定",
        font=("Segoe UI", 11),
        bg=accent_color,
        fg="white",
        padx=30,
        pady=8,
        relief="flat",
        command=on_confirm
    ).pack(side="left", padx=5)
    
    tk.Button(
        button_frame,
        text="退出",
        font=("Segoe UI", 11),
        bg="#333333",
        fg=fg_color,
        padx=30,
        pady=8,
        relief="flat",
        command=on_cancel
    ).pack(side="left", padx=5)
    
    # 处理窗口关闭事件
    def on_closing():
        nonlocal dialog_closed
        dialog_closed = True
        dialog.destroy()
    
    dialog.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 等待对话框关闭
    dialog.wait_window()
    root.destroy()
    
    # 返回结果
    if dialog_closed and user_input_result is None:
        return "/exit"  # 用户关闭窗口，相当于输入/exit
    return user_input_result

def token_count(history):       #计算历史tocken长度
    encoding = tiktoken.get_encoding("cl100k_base")
    history_text = ""
    for msg in history:
        history_text += f"{msg['role']}: {msg['content']}\n"
    tokens = len(encoding.encode(history_text))
    return tokens

def generate_todo_html(history, filename="todo_list.html"):
    """生成HTML格式的待办列表"""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    filename = os.path.join(desktop, "todo_list.html")
    
    todos = []
    for i in range(len(history)):
        if history[i]["role"] == "assistant":
            content = history[i]["content"]
            if "待办" in content or "事项" in content or "1." in content:
                todos.append(content)
    
    html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>待办事项清单</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .title {{
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        .todo-card {{
            background: #f8f9fa;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            transition: transform 0.2s;
        }}
        .todo-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .todo-number {{
            display: inline-block;
            background: #3498db;
            color: white;
            width: 30px;
            height: 30px;
            line-height: 30px;
            text-align: center;
            border-radius: 50%;
            margin-right: 10px;
        }}
        .todo-content {{
            display: inline-block;
            color: #2c3e50;
            font-size: 16px;
        }}
        .statistics {{
            background: #e8f4fc;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #95a5a6;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">📋 待办事项清单</h1>
            <div class="subtitle">生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="statistics">
            <strong>📊 统计信息:</strong>
            <div>待办总数: {len(todos)} 项</div>
        </div>
    '''
    
    # 添加待办事项
    for i, todo in enumerate(todos, 1):
        # 简单格式化处理
        formatted_todo = todo.replace('\n', '<br>').replace(' ', '&nbsp;')
        html_content += f'''
        <div class="todo-card">
            <div class="todo-number">{i}</div>
            <div class="todo-content">{formatted_todo}</div>
        </div>
        '''
    
    html_content += f'''
        <div class="footer">
            由 通知总结助手 生成 | {datetime.datetime.now().strftime('%Y年%m月%d日')}
        </div>
    </div>
</body>
</html>
'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"待办清单HTML已保存到: {filename}")
    print(f"请用浏览器打开查看")

setting = """你是用户的得力助理，你的任务是帮助用户从海量的微信通知.现在的时间是 {current_time}，你可以作为参考。但请注意这不一定是消息的发布时间\
            和聊天记录中提取用户需要的内容，为用户总结成代办。你的记性非常好，做事严谨认真，擅于提炼聊天和通知中关键的事件，时间，地点等信息。\
            首先，你要仔细阅读用户给你的通知和聊天记录。然后给用户提供一个简洁的代办，每项代办都会带上代办的发布时间，发布者，截止时间。\
            请主要关注行政通知以及必办的事项，而对于选做的活动要尽可能地简洁\
            在代办前会有一个快速索引，如果该事件已经截止，会有提醒\
            代办将不止包含用户新上传的内容，还将包括历史的所有内容\
            如果你无法保证代办是准确的，你会提供原文，而绝不会自己添加细节\
            用户又粗心又没耐心。你必须非常简洁又不错过要点。减少不必要的换行。"""

def main():
    history = []  #初始化对话历史
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #获取时间

    #无限循环对话，输入/exit或按退出或关闭窗口退出
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #获取时间
               
        user_input = get_user_input_gui()
        
        if user_input is None or user_input == "/exit":
            print("程序结束")
            break
        
        if not user_input.strip():
            continue
        
        prompt = f"{setting}{user_input}"
        
        history.append({"role": "user", "content": prompt})

        if token_count(history) > 2000:
            print("历史记录过长，仅保留最近一次对话...")            
            if len(history) >= 2:               
                history = history[-2:]
            print(f"清理完成，保留 {len(history)} 条记录")

        response = openai.ChatCompletion.create(
                model="deepseek-chat",  # 设置模型
                messages=history,       
                max_tokens=800,
                temperature=0.7,
            )

        answer = response.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        print(f"Assistant: {answer}")

        generate_todo_html(history)

if __name__ == '__main__' :
    print("这是一个可以将通知总结为代办的程序，结果将会以hcml文件形式在桌面呈现")
    print("输入/exit，点击取消或关闭窗口可以退出")
    main()
