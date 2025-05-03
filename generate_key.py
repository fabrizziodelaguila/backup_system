from cryptography.fernet import Fernet

# Generar una clave
key = Fernet.generate_key()

# Guardarla en un archivo llamado 'secret.key'
with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("Clave generada y guardada en 'secret.key'")