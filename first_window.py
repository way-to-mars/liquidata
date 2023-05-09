import sys
import time
import customtkinter
import webbrowser
import message_box
import tkinter.filedialog
import tkinter.messagebox
import tkinter.scrolledtext

from datetime import date, timedelta
from PIL import Image, ImageTk
from screeninfo import get_monitors
from tkcalendar import DateEntry
from threading import Thread

from csv_actions import *
from excel_trying import create_excel
from my_prediction import MyPrediction
from strings_format import *
from json_actions import parse_inn


class App1(customtkinter.CTk):
    # (custom)Tkinter Varibles
    TKINTER_WIDGETS = {}
    TKINTER_DATA = {}

    primary_window_width = 1920
    primary_window_height = 1080

    INPUT_ENCODING = "WINDOWS-1251"
    OUTPUT_ENCODING = "WINDOWS-1251"
    CHAR_DELIMITER = "\t"
    OUTPUT_LIMIT = 10000  # Ограничение на кол-во найденных организаций

    # число строк в исходной базе UL_LIQUIDATION.csv
    # точное значение определим функцией searching_size_of_base()
    # False - примерное значение, True - точное
    size_of_egrul = (False, 8500000)
    input_file_name = ""
    output_csv_file = ""

    egrul_url = "https://cbr.ru/vfs/egrulinfo/egrul.rar"
    regions_to_use = []
    strvar_region_to_use = None

    forbidden_grocery_names = ['НЕФТЕГАЗ', 'КЛИНИНГОВ', 'КОММУНАЛЬН', 'РЕМОНТН', 'ГЕОХИМ', 'ЮРИДИЧЕСК', 'СТРОИТЕЛЬН',
                               'ТЕПЛОСНАБ', 'ПРОИЗВОДСТВЕНН', 'ТЕХСТРОЙ', 'ЖИЛСТРОЙ', 'СИБСТРОЙ', 'СТРОЙСЕРВИС',
                               'ГАЗСТРОЙ',
                               'ПРОМТОРГ', 'САНТЕХ', 'ЖИЛСЕРВИС', 'ПРОМРЕСУРС', 'ПРОМБЕТОН', 'МЕДИЦИНСК', 'ТЕХКОМПЛЕКТ',
                               'СТРОЙМОНТАЖ', 'СНАБСЕРВИС', 'ДИАГНОСТ', 'ТРАНСПОРТ', 'ФАРМАЦЕВТ', 'ИНЖИНИРИНГ',
                               'ТУРИСТИЧ',
                               'МОНТАЖЭНЕРГО', 'ЭНЕРГОРЕМОНТ', 'ЭЛЕКТРОМОНТАЖ', 'ПРОМХОЗ', 'ЛЕССТРОЙ', 'КАДАСТР']
    # нужны только ООО (АО, ПАО, ЗАО...)
    necessary_part_of_name = 'ОБЩЕСТВО'

    string_w1_f1_button = f'Скачать базу'
    string_w1_f1_text = f'Для начала необходима актуальная база данных со сведениями обо всех ' \
                        f'ликвидированных юридических лицах.\n' \
                        f'Эта база поставляется в сжатом виде формата "RAR", который находится по адресу:\n' \
                        f'   https://cbr.ru/vfs/egrulinfo/egrul.rar\n' \
                        f'Скачать его можно нажав на кнопку "{string_w1_f1_button}."\n' \
                        f'После завершения перейдите к следующему пункту.'
    string_w1_f2_button = f'Открыть'
    string_w1_f2_text = f'В скачанном архиве egrul.rar нас интересует только один файл (на иллюстрации слева):\n  UL_LIQUIDATION.csv\n' \
                        f'Его необходимо извлечь (например, в "Мои Документы")\n\n' \
                        f'Далее нажмите кнопку "{string_w1_f2_button}" и укажите этот файл.'
    string_w1_f3_awaiting = f'Ждём...'
    string_w1_f3_button = f'Продолжить'
    string_w2_f1_text = 'Диапазон дат для поиска'
    string_w2_f2_text = 'Регионы для поиска\t<<\t выберите из списка справа'
    string_w2_f3_text = 'Неизменяемо! Фильтр непродовольственных названий'

    string_msgbox_text = 'Крайне желательно выбрать нужные вам регионы.' \
                         ' Иначе поиск займет многие часы, а то и пару суток'

    def __init__(self):
        super().__init__()

        self.title("Шаг 1. База данных")
        self.set_geometry()
        self.resizable(True, True)

        files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output_files")
        self.output_csv_file = os.path.join(files_path, "output.csv")
        self.output_xlsx_file = os.path.join(files_path, "output.xlsx")
        # Здесь будет полный путь + имя файла UL_LIQUIDATION.csv
        self.input_file_name = ''

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gui_images")
        self.csv_logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "csv_logo.png")),
                                                     size=(40, 40))
        self.rar_logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "rar_logo.png")),
                                                     size=(40, 40))
        self.win_rar = customtkinter.CTkImage(Image.open(os.path.join(image_path, "win_rar_wide.png")), size=(547, 208))
        self.awaiting_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "awaiting.png")),
                                                     size=(40, 40))
        self.done_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "png_done.png")), size=(52, 40))
        self.vovka_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "vovka.png")), size=(96, 116))
        self.stopit_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "stopit.png")),
                                                   size=(32, 32))

        self.iconbitmap(os.path.join(image_path, "award_icon.ico"))

        self.msgbox_ico = Image.open(os.path.join(image_path, "win_rar_wide.png"))
        self.msgbox_photo = ImageTk.PhotoImage(self.msgbox_ico)

        '''
        Все окна реализованы в виде набора виджетов, которые привязаны к своему корневому CTkFrame
            self.first_layout
            self.second_layout
            self.third_layout
        Каждый такой набор легко скрыть командой self.***_layout.grid_forget()
        '''
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.first_layout = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.init_first_window(self.first_layout)
        self.second_layout = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.init_second_window(self.second_layout)
        self.third_layout = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.init_third_window(self.third_layout)
        self.first_layout.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

    # Первое окно
    def init_first_window(self, parent1):
        # set grid layout 3x1
        parent1.grid_columnconfigure(0, weight=1)
        parent1.grid_rowconfigure(0, weight=1)
        parent1.grid_rowconfigure(1, weight=0)
        parent1.grid_rowconfigure(2, weight=0)

        # create frames
        self.path_frame = customtkinter.CTkFrame(parent1, corner_radius=10)
        self.path_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 0), padx=20, ipady=10, ipadx=10)
        self.path_frame.grid_rowconfigure(0, weight=1)
        self.path_frame.grid_columnconfigure(0, weight=1)

        self.link_frame = customtkinter.CTkFrame(parent1, corner_radius=10)
        self.link_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0), padx=20, ipady=10, ipadx=10)
        self.link_frame.grid_columnconfigure(1, weight=1)
        self.link_frame.grid_rowconfigure(0, weight=1)

        self.gonext_button = customtkinter.CTkButton(parent1, text=self.string_w1_f3_awaiting,
                                                     image=self.awaiting_image,
                                                     compound="left",
                                                     corner_radius=10,
                                                     command=self.start_second_window,
                                                     font=customtkinter.CTkFont(size=24, weight="bold"))
        self.gonext_button.grid(row=2, column=0, sticky="we", pady=(20, 20), padx=round(self.x_width / 3), ipady=10,
                                ipadx=10)
        self.gonext_button.configure(state='disabled')

        # ...frame1... "path_frame"
        self.path_frame_text = customtkinter.CTkTextbox(self.path_frame,
                                                        fg_color='lightgrey',
                                                        font=customtkinter.CTkFont(size=18, weight="normal"))
        self.path_frame_text.grid(row=0, column=0, sticky="nswe", padx=10, pady=(10, 0))
        self.path_frame_text.insert("0.0", self.string_w1_f1_text)
        self.path_frame_text.configure(state="disabled")

        self.path_frame_button = customtkinter.CTkButton(self.path_frame, text=self.string_w1_f1_button,
                                                         image=self.rar_logo_image,
                                                         compound="left",
                                                         corner_radius=10,
                                                         font=customtkinter.CTkFont(size=18, weight="bold"),
                                                         command=lambda: webbrowser.open(self.egrul_url, new=1)
                                                         # command=download_egrul
                                                         )
        self.path_frame_button.grid(row=1, column=0, padx=10, pady=(10, 10))

        # ...frame2... "link_frame"
        self.link_frame_text = customtkinter.CTkTextbox(self.link_frame,
                                                        fg_color='lightgrey',
                                                        font=customtkinter.CTkFont(size=18, weight="normal"))
        self.link_frame_text.grid(row=0, column=1, sticky="we", padx=(10, 10), pady=(0, 0))
        self.link_frame_text.insert("0.0", self.string_w1_f2_text)
        self.link_frame_text.configure(state="disabled")
        self.link_frame_label = customtkinter.CTkLabel(self.link_frame,
                                                       image=self.win_rar,
                                                       text="")
        self.link_frame_label.grid(row=0, column=0, padx=10, pady=0, sticky="ns")
        self.link_frame_button = customtkinter.CTkButton(self.link_frame, text=self.string_w1_f2_button,
                                                         image=self.csv_logo_image,
                                                         compound="left",
                                                         corner_radius=10,
                                                         font=customtkinter.CTkFont(size=18, weight="bold"),
                                                         command=self.openfile
                                                         # command=self.msg_box
                                                         )
        self.link_frame_button.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="s")

    # Второе Окно
    def init_second_window(self, parent1):
        # set grid layout 3x1
        parent1.grid_columnconfigure(0, weight=0)
        parent1.grid_columnconfigure(1, weight=1)
        parent1.grid_rowconfigure(0, weight=1)
        parent1.grid_rowconfigure(1, weight=0)
        parent1.grid_rowconfigure(2, weight=0)

        # create frames
        self.date_frame = customtkinter.CTkFrame(parent1, corner_radius=10)
        self.date_frame.grid(row=0, column=0, sticky="nsew", pady=(20, 0), padx=(20, 10), ipady=20, ipadx=20)
        self.date_frame.grid_rowconfigure(0, weight=0)
        self.date_frame.grid_rowconfigure(1, weight=0)
        self.date_frame.grid_rowconfigure(2, weight=1)
        self.date_frame.grid_columnconfigure(0, weight=0)
        self.date_frame.grid_columnconfigure(1, weight=1)
        self.date_frame.grid_columnconfigure(2, weight=0)
        self.date_frame.grid_columnconfigure(3, weight=1)

        self.region_filter_frame = customtkinter.CTkFrame(parent1, corner_radius=10)
        self.region_filter_frame.grid(row=0, column=1, sticky="nsew", pady=(20, 0), padx=(10, 20), ipady=10, ipadx=10)
        self.region_filter_frame.grid_columnconfigure(0, weight=1)
        self.region_filter_frame.grid_columnconfigure(1, weight=0)
        self.region_filter_frame.grid_columnconfigure(2, weight=1)
        self.region_filter_frame.grid_columnconfigure(3, weight=0)
        self.region_filter_frame.grid_rowconfigure(1, weight=1)

        self.forbidnames_frame = customtkinter.CTkFrame(parent1, corner_radius=10)
        self.forbidnames_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(20, 0), padx=20, ipady=10,
                                    ipadx=10)
        self.forbidnames_frame.grid_columnconfigure(0, weight=1)
        self.forbidnames_frame.grid_rowconfigure(0, weight=0)
        # self.forbidnames_frame.grid_rowconfigure(1, weight=1)

        self.gonext_button2 = customtkinter.CTkButton(parent1, text=self.string_w1_f3_awaiting,
                                                      image=self.awaiting_image,
                                                      compound="left",
                                                      corner_radius=10,
                                                      command=self.before_start_third_window,
                                                      font=customtkinter.CTkFont(size=24, weight="bold"))
        self.gonext_button2.grid(row=3, column=0, columnspan=2, sticky="we", pady=(20, 20),
                                 padx=round(self.x_width / 3), ipady=10,
                                 ipadx=10)
        self.gonext_button2.configure(state='disabled')

        self.progress_label_1 = customtkinter.CTkLabel(master=parent1, height=30,
                                                       text="Анализируем файл базы данных...\nЗадайте фильтры, дождитесь завершения",
                                                       font=customtkinter.CTkFont(size=20, weight="normal"))
        self.progress_label_1.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1 = customtkinter.CTkProgressBar(parent1)
        self.progressbar_1.grid(row=2, column=1, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()

        ''' 
        Current Date Time

        cal = Calendar(top, font="Arial 14", selectmode='day', locale='ru_ru',
                       mindate=mindate, maxdate=today, disabledforeground='red',
                       cursor="hand1"
                       # , year=2018, month=2, day=5
                       )
        '''
        self.end_date_time = date.today()
        self.start_date_time = date.today() - timedelta(days=30)

        customtkinter.CTkLabel(master=self.date_frame, height=30, text=self.string_w2_f1_text, anchor='center',
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=0, column=0, columnspan=4, padx=(10, 0), pady=10, sticky='nw')

        customtkinter.CTkLabel(master=self.date_frame, height=30, text="c",
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=1, column=0, padx=(5, 5), pady=20)

        self.date_start_entry = DateEntry(master=self.date_frame, width=10, background='#5676FE', locale='ru_ru',
                                          foreground='white',
                                          year=self.start_date_time.year,
                                          month=self.start_date_time.month,
                                          day=self.start_date_time.day,
                                          maxdate=datetime.date.today(),
                                          font=customtkinter.CTkFont(size=20, weight="normal"))
        self.date_start_entry.grid(row=1, column=1, padx=0, pady=20, sticky="new")
        self.date_start_entry.bind('<<DateEntrySelected>>', self.on_date_select)

        customtkinter.CTkLabel(master=self.date_frame, height=30, text="- по",
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=1, column=2, padx=(5, 5), pady=20)

        self.date_end_entry = DateEntry(master=self.date_frame, locale='ru_ru', background='#5A5AF5',
                                        foreground='white',
                                        year=self.end_date_time.year,
                                        month=self.end_date_time.month,
                                        day=self.end_date_time.day,
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
        Filter for regions
        '''
        customtkinter.CTkLabel(master=self.region_filter_frame, height=30, text=self.string_w2_f2_text,
                               justify=customtkinter.CENTER,
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=0, column=0, columnspan=4, padx=(10, 10), pady=10, sticky='w')
        self.region_filter = tkinter.Listbox(self.region_filter_frame,
                                             selectmode=tkinter.SINGLE,
                                             height=6,
                                             font=customtkinter.CTkFont(size=18, weight="normal"))
        self.region_filter.grid(row=1, column=0, sticky="nswe", padx=(10, 0), pady=10)
        self.strvar_region_to_use = tkinter.StringVar(value=self.regions_to_use)
        self.region_filter.configure(listvariable=self.strvar_region_to_use)

        self.scrollbar1 = tkinter.Scrollbar(
            self.region_filter_frame,
            orient=tkinter.VERTICAL,
            command=self.region_filter.yview)
        self.scrollbar1.grid(row=1, column=1, pady=10, padx=(0, 10), sticky="nsw")
        self.region_filter['yscrollcommand'] = self.scrollbar1.set
        self.region_filter.bind('<<ListboxSelect>>', self.on_region_filter_click)

        self.regions_list = tkinter.Listbox(self.region_filter_frame,
                                            selectmode=tkinter.SINGLE,
                                            height=6,
                                            font=customtkinter.CTkFont(size=18, weight="normal"))
        fill_listbox_with_regions(self.regions_list)
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
        customtkinter.CTkLabel(master=self.forbidnames_frame, text=self.string_w2_f3_text,
                               font=customtkinter.CTkFont(size=20, weight="normal")).grid(
            row=0, column=0, padx=(10, 10), pady=10, sticky='w')
        self.names_filter = customtkinter.CTkTextbox(self.forbidnames_frame, text_color='grey',
                                                     font=customtkinter.CTkFont(size=18, weight="normal"))
        self.names_filter.grid(row=1, column=0, sticky="nswe", padx=10, pady=(0, 10))
        self.names_filter.insert("0.0", self.forbidden_grocery_names)
        self.names_filter.configure(state="disabled")

    # Третье Окно
    def init_third_window(self, parent):
        # set grid layout 3x1
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(2, weight=0)

        self.search_header_frame = customtkinter.CTkFrame(parent, corner_radius=20)
        self.search_header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 10))

        self.search_console_frame = customtkinter.CTkFrame(parent, corner_radius=20)
        self.search_console_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.basement_frame = customtkinter.CTkFrame(parent, corner_radius=20, fg_color="transparent")
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
                                                    image=self.stopit_image,
                                                    compound="left",
                                                    corner_radius=10,
                                                    font=customtkinter.CTkFont(size=18, weight="bold"),
                                                    command=self.break_the_cycle
                                                    )
        self.break_button.pack(side=customtkinter.RIGHT, padx=(0, 20), pady=10)

    def break_the_cycle(self):
        self.OUTPUT_LIMIT = 0

    def set_geometry(self):
        for m in get_monitors():  # trying to find Primary monitor's resolution
            if m.is_primary:  # if nothing - using defaults 1920x1080
                self.primary_window_width = m.width
                self.primary_window_height = m.height
        self.x_width = round(self.primary_window_width * 0.45)
        self.y_height = round(self.primary_window_height * 0.5)
        x_offset = round((self.primary_window_width - self.x_width) / 2)
        y_offset = round((self.primary_window_height - self.y_height) / 2)
        self.geometry(f'{self.x_width}x{self.y_height}+{x_offset}+{y_offset}')
        self.minsize(self.x_width, self.y_height)

        # if self.primary_window_height <= 900:
        #     customtkinter.set_widget_scaling(1.0)
        # elif self.primary_window_height <= 1024:
        #     customtkinter.set_widget_scaling(1.1)
        # else:
        #     customtkinter.set_widget_scaling(1.2)

    def openfile(self):
        filename = tkinter.filedialog.askopenfilename(parent=self, title="Разыскивается UL_LIQUIDATION.csv",
                                                      multiple=False,
                                                      filetypes=[("UL_LIQUIDATION файл", "UL_LIQUIDATION.csv"),
                                                                 ("Файлы .csv", "*.csv"), ("Все файлы", "*.*")])
        if len(filename) == 0:
            return

        isOk, message = check_headers(filename, "windows-1251", "\t")
        if isOk:
            self.set_1st_frame_next_able(True)
            self.input_file_name = filename
            return
        else:
            self.set_1st_frame_next_able(False)
            tkinter.messagebox.showerror("Ошибка openfile", message)

    '''
        Для первого окна.
        Если файл .csv задан верно, то активируем кнопку "Продолжить"
    '''

    def set_1st_frame_next_able(self, state=True):
        if state:
            self.gonext_button.configure(state='enabled', text=self.string_w1_f3_button, image=self.done_image)
        else:
            self.gonext_button.configure(state='disabled', text=self.string_w1_f3_awaiting, image=self.awaiting_image)

    '''
        Для второго окна
        (после завершения подсчета строк в базе)
        Останавливаем индикатор прогресса, выводим количество строк в виджет, активируем кнопку "продолжить"
    '''

    def set_2nd_frame_next_able(self):
        if (self.size_of_egrul[0] and (self.start_date_time <= self.end_date_time)):
            self.gonext_button2.configure(state='enabled', text=self.string_w1_f3_button, image=self.done_image)
            # self.gonext_button2.configure(image=self.done_image)
        else:
            self.gonext_button2.configure(state='disabled', text=self.string_w1_f3_awaiting, image=self.awaiting_image)
            # self.gonext_button2.configure(image=self.awaiting_image)
        self.update()

    def start_second_window(self):
        # print(f'input file name = {self.input_file_name}')
        self.first_layout.grid_forget()
        self.second_layout.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.update()
        self.title("Шаг 2. Параметры поиска")
        Thread(target=self.searching_size_of_base, args=(self.input_file_name,)).start()

    def before_start_third_window(self):
        size_of = self.region_filter.size()
        if size_of == 0:
            # пустой фильтр - это долго и плохо
            dialog = message_box.message_box(text=self.string_msgbox_text,
                                             title="Это важно! Пустой список регионов для поиска",
                                             image=self.vovka_image)
            if dialog.get_input() != False:
                return
            # если пользователь настойчив, будем работать с пустым фильтром
            # так или иначе в алгоритме заложен предел для результатов поиска {OUTPUT_LIMIT}
            self.regions_to_use.clear()
        else:
            self.regions_to_use.clear()
            for i in range(size_of):
                self.regions_to_use.append(str.upper(self.region_filter.get(i)))  # сравнивать будем в верхнем регистре
        self.start_third_window()

    def start_third_window(self):
        # print(self.region_filter.get("1.0", "end"))
        # print(combine_lists(self.regions_to_use, self.region_filter.get("1.0", "end")))
        self.second_layout.grid_forget()
        self.third_layout.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.update()
        self.title("Шаг 3. Поиск")
        # redirect stdout
        from strings_format import RedirectText
        redir = RedirectText(self.console_text)
        sys.stdout = redir
        Thread(target=self.the_big_search).start()

    def searching_size_of_base(self, filename):
        with open(filename, encoding=self.INPUT_ENCODING) as r_file:
            file_counter = csv.DictReader(r_file, delimiter=self.CHAR_DELIMITER)
            # print(f'Старт. Читаем файл...')
            total_lines = sum(1 for line in file_counter)
            # total_lines = 8550000
            # total_lines = 0
            # for line in file_counter:
            #     total_lines += 1
            #     # if total_lines >900000:
            #     #      break
            #     if total_lines % 500000 == 0:
            #         print(group_digits(total_lines))
            # print(f'Найдено {group_digits(total_lines)} записей')
        self.size_of_egrul = (True, total_lines)
        # total_text = '{0:,}'.format(total_lines).replace(',', ' ')
        total_text = group_digits(total_lines)
        self.progress_label_1.configure(text=f'База содержит {total_text} записей.')
        self.progressbar_1.stop()
        self.progressbar_1.configure(mode="determinate")
        self.progressbar_1.grid_forget()
        Thread(target=self.set_2nd_frame_next_able).start()
        #  self.set_2nd_frame_next_able

    def on_date_select(event, *args):
        print("Date selected, args=", args)
        event.start_date_time = event.date_start_entry.get_date()
        event.end_date_time = event.date_end_entry.get_date()
        if (event.start_date_time <= event.end_date_time):
            print(f'OK -- {event.start_date_time} {event.start_date_time <= event.end_date_time} {event.end_date_time}')
            event.date_warning.grid_forget()
        else:
            print('bad range!!!')
            event.date_warning.grid(row=2, column=0, columnspan=4, padx=(10, 10), pady=10, sticky='nw')
        event.set_2nd_frame_next_able()

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

    def the_big_search(self):
        with open(self.input_file_name, encoding=self.INPUT_ENCODING) as r_file:
            with open(self.output_csv_file, mode="w", encoding='WINDOWS-1251') as w_file:
                fieldnames = ['ИНН', 'Дата прекращения', 'Код', 'Причина прекращения', 'Наименование (краткое)',
                              'Основной ОКВЭД', 'Расшифровка ОКВЭД']
                # write headers
                w_file.write(f"{self.CHAR_DELIMITER.join(fieldnames)}\n")

                file_reader = csv.DictReader(r_file, delimiter=self.CHAR_DELIMITER)

                total_write = 0
                total_read = 0
                total_lines = self.size_of_egrul[1]

                mp = MyPrediction(25)  # "Предсказатель" оставшегося времени выполнения по {arg} точкам
                digit_delimiter = "'"  # разделитель групп разрядов

                # Считывание данных из CSV файла
                for row in file_reader:
                    total_read += 1
                    x_name_long = row['NAMEP']
                    x_date = row['DATAPREKRUL']
                    x_region = row['REGION_NAME']
                    x_kpp = row['KPP']
                    x_okato = row['OKATO']
                    x_inner_id = row['STATUS_LIQUIDATION_INNER_ID']

                    flag_date = check_date(x_date, self.start_date_time, self.end_date_time)
                    flag_obshestvo = is_ooo(x_name_long, self.necessary_part_of_name)
                    # flag_region = check_region(x_region, self.regions_to_use)
                    flag_region, rating_regions = triple_check_region(region_name=x_region,
                                                                      regions_list=self.regions_to_use,
                                                                      kpp=x_kpp,
                                                                      okato=x_okato)

                    if flag_date & flag_obshestvo & flag_region:
                        if check_forbidden_names(x_name_long, self.forbidden_grocery_names):
                            print(f'[{total_read / total_lines:.2%}] Отклонено! Непрофильное название: {x_name_long}')
                        else:
                            total_write += 1
                            self.search_founded.delete(0, tkinter.END)
                            self.search_founded.insert(0, f"Найдено: {total_write}")
                            percentage = total_read / total_lines
                            self.search_progressbar.set(percentage)
                            mp.add_point(time.time(), percentage)
                            x_inn = row['INN']
                            x_name_short = row['NAMES']
                            x_reason, x_okved, x_okved_name = parse_inn(x_inn)
                            print(f'[{percentage:.1%}] {group_digits(total_write, digit_delimiter)}: ИНН {x_inn}\t'
                                  f'{x_name_short}\tдата прекращения: {x_date}\tпричина: {x_reason}\n'
                                  f'\t\tОКВЭД {x_okved} {x_okved_name}')

                            # file_writer.writerow({'ИНН': x_inn, 'Наименование': x_name_long, 'Дата прекращения': x_date,
                            #                       'Причина прекращения': x_reason, 'Основной ОКВЭД': x_okved,
                            #                       'Расшифровка ОКВЭД': x_okved_name})

                            w_file.write(f'{x_inn}{self.CHAR_DELIMITER}'
                                         f'{x_date}{self.CHAR_DELIMITER}'
                                         f'{(int(x_inner_id), rating_regions)}{self.CHAR_DELIMITER}'
                                         f'{x_reason}{self.CHAR_DELIMITER}'
                                         f'{x_name_short}{self.CHAR_DELIMITER}'
                                         f'{x_okved}{self.CHAR_DELIMITER}'
                                         f'{x_okved_name}\n')

                    # раз в --- шагов обновляем индикатор прогресса
                    if (total_read % 10000) == 9999:
                        percentage = total_read / total_lines
                        self.search_progressbar.set(percentage)
                        mp.add_point(time.time(), percentage)
                        self.elapsed_time_text.configure(
                            text=f'{seconds_to_timestr(mp.seek_time())}')

                    self.break_button.event_generate("<<DoExcel>>", when="tail")

                    # ограничим количество строк для записи значением {limit_output}
                    if total_write >= self.OUTPUT_LIMIT:
                        if self.OUTPUT_LIMIT > 0:
                            print(f'Достигнут предел искомых строк {self.OUTPUT_LIMIT}, поиск завершён')
                        else:
                            print(f'Выполнение поиска прервано пользователем')
                        break

        print(
            f'Прочитано {total_read} {name_count_strings(total_read)}, найдено {total_write} {name_count_strings(total_write)}')
        self.basement_frame.grid_forget()
        print("Выгружаем результат в Excel...", end="")
        create_excel(self.output_csv_file, self.output_xlsx_file)
        print("- готово.")
        self.search_text.configure(
            text=f'Программа завершила свою работу. В открывшемся окне Excel можно насладиться результатами )))')
