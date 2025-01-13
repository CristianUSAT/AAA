from bd import obtener_conexion

def obtener_empresas():
    conexion = obtener_conexion()
    resultado = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM Empresa")
        resultado = cursor.fetchall()
    conexion.close()
    return resultado


def obtener_empresasDoc2(buscar):
    conexion = obtener_conexion()
    resultado = []
    with conexion.cursor() as cursor:
        if buscar =='0' :
            cursor.execute("SELECT * FROM Empresa ORDER BY razSocEmpresa")
        else:
            cursor.execute(f"SELECT * FROM Empresa where LOWER(razSocEmpresa) LIKE LOWER('%{buscar}%') ORDER BY razSocEmpresa")
        resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_empresa_por_id(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM Empresa WHERE id = %s", (id,))
        empresa = cursor.fetchone()
    conexion.close()
    return empresa

def obtener_empresa_por_nombre(razSocEmpresa):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM Empresa WHERE razSocEmpresa = %s", (razSocEmpresa,))
        empresa = cursor.fetchone()
    conexion.close()
    return empresa



def agregar_empresa(codEstEmpresa, razSocEmpresa, dirEmpresa, girEmpresa, repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, orgEmpresa):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Insertar la empresa en la tabla Empresa
            cursor.execute(
                "INSERT INTO Empresa (razSocEmpresa, dirEmpresa, girEmpresa, repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, orgEmpresa) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (razSocEmpresa, dirEmpresa, girEmpresa, repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, orgEmpresa)
            )
            id_generado = cursor.lastrowid  # Obtener el ID de la empresa recién insertada

            # Insertar la relación en la tabla EmpresaEstudiante
            cursor.execute(
                "INSERT INTO EmpresaEstudiante (empresaId, estudianteId) VALUES (%s, %s)",
                (id_generado, codEstEmpresa)
            )

        conexion.commit()
    except Exception as e:
        print(f"Error al agregar la empresa: {e}")
        conexion.rollback()
        id_generado = None
    finally:
        conexion.close()
    
    return id_generado


###### ACTUALIZA EMPRESA ######

def actualizar_empresa(id, razSocEmpresa, dirEmpresa, girEmpresa, repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, orgEmpresa):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "UPDATE Empresa SET razSocEmpresa = %s, dirEmpresa = %s, girEmpresa = %s, repreEmpresa = %s, canTraEmpresa = %s, visEmpresa = %s, misEmpresa = %s, orgEmpresa = %s "
                "WHERE id = %s",
                (razSocEmpresa, dirEmpresa, girEmpresa, repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, orgEmpresa, id)
            )
        conexion.commit()
    except Exception as e:
        print(f"Error al actualizar la empresa: {e}")
        conexion.rollback()
    finally:
        conexion.close()


##############################


###### ELIMINAR EMPRESA ######

def eliminar_empresa(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM Empresa WHERE id = %s", (id,))
    conexion.commit()
    conexion.close()


def eliminar_relacion_empresa_estudiante(id_empresa):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si hay responsables relacionados con la empresa que estén relacionados con algún estudiante
            query_verificacion = """
            SELECT COUNT(*)
            FROM Responsable r
            JOIN EstudianteResponsable er ON r.id = er.responsableId
            WHERE r.codEmpResponsable = %s
            """
            cursor.execute(query_verificacion, (id_empresa,))
            result = cursor.fetchone()
            
            if result[0] == 0:
                # Eliminar la relación entre la empresa y los estudiantes en la tabla intermedia
                cursor.execute("DELETE FROM EmpresaEstudiante WHERE empresaId = %s", (id_empresa,))
            else:
                raise Exception("No se puede eliminar la relación porque la empresa tiene responsables relacionados con estudiantes.")
                
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        print("Error en eliminar_relacion_empresa_estudiante:", e)
        raise e
    finally:
        conexion.close()





##############################

def obtener_empresas_por_estudiante(codEstudiante):
    conexion = obtener_conexion()
    empresas = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT e.*
            FROM Empresa e
            JOIN EmpresaEstudiante ee ON e.id = ee.empresaId
            WHERE ee.estudianteId = %s
        """, (codEstudiante,))
        empresas = cursor.fetchall()
    conexion.close()
    return empresas


def obtener_imagen_actual(empresa_id):
    # Consultar la empresa por su ID para obtener el nombre de la imagen del organigrama
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT orgEmpresa FROM Empresa WHERE id = %s", (empresa_id,))
        resultado = cursor.fetchone()

    conexion.close()

    if resultado and resultado[0]:
        # Si se encontró la imagen, se retorna el nombre del archivo
        return resultado[0]
    else:
        # Si no se encontró una imagen, puede devolver un valor por defecto o None
        return None  # O podrías devolver un valor como "default.png" si lo prefieres


def obtener_empresas2():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM Empresa")
            empresas = cursor.fetchall()
    finally:
        conexion.close()
    return empresas

def agregar_empresa_estudiante(estudiante_id, empresa_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO EmpresaEstudiante (empresaId, estudianteId) VALUES (%s, %s)",
                (empresa_id, estudiante_id)
            )
        conexion.commit()
    except Exception as e:
        print(f"Error al asociar la empresa: {e}")
        conexion.rollback()
    finally:
        conexion.close()

def obtener_empresas_no_vinculadas(estudiante_id):
    conexion = obtener_conexion()
    resultado = []
    with conexion.cursor() as cursor:
        # Consulta para obtener todas las columnas de la tabla Empresa
        query = """
            SELECT e.*
            FROM Empresa e
            LEFT JOIN EmpresaEstudiante ee ON e.id = ee.empresaId AND ee.estudianteId = %s
            WHERE ee.id IS NULL;
        """
        cursor.execute(query, (estudiante_id,))
        resultado = cursor.fetchall()
    conexion.close()
    return resultado

def agregar_empresa_simple(razSocEmpresa, dirEmpresa, girEmpresa, repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, orgEmpresa):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Insertar la empresa en la tabla Empresa
            cursor.execute(
                "INSERT INTO Empresa (razSocEmpresa, dirEmpresa, girEmpresa, repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, orgEmpresa) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (razSocEmpresa, dirEmpresa, girEmpresa, repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, orgEmpresa)
            )
            id_generado = cursor.lastrowid  # Obtener el ID de la empresa recién insertada

        conexion.commit()
    except Exception as e:
        print(f"Error al agregar la empresa: {e}")
        conexion.rollback()
        id_generado = None
    finally:
        conexion.close()
    
    return id_generado


def obtener_empresas_con_cantidad_estudiantes():
    conexion = obtener_conexion()
    resultado = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.razSocEmpresa, COUNT(ee.estudianteId) AS cantidad_estudiantes
            FROM Empresa e
            LEFT JOIN EmpresaEstudiante ee ON e.id = ee.empresaId
            GROUP BY e.id, e.razSocEmpresa
        """)
        resultado = cursor.fetchall()
    conexion.close()
    return resultado
