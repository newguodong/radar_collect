from tkinter import messagebox as box
from tkinter import Label
import tkinter as tk
 
 
def main_menu():
    window = tk.Tk()
    window.title('安安教具-anchor演示')
    window.geometry('800x800')
    window.configure(background = 'black')
 
    label = Label(window, text = 'Label1', fg = 'light green', bg = 'black', font = (None, 30), height = 2)
    label.pack(side = 'top')
 
    show_label1 = Label(window, text = '标签1', width = 25, height = 2)
    show_label1.pack(pady = 0, padx = 0, anchor = 'w')
 
    show_label2 = Label(window, text = '标签2', width = 25, height = 2)
    show_label2.pack(pady = 10, padx = 25, anchor = 'w')
 
    show_label3 = Label(window, text = '标签3', width = 25, height = 2)
    show_label3.pack(pady = 10, padx = 25, anchor = 'w')
 
    show_label4 = Label(window, text = '标签4', width = 25, height = 2)
    show_label4.pack(pady = 10, padx = 25, anchor = 'w')
 
    show_label5 = Label(window, text = '标签5', width = 25, height = 2)
    show_label5.pack(pady = 10, padx = 25, anchor = 'w')
 
    show_label6 = Label(window, text = '标签6', width = 25, height = 2)
    show_label6.pack(pady = 10, padx = 25, anchor = 'w')
 
    show_label7 = Label(window, text = '标签7', width = 25, height = 2)
    show_label7.pack(pady = 10, padx = 25, anchor = 'n')
 
    show_label8 = Label(window, text = '标签8', width = 25, height = 2)
    show_label8.pack(pady = 10, padx = 25, anchor = 'n')
 
    window.mainloop()
 
 
 
main_menu()