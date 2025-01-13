from bd import obtener_conexion

def obtener_lineas(escuela, buscar):
    conexion = obtener_conexion()
    resultado = []
    with conexion.cursor() as cursor:
        if escuela == '0' and buscar == '0':
            cursor.execute("SELECT es.*, fac.nomEscuela FROM lineadesarrollo es INNER JOIN escuelaprofesional fac ON es.codEscArea = fac.id ORDER BY es.nomArea")
        elif escuela != '0':
            cursor.execute("SELECT es.*, fac.nomEscuela FROM lineadesarrollo es INNER JOIN escuelaprofesional fac ON es.codEscArea = fac.id WHERE fac.nomEscuela = %s ORDER BY es.nomArea", (escuela))
        else:
            cursor.execute("""
                SELECT es.*, fac.nomEscuela 
                FROM lineadesarrollo es 
                INNER JOIN escuelaprofesional fac 
                ON es.codEscArea = fac.id 
                WHERE LOWER(es.nomArea) LIKE LOWER(%s) 
                ORDER BY es.nomArea
            """, (f"%{buscar}%",)) 
        resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_id(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select id from lineadesarrollo where id = %s",(id,))
        linea = cursor.fetchone()
    conexion.close()
    return linea


def obtener_linea(codEscA):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select * from lineadesarrollo where nomArea = %s",(codEscA,))
        linea = cursor.fetchone()
    conexion.close()
    return linea

def agregar_linea(nomA, estA, codEA):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO lineadesarrollo (nomArea, estArea, codEscArea) "
            "VALUES (%s, %s, %s)",
            (nomA, estA, codEA)
        )
    id_generado = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado

def modificarEstLinea(estado,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update lineadesarrollo set estArea = %s where id = %s",(estado,id))
    conexion.commit()
    conexion.close()

def actualizarLinea(id, nom, est, escu):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE lineadesarrollo SET nomArea = %s, estArea = %s, codEscArea = %s WHERE id = %s",
            (nom, est, escu, id)
        )
    conexion.commit()
    conexion.close()

def eliminarLinea(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("delete from lineadesarrollo where id = %s",(id,))
    conexion.commit()
    conexion.close()


def reporteCantidadPorLinea():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    sa.nomSemestre AS sem_aca_nombre,
                    ld.nomArea AS lin_des_descripcion,
                    COUNT(p.id) AS cantidad,
                    COALESCE(p.estPPP, 'N/A') AS ppp_estadovigencia
                FROM 
                    PPP p
                INNER JOIN 
                    SemestreAcademico sa ON p.codSemIniPPP = sa.id
                INNER JOIN 
                    LineaDesarrollo ld ON p.codLinPPP = ld.id
                GROUP BY 
                    sa.nomSemestre, ld.nomArea, p.estPPP
                ORDER BY 
                    sa.nomSemestre, ld.nomArea
            """)
            resultados = cursor.fetchall()
            
            print("Resultados de la consulta:", resultados)  
            return resultados
    except Exception as e:
        print(f"Error al obtener reporte: {e}")
        return []
    finally:
        conexion.close()


