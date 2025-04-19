import os
import json
import pyfiglet
from telethon import TelegramClient, functions
from telethon.tl.types import User
import asyncio
from collections import Counter
import requests
from cryptography.fernet import Fernet

class TelegramOSINT:
    def __init__(self):
        self.config_file = "telegram_osint_config.enc"
        self.key_file = "telegram_osint_key.key"
        self.api_id = None
        self.api_hash = None
        self.load_or_request_credentials()
        self.show_banner()

    def show_banner(self):
        """Muestra el banner ASCII art"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(pyfiglet.figlet_format("Telegram Scout", font="slant"))
        print("🕵️ Herramienta de análisis para Telegram")
        print("👤 Creado por @ivancastl")
        print("🌐 Grupo: t.me/+_g4DIczsuI9hOWZh")
        print("="*60 + "\n")

    def get_encryption_key(self):
        """Genera o recupera la clave de encriptación"""
        if not os.path.exists(self.key_file):
            with open(self.key_file, "wb") as f:
                f.write(Fernet.generate_key())
        with open(self.key_file, "rb") as f:
            return f.read()

    def load_or_request_credentials(self):
        """Carga o solicita las credenciales"""
        if os.path.exists(self.config_file):
            try:
                cipher_suite = Fernet(self.get_encryption_key())
                with open(self.config_file, "rb") as f:
                    encrypted_data = f.read()
                creds = json.loads(cipher_suite.decrypt(encrypted_data).decode())
                self.api_id = creds.get('api_id')
                self.api_hash = creds.get('api_hash')
            except Exception as e:
                print(f"⚠️ Error cargando credenciales: {e}")
                self.request_and_save_credentials()
        else:
            self.request_and_save_credentials()

    def request_and_save_credentials(self):
        """Solicita y guarda las credenciales de forma segura"""
        self.show_banner()
        print("🔑 Configuración de credenciales\n")
        
        self.api_id = input("Introduce tu api_id: ").strip()
        self.api_hash = input("Introduce tu api_hash: ").strip()

        try:
            cipher_suite = Fernet(self.get_encryption_key())
            encrypted_data = cipher_suite.encrypt(json.dumps({
                'api_id': self.api_id,
                'api_hash': self.api_hash
            }).encode())
            with open(self.config_file, "wb") as f:
                f.write(encrypted_data)
            print("\n🛡️ Credenciales guardadas de forma segura")
        except Exception as e:
            print(f"\n🔴 Error guardando credenciales: {e}")
        input("\nPresiona Enter para continuar...")

    async def buscar_usuarios(self, client, query):
        """Busca usuarios en Telegram"""
        try:
            result = await client(functions.contacts.SearchRequest(
                q=query,
                limit=50
            ))
            
            if result.users:
                print(f"\n📡 Se encontraron {len(result.users)} coincidencias:")
                for user in result.users:
                    print(f"\n📄 ID: {user.id}")
                    print(f"👤 Username: @{user.username}" if user.username else "👤 Username: [Ninguno]")
                    print(f"📛 Nombre: {user.first_name or ''} {user.last_name or ''}")
                    print(f"📱 Teléfono: {user.phone or '[Oculto]'}")
                    print("-"*40)
            else:
                print(f"\n🤔 No se encontraron coincidencias para '{query}'")
        except Exception as e:
            print(f"\n🔴 Error buscando usuarios: {e}")

    async def obtener_historial_grupo(self, client):
        """Obtiene el historial de mensajes de un grupo"""
        group_link = input("🔗 Introduce el enlace del grupo: ").strip()
        
        try:
            group = await client.get_entity(group_link)
            file_path = "historial_grupo.txt"
            
            if os.path.exists(file_path):
                file_path = file_path.replace(".txt", "_new.txt")

            user_counter = Counter()
            
            with open(file_path, "w", encoding="utf-8") as file:
                print(f"\n⏳ Obteniendo mensajes de {group.title}...")
                
                async for message in client.iter_messages(group):
                    sender = await message.get_sender()
                    username = sender.username if isinstance(sender, User) and sender.username else "[Sin username]"
                    is_bot = "Sí" if isinstance(sender, User) and sender.bot else "No"
                    
                    if isinstance(sender, User):
                        user_counter[sender.id] += 1

                    file.write(f"\nID: {message.id}")
                    file.write(f"\nFecha: {message.date}")
                    file.write(f"\nDe: {message.sender_id} (@{username})")
                    file.write(f"\nEs Bot: {is_bot}")
                    file.write(f"\nMensaje: {message.text or '[Sin texto]'}")
                    file.write("\n" + "-"*40 + "\n")

                # Estadísticas
                file.write("\nTOP 10 USUARIOS MÁS ACTIVOS:\n")
                for user_id, count in user_counter.most_common(10):
                    file.write(f"ID {user_id}: {count} mensajes\n")
            
            print(f"\n📁 Historial guardado en {file_path}")
            print(f"📊 Total mensajes procesados: {sum(user_counter.values())}")
            
        except Exception as e:
            print(f"\n🔴 Error obteniendo mensajes: {e}")

    async def obtener_id_grupo(self, client):
        """Obtiene el ID de un grupo o canal"""
        group_username = input("🔗 Introduce el username o enlace del grupo: ").strip()
        
        try:
            group = await client.get_entity(group_username)
            print(f"\n📄 ID del grupo/canal: {group.id}")
            print(f"📛 Nombre: {group.title}")
        except Exception as e:
            print(f"\n🔴 Error obteniendo ID: {e}")

    async def buscar_palabra_clave(self, client):
        """Busca una palabra clave en todos los grupos"""
        keyword = input("🕵️ Introduce la palabra clave: ").strip()
        contador = 0
        group_counter = Counter()
        file_path = "resultados_busqueda.txt"
        
        if os.path.exists(file_path):
            file_path = file_path.replace(".txt", "_new.txt")

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"RESULTADOS PARA: '{keyword}'\n\n")
            
            try:
                print(f"\n🕵️ Buscando '{keyword}' en todos los grupos...")
                
                async for dialog in client.iter_dialogs():
                    if dialog.is_group or dialog.is_channel:
                        print(f"💬 Escaneando {dialog.name}...")
                        
                        async for message in client.iter_messages(dialog, search=keyword):
                            file.write(f"\n[Grupo] {dialog.name} (ID: {dialog.id})")
                            file.write(f"\n[Fecha] {message.date}")
                            file.write(f"\n[Usuario] {message.sender_id}")
                            file.write(f"\n[Mensaje] {message.text or '[Sin texto]'}")
                            file.write("\n" + "-"*40 + "\n")
                            group_counter[dialog.id] += 1
                            contador += 1

            except Exception as e:
                print(f"\n🔴 Error en búsqueda: {e}")

            finally:
                file.write("\nESTADÍSTICAS:\n")
                for group_id, count in group_counter.most_common(10):
                    group = await client.get_entity(group_id)
                    file.write(f"{group.title}: {count} menciones\n")
                
                print(f"\n🏁 Se encontraron {contador} mensajes con '{keyword}'")
                print(f"📄 Resultados guardados en {file_path}")

    async def run(self):
        """Ejecuta la aplicación principal"""
        client = TelegramClient("telegram_scout_session", self.api_id, self.api_hash)
        await client.start()
        
        while True:
            self.show_banner()
            print("⚙️ Menú Principal")
            print("1 📡 Buscar usuarios")
            print("2 📥 Obtener historial de grupo")
            print("3 📄 Obtener ID de grupo")
            print("4 🕵️ Buscar por palabra clave")
            print("5 🚪 Salir\n")
            
            choice = input("🚩 Selecciona una opción: ").strip()
            
            if choice == "1":
                query = input("📡 Término de búsqueda: ")
                await self.buscar_usuarios(client, query)
            elif choice == "2":
                await self.obtener_historial_grupo(client)
            elif choice == "3":
                await self.obtener_id_grupo(client)
            elif choice == "4":
                await self.buscar_palabra_clave(client)
            elif choice == "5":
                print("\n👋 ¡Hasta pronto!")
                break
            else:
                print("\n⚠️ Opción no válida")
            
            input("\nPresiona Enter para continuar...")
        
        await client.disconnect()

if __name__ == "__main__":
    try:
        osint_tool = TelegramOSINT()
        asyncio.run(osint_tool.run())
    except KeyboardInterrupt:
        print("\n🛑 Programa interrumpido")
    except Exception as e:
        print(f"\n🔴 Error crítico: {e}")