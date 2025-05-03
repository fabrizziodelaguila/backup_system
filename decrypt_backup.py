import os
from cryptography.fernet import Fernet

# Rutas
KEY_PATH = 'secret.key'
ENCRYPTED_DIR = 'backups'
DECRYPTED_DIR = 'decrypted'

def load_key():
    with open(KEY_PATH, 'rb') as key_file:
        return key_file.read()

def decrypt_file(input_path, output_path, fernet):
    with open(input_path, 'rb') as enc_file:
        encrypted_data = enc_file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(output_path, 'wb') as dec_file:
        dec_file.write(decrypted_data)

def decrypt_all():
    # Validaciones iniciales
    if not os.path.exists(KEY_PATH):
        print(f"❌ No se encontró el archivo de clave: {KEY_PATH}")
        return
    if not os.path.exists(ENCRYPTED_DIR):
        print(f"❌ No se encontró el directorio: {ENCRYPTED_DIR}")
        return

    os.makedirs(DECRYPTED_DIR, exist_ok=True)

    key = load_key()
    fernet = Fernet(key)

    files = [f for f in os.listdir(ENCRYPTED_DIR) if f.endswith('.json')]
    if not files:
        print("⚠ No se encontraron archivos .json.enc para desencriptar.")
        return

    for file in files:
        input_path = os.path.join(ENCRYPTED_DIR, file)
        output_filename = file.replace('.json', '.json')
        output_path = os.path.join(DECRYPTED_DIR, output_filename)

        try:
            decrypt_file(input_path, output_path, fernet)
            print(f"✔ {file} → {output_filename}")
        except Exception as e:
            print(f"❌ Error al desencriptar {file}: {e}")

if __name__ == '__main__':
    decrypt_all()
