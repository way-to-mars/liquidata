import customtkinter

from customtkinter import CTkToplevel, CTkLabel, CTkButton, CTkFrame, CTkImage
from typing import Union


class MyMessageBox(CTkToplevel):
    def __init__(self,
                 title: str,
                 text: str,
                 image: CTkImage):
        super().__init__()

        self._user_input: Union[bool, None] = None
        self._running: bool = False
        self._text = text
        self._image = image

        self.title(title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10,
                   self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._top_frame = CTkFrame(master=self,
                                   width=400,
                                   fg_color="transparent"
                                   )
        self._top_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._label = CTkLabel(master=self._top_frame,
                               width=300,
                               wraplength=300,
                               fg_color="transparent",
                               justify=customtkinter.LEFT,
                               font=customtkinter.CTkFont(size=20),
                               text=self._text)
        self._label.grid(row=0, column=1, padx=10, pady=10, sticky="wn")

        # self._entry = CTkEntry(master=self,
        #                        width=230)
        # self._entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        if self._image is not None:
            picture = CTkLabel(master=self._top_frame,
                               image=self._image,
                               text="")
            picture.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        self._ok_button = CTkButton(master=self,
                                    width=100,
                                    border_width=0,
                                    text='Ок',
                                    command=self._ok_event,
                                    font=customtkinter.CTkFont(size=20))
        self._ok_button.grid(row=1, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")

        self._cancel_button = CTkButton(master=self,
                                        width=100,
                                        border_width=0,
                                        text='И так сойдёт!',
                                        command=self._cancel_event,
                                        font=customtkinter.CTkFont(size=20))
        self._cancel_button.grid(row=1, column=1, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew")

        # self.after(150, lambda: self._entry.focus())  # set focus to entry with slight delay, otherwise it won't work
        # self._entry.bind("<Return>", self._ok_event)

    def _ok_event(self, event=None):
        self._user_input = True
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self._user_input = False
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self._user_input
