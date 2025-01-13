from bd import obtener_conexion

def obtener_escuelas(facultad, buscar):
    conexion = obtener_conexion()
    escuela = []
    with conexion.cursor() as cursor:
        if facultad == '0' and buscar == '0':
            cursor.execute("SELECT es.*, fac.nomFacultad FROM escuelaprofesional es INNER JOIN facultad fac ON es.codFacEscuela = fac.id ORDER BY es.nomEscuela")
        elif facultad !='0':
            cursor.execute("SELECT es.*, fac.nomFacultad FROM escuelaprofesional es INNER JOIN facultad fac ON es.codFacEscuela = fac.id where fac.nomFacultad=%s ORDER BY es.nomEscuela",(facultad))
        else:
            cursor.execute(f"SELECT es.*, fac.nomFacultad FROM escuelaprofesional es INNER JOIN facultad fac ON es.codFacEscuela = fac.id WHERE LOWER(es.nomEscuela) LIKE LOWER('%{buscar}%') ORDER BY es.nomEscuela")
        escuela = cursor.fetchall()
    conexion.close()
    return escuela

def obtener_escuelasa(buscar):
    conexion = obtener_conexion()
    escuela=[]
    with conexion.cursor() as cursor:
        if buscar =='0' :
            cursor.execute("select * from escuelaprofesional order by nomEscuela")
        else:
            cursor.execute(f"select * from escuelaprofesional where  lower(nomEscuela) like lower('%{buscar}%') order by nomEscuela")
        escuela = cursor.fetchall()
    conexion.close()
    return escuela

def obtener_id(id):
    conexion = obtener_conexion()
    escuela = []
    with conexion.cursor() as cursor:
        cursor.execute("select id from escuelaprofesional where id = %s",(id,))
        escuela = cursor.fetchone()
    conexion.close()
    return escuela

def obtener_escuela(nomEsc):
    conexion = obtener_conexion()
    escuela = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from escuelaprofesional where nomEscuela = %s",(nomEsc,))
        escuela = cursor.fetchone()
    conexion.close()
    return escuela

def agregar_escuela(nom, estado, facultad):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO  escuelaprofesional(nomEscuela, estEscuela, codFacEscuela)"
            "VALUES (%s, %s, %s)",
            (nom,estado, facultad)
        )
    id_generado = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado

def modificarEstEscuela(estado,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update escuelaprofesional set estEscuela = %s where id = %s",(estado,id))
    conexion.commit()
    conexion.close()

    
def modificarEscuela(id, nomEscuela, estEscuela, codFacEscuela):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE escuelaprofesional SET nomEscuela = %s, estEscuela = %s, codFacEscuela = %s WHERE id = %s",
            (nomEscuela, estEscuela, codFacEscuela, id)
        )
    conexion.commit()
    conexion.close()


def eliminarEscuela(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("delete from escuelaprofesional where id = %s",(id,))
    conexion.commit()
    conexion.close()

