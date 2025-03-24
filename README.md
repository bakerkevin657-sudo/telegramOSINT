# 🌐 Telegram OSINT 🚀

**TelegramOSINTT** es un script diseñado para interactuar con la API de Telegram utilizando **Telethon**. 
Este script permite realizar tareas relacionadas con **Open-Source Intelligence (OSINT)**, 
como buscar usuarios, obtener historiales de mensajes, monitorear palabras clave y generar estadísticas.

## funcionalidades
1. 🔍 **Buscar Usuarios**: Encuentra usuarios por nombre, ID o username.
2. 💬 **Obtener Historial de Mensajes**: Descarga los mensajes de un grupo o canal de Telegram 
   y genera estadísticas de los 10 usuarios más activos.
3. 🆔 **Obtener el ID de un Grupo**: Identifica el ID único de cualquier grupo o canal.
4. 🗣️ **Monitorear Palabras Clave**: Escanea todos los mensajes de tus grupos o canales para 
   encontrar coincidencias con palabras clave y genera estadísticas de los 10 grupos con más menciones.

## 📦 instalación Kali Linux

### **Paso 1:**
# Clona este repositorio 
```bash
git clone https://github.com/Ivancastl/contacts.git
```

### **Paso 2:**
# Accede al directorio del proyecto.
```bash
cd generador_contactos
```

### **Paso 3:**
# Instala las dependencias necesarias.
```bash
pip install -r requirements.txt
```

### **Paso 4:**
# Ejecuta el script principal
```bash
python generar_contacts_csv.py
```

El script te pedirá que ingreses:

- **Cómo quieres llamar a los contactos** (Ejemplo: Persona, Usuario, Contacto).
- **Cuántos números deseas generar** (Ejemplo: 10).
- **Cuál es la lada de la región** (Ejemplo: 777 para Ciudad de México).
- **Si quieres poner 3 números fijos y el resto aleatorios** (Responde "sí" o "no").

El archivo CSV con los contactos generados se guardará en el directorio del proyecto con el nombre **\`datos_personalizados.csv\`**.






