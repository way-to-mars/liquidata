import os

APP_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_OUTPUT_DIR = os.path.join(APP_ROOT_DIR, "output_files")
APP_DATA_DIR = os.path.join(APP_ROOT_DIR, "data_files")
APP_IMAGES_DIR = os.path.join(APP_ROOT_DIR, "view_model", "gui_images")

globals_user_break = False  # this global variable is for stopping "the big search"


def prepare_environment():
    def create_path_if_not_exists(path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    create_path_if_not_exists(APP_OUTPUT_DIR)
    create_path_if_not_exists(APP_DATA_DIR)
    create_path_if_not_exists(APP_IMAGES_DIR)

    print(f'"prepare_environment" function is invoked:\n'
          f' ✔ APP_ROOT_DIR → {APP_ROOT_DIR}\n'
          f' ✔ APP_OUTPUT_DIR → {APP_OUTPUT_DIR}\n'
          f' ✔ APP_DATA_DIR → {APP_DATA_DIR}\n'
          f' ✔ APP_IMAGES_DIR → {APP_IMAGES_DIR}\n'
          )


# Call this function in any way
prepare_environment()
