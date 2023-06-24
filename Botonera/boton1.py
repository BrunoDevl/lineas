import telebot
from telebot import types
import re
import time
import os
import threading

TOKEN = '5887216770:AAEq3vOckXWH9HojKfkxaDeW2JQPYCWfdk0'  # Reemplaza con tu token
bot = telebot.TeleBot(TOKEN)

registered_channels = []  # Lista para almacenar los IDs de los canales registrados
post_buttons = []  # Lista para almacenar los botones del post
custom_post_caption = None  # Variable para almacenar la descripción personalizada del comando /post
custom_post_photo = None  # Variable para almacenar la imagen personalizada del comando /post
custom_post_video = None  # Variable para almacenar el video personalizado del comando /post
sent_messages = {}  # Diccionario para almacenar los mensajes enviados a cada canal

# Verifica que el mensaje provenga del usuario autorizado
def is_authorized_user(message):
    authorized_user_id = '5497883061'  # Reemplaza con el ID del usuario autorizado
    return str(message.from_user.id) == authorized_user_id

# Comando /start
@bot.message_handler(commands=['start'])
def start(message):
    if is_authorized_user(message):
        welcome_message = '''
        <a href='https://api.grouphelp.top/chelp/index.php?f=AgACAgEAAxkBCmfMGGRsVavhZ3TCpnOQDhZm_rlkNOAQAAI2qzEbrIpgR1gCGQxDGEdKAQADAgADeQADLwQ'><b>🤖</b></a>¡Bienvenido al <b>Bot de Publicación</b>!

        <b>Este bot te permite enviar mensajes personalizados a canales registrados. Puedes utilizar los siguientes comandos:</b>
        
        - /post: <code>Envía un mensaje personalizado a todos los canales registrados.</code>

        - /setbutton {texto - enlace}: <code>Agrega un botón al mensaje personalizado.</code>

        - /send: <code>Con este comando podrás enviar el post personalizado preconfigurado que hiciste al principio. (Si le agregas un número al lado, se borrará el post automáticamente después de ese tiempo)</code>
        -- Ejemplo: /send 60s (1 minuto)

        - /add {ID del canal}: <code>Agrega un canal a la lista de canales registrados.</code>

        - /delall: <code>Elimina todos los canales de la lista de canales registrados.</code>

        🤩¡Comienza utilizando /post para crear un mensaje personalizado!😱

        <b>🌐 Powered By @KyleProyectOficial</b>
        '''
        bot.send_message(chat_id=message.chat.id, text=welcome_message, parse_mode='HTML')
    else:
        bot.reply_to(message, "⛔️ No estás autorizado para usar este bot.")

# Comando /post
@bot.message_handler(commands=['post'])
def post_to_channels(message):
    if is_authorized_user(message):
        if len(registered_channels) == 0:
            bot.reply_to(message, "🤷‍♂️ No hay canales registrados.")
            return

        global custom_post_caption, custom_post_photo, custom_post_video
        custom_post_caption = None
        custom_post_photo = None
        custom_post_video = None

        msg = bot.send_message(chat_id=message.chat.id, text="Envía el mensaje personalizado que deseas enviar a los canales registrados:")
        bot.register_next_step_handler(msg, process_custom_post)
    else:
        bot.reply_to(message, "⛔️ No estás autorizado para usar este comando.")

# Procesa el mensaje personalizado y pregunta si se desea agregar una foto o video
def process_custom_post(message):
    global custom_post_caption
    custom_post_caption = message.text

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.KeyboardButton('Agregar Foto'), types.KeyboardButton('Agregar Video'), types.KeyboardButton('No agregar'))
    msg = bot.send_message(chat_id=message.chat.id, text="¿Deseas agregar una foto o video al mensaje personalizado?", reply_markup=keyboard)
    bot.register_next_step_handler(msg, process_custom_post_media)

# Procesa la respuesta sobre agregar una foto o video
def process_custom_post_media(message):
    global custom_post_photo, custom_post_video

    if message.text == 'Agregar Foto':
        msg = bot.send_message(chat_id=message.chat.id, text="Envía la foto que deseas agregar al mensaje personalizado:")
        bot.register_next_step_handler(msg, process_custom_post_photo)
    elif message.text == 'Agregar Video':
        msg = bot.send_message(chat_id=message.chat.id, text="Envía el video que deseas agregar al mensaje personalizado:")
        bot.register_next_step_handler(msg, process_custom_post_video)
    else:
        send_custom_post(message)

# Procesa la foto enviada para el mensaje personalizado
def process_custom_post_photo(message):
    global custom_post_photo

    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        custom_post_photo = bot.get_file(file_id)
        send_custom_post(message)
    else:
        msg = bot.send_message(chat_id=message.chat.id, text="El archivo enviado no es una foto. Intenta nuevamente:")
        bot.register_next_step_handler(msg, process_custom_post_photo)

# Procesa el video enviado para el mensaje personalizado
def process_custom_post_video(message):
    global custom_post_video

    if message.content_type == 'video':
        file_id = message.video.file_id
        custom_post_video = bot.get_file(file_id)
        send_custom_post(message)
    else:
        msg = bot.send_message(chat_id=message.chat.id, text="El archivo enviado no es un video. Intenta nuevamente:")
        bot.register_next_step_handler(msg, process_custom_post_video)

# Envia el mensaje personalizado a todos los canales registrados
def send_custom_post(message):
    global custom_post_caption, custom_post_photo, custom_post_video, post_buttons

    for channel_id in registered_channels:
        chat_id = '@' + channel_id
        try:
            sent_message = None
            if custom_post_photo is not None:
                sent_message = bot.send_photo(chat_id=chat_id, photo=custom_post_photo.file_id, caption=custom_post_caption, reply_markup=post_buttons[-1])
            elif custom_post_video is not None:
                sent_message = bot.send_video(chat_id=chat_id, data=custom_post_video.file_id, caption=custom_post_caption, reply_markup=post_buttons[-1])
            else:
                sent_message = bot.send_message(chat_id=chat_id, text=custom_post_caption, reply_markup=post_buttons[-1])

            if sent_message is not None:
                sent_messages[sent_message.message_id] = chat_id
        except telebot.apihelper.ApiException as e:
            bot.reply_to(message, f"❗️ Error al enviar el mensaje a {chat_id}: {e}")

    custom_post_caption = None
    custom_post_photo = None
    custom_post_video = None
    post_buttons = []
    bot.reply_to(message, f"✅ Mensaje enviado a {len(registered_channels)} canales.")

# Comando /setbutton
@bot.message_handler(commands=['setbutton'])
def set_button(message):
    if is_authorized_user(message):
        if custom_post_caption is None:
            bot.reply_to(message, "❗️ Primero debes enviar un mensaje personalizado usando el comando /post.")
            return

        button_text = re.search(r'(?<=/setbutton\s).*?(?=\s-)', message.text)
        button_link = re.search(r'(?<=-\s).*', message.text)

        if button_text is None or button_link is None:
            bot.reply_to(message, "❗️ El comando /setbutton debe tener el siguiente formato:\n\n/setbutton {texto - enlace}")
            return

        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text=button_text.group(0), url=button_link.group(0))
        keyboard.add(url_button)
        post_buttons.append(keyboard)
        bot.reply_to(message, f"✅ Botón agregado al mensaje personalizado.")

    else:
        bot.reply_to(message, "⛔️ No estás autorizado para usar este comando.")

# Comando /send
@bot.message_handler(commands=['send'])
def send_post(message):
    if is_authorized_user(message):
        if len(registered_channels) == 0:
            bot.reply_to(message, "🤷‍♂️ No hay canales registrados.")
            return

        global custom_post_caption, custom_post_photo, custom_post_video, post_buttons

        if custom_post_caption is None:
            bot.reply_to(message, "❗️ Primero debes enviar un mensaje personalizado usando el comando /post.")
            return

        match = re.search(r'(?<=/send\s).*', message.text)
        if match is not None:
            time_string = match.group(0)
            if re.match(r'^\d+[smhd]$', time_string):
                time_amount = int(time_string[:-1])
                time_unit = time_string[-1]
                time_in_seconds = convert_to_seconds(time_amount, time_unit)
                threading.Timer(time_in_seconds, delete_post, args=(message,)).start()
            else:
                bot.reply_to(message, "❗️ El formato de tiempo debe ser un número seguido de 's' (segundos), 'm' (minutos), 'h' (horas) o 'd' (días).")
                return

        send_custom_post(message)

    else:
        bot.reply_to(message, "⛔️ No estás autorizado para usar este comando.")

# Convierte una cantidad de tiempo en segundos
def convert_to_seconds(amount, unit):
    if unit == 's':
        return amount
    elif unit == 'm':
        return amount * 60
    elif unit == 'h':
        return amount * 60 * 60
    elif unit == 'd':
        return amount * 60 * 60 * 24

# Borra el mensaje enviado por el bot
def delete_post(message):
    chat_id = message.chat.id
    message_id = message.message_id

    if chat_id in sent_messages.values():
        for key, value in sent_messages.items():
            if value == chat_id and key == message_id:
                try:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                    del sent_messages[key]
                    bot.reply_to(message, "✅ El mensaje ha sido eliminado.")
                except telebot.apihelper.ApiException as e:
                    bot.reply_to(message, f"❗️ Error al eliminar el mensaje: {e}")
                break
    else:
        bot.reply_to(message, "⛔️ No se encontró el mensaje en los canales registrados.")

# Comando /add
@bot.message_handler(commands=['add'])
def add_channel(message):
    if is_authorized_user(message):
        channel_id = re.search(r'(?<=/add\s).*', message.text)

        if channel_id is None:
            bot.reply_to(message, "❗️ El comando /add debe tener el siguiente formato:\n\n/add {ID del canal}")
            return

        if channel_id.group(0) not in registered_channels:
            registered_channels.append(channel_id.group(0))
            bot.reply_to(message, f"✅ Canal {channel_id.group(0)} agregado a la lista de canales registrados.")
        else:
            bot.reply_to(message, f"ℹ️ El canal {channel_id.group(0)} ya está en la lista de canales registrados.")

    else:
        bot.reply_to(message, "⛔️ No estás autorizado para usar este comando.")

# Comando /delall
@bot.message_handler(commands=['delall'])
def delete_all_channels(message):
    if is_authorized_user(message):
        global registered_channels
        registered_channels = []
        bot.reply_to(message, "✅ Todos los canales han sido eliminados de la lista de canales registrados.")

    else:
        bot.reply_to(message, "⛔️ No estás autorizado para usar este comando.")

# Manejador de errores
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if is_authorized_user(message):
        bot.reply_to(message, "❗️ Comando no reconocido. Utiliza /start para ver la lista de comandos disponibles.")
    else:
        bot.reply_to(message, "⛔️ No estás autorizado para usar este bot.")

# Función principal para ejecutar el bot
def main():
    bot.polling()

if __name__ == '__main__':
    main()