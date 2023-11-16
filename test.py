from tkinter import *
# 创建窗体
win = Tk()
win.title("C语言中文网")
win.geometry('300x300')
# 创建一个容器来包括其他控件
frame = Frame (win)
# 创建一个计算器

time_interval = 0

def calc() :
# 用户输入的表达式，计算结果后转换为字符串
    input_str = expression.get()
    try:
        input_int = int(input_str)
        print(f"input_str={input_str}")
        print(f"input_int={input_int}")
    except(ValueError):
        print("ValueError")
        print(f"time_interval={time_interval}")
    else:
        time_interval = input_int
        print(f"time_interval={time_interval}")
#创建一个Label控件
label = Label (frame)
#创建一个Entry控件
entry = Entry (frame)
#读取用户输入的表达式
expression = StringVar ()
#将用户输入的表达式显示在Entry控件上
entry ["textvariable"] = expression
#创建-一个 Button控件.当用户输入完毕后，单击此按钮即计算表达式的结果
button1 = Button (frame, text="等 于",command=calc)
#设置Entry控件为焦点所在
entry.focus ()
frame.pack ()
#Entry控件位于窗体的上方
entry .pack(side="left")
#Label控件位于窗体的左方
label .pack (side="left")
#Button控件位于窗体的右方
button1.pack (side="right")
#开始程序循环
frame .mainloop()