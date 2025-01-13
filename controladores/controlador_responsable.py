from bd import obtener_conexion

def obtener_responsables_por_estudiante(codEstudiante):
    conexion = obtener_conexion()
    responsables = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT r.*, e.razSocEmpresa AS nombre_empresa
            FROM Responsable r
            INNER JOIN EstudianteResponsable er ON er.responsableId = r.id
            INNER JOIN Empresa e ON r.codEmpResponsable = e.id
            WHERE er.estudianteId = %s
        """, (codEstudiante,))
        responsables = cursor.fetchall()
    conexion.close()
    return responsables


def obtener_responsables_por_estudiante2(codEstudiante,buscar):
    conexion = obtener_conexion()
    responsables = []
    with conexion.cursor() as cursor:
        if buscar == '0':
            cursor.execute("""
                SELECT r.*, e.razSocEmpresa AS nombre_empresa
                FROM Responsable r
                INNER JOIN EstudianteResponsable er ON er.responsableId = r.id
                INNER JOIN Empresa e ON r.codEmpResponsable = e.id
                WHERE er.estudianteId = %s
                ORDER BY r.apeNomResponsable
            """, (codEstudiante,))
        else:
            cursor.execute("""
                SELECT r.*, e.razSocEmpresa AS nombre_empresa
                FROM Responsable r
                INNER JOIN EstudianteResponsable er ON er.responsableId = r.id
                INNER JOIN Empresa e ON r.codEmpResponsable = e.id
                WHERE er.estudianteId = %s
                AND LOWER(r.apeNomResponsable) LIKE LOWER(%s)
                ORDER BY r.apeNomResponsable
            """, (codEstudiante,f'%{buscar}%',))
        responsables = cursor.fetchall()
    conexion.close()
    return responsables




def obtener_todos_responsables(buscar):
    conexion = obtener_conexion()
    responsables = []
    with conexion.cursor() as cursor:
        if buscar == '0':
            cursor.execute("""
                SELECT r.*, e.razSocEmpresa AS nombre_empresa 
                FROM Responsable r
                INNER JOIN Empresa e ON r.codEmpResponsable = e.id
            """)
        else:
            cursor.execute("""
                SELECT r.*, e.razSocEmpresa AS nombre_empresa 
                FROM Responsable r
                INNER JOIN Empresa e ON r.codEmpResponsable = e.id
                where LOWER(r.apeNomResponsable) LIKE LOWER(%s)
                ORDER BY r.apeNomResponsable
            """, (f'%{buscar}%',))
        responsables = cursor.fetchall()
    conexion.close()
    return responsables



def obtener_responsable_por_id(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM Responsable WHERE id = %s", (id,))
        responsable = cursor.fetchone()
    conexion.close()
    return responsable

def agregar_responsable(codEmpResponsable, apeNomResponsable, carResponsable, telResponsable, corResponsable, horResponsable):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Responsable (codEmpResponsable, apeNomResponsable, carResponsable, telResponsable, corResponsable, horResponsable) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (codEmpResponsable, apeNomResponsable, carResponsable, telResponsable, corResponsable, horResponsable)
        )
        id_generado = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado

def obtener_responsables_por_empresa2(estudiante_id):
    conexion = obtener_conexion()
    responsables_por_empresa = {}

    try:
        with conexion.cursor() as cursor:
            # Consultar las empresas vinculadas con el estudiante
            query_empresas = """
                SELECT e.id, e.razSocEmpresa
                FROM Empresa e
                JOIN EmpresaEstudiante ee ON e.id = ee.empresaId
                WHERE ee.estudianteId = %s;
            """
            cursor.execute(query_empresas, (estudiante_id,))
            empresas = cursor.fetchall()

            # Para cada empresa, obtener los responsables no vinculados al estudiante
            for empresa in empresas:
                empresa_id = empresa[0]
                empresa_nombre = empresa[1]
                
                query_responsables = """
                    SELECT r.id, r.apeNomResponsable, r.carResponsable, r.telResponsable, r.corResponsable
                    FROM Responsable r
                    LEFT JOIN EstudianteResponsable er ON r.id = er.responsableId
                    WHERE r.codEmpResponsable = %s
                    AND (er.estudianteId IS NULL OR er.estudianteId != %s);
                """
                cursor.execute(query_responsables, (empresa_id, estudiante_id))
                responsables = cursor.fetchall()

                # Añadir la lista de responsables no relacionados al diccionario, con la empresa como clave
                if responsables:
                    responsables_por_empresa[empresa_nombre] = responsables

    except Exception as e:
        print(f"Error al obtener responsables: {e}")
    finally:
        conexion.close()

    return responsables_por_empresa






def agregar_relacion_estudiante_responsable(codEstResponsable, codResponsable):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO EstudianteResponsable (estudianteId, responsableId) "
                "VALUES (%s, %s)",
                (codEstResponsable, codResponsable)
            )
        conexion.commit()
    except Exception as e:
        print(f"Error al asociar el responsable: {e}")
        conexion.rollback()
    finally:
        conexion.close()



def actualizar_responsable(id, codEmpResponsable, apeNomResponsable, carResponsable, telResponsable, corResponsable, horResponsable):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE Responsable SET codEmpResponsable = %s, apeNomResponsable = %s, carResponsable = %s, telResponsable = %s, corResponsable = %s, horResponsable = %s "
            "WHERE id = %s",
            ( codEmpResponsable, apeNomResponsable, carResponsable, telResponsable, corResponsable, horResponsable, id)
        )
    conexion.commit()
    conexion.close()

def eliminar_responsable(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM Responsable WHERE id = %s", (id,))
    conexion.commit()
    conexion.close()

def eliminar_relacion_estudiante_responsable(idResponsable):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM EstudianteResponsable WHERE responsableId = %s", (idResponsable,))
    conexion.commit()
    conexion.close()


def obtener_responsables_por_empresa(codEmpresa):
    conexion = obtener_conexion()
    responsables = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT * FROM Responsable WHERE codEmpResponsable = %s", (codEmpresa,))
        responsables = cursor.fetchall()
    conexion.close()
    return responsables
