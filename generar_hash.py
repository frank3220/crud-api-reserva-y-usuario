from getpass import getpass
import sys

from passlib.hash import argon2


try:
    password = getpass("Contrasena a hashear: ")
    if not password:
        raise ValueError("La contrasena no puede estar vacia.")

    correct_hash = argon2.hash(password)

    print("--- HASH GENERADO ---")
    print(f"Hash correcto para la base de datos: {correct_hash}")
    print("---------------------")
    print("No guardes ni pegues contrasenas en texto plano.")

except Exception:
    print("ERROR: no se pudo generar el hash. Verifica passlib[argon2] y la entrada.")
    sys.exit(1)
