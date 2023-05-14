from customtkinter import CTkImage as ctkImage
from os.path import join as join
from PIL import Image


def load_images(path: str) -> dict:
    return {
        'csv_logo': ctkImage(Image.open(join(path, "csv_logo.png")), size=(40, 40)),
        'rar_logo': ctkImage(Image.open(join(path, "rar_logo.png")), size=(40, 40)),
        'win_rar': ctkImage(Image.open(join(path, "win_rar_wide.png")), size=(547, 208)),
        'awaiting': ctkImage(Image.open(join(path, "awaiting.png")), size=(40, 40)),
        'done': ctkImage(Image.open(join(path, "png_done.png")), size=(52, 40)),
        'vovka': ctkImage(Image.open(join(path, "vovka.png")), size=(96, 116)),
        'stopit': ctkImage(Image.open(join(path, "stopit.png")), size=(32, 32)),
    }
