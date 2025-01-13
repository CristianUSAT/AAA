import pymysql
from pymysql import err
from bd import obtener_conexion


def verificar_usuario(user,contra):
    conexion = obtener_conexion()
    usuario = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from docente where corDocente= %s and passDocente = %s",(user,contra))
        usuario=cursor.fetchone()
    conexion.close()
    return usuario

def actualizar_token(user,token):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update docente set token = %s where corDocente = %s ",(token,user))
    conexion.commit()
    conexion.close()

def obtener_docente(user):
    conexion = obtener_conexion()
    docente = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from docente where corDocente = %s ",(user,))
        docente = cursor.fetchone()
    conexion.close()
    return docente

def obtener_semestres():
    conexion=obtener_conexion()
    semestre = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from semestreacademico")
    semestre = cursor.fetchall()
    conexion.close()
    return semestre

def obtener_docentes():
    conexion=obtener_conexion()
    docentes = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from docente")
    docentes = cursor.fetchall()
    conexion.close()
    return docentes

def obtener_docentes2(buscar):
    conexion = obtener_conexion()
    docentes = []
    with conexion.cursor() as cursor:
        if buscar == '0':
            cursor.execute("select * from docente order by apeNomDocente")
        else:
            cursor.execute("select * from docente where lower(apeNomDocente) like lower(%s) order by apeNomDocente", (f'%{buscar}%',))
        docentes = cursor.fetchall()
        
    conexion.close()
    return docentes



def obtener_docente_por_id(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM Docente WHERE id = %s", (id,))
        docente = cursor.fetchone()
    conexion.close()
    return docente


def agregar_docente(apeNomDocente, dniDocente, corDocente, estDocente, passDocente):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Docente (apeNomDocente, dniDocente, corDocente, estDocente, passDocente) "
                "VALUES (%s, %s, %s, %s, %s)",
                (apeNomDocente, dniDocente, corDocente, estDocente, passDocente)
            )
        id_generado = cursor.lastrowid
        conexion.commit()
        return id_generado
    except pymysql.MySQLError as e:
        if e.args[0] == 1062:  # Código de error para entrada duplicada
            raise ValueError("duplicate_entry", e.args[1])
        else:
            raise
    finally:
        conexion.close()


def actualizar_docente(id, apeNomDocente, dniDocente, corDocente, estDocente, passDocente):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "UPDATE Docente SET apeNomDocente = %s, dniDocente = %s, corDocente = %s, estDocente = %s, passDocente = %s "
                "WHERE id = %s",
                (apeNomDocente, dniDocente, corDocente, estDocente, passDocente, id)
            )
        conexion.commit()
    except pymysql.MySQLError as e:
        if e.args[0] == 1062:  # Código de error para entrada duplicada
            raise ValueError("duplicate_entry", e.args[1])
        else:
            raise
    finally:
        conexion.close()

def modificarEstDocente(estado,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update docente set estDocente = %s where id = %s",(estado,id))
    conexion.commit()
    conexion.close()

def eliminar_docente(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM Docente WHERE id = %s", (id,))
    conexion.commit()
    conexion.close()
