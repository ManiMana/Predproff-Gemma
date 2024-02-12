import cv2
import numpy as np
from picamera import PiCamera
from time import sleep
from datetime import datetime
import yadisk

disk = yadisk.YaDisk(id = 'robert.ginosian@yandex.ru', secret = 'RO2B0E0RT6',token="y0_AgAAAAA_I8y4AAtCtAAAAAD6aFXwAADc5BjPJ_hFj5wmfF1iYw5vaFHkuw")

def find_object_and_class(image_path):
    def find_object_bounding_box(image):
        black_pixels = np.argwhere(image <= 70) # Находим координаты черных пикселей

        if len(black_pixels) == 0:
            return None

        max_x, max_y = np.max(black_pixels, axis=0) # Ищем координаты границ рамки
        min_x, min_y = np.min(black_pixels, axis=0)

        return (max_x, max_y, min_x, min_y)

    def crop_image(image, x_min, y_min, x_max, y_max):
        cropped_image = image[x_min-15:x_max+15, y_min-15:y_max+15] # Обрезаем изображение по заданным координатам
        return cropped_image

    def get_image_section(layer, row_from, row_to, col_from, col_to):
        sub_section = layer[:, row_from:row_to, col_from:col_to]
        return sub_section.reshape(-1, 1, row_to - row_from, col_to - col_from)

    tanh = lambda x: np.tanh(x)
    softmax = lambda x: np.exp(x) / np.sum(np.exp(x), axis=1, keepdims=True)

    def predict(image, kernels, weights_1_2):
        kernel_rows, kernel_cols = 3, 3
    
        layer_0 = image.reshape(1, 28, 28)
    
        sects = []
        for row_start in range(layer_0.shape[1] - kernel_rows + 1):
            for col_start in range(layer_0.shape[2] - kernel_cols + 1):
                sect = get_image_section(layer_0, row_start, row_start + kernel_rows,
                                         col_start, col_start + kernel_cols)
                sects.append(sect)
    
        expanded_input = np.concatenate(sects, axis=1)
        es = expanded_input.shape
        flattened_input = expanded_input.reshape(es[0]*es[1], -1)
    
        kernel_output = flattened_input.dot(kernels)
        layer_1 = tanh(kernel_output.reshape(es[0], -1))
    
        layer_2 = softmax(layer_1.dot(weights_1_2).reshape(-1, 2))
    
        predicted_class = np.argmax(layer_2)
    
        return predicted_class

    image = cv2.imread(image_path, 0)
    max_x, max_y, min_x, min_y = find_object_bounding_box(image)
    cropped_image = crop_image(image, min_x, min_y, max_x, max_y)
    cropped_image = cv2.resize(cropped_image, (28, 28)).reshape(784,)

    weight_path1 = "веса1.npy"
    weight_path2 = "веса2.npy"

    weights_1 = np.load(weight_path1)
    weights_2 = np.load(weight_path2)

    predicted_class = predict(cropped_image, weights_1, weights_2)

    return (int((max_x + min_x)//2), int((min_y + max_y)//2), predicted_class)


def capture_photo():
    camera = PiCamera(sensor_mode=0, resolution=(3280, 2464))
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    photo_filename = f'photo_{timestamp}.jpg'
    camera.start_preview()
    sleep(2)
    camera.capture(photo_filename)
    camera.stop_preview()
    return photo_filename


def main():
    # Step 1: Capture a photo
    photo_filename = capture_photo()
    
    disk.upload(photo_filename, photo_filename)

    # Step 5: Check for recognized characters
    recognized_characters = find_object_and_class(photo_filename)

    # Step 6: Perform actions based on recognized characters

    if recognized_characters[2] == 0:
        print("Выполнение действий для 'м.ш.'")
        print(f"Перемещение на координаты x={recognized_characters[0]} y={recognized_characters[1]}")
    elif recognized_characters[2] == 1:
        print("Выполнение действий для 'м.п.'")
        print(f"Перемещение на координаты x={recognized_characters[0]} y={recognized_characters[1]}")
    else:
        print("Символы не найдены")

if __name__ == "__main__":
    main()