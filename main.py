import sys

from utilities.redirectoutput import RedirectOutputBuffer

stdout_buffer: list[str] = []
new_stdout = RedirectOutputBuffer(stdout_buffer)
sys.stdout = new_stdout

from view_model.main_window import App1

if __name__ == '__main__':
    app1 = App1()
    app1.mainloop()
