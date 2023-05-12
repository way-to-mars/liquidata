import tkinter


class RedirectOutput(object):
    def __init__(self, text_ctrl):
        """Constructor"""
        self.output = text_ctrl

    def write(self, string):
        """"""
        self.output.insert(tkinter.END, string)
        self.output.see("end")

    def flush(self):
        pass
