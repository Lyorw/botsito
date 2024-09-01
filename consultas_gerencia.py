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

def obtener_aplicaciones_por_falla(canal_de_venta_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = "SELECT nombre FROM Aplicacion WHERE canal_de_venta_id = %s"
        cursor.execute(query, (canal_de_venta_id,))
        aplicaciones = [row[0] for row in cursor.fetchall()]
        conn.close()
        return aplicaciones
    else:
        return []

def obtener_torre_por_aplicacion(aplicacion_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT TorreDeApp.nombre 
            FROM TorreDeApp 
            INNER JOIN Aplicacion ON TorreDeApp.id = Aplicacion.aplicacion_id
            WHERE Aplicacion.id = %s
        """
        cursor.execute(query, (aplicacion_id,))
        torre = cursor.fetchone()
        conn.close()
        if torre:
            return torre[0]
        else:
            return "No se encontró la torre asociada"
    else:
        return "Error de conexión"

def obtener_fallas_por_torre(aplicacion_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT Falla.nombre 
            FROM Falla
            INNER JOIN Aplicacion ON Falla.aplicacion_id = Aplicacion.id
            WHERE Aplicacion.id = %s
        """
        cursor.execute(query, (aplicacion_id,))
        fallas = [row[0] for row in cursor.fetchall()]
        conn.close()
        return fallas
    else:
        return []
