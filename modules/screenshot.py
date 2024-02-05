from PIL import Image
import os
import dxcam
import hashlib
from datetime import datetime
import io

def get_last_directory_name(path):
    """
    Returns the name of the last directory within a given directory path.
    """
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    if directories:
        last_directory = max(directories, key=lambda d: os.path.getmtime(os.path.join(path, d)))
        return os.path.basename(last_directory)
    else:
        return None

camera = None 

def take_screenshot(save_image=True):
    global camera, last_successful_screenshot

    if camera is None:
        camera = dxcam.create()

    img = camera.grab()

    # Verifica si la captura de pantalla fue exitosa
    if img is None:
        print("Unable to capture screen. Using the last successful capture.")
        return last_successful_screenshot

    # Procede con la conversión de la imagen y el cálculo del hash
    img_byte_arr = io.BytesIO()
    Image.fromarray(img).save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    sha256_hash = hashlib.sha256()
    sha256_hash.update(img_byte_arr)
    hashed_img = sha256_hash.hexdigest()

    # Guardar la imagen si se requiere
    if save_image:
        directory = os.path.join("screenshots", get_last_directory_name("screenshots"))
        if not os.path.exists(directory):
            os.makedirs(directory)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        counter = len([filename for filename in os.listdir(directory) if filename.endswith('.png')])
        filename = os.path.join(directory, f"{counter+1}_{hashed_img[:8]}_{timestamp}.png")
        with open(filename, 'wb') as f:
            f.write(img_byte_arr)
        last_successful_screenshot = filename

    return filename