from bd import obtener_conexion

def obtener_plans(escuela, buscar):
    conexion = obtener_conexion()
    resultado = []
    with conexion.cursor() as cursor:
        if escuela == '0' and buscar == '0':
            cursor.execute("SELECT es.*, fac.nomEscuela FROM planestudio  es INNER JOIN escuelaprofesional fac ON es.codEscPlan  = fac.id ORDER BY es.nomPlan")
        elif escuela != '0':
            cursor.execute("SELECT es.*, fac.nomEscuela FROM planestudio  es INNER JOIN escuelaprofesional fac ON es.codEscPlan  = fac.id WHERE fac.nomEscuela = %s ORDER BY es.nomPlan", (escuela))
        else:
            cursor.execute("SELECT es.*, fac.nomEscuela FROM planestudio  es INNER JOIN escuelaprofesional fac ON es.codEscPlan  = fac.id WHERE LOWER(es.nomPlan) LIKE LOWER(("%{buscar}%")) ORDER BY es.nomPlan")  
        resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_id(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select id from planestudio where id = %s",(id,))
        plan = cursor.fetchone()
    conexion.close()
    return plan


def obtener_plan(codEP):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select * from planestudio where codEscPlan = %s",(codEP,))
        plan = cursor.fetchone()
    conexion.close()
    return plan

def agregar_plan(nomP, creP, estP, codEP):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO planestudio (nomPlan, crePlan, estPlan, codEscPlan) "
            "VALUES (%s, %s, %s, %s)",
            (nomP, creP, estP, codEP)
        )
    id_generado = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado

def modificarEstPlan(estado,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update planestudio set estPlan = %s where id = %s",(estado,id))
    conexion.commit()
    conexion.close()

def actualizarPlan(id, nom, cre, est, escu):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE planestudio SET nomPlan = %s, crePlan = %s, estPlan = %s, codEscPlan = %s WHERE id = %s",
            (nom, cre, est, escu, id)
        )
    conexion.commit()
    conexion.close()

def eliminarPlan(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("delete from planestudio where id = %s",(id,))
    conexion.commit()
    conexion.close()
