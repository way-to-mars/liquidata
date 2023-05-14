import tkinter
import tkinter.scrolledtext

import customtkinter

'''
    Класс инициализирует все вьюшки третьего окна
'''


class Frame3:
    def __init__(self,
                 parent_frame: customtkinter.CTkFrame,
                 images: dict,
                 func_break_the_cycle,
                 ):
        # set grid layout 3x1
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(0, weight=0)
        parent_frame.grid_rowconfigure(1, weight=1)
        parent_frame.grid_rowconfigure(2, weight=0)

        self.search_header_frame = customtkinter.CTkFrame(parent_frame, corner_radius=20)
        self.search_header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 10))

        self.search_console_frame = customtkinter.CTkFrame(parent_frame, corner_radius=20)
        self.search_console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.basement_frame = customtkinter.CTkFrame(parent_frame, corner_radius=20, fg_color="transparent")
        self.basement_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.search_header_frame.grid_columnconfigure(0, weight=0)
        self.search_header_frame.grid_columnconfigure(1, weight=1)

        self.search_console_frame.grid_columnconfigure(0, weight=1)
        self.search_console_frame.grid_rowconfigure(0, weight=1)

        self.search_text = customtkinter.CTkLabel(master=self.search_header_frame,
                                                  text="Идёт продолжительный творческий процесс. Нужно подождать...",
                                                  font=customtkinter.CTkFont(size=20, weight="normal"))
        self.search_text.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky='w')

        self.search_founded = customtkinter.CTkEntry(master=self.search_header_frame, width=170,
                                                     font=customtkinter.CTkFont(size=20, weight="normal"))
        self.search_founded.grid(row=1, column=0, padx=20, pady=(20, 20))
        self.search_founded.insert(0, "Найдено: 0")

        self.search_progressbar = customtkinter.CTkProgressBar(master=self.search_header_frame,
                                                               orientation='horizontal',
                                                               mode='determinate')
        self.search_progressbar.grid(row=1, column=1, padx=(10, 30), pady=(20, 20), sticky="ew")
        self.search_progressbar.set(0.0)

        self.console_text = tkinter.scrolledtext.ScrolledText(self.search_console_frame,
                                                              font=("Lucida Console", 10),
                                                              background="#303030",
                                                              foreground="#60F060")
        self.console_text.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")

        self.elapsed_time_label = customtkinter.CTkLabel(master=self.basement_frame,
                                                         text="До завершения ~",
                                                         font=customtkinter.CTkFont(size=20, weight="normal"))
        self.elapsed_time_label.pack(side=customtkinter.LEFT, padx=(20, 0), pady=10)
        self.elapsed_time_text = customtkinter.CTkLabel(master=self.basement_frame,
                                                        text="...",
                                                        font=customtkinter.CTkFont(size=20, weight="normal"))
        self.elapsed_time_text.pack(side=customtkinter.LEFT)

        self.break_button = customtkinter.CTkButton(master=self.basement_frame,
                                                    text="Стоп! Не могу больше ждать",
                                                    image=images['stopit'],
                                                    compound="left",
                                                    corner_radius=10,
                                                    font=customtkinter.CTkFont(size=18, weight="bold"),
                                                    command=func_break_the_cycle
                                                    )
        self.break_button.pack(side=customtkinter.RIGHT, padx=(0, 20), pady=10)
