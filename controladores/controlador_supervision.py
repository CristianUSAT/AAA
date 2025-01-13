from bd import obtener_conexion
import os
from werkzeug.utils import secure_filename

def obtener_supervisiones():
    conexion = obtener_conexion()
    lista_cero = []
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT pp.numeroPPP, pp.iniPPP, pp.finPPP, pp.horas, es.id AS estudiante_id, 
                   su.numero AS supervision_numero, su.fecha, su.hora, pp.id AS ppp_id
            FROM ppp pp
            LEFT JOIN super su ON pp.id = su.superPPP
            LEFT JOIN estudiante es ON es.id = pp.codEstPPP
            ORDER BY pp.id, su.numero
            """
        )
        lista_cero = cursor.fetchall()
    conexion.close()
    return lista_cero

# Obtener la lista única de PPP sin duplicados
def obtener_lista_ppp():
    conexion = obtener_conexion()
    ppp_lista = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT pp.id AS ppp_id, pp.numeroPPP, pp.iniPPP, pp.finPPP, pp.horas, es.id AS estudiante_id
            FROM ppp pp
            LEFT JOIN estudiante es ON es.id = pp.codEstPPP
            ORDER BY pp.id;
        """)
        ppp_lista = cursor.fetchall()
    conexion.close()
    return ppp_lista

def obtener_supervisiones_por_ppp(ppp_id):
    conexion = obtener_conexion()
    supervisiones = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT su.numero AS supervision_numero, su.fecha, su.hora, su.id as codigo
            FROM super su
            WHERE su.superPPP = %s
            ORDER BY su.numero;
        """, (ppp_id,))
        supervisiones = cursor.fetchall()
    conexion.close()
    
    # Imprimir para verificar si los datos se están obteniendo
    print(f"PPP ID {ppp_id} tiene supervisiones: {supervisiones}")
    return supervisiones

def guardar_archivo(archivo, carpeta_destino):
    if archivo and archivo.filename != '':
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
        filename = secure_filename(archivo.filename)
        ruta_completa = os.path.join(carpeta_destino, filename)
        archivo.save(ruta_completa)
        return filename
    return None

def crear_supervision(superEstu, superPPP, fecha, hora, superEmpr, ubicacion, responsable, area_desempenio, funciones, observaciones, firmaEstu, firmaJefe, firmaDoce):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        # Obtener el último número de supervisión para el PPP específico
        cursor.execute("""
            SELECT COALESCE(MAX(numero), 0) + 1 FROM super WHERE superPPP = %s
        """, (superPPP,))
        numero_supervision = cursor.fetchone()[0]

        # Guardar archivos
        carpeta_firmas = 'static/uploads/firmas'
        firmaEstu_nombre = guardar_archivo(firmaEstu, carpeta_firmas)
        firmaJefe_nombre = guardar_archivo(firmaJefe, carpeta_firmas)
        firmaDoce_nombre = guardar_archivo(firmaDoce, carpeta_firmas)
        
        # Insertar la nueva supervisión con el número calculado
        cursor.execute("""
            INSERT INTO super (superEstu, superPPP, fecha, hora, superEmpr, ubicacion, responsable, area_desempenio, funciones, observaciones, firmaEstu, firmaJefe, firmaDoce, numero)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (superEstu, superPPP, fecha, hora, superEmpr, ubicacion, responsable, area_desempenio, funciones, observaciones, firmaEstu_nombre, firmaJefe_nombre, firmaDoce_nombre, numero_supervision))
        
        conexion.commit()
    conexion.close()

def obtener_supervision(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id, superEstu, superPPP, fecha, hora, superEmpr, ubicacion, area_desempenio,
                   responsable, funciones, observaciones, firmaEstu, firmaJefe, firmaDoce
            FROM super WHERE id = %s
        """, (id,))
        supervisioon = cursor.fetchone()
    conexion.close()
    return supervisioon

def actualizar_supervision(id, superEmpr, ubicacion, area_desempenio, responsable, funciones, observaciones, firmaEstu, firmaJefe, firmaDoce):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            UPDATE super
            SET superEmpr = %s, ubicacion = %s, area_desempenio = %s, responsable = %s,
                funciones = %s, observaciones = %s, firmaEstu = %s, firmaJefe = %s, firmaDoce = %s
            WHERE id = %s
        """, (superEmpr, ubicacion, area_desempenio, responsable, funciones, observaciones, firmaEstu, firmaJefe, firmaDoce, id))
        conexion.commit()
    conexion.close()


def eliminar_supervision(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM super WHERE id = %s", (id,))
        conexion.commit()
    conexion.close()


def obtener_responsables():
    conexion = obtener_conexion()
    responsables = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id, apeNomResponsable FROM Responsable")
        responsables = cursor.fetchall()
    conexion.close()
    return responsables

def obtener_empresas():
    conexion = obtener_conexion()
    empresas = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id, razSocEmpresa FROM Empresa")
        empresas = cursor.fetchall()
    conexion.close()
    return empresas

def obtener_estudiantes():
    conexion = obtener_conexion()
    estudiante = []
    try:
        with conexion.cursor() as cursor:
            # Seleccionamos todas las filas de la tabla estudiante
            cursor.execute("SELECT * FROM estudiante")
            estudiante = cursor.fetchall()  # Devuelve todas las filas como una lista
    finally:
        conexion.close()
    return estudiante