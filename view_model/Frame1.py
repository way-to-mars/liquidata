import customtkinter
import webbrowser

'''
    Класс инициализирует все вьюшки первого окна
'''


class Frame1:
    str1_download_base = f'Скачать базу'
    str1_description = f'Для начала необходима актуальная база данных со сведениями обо всех ' \
                       f'ликвидированных юридических лицах.\n' \
                       f'Эта база поставляется в сжатом виде формата "RAR", который находится по адресу:\n' \
                       f'   https://cbr.ru/vfs/egrulinfo/egrul.rar\n' \
                       f'Скачать его можно нажав на кнопку "{str1_download_base}."\n' \
                       f'После завершения перейдите к следующему пункту.'
    str2_open_file = f'Открыть'
    str2_description = f'В скачанном архиве egrul.rar нас интересует только один файл (на иллюстрации слева):\n' \
                       f'  UL_LIQUIDATION.csv\n' \
                       f'Его необходимо извлечь (например, в "Мои Документы")\n\n' \
                       f'Далее нажмите кнопку "{str2_open_file}" и укажите этот файл.'
    str_button_waiting = f'Ждём...'
    str_button_go_next = f'Продолжить'

    def __init__(self,
                 parent_frame: customtkinter.CTkFrame,
                 images: dict,
                 egrul_rar_url: str,
                 window_width: int,
                 func_start_next_window,
                 func_openfile,
                 ):

        self.images = images  # store images here

        # set grid layout 3x1
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=0)
        parent_frame.grid_rowconfigure(2, weight=0)

        # create frames
        self.path_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10)
        self.path_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 0), padx=20, ipady=10, ipadx=10)
        self.path_frame.grid_rowconfigure(0, weight=1)
        self.path_frame.grid_columnconfigure(0, weight=1)

        self.link_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10)
        self.link_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0), padx=20, ipady=10, ipadx=10)
        self.link_frame.grid_columnconfigure(1, weight=1)
        self.link_frame.grid_rowconfigure(0, weight=1)

        self.gonext_button = customtkinter.CTkButton(parent_frame, text=self.str_button_waiting,
                                                     image=images['awaiting'],
                                                     compound="left",
                                                     corner_radius=10,
                                                     command=func_start_next_window,
                                                     font=customtkinter.CTkFont(size=24, weight="bold"))
        self.gonext_button.grid(row=2, column=0, sticky="we", pady=(20, 20), padx=round(window_width / 3), ipady=10,
                                ipadx=10)
        self.gonext_button.configure(state='disabled')

        # ...frame1... "path_frame"
        self.path_frame_text = customtkinter.CTkTextbox(self.path_frame,
                                                        fg_color='lightgrey',
                                                        font=customtkinter.CTkFont(size=18, weight="normal"))
        self.path_frame_text.grid(row=0, column=0, sticky="nswe", padx=10, pady=(10, 0))
        self.path_frame_text.insert("0.0", self.str1_description)
        self.path_frame_text.configure(state="disabled")

        # noinspection PyTypeChecker
        self.path_frame_button = customtkinter.CTkButton(self.path_frame, text=self.str1_download_base,
                                                         image=images['rar_logo'],
                                                         compound="left",
                                                         corner_radius=10,
                                                         font=customtkinter.CTkFont(size=18, weight="bold"),
                                                         command=lambda: webbrowser.open(egrul_rar_url, new=1)
                                                         )
        self.path_frame_button.grid(row=1, column=0, padx=10, pady=(10, 10))

        # ...frame2... "link_frame"
        self.link_frame_text = customtkinter.CTkTextbox(self.link_frame,
                                                        fg_color='lightgrey',
                                                        font=customtkinter.CTkFont(size=18, weight="normal"))
        self.link_frame_text.grid(row=0, column=1, sticky="we", padx=(10, 10), pady=(0, 0))
        self.link_frame_text.insert("0.0", self.str2_description)
        self.link_frame_text.configure(state="disabled")
        self.link_frame_label = customtkinter.CTkLabel(self.link_frame,
                                                       image=images['win_rar'],
                                                       text="")
        self.link_frame_label.grid(row=0, column=0, padx=10, pady=0, sticky="ns")
        self.link_frame_button = customtkinter.CTkButton(self.link_frame, text=self.str2_open_file,
                                                         image=images['csv_logo'],
                                                         compound="left",
                                                         corner_radius=10,
                                                         font=customtkinter.CTkFont(size=18, weight="bold"),
                                                         command=func_openfile
                                                         # command=self.msg_box
                                                         )
        self.link_frame_button.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="s")

    '''
        Если файл .csv задан верно, то активируем кнопку "Продолжить"
    '''

    def second_frame_able(self, state=True):
        if state:
            self.gonext_button.configure(state='enabled', text=self.str_button_go_next, image=self.images['done'])
        else:
            self.gonext_button.configure(state='disabled', text=self.str_button_waiting,
                                         image=self.images['awaiting'])
