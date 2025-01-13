from bd import obtener_conexion

def obtener_semestres(buscar):
    conexion = obtener_conexion()
    escuela = []
    with conexion.cursor() as cursor:
        if buscar == '0':
            cursor.execute("SELECT * from semestreacademico")
        else:
            cursor.execute(f"select * from semestreacademico where nomSemestre like '%{buscar}%'")
        escuela = cursor.fetchall()
    conexion.close()
    return escuela

def modificarEstSemestre(estado,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update semestreacademico set estSemestre = %s where id = %s",(estado,id))
    conexion.commit()
    conexion.close()

def modificarSemestre(nomSemestre,iniSemestre,finSemestre,estSemestre,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update semestreacademico set nomSemestre=%s, iniSemestre=%s,finSemestre=%s,estSemestre=%s where id=%s",
                       (nomSemestre,iniSemestre,finSemestre,estSemestre,id))
    conexion.commit()
    conexion.close()

def agregarSemestre(nomSemestre,iniSemestre,finSemestre,estSemestre):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("insert into semestreacademico(nomSemestre,iniSemestre,finSemestre,estSemestre) values (%s,%s,%s,%s)",
                       (nomSemestre,iniSemestre,finSemestre,estSemestre))
    conexion.commit()
    conexion.close()

def eliminarSemestre(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("delete from semestreacademico where id = %s",(id,))
        
    conexion.commit()
    conexion.close()