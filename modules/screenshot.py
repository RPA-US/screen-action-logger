from PIL import Image
import os
import dxcam
import hashlib
from datetime import datetime

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
    """
    Takes a screenshot and saves it to a directory with a filename based on its hash, current date/time and order of capture.
    """
    global camera  # usa la variable global camera

    # Si no hay instancia de cámara, crear una nueva instancia
    if camera is None:
        camera = dxcam.create()
        print("Creating new camera instance")
    img = camera.grab()

    # Calculamos el hash de la imagen
    sha256_hash = hashlib.sha256()
    sha256_hash.update(img)
    hashed_img = sha256_hash.hexdigest()

    # Acortar el hash para el nombre
    short_hash = hashed_img[:8]

    # Guardar la imagen en el directorio correspondiente. Nombre dependiente de hash
    if save_image:
        directory = os.path.join("screenshots", get_last_directory_name("screenshots"))
        if not os.path.exists(directory):
            os.makedirs(directory)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        counter = len([filename for filename in os.listdir(directory) if filename.endswith('.png')])
        filename = os.path.join(directory, f"{counter+1}_{short_hash}_{timestamp}.png")
        
        # Guarda la imagen y elimina compresión
        Image.fromarray(img).save(filename, compress_level=0)
    print(filename)
    return filename





