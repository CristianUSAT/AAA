from bd import obtener_conexion

def obtener_facultades(buscar):
    conexion = obtener_conexion()
    facultad=[]
    with conexion.cursor() as cursor:
        if buscar =='0' :
            cursor.execute("select * from facultad order by nomFacultad")
        else:
            cursor.execute(f"select * from facultad where lower(nomFacultad) like lower('%{buscar}%') order by nomFacultad")
        facultad = cursor.fetchall()
    conexion.close()
    return facultad


def obtener_id(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select id from facultad where id = %s",(id,))
        facultad = cursor.fetchone()
    conexion.close()
    return facultad

def obtener_facultad(nomEsc):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select * from facultad where nomFacultad = %s",(nomEsc,))
        facultad = cursor.fetchone()
    conexion.close()
    return facultad

def agregar_facultad(nom, estado):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO  facultad(nomFacultad, estFacultad)"
            "VALUES (%s, %s)",
            (nom,estado)
        )
    id_generado = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado

def modificarEstFacultad(estado,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update facultad set estFacultad = %s where id = %s",(estado,id))
    conexion.commit()
    conexion.close()

def actualizarFacultad(nom, est, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE facultad SET nomFacultad = %s, estFacultad = %s WHERE id = %s",
            (nom, est, id)
        )
    conexion.commit()
    conexion.close()

def eliminarFacultad(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("delete from facultad where id = %s",(id,))
    conexion.commit()
    conexion.close()
