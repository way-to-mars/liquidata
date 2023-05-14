import customtkinter
from view_model.message_box import MyMessageBox
import tkinter.filedialog
import tkinter.messagebox
import tkinter.scrolledtext
from tkcalendar import DateEntry
import datetime
import tkinter

'''
    Класс инициализирует все вьюшки и логику второго окна
'''


class Frame2:
    str1_date = 'Диапазон дат для поиска'
    str2_description = 'Регионы для поиска << выберите из списка справа'
    str3_description = 'Фильтр ОКВЭД'
    str_button_waiting = f'Ждём...'
    str_button_go_next = f'Продолжить'
    string_message_box = 'Крайне желательно выбрать нужные вам регионы.' \
                         ' Иначе поиск займет многие часы, а то и пару суток'

    def __init__(self,
                 parent_frame: customtkinter.CTkFrame,
                 images: dict,
                 window_width: int,
                 all_regions: list[str],
                 regions_to_use: list[str],
                 func_start_next_window,
                 size_of_egrul,
                 ):

        self.images = images  # store images here
        self.size_of_egrul = size_of_egrul
        self.regions_to_use = regions_to_use
        self.func_start_next_window = func_start_next_window

        # set grid layout 3x1
        parent_frame.grid_columnconfigure(0, weight=0)
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=0)
        parent_frame.grid_rowconfigure(2, weight=0)
        parent_frame.grid_rowconfigure(3, weight=0)

        # create frames
        self.date_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10)
        self.date_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 0), padx=(20, 10), ipady=20, ipadx=20)
        self.date_frame.grid_rowconfigure(0, weight=0)
        self.date_frame.grid_rowconfigure(1, weight=0)
        self.date_frame.grid_rowconfigure(2, weight=1)
        self.date_frame.grid_columnconfigure(0, weight=0)
        self.date_frame.grid_columnconfigure(1, weight=1)
        self.date_frame.grid_columnconfigure(2, weight=0)
        self.date_frame.grid_columnconfigure(3, weight=1)

        self.region_filter_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10)
        self.region_filter_frame.grid(row=0, column=1, rowspan=2,
                                      sticky="nsew", pady=(20, 0), padx=(10, 20), ipady=10, ipadx=10)
        self.region_filter_frame.grid_columnconfigure(0, weight=1)
        self.region_filter_frame.grid_columnconfigure(1, weight=0)
        self.region_filter_frame.grid_columnconfigure(2, weight=1)
        self.region_filter_frame.grid_columnconfigure(3, weight=0)
        self.region_filter_frame.grid_rowconfigure(1, weight=1)

        self.forbidnames_frame = customtkinter.CTkFrame(parent_frame, corner_radius=10)
        self.forbidnames_frame.grid(row=1, column=0,
                                    # columnspan=2,
                                    sticky="nsew", pady=(20, 0), padx=20, ipady=10,
                                    ipadx=10)
        self.forbidnames_frame.grid_columnconfigure(0, weight=1)
        self.forbidnames_frame.grid_rowconfigure(0, weight=0)
        # self.forbidnames_frame.grid_rowconfigure(1, weight=1)

        self.gonext_button2 = customtkinter.CTkButton(parent_frame, text=self.str_button_waiting,
                                                      image=images['awaiting'],
                                                      compound="left",
                                                      corner_radius=10,
                                                      command=self.before_start_third_window,
                                                      font=customtkinter.CTkFont(size=24, weight="bold"))
        self.gonext_button2.grid(row=3, column=0, columnspan=2, sticky="we", pady=(20, 20),
                                 padx=round(window_width / 3), ipady=10,
                                 ipadx=10)
        self.gonext_button2.configure(state='disabled')

        self.progress_label_1 = customtkinter.CTkLabel(master=parent_frame, height=30,
                                                       text="Анализируем файл базы данных...\n"
                                                            "Задайте фильтры, дождитесь завершения",
                                                       font=customtkinter.CTkFont(size=20, weight="normal"))
        self.progress_label_1.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1 = customtkinter.CTkProgressBar(parent_frame)
        self.progressbar_1.grid(row=2, column=1, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1.configure(mode="indeterminate")
        self.progressbar_1.start()

        self.end_date = datetime.date.today()
        self.start_date = datetime.date.today() - datetime.timedelta(days=30)

        customtkinter.CTkLabel(master=self.date_frame, height=30, text=self.str1_date, anchor='center',
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=0, column=0, columnspan=4, padx=(10, 0), pady=10, sticky='nw')

        customtkinter.CTkLabel(master=self.date_frame, height=30, text="c",
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=1, column=0, padx=(5, 5), pady=20)

        self.date_start_entry = DateEntry(master=self.date_frame, width=10, background='#5676FE', locale='ru_ru',
                                          foreground='white',
                                          year=self.start_date.year,
                                          month=self.start_date.month,
                                          day=self.start_date.day,
                                          maxdate=datetime.date.today(),
                                          font=customtkinter.CTkFont(size=20, weight="normal"))
        self.date_start_entry.grid(row=1, column=1, padx=0, pady=20, sticky="new")
        self.date_start_entry.bind('<<DateEntrySelected>>', self.on_date_select)

        customtkinter.CTkLabel(master=self.date_frame, height=30, text="- по",
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=1, column=2, padx=(5, 5), pady=20)

        self.date_end_entry = DateEntry(master=self.date_frame, locale='ru_ru', background='#5A5AF5',
                                        foreground='white',
                                        year=self.end_date.year,
                                        month=self.end_date.month,
                                        day=self.end_date.day,
                                        maxdate=datetime.date.today(),
                                        font=customtkinter.CTkFont(size=20, weight="normal"))
        self.date_end_entry.grid(row=1, column=3, padx=(0, 10), pady=20, sticky="new")
        self.date_end_entry.bind('<<DateEntrySelected>>', self.on_date_select)

        self.date_warning = customtkinter.CTkLabel(master=self.date_frame, height=10,
                                                   text_color='red',
                                                   text="Дата начала больше, чем дата конца!",
                                                   font=customtkinter.CTkFont(size=20, weight="normal"))
        # self.date_warning.grid(row=2, column=0, columnspan=4, padx=(10,10), pady=10, sticky='nw')

        ''' 
        Filtered regions
        '''
        customtkinter.CTkLabel(master=self.region_filter_frame, height=30, text=self.str2_description,
                               justify=customtkinter.CENTER,
                               font=customtkinter.CTkFont(size=20, weight="normal")). \
            grid(row=0, column=0, columnspan=4, padx=(10, 10), pady=10, sticky='w')
        self.region_filter = tkinter.Listbox(self.region_filter_frame,
                                             selectmode=tkinter.SINGLE,
                                             height=6,
                                             font=customtkinter.CTkFont(size=18, weight="normal"))
        self.region_filter.grid(row=1, column=0, sticky="nswe", padx=(10, 0), pady=10)
        filtered_regions_varlist = tkinter.Variable()
        filtered_regions_varlist.set(regions_to_use)  # this will receive filtered regions
        self.region_filter.configure(listvariable=filtered_regions_varlist)

        self.scrollbar1 = tkinter.Scrollbar(
            self.region_filter_frame,
            orient=tkinter.VERTICAL,
            command=self.region_filter.yview)
        self.scrollbar1.grid(row=1, column=1, pady=10, padx=(0, 10), sticky="nsw")
        self.region_filter['yscrollcommand'] = self.scrollbar1.set
        self.region_filter.bind('<<ListboxSelect>>', self.on_region_filter_click)

        ''' 
        All the regions
        '''
        self.regions_list = tkinter.Listbox(self.region_filter_frame,
                                            selectmode=tkinter.SINGLE,
                                            height=6,
                                            font=customtkinter.CTkFont(size=18, weight="normal"))
        all_regions_varlist = tkinter.Variable()
        all_regions_varlist.set(all_regions)
        self.regions_list.configure(listvariable=all_regions_varlist)

        self.regions_list.grid(row=1, column=2, sticky="nswe", padx=0, pady=10)
        self.scrollbar2 = tkinter.Scrollbar(
            self.region_filter_frame,
            orient=tkinter.VERTICAL,
            command=self.regions_list.yview)
        self.scrollbar2.grid(row=1, column=3, pady=10, padx=(0, 10), sticky="nsw")
        self.regions_list['yscrollcommand'] = self.scrollbar2.set
        self.regions_list.bind('<<ListboxSelect>>', self.on_regions_list_click)

        ''' 
        Filter for names
        '''
        customtkinter.CTkLabel(master=self.forbidnames_frame, text=self.str3_description,
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=0, column=0, padx=(10, 10), pady=10, sticky='w')
        self.names_filter = customtkinter.CTkTextbox(self.forbidnames_frame, text_color='grey',
                                                     font=customtkinter.CTkFont(size=18, weight="normal"))
        self.names_filter.grid(row=1, column=0, sticky="nswe", padx=10, pady=(0, 10))
        # self.names_filter.insert("0.0", self.forbidden_grocery_names)
        self.names_filter.configure(state="disabled")

    def on_date_select(self, *args):
        print("Date selected, args=", args)
        self.start_date = self.date_start_entry.get_date()
        self.end_date = self.date_end_entry.get_date()
        if self.start_date <= self.end_date:
            print(f'OK -- {self.start_date} {self.start_date <= self.end_date} {self.end_date}')
            self.date_warning.grid_forget()
        else:
            print('bad date range!!!')
            self.date_warning.grid(row=2, column=0, columnspan=4, padx=(10, 10), pady=10, sticky='nw')
        self.set_2nd_frame_next_able()

    '''
          после завершения подсчета строк в базе
          Останавливаем индикатор прогресса, выводим количество строк в виджет, активируем кнопку "продолжить"
      '''

    def set_2nd_frame_next_able(self):
        if self.size_of_egrul[0] and (self.start_date <= self.end_date):
            self.gonext_button2.configure(state='enabled', text=self.str_button_go_next, image=self.images['done'])
            # self.gonext_button2.configure(image=self.done_image)
        else:
            self.gonext_button2.configure(state='disabled', text=self.str_button_waiting,
                                          image=self.images['awaiting'])
            # self.gonext_button2.configure(image=self.awaiting_image)

    # self.update()

    # Клик мышкой по списку регионов переносит строку в левый лист_бокс
    def on_regions_list_click(self, event):
        selected_indices = self.regions_list.curselection()
        if len(selected_indices) == 0:
            return
        selected_index = selected_indices[0]
        selected_string = self.regions_list.get(selected_index)
        self.regions_list.delete(selected_index)
        self.region_filter.insert(customtkinter.END, selected_string)

    # Клик мышкой по фильтру регионов возвращает строку в правый лист_бокс
    def on_region_filter_click(self, event):
        selected_indices = self.region_filter.curselection()
        if len(selected_indices) == 0:
            return
        selected_index = selected_indices[0]
        selected_string = self.region_filter.get(selected_index)
        self.region_filter.delete(selected_index)
        self.regions_list.insert(customtkinter.END, selected_string)

    # Before starting the next window check the filtered regions list
    # Trying to avoid an empty filter usage
    def before_start_third_window(self):
        size_of = self.region_filter.size()
        self.regions_to_use.clear()
        if size_of == 0:
            # Displaying a message box asking user not to use a void filter
            dialog = MyMessageBox(text=self.string_message_box,
                                  title="Это важно! Пустой список регионов для поиска",
                                  image=self.images['vovka'])
            # of "Ok" then go back to editing preferences
            if dialog.get_input():
                return
        else:
            for i in range(size_of):
                self.regions_to_use.append(str.upper(self.region_filter.get(i)))  # сравнивать будем в верхнем регистре
        self.func_start_next_window()
