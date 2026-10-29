import bcrypt
import getpass

for usuario in ["editor", "visualizador"]:
    print(f"\nContraseña para {usuario}:")
    clave = getpass.getpass("Escribe la contraseña: ")

    hash_clave = bcrypt.hashpw(
        clave.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    print(f"Hash de {usuario}:")
    print(hash_clave)