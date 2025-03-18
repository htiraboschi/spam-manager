import imaplib
import email
from email.header import decode_header
import json
import sys

# Lectura de configuraciones
# Ruta al archivo JSON
config_file = 'config.json'

try:
    with open(config_file,'r') as file:
        config_data = json.load(file)
except FileNotFoundError:
    print(f"Error: El archivo {config_file} no existe.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: El archivo {config_file} no es un JSON válido.")
    sys.exit(1)
except Exception as e:
    print(f"Error inesperado: {e}")
    sys.exit(1)

# Configuración de la conexión
EMAIL = config_data["conection"]["EMAIL"]  # Tu dirección de correo
PASSWORD = config_data["conection"]["PASSWORD"]     # Tu contraseña o contraseña de aplicación
IMAP_SERVER = config_data["conection"]["IMAP_SERVER"]  # Servidor IMAP

#carpeta de eliminados de spam
ELIMINADOSSPAM = 'Papelera'
# Conectarse al servidor IMAP
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, PASSWORD)

# Seleccionar la carpeta de spam
mail.select('"[Gmail]/Spam"')  # Para Gmail. En Outlook, usa 'Spam'.

# Buscar correos en spam
status, messages = mail.search(None, 'ALL')  # Busca todos los correos
messages = messages[0].split()  # Obtener los IDs de los correos

# Función para mover correos
def mover_correo(correo_id, carpeta_destino):
    # Copiar el correo a la carpeta destino
    mail.copy(correo_id, carpeta_destino)
    # Marcar el correo original para eliminarlo
    mail.store(correo_id, '+FLAGS', '\\Deleted')
    print(f"Correo {correo_id} movido a {carpeta_destino}.")

# Reglas personalizadas (puedes modificarlas según tus necesidades)
def aplicar_reglas(asunto, remitente):
    if "Oferta especial" in asunto:  # Ejemplo: Mover correos con "Oferta especial" en el asunto
        return "INBOX"  # Mover a la bandeja de entrada
    elif "info@montillarealtyteam.com" in remitente.lower():  # Ejemplo: Mover newsletters a una carpeta específica
        return ELIMINADOSSPAM
    return None  # No mover el correo

# Procesar cada correo
for correo_id in messages:
    # Obtener el correo
    status, msg_data = mail.fetch(correo_id, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    # Obtener asunto y remitente
    asunto = decode_header(msg["Subject"])[0][0]
    if isinstance(asunto, bytes):
        asunto = asunto.decode()
    remitente = msg["From"]

    # Aplicar reglas
    carpeta_destino = aplicar_reglas(asunto, remitente)
    if carpeta_destino:
        mover_correo(correo_id, carpeta_destino)

# Eliminar correos marcados como eliminados
mail.expunge()
# Cerrar la conexión
mail.logout()