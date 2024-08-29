import pymssql

# Configurar los parámetros de la conexión
server = 'chatwsp.database.windows.net'  # Nombre del servidor SQL
database = 'chatbot'         # Nombre de la base de datos
username = 'wspbot'      # Tu nombre de usuario de SQL Server
password = 'B@t264as'   # Tu contraseña de SQL Server

# Establecer la conexión
try:
    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    print("Conexión exitosa")

    # Crear un cursor para ejecutar consultas
    cursor = conn.cursor()

    # Ejemplo de consulta
    cursor.execute("SELECT @@VERSION;")
    row = cursor.fetchone()
    print(f"Versión de SQL Server: {row[0]}")

except pymssql.Error as e:
    print("Error al conectar a la base de datos:", e)

finally:
    # Cerrar la conexión
    if 'conn' in locals() and conn:
        conn.close()
        print("Conexión cerrada")
