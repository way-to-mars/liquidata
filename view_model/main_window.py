import sys

import customtkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.scrolledtext

from screeninfo import get_monitors
from threading import Thread

import data_processing.big_search
import globals
from globals import APP_OUTPUT_DIR, APP_IMAGES_DIR
from view_model.Frame1 import Frame1
from view_model.Frame2 import Frame2
from view_model.Frame3 import Frame3
from view_model.image_resourses import load_images
from utilities.redirectoutput import RedirectOutputCTk
from data_processing.csv_actions import *
from utilities.strings_format import *


'''
 Все окна реализованы в виде набора виджетов, которые привязаны к своему корневому CTkFrame
     self.first_layout
     self.second_layout
     self.third_layout
 Каждый такой набор легко скрыть командой self.***_layout.grid_forget()
 '''


class App1(customtkinter.CTk):
    window_width = 1920  # just initial values
    window_height = 1080  # will be overridden by set_geometry method

    INPUT_ENCODING = "WINDOWS-1251"
    OUTPUT_ENCODING = "WINDOWS-1251"
    CHAR_DELIMITER = "\t"

    size_of_egrul = [False, 8500000]  # False until it's not calculated in runtime
    input_file_name = ""
    output_csv_file = ""
    egrul_rar_url = "https://cbr.ru/vfs/egrulinfo/egrul.rar"
    regions_to_use = []

    def __init__(self):
        super().__init__()

        self.title("Шаг 1. База данных")
        self.set_geometry()
        self.resizable(True, True)

        self.output_csv_file = os.path.join(APP_OUTPUT_DIR, "output.csv")
        self.output_xlsx_file = os.path.join(APP_OUTPUT_DIR, "output.xlsx")
        self.input_file_name = ''   # Здесь будет полный путь + имя файла UL_LIQUIDATION.csv

        self.images = load_images(APP_IMAGES_DIR)
        self.iconbitmap(os.path.join(APP_IMAGES_DIR, "award_icon.ico"))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.first_layout = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.first_frame = Frame1(
            parent_frame=self.first_layout,
            images=self.images,
            egrul_rar_url=self.egrul_rar_url,
            window_width=self.window_width,
            func_start_next_window=self.start_second_window,
            func_openfile=self.openfile,
        )

        self.second_layout = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame = Frame2(
            parent_frame=self.second_layout,
            images=self.images,
            window_width=self.window_width,
            all_regions=init_regions_and_get_list(True),  # loads a list of all_regions from a csv file
            regions_to_use=self.regions_to_use,
            func_start_next_window=self.start_third_window,
            size_of_egrul=self.size_of_egrul,
        )

        self.third_layout = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.third_frame = Frame3(
            parent_frame=self.third_layout,
            images=self.images,
            func_break_the_cycle=self.break_the_cycle,
        )

        self.first_layout.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

    @staticmethod
    def break_the_cycle():
        globals.globals_user_break = True

    def set_geometry(self):
        screen_width = 1920
        screen_height = 1080
        for m in get_monitors():  # trying to find Primary monitor's resolution
            if m.is_primary:  # if nothing - using defaults 1920x1080
                screen_width = m.width
                screen_height = m.height
        self.window_width = round(screen_width * 0.45)
        self.window_height = round(screen_height * 0.5)
        x_offset = round((screen_width - self.window_width) / 2)
        y_offset = round((screen_height - self.window_height) / 2)
        self.geometry(f'{self.window_width}x{self.window_height}+{x_offset}+{y_offset}')
        self.minsize(self.window_width, self.window_height)

        # if self.primary_window_height <= 900:
        #     customtkinter.set_widget_scaling(1.0)
        # elif self.primary_window_height <= 1024:
        #     customtkinter.set_widget_scaling(1.1)
        # else:
        #     customtkinter.set_widget_scaling(1.2)

    def openfile(self):
        filename = tkinter.filedialog.askopenfilename(
            parent=self,
            title="Разыскивается UL_LIQUIDATION.csv",
            # multiple=False,
            filetypes=[
                ("UL_LIQUIDATION файл", "UL_LIQUIDATION.csv"),
                ("Файлы .csv", "*.csv"),
                ("Все файлы", "*.*")
            ])
        if len(filename) == 0:
            return

        is_ok, message = check_headers(filename, "windows-1251", "\t")
        self.first_frame.second_frame_able(is_ok)
        if is_ok:
            self.input_file_name = filename
            return
        else:
            tkinter.messagebox.showerror("Ошибка openfile", message)

    def start_second_window(self):
        self.first_layout.grid_forget()
        self.second_layout.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.update()
        self.title("Шаг 2. Параметры поиска")
        Thread(target=self.get_base_size, args=(self.input_file_name,)).start()

    def start_third_window(self):
        self.second_layout.grid_forget()
        self.third_layout.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.update()
        self.title("Шаг 3. Поиск")

        # fetch okved filters
        is_main = True if self.second_frame.checkbox_is_main.get() == 1 else False
        choice = self.second_frame.filters_combobox.get()
        filter_id = self.second_frame.filters.get_list().index(choice)
        func_okved_filter = self.second_frame.filters.get_filter_func(filter_id, is_main)

        # extract buffer
        stdout_buffer = sys.stdout.buffer
        # redirect stdout
        console_context = RedirectOutputCTk(self.third_frame.console_text)
        sys.stdout = console_context
        # print out all data from buffer
        for line in stdout_buffer:
            print(line, end="")

        print(self.second_frame.filters.get_filter_description(filter_id, is_main))

        Thread(target=data_processing.big_search.big_search,
               kwargs={
                    "start_date": self.second_frame.start_date,
                    "end_date": self.second_frame.end_date,
                    "regions_to_use": self.regions_to_use,
                    "input_file_name": self.input_file_name,
                    "input_encoding": self.INPUT_ENCODING,
                    "output_csv_file": self.output_csv_file,
                    "output_xlsx_file": self.output_xlsx_file,
                    "char_delimiter": self.CHAR_DELIMITER,
                    "total_lines": int(self.size_of_egrul[1]),
                    "func_callback_progress": self.callback_progress,
                    "func_callback_on_finish": self.callback_on_finish,
                    "func_okved_filter": func_okved_filter,
               }
               ).start()

    def callback_progress(self, percentage, predicted_time, total_write):
        self.third_frame.search_progressbar.set(percentage)
        self.third_frame.elapsed_time_text.configure(
            text=f'{seconds_to_time_string(predicted_time)}')
        self.third_frame.search_founded.delete(0, tkinter.END)
        self.third_frame.search_founded.insert(0, f"Найдено: {total_write}")

    def callback_on_finish(self, is_correct: bool):
        self.third_frame.basement_frame.grid_forget()
        if is_correct:
            self.third_frame.search_text.configure(
                text=f'Программа завершила свою работу. В открывшемся окне Excel можно насладиться результатами )))')
        else:
            self.third_frame.search_text.configure(
                text=f'Программа завершила работу с ошибкой')

    def get_base_size(self, filename):
        with open(filename, 'r') as fp:
            total_lines = sum(1 for _ in fp)
        self.size_of_egrul[0] = True
        self.size_of_egrul[1] = total_lines
        total_text = group_digits(total_lines)
        self.second_frame.progress_label_1.configure(text=f'База содержит {total_text} записей.')
        self.second_frame.progressbar_1.stop()
        self.second_frame.progressbar_1.configure(mode="determinate")
        self.second_frame.progressbar_1.grid_forget()
        Thread(target=self.second_frame.set_2nd_frame_next_able).start()
