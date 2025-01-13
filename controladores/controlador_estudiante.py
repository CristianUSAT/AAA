from bd import obtener_conexion

def verificar_usuario(user,contra):
    conexion = obtener_conexion()
    usuario = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from estudiante where corUniEstudiante= %s and passestudiante = %s",(user,contra))
        usuario=cursor.fetchone()
    conexion.close()
    return usuario

def actualizar_token(user,token):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update estudiante set token = %s where corUniEstudiante = %s ",(token,user))
    conexion.commit()
    conexion.close()

def obtener_estudiante(user):
    conexion = obtener_conexion()
    estudiante = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from estudiante where corUniEstudiante = %s ",(user,))
        estudiante = cursor.fetchone()
    conexion.close()
    return estudiante

def obtener_estudiantes(escuela,buscar):
    conexion = obtener_conexion()
    estudiante = []
    with conexion.cursor() as cursor:
        if escuela == '0' and buscar == '0':
            cursor.execute("select es.*,esc.nomEscuela from estudiante es inner join escuelaprofesional esc on es.codEscEstudiante=esc.id "
                        " where es.estEstudiante=1 order by es.apeNomEstudiante")
        elif escuela !='0':
            cursor.execute("select es.*,esc.nomEscuela from estudiante es inner join escuelaprofesional esc on es.codEscEstudiante=esc.id "
                        " where esc.nomEscuela=%s order by es.apeNomEstudiante",(escuela,))
        else:
            cursor.execute("select es.*,esc.nomEscuela from estudiante es inner join escuelaprofesional esc on es.codEscEstudiante=esc.id "
                        f" where lower(es.apeNomEstudiante) like lower('%{buscar}%') order by es.apeNomEstudiante")
        estudiante = cursor.fetchall()
            
    conexion.close()
    return estudiante


def agregar_estudiante(cod, nom, esc, dni, tel, correo, estado, pas):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO estudiante (codUniEstudiante, apeNomEstudiante, codEscEstudiante, dniEstudiante, telEstudiante, corUniEstudiante, estEstudiante, passEstudiante) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (cod, nom, esc, dni, tel, correo, estado, pas)
        )
    id_generado = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado

def modificarEstEstudiante(estado,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update estudiante set estEstudiante = %s where id = %s",(estado,id))
    conexion.commit()
    conexion.close()

def modificarEstudiante(codUniEstudiante,apeNomEstudiante,codEscEstudiante,dniEstudiante,telEstudiante,corUniEstudiante,estEstudiante,passEstudiante,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update estudiante set codUniEstudiante=%s,apeNomEstudiante=%s,codEscEstudiante=%s, "
                       "dniEstudiante=%s,telEstudiante=%s,corUniEstudiante=%s,estEstudiante=%s,passEstudiante=%s where id=%s",
                       (codUniEstudiante,apeNomEstudiante,codEscEstudiante,dniEstudiante,telEstudiante,corUniEstudiante,estEstudiante,passEstudiante,id))
    conexion.commit()
    conexion.close()

def eliminarEstudiante(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("delete from estudiante where id = %s",(id,))
    conexion.commit()
    conexion.close()



def obtenerEmpresa(id):
    conexion = obtener_conexion()
    empresas = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT e.*
                FROM Empresa e
                INNER JOIN EmpresaEstudiante ee ON e.id = ee.empresaId
                WHERE ee.estudianteId = %s
            """, (id,))
            empresas = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener las empresas: {e}")
    finally:
        conexion.close()
    return empresas


def obtener_empresa2(id,buscar):
    conexion = obtener_conexion()
    empresas = []
    try:
        with conexion.cursor() as cursor:
            if buscar == '0':
                cursor.execute("""
                SELECT e.*
                FROM Empresa e
                INNER JOIN EmpresaEstudiante ee ON e.id = ee.empresaId
                WHERE ee.estudianteId = %s
                ORDER BY e.razSocEmpresa
            """, (id,))
            else:
                cursor.execute("""
                    SELECT e.*
                    FROM Empresa e
                    INNER JOIN EmpresaEstudiante ee ON e.id = ee.empresaId
                    WHERE ee.estudianteId = %s
                    AND LOWER(e.razSocEmpresa) LIKE LOWER(%s)
                    ORDER BY e.razSocEmpresa
                """, (id,f'%{buscar}%',))
            empresas = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener las empresas: {e}")
    finally:
        conexion.close()
    return empresas





def obtener_id_estudiante(username):
    """
    Obtiene el código del estudiante basado en su nombre de usuario (correo).
    
    :param username: El nombre de usuario o correo del estudiante.
    :return: El código del estudiante si existe, de lo contrario, None.
    """
    conexion = obtener_conexion()
    codigo = None
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id FROM estudiante WHERE corUniEstudiante = %s", (username,))
        resultado = cursor.fetchone()
        if resultado:
            codigo = resultado[0]  # Asume que codUniEstudiante es la primera columna en el resultado
    conexion.close()
    return codigo





def obtenerEmpresasPorEstudiante(estudiante_id):
    conexion = obtener_conexion()
    empresas_relacionadas = []
    empresas_no_relacionadas = []
    
    try:
        with conexion.cursor() as cursor:
            # Empresas relacionadas
            cursor.execute("""
                SELECT e.id, e.razSocEmpresa
                FROM Empresa e
                INNER JOIN EmpresaEstudiante ee ON e.id = ee.empresaId
                WHERE ee.estudianteId = %s
            """, (estudiante_id,))
            empresas_relacionadas = cursor.fetchall()

            # Empresas no relacionadas
            cursor.execute("""
                SELECT e.id, e.razSocEmpresa
                FROM Empresa e
                WHERE e.id NOT IN (
                    SELECT empresaId 
                    FROM EmpresaEstudiante 
                    WHERE estudianteId = %s
                )
            """, (estudiante_id,))
            empresas_no_relacionadas = cursor.fetchall()
            
    except Exception as e:
        print(f"Error al obtener las empresas: {e}")
    finally:
        conexion.close()
    
    return empresas_relacionadas, empresas_no_relacionadas


def obtenerResponsablesPorEstudiante(estudiante_id):
    conexion = obtener_conexion()
    responsables_relacionados = []
    responsables_no_relacionados = []
    
    try:
        with conexion.cursor() as cursor:
            # Responsables relacionados
            cursor.execute("""
                SELECT r.id, r.apeNomResponsable
                FROM Responsable r
                INNER JOIN EstudianteResponsable er ON r.id = er.responsableId
                WHERE er.estudianteId = %s
            """, (estudiante_id,))
            responsables_relacionados = cursor.fetchall()

            # Responsables no relacionados pero relacionados con empresas del estudiante
            cursor.execute("""
                SELECT r.id, r.apeNomResponsable
                FROM Responsable r
                WHERE r.id NOT IN (
                    SELECT responsableId 
                    FROM EstudianteResponsable 
                    WHERE estudianteId = %s
                )
                AND r.codEmpResponsable IN (
                    SELECT empresaId
                    FROM EmpresaEstudiante
                    WHERE estudianteId = %s
                )
            """, (estudiante_id, estudiante_id))
            responsables_no_relacionados = cursor.fetchall()

    except Exception as e:
        print(f"Error al obtener los responsables: {e}")
    finally:
        conexion.close()

    return responsables_relacionados, responsables_no_relacionados





#####

def desasociar_empresa(estudiante_id, empresa_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si la relación entre la empresa y el estudiante existe
            cursor.execute("SELECT 1 FROM EmpresaEstudiante WHERE empresaId = %s AND estudianteId = %s", (empresa_id, estudiante_id))
            relacion_existe = cursor.fetchone()
            if not relacion_existe:
                raise ValueError(f"La empresa con ID {empresa_id} no está asociada con el estudiante con ID {estudiante_id}.")
            
            # Verificar si hay algún responsable de la empresa asociado con el estudiante
            cursor.execute("""
                SELECT 1
                FROM EstudianteResponsable er
                INNER JOIN Responsable r ON er.responsableId = r.id
                WHERE er.estudianteId = %s AND r.codEmpResponsable = %s
            """, (estudiante_id, empresa_id))
            responsable_asociado = cursor.fetchone()
            if responsable_asociado:
                raise ValueError(f"No se puede desasociar la empresa con ID {empresa_id} porque hay responsables de esta empresa asociados con el estudiante con ID {estudiante_id}.")
            
            # Eliminar la relación de la tabla intermedia
            cursor.execute("DELETE FROM EmpresaEstudiante WHERE empresaId = %s AND estudianteId = %s", (empresa_id, estudiante_id))
            conexion.commit()
    except Exception as e:
        print(f"Error al desasociar la empresa: {e}")
        raise e
    finally:
        conexion.close()



def asociar_empresa(estudiante_id, empresa_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar que el estudiante existe
            cursor.execute("SELECT 1 FROM Estudiante WHERE id = %s", (estudiante_id,))
            estudiante_existe = cursor.fetchone()
            if not estudiante_existe:
                raise ValueError(f"El estudiante con ID {estudiante_id} no existe.")
            
            # Verificar que la empresa existe
            cursor.execute("SELECT 1 FROM Empresa WHERE id = %s", (empresa_id,))
            empresa_existe = cursor.fetchone()
            if not empresa_existe:
                raise ValueError(f"La empresa con ID {empresa_id} no existe.")
            
            # Verificar si la relación ya existe
            cursor.execute("SELECT 1 FROM EmpresaEstudiante WHERE empresaId = %s AND estudianteId = %s", (empresa_id, estudiante_id))
            relacion_existe = cursor.fetchone()
            if relacion_existe:
                raise ValueError(f"La empresa con ID {empresa_id} ya está asociada con el estudiante con ID {estudiante_id}.")
            
            # Insertar la relación en la tabla intermedia
            cursor.execute("INSERT INTO EmpresaEstudiante (empresaId, estudianteId) VALUES (%s, %s)", (empresa_id, estudiante_id))
            conexion.commit()
    except Exception as e:
        print(f"Error al asociar la empresa: {e}")
        raise e
    finally:
        conexion.close()



def desasociar_responsable(estudiante_id, responsable_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si la relación existe
            cursor.execute("SELECT 1 FROM EstudianteResponsable WHERE responsableId = %s AND estudianteId = %s", (responsable_id, estudiante_id))
            relacion_existe = cursor.fetchone()
            if not relacion_existe:
                raise ValueError(f"El responsable con ID {responsable_id} no está asociado con el estudiante con ID {estudiante_id}.")
            
            # Eliminar la relación de la tabla intermedia
            cursor.execute("DELETE FROM EstudianteResponsable WHERE responsableId = %s AND estudianteId = %s", (responsable_id, estudiante_id))
            conexion.commit()
    except Exception as e:
        print(f"Error al desasociar el responsable: {e}")
        raise e
    finally:
        conexion.close()



def asociar_responsable(estudiante_id, responsable_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar que el estudiante existe
            cursor.execute("SELECT 1 FROM Estudiante WHERE id = %s", (estudiante_id,))
            estudiante_existe = cursor.fetchone()
            if not estudiante_existe:
                raise ValueError(f"El estudiante con ID {estudiante_id} no existe.")
            
            # Verificar que el responsable existe
            cursor.execute("SELECT 1 FROM Responsable WHERE id = %s", (responsable_id,))
            responsable_existe = cursor.fetchone()
            if not responsable_existe:
                raise ValueError(f"El responsable con ID {responsable_id} no existe.")
            
            # Verificar si la relación ya existe
            cursor.execute("SELECT 1 FROM EstudianteResponsable WHERE responsableId = %s AND estudianteId = %s", (responsable_id, estudiante_id))
            relacion_existe = cursor.fetchone()
            if relacion_existe:
                raise ValueError(f"El responsable con ID {responsable_id} ya está asociado con el estudiante con ID {estudiante_id}.")
            
            # Insertar la relación en la tabla intermedia
            cursor.execute("INSERT INTO EstudianteResponsable (responsableId, estudianteId) VALUES (%s, %s)", (responsable_id, estudiante_id))
            conexion.commit()
    except Exception as e:
        print(f"Error al asociar el responsable: {e}")
        raise e
    finally:
        conexion.close()


