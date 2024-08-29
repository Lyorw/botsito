import pymssql

def obtener_mensaje_por_id(id):
    # Configurar los parámetros de la conexión
    server = 'chatwsp.database.windows.net'  # Nombre del servidor SQL
    database = 'chatbot'         # Nombre de la base de datos
    username = 'wspbot'      # Tu nombre de usuario de SQL Server
    password = 'B@t264as'   # Tu contraseña de SQL Server

    # Establecer la conexión
    try:
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        cursor = conn.cursor()

        # Consulta para obtener el mensaje por ID
        cursor.execute("SELECT formulario FROM Preguntas WHERE ID = %s", (id,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
        else:
            return None

    except pymssql.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None

    finally:
        if 'conn' in locals() and conn:
            conn.close()
