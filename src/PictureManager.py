class PictureManager:
    def __init__(self, is_open_func, open_image_path, closed_image_path):
        self.is_open_func = is_open_func
        self.open_image_path = open_image_path
        self.closed_image_path = closed_image_path

    def get_image(self):
        if self.is_open_func():
            with open(self.open_image_path, "rb") as image_file:
                return image_file.read()
        else:
            with open(self.closed_image_path, "rb") as image_file:
                return image_file.read()