import pymssql

# Función para obtener la conexión a la base de datos
def obtener_conexion():
    server = 'chatwsp.database.windows.net'  # Nombre del servidor SQL
    database = 'chatbot'         # Nombre de la base de datos
    username = 'wspbot'      # Tu nombre de usuario de SQL Server
    password = 'B@t264as'   # Tu contraseña de SQL Server

    try:
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        return conn
    except pymssql.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None

# Función para obtener el mensaje desde la tabla Preguntas basado en el ID
def obtener_mensaje_por_id(id):
    conn = obtener_conexion()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT formulario FROM Preguntas WHERE ID = %s", (id,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
        else:
            return None
    except pymssql.Error as e:
        print("Error al ejecutar la consulta:", e)
        return None
    finally:
        conn.close()

# Función para obtener las alternativas desde la tabla alternativas_preguntas basado en el ID de la pregunta
def obtener_alternativas_por_id_pregunta(id_pregunta):
    conn = obtener_conexion()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT alternativas FROM alternativas_preguntas WHERE ID_pregunta = %s", (id_pregunta,))
        rows = cursor.fetchall()
        
        if rows:
            return [row[0] for row in rows]  # Devuelve una lista de alternativas
        else:
            return []
    except pymssql.Error as e:
        print("Error al ejecutar la consulta:", e)
        return []
    finally:
        conn.close()
