from app.config.database import engine

try:
    # Probar conexión
    connection = engine.connect()
    print("Conexión a la base de datos establecida correctamente")
    connection.close()
except Exception as e:
    print(" ERROR: No conectando a la base de datos:", e)
