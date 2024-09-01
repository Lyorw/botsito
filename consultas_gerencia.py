import pymssql

def obtener_conexion():
    server = 'chatwsp.database.windows.net'
    database = 'chatbot'
    username = 'wspbot'
    password = 'B@t264as'

    try:
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        return conn
    except pymssql.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None

def obtener_nombres_gerencia():
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = "SELECT nombre FROM Gerencia"
        cursor.execute(query)
        nombres = [row[0] for row in cursor.fetchall()]
        conn.close()
        return nombres
    else:
        return []
