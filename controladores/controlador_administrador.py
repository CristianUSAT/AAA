from bd import obtener_conexion

def verificar_usuario(user,contra):
    conexion = obtener_conexion()
    usuario = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from administrador where correo= %s and contraseña = %s",(user,contra))
        usuario=cursor.fetchone()
    conexion.close()
    return usuario

def actualizar_token(user,token):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update administrador set token = %s where correo = %s ",(token,user))
    conexion.commit()
    conexion.close()

def obtener_administrador(user):
    conexion = obtener_conexion()
    administrador = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from administrador where correo = %s ",(user,))
        administrador = cursor.fetchone()
    conexion.close()
    return administrador