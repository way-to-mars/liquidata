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
    str2_button_opencsv = f'Открыть'
    str2_description = f'В скачанном архиве egrul.rar нас интересует только один файл (на иллюстрации слева):\n' \
                       f'  UL_LIQUIDATION.csv\n' \
                       f'Его необходимо извлечь (например, в "Мои Документы")\n\n' \
                       f'Далее нажмите кнопку "{str2_button_opencsv}" и укажите этот файл.'
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
        self.download_frame = FrameDownload(master=parent_frame, corner_radius=10,
                                            message=self.str1_description,
                                            button_text=self.str1_download_base,
                                            button_image=images['rar_logo'])
        self.download_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 0), padx=20, ipady=10, ipadx=10)
        self.download_frame.grid_rowconfigure(0, weight=1)
        self.download_frame.grid_columnconfigure(0, weight=1)
        self.download_frame.button.configure(command=lambda: webbrowser.open(egrul_rar_url, new=1))

        self.opencsv_frame = FrameOpenCsv(master=parent_frame, corner_radius=10,
                                          description_text=self.str2_description,
                                          rar_image=images['win_rar'],
                                          button_text=self.str2_button_opencsv,
                                          button_image=images['csv_logo'],
                                          func_openfile=func_openfile,
                                          )
        self.opencsv_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0), padx=20, ipady=10, ipadx=10)
        self.opencsv_frame.grid_columnconfigure(1, weight=1)
        self.opencsv_frame.grid_rowconfigure(0, weight=1)

        self.gonext_button = customtkinter.CTkButton(parent_frame, text=self.str_button_waiting,
                                                     image=images['awaiting'],
                                                     compound="left",
                                                     corner_radius=10,
                                                     command=func_start_next_window,
                                                     font=customtkinter.CTkFont(size=24, weight="bold"))
        self.gonext_button.grid(row=2, column=0, sticky="we", pady=(20, 20), padx=round(window_width / 3), ipady=10,
                                ipadx=10)
        self.gonext_button.configure(state='disabled')


    '''
        Если файл .csv задан верно, то активируем кнопку "Продолжить"
    '''

    def second_frame_able(self, state=True):
        if state:
            self.gonext_button.configure(state='enabled', text=self.str_button_go_next, image=self.images['done'])
        else:
            self.gonext_button.configure(state='disabled', text=self.str_button_waiting,
                                         image=self.images['awaiting'])


class FrameDownload(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)

        self.text = customtkinter.CTkTextbox(self,
                                             fg_color='lightgrey',
                                             wrap='word',
                                             font=customtkinter.CTkFont(size=18, weight="normal"))
        self.text.grid(row=0, column=0, sticky="nswe", padx=10, pady=(10, 0))
        self.text.insert("0.0", kwargs['message'])
        self.text.configure(state="disabled")

        self.button = customtkinter.CTkButton(self,
                                              text=kwargs['button_text'],
                                              image=kwargs['button_image'],
                                              compound="left",
                                              corner_radius=10,
                                              font=customtkinter.CTkFont(size=18, weight="bold"),
                                              # command=lambda: webbrowser.open(egrul_rar_url, new=1)
                                              )
        self.button.grid(row=1, column=0, padx=10, pady=(10, 10))


class FrameOpenCsv(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.link_frame_text = customtkinter.CTkTextbox(self,
                                                        fg_color='lightgrey',
                                                        font=customtkinter.CTkFont(size=18, weight="normal"))
        self.link_frame_text.grid(row=0, column=1, sticky="we", padx=(10, 10), pady=(0, 0))
        self.link_frame_text.insert("0.0", kwargs['description_text'])
        self.link_frame_text.configure(state="disabled")
        self.link_frame_label = customtkinter.CTkLabel(self,
                                                       image=kwargs['rar_image'],
                                                       text="")
        self.link_frame_label.grid(row=0, column=0, padx=10, pady=0, sticky="ns")
        self.link_frame_button = customtkinter.CTkButton(self,
                                                         text=kwargs['button_text'],
                                                         image=kwargs['button_image'],
                                                         compound="left",
                                                         corner_radius=10,
                                                         font=customtkinter.CTkFont(size=18, weight="bold"),
                                                         command=kwargs['func_openfile']
                                                         # command=self.msg_box
                                                         )
        self.link_frame_button.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="s")
