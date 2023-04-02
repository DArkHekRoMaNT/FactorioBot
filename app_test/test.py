from tkinter import *

root = Tk()

text = Text()
text.config(font=('courier', 15, 'normal'))
text.config(width=20, height=12)
text.pack(expand=YES, fill=BOTH)
text.insert(END, 'Line 1\nLine 2\nLine 3\n')

text.tag_add('demo', '1.0', '1.3')
text.tag_config('demo', foreground='red')

root.mainloop()
