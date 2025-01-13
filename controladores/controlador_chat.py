from bd import obtener_conexion

def lista_mensajes_chat(idE,idD):
    conexion = obtener_conexion()
    mensajes = []
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT id, texto,DATE_FORMAT(fechaEnvio, '%Y-%m-%d') AS fechaEnvio, DATE_FORMAT(hora, '%H:%i:%s')"
                                " AS hora,estado, idEstudiante, idDocente, emisor FROM mensajes WHERE"
                                f" idEstudiante={idE} and idDocente={idD} order by id asc")
        mensajes=cursor.fetchall()
    conexion.close()
    return mensajes

def procesar_form_chat(mensaje, idE, idD,emisor):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        # Inserta el mensaje en la base de datos
        cursor.execute("INSERT INTO mensajes (texto, estado, idEstudiante, idDocente, emisor) VALUES (%s, %s, %s, %s,%s)",
                       (mensaje, '0', idE, idD,emisor))
        conexion.commit()
        # Obtiene el mensaje recién insertado
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_mensaje = cursor.fetchone()[0]
        cursor.execute("SELECT id, texto,DATE_FORMAT(fechaEnvio, '%%Y-%%m-%%d') AS fechaEnvio, DATE_FORMAT(hora, '%%H:%%i:%%s')" 
                       " AS hora,estado, idEstudiante, idDocente, emisor FROM mensajes WHERE id = %s", (id_mensaje,))
        mensaje_insertado = cursor.fetchone()
    conexion.close()
    return mensaje_insertado


def obtener_docentes(user):
    conexion = obtener_conexion()
    docente = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT d.*, m.id AS mensaje_id, m.estado,m.emisor, m.idEstudiante "
                        "FROM docente d LEFT JOIN (SELECT id, estado,emisor, idDocente, idEstudiante FROM mensajes "
                        f"WHERE idEstudiante = {user} AND id IN (SELECT MAX(id) FROM mensajes WHERE idEstudiante = {user} GROUP BY idDocente)) "
                        "m ON m.idDocente = d.id ORDER BY m.id DESC;")
        docente = cursor.fetchall()
    conexion.close()
    return docente

def obtener_estudiantes(user):
    conexion = obtener_conexion()
    docente = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT d.*, m.id AS mensaje_id, m.estado,m.emisor, m.idDocente "
                        "FROM estudiante d LEFT JOIN (SELECT id, estado,emisor, idDocente, idEstudiante FROM mensajes "
                        f"WHERE idDocente = {user} AND id IN (SELECT MAX(id) FROM mensajes WHERE idDocente = {user} GROUP BY idEstudiante)) "
                        "m ON m.idEstudiante = d.id ORDER BY m.id DESC;")
        docente = cursor.fetchall()
    conexion.close()
    return docente

def actualizar_visto(idE,idD,nombre):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"update mensajes set estado='1' where idEstudiante={idE} and idDocente={idD} and emisor!='{nombre}'")
    conexion.commit()
    conexion.close()

def buscar_mensajes(buscar,id,user):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"select estado from mensajes where estado='0' and {buscar}={id} and emisor!='{user}'")
        valor = cursor.fetchone()
    conexion.close()
    return valor