from bd import obtener_conexion

def obtener_horarios_por_estudiante(idEstudiante):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT dia, hora FROM Horario WHERE idEstudiante = %s",
                (idEstudiante,)
            )
            horarios = cursor.fetchall()
        
        # Mostrar los horarios en la terminal
        print("Horarios obtenidos:", horarios)

        return horarios
    except Exception as e:
        print(f"Error al obtener horarios: {e}")
        return None
    finally:
        if conexion:
            conexion.close()


def agregar_horario(idEstudiante, dia, hora):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Horario (idEstudiante, dia, hora) VALUES (%s, %s, %s);",
                (idEstudiante, dia, hora)
            )
            conexion.commit()
            print(f"Horario guardado: {idEstudiante}, {dia}, {hora}")
    except Exception as e:
        print(f"Error al agregar horario: {e}")
        conexion.rollback()
        raise e  # Asegúrate de que cualquier error se propague
    finally:
        if conexion:
            conexion.close()

def eliminar_horario(idEstudiante):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Eliminamos el horario existente para el estudiante
            cursor.execute(
                "DELETE FROM HORARIO WHERE idEstudiante = %s;",
                (idEstudiante,)
            )
            # Confirmamos los cambios en la base de datos
            conexion.commit()
            print(f"Horario eliminado para el estudiante: {idEstudiante}")
    except Exception as e:
        print(f"Error al eliminar horario: {e}")
        conexion.rollback()
        raise e  # Propaga el error
    finally:
        if conexion:
            conexion.close()