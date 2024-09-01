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

def obtener_canales_por_gerencia(gerencia_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = "SELECT nombre FROM CanalDeVenta WHERE gerencia_id = %s"
        cursor.execute(query, (gerencia_id,))
        canales = [row[0] for row in cursor.fetchall()]
        conn.close()
        return canales
    else:
        return []

def obtener_tipos_de_falla(canal_de_venta_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = "SELECT nombre FROM TipoDeFalla WHERE canal_de_venta_id = %s"
        cursor.execute(query, (canal_de_venta_id,))
        tipos_falla = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tipos_falla
    else:
        return []

def obtener_aplicaciones(tipo_de_falla_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = "SELECT nombre FROM Aplicacion WHERE tipo_de_falla_id = %s"
        cursor.execute(query, (tipo_de_falla_id,))
        aplicaciones = [row[0] for row in cursor.fetchall()]
        conn.close()
        return aplicaciones
    else:
        return []
