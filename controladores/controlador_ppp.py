from bd import obtener_conexion

def crear_ppp(code,iniE,finE,iniEm,finEm,des):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"select COALESCE(MAX(numeroPPP), 0)+1 from ppp where codEstPPP={code}")
        numero = cursor.fetchone()
        cursor.execute(
            "insert into ppp(codEstPPP, numeroPPP,codinformeinicialEst,codinformefinalEst,codinformeinicialEmp,codinformefinalEmp,codFichaDesempenio,horas_requeridas,horas_pendientes,estPPP)"
            " VALUES (%s, %s,%s,%s,%s,%s,%s,260,260,'Pendiente')",
            (code,numero[0],iniE,finE,iniEm,finEm,des)
        )
        id_generado=cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_generado

def eliminar_ppp(code):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select codinformeinicialEst,codinformefinalEst,codinformeinicialEmp,codinformefinalEmp,codFichaDesempenio "
                        f"from ppp where id={code}")
        claves = cursor.fetchone()
        cursor.execute(f"delete from cartas where codPPP = {code}")
        cursor.execute(f"delete from ppp where id = {code}")
        cursor.execute(f"delete from informeinicialestudiante where id = {claves[0]}")
        cursor.execute(f"delete from plantrabajo where codInfTrabajo = {claves[0]}")
        cursor.execute(f"delete from informefinalestudiante where id = {claves[1]}")
        cursor.execute(f"delete from informeinicialempresa where id = {claves[2]}")
        cursor.execute(f"delete from informefinalempresa where id = {claves[3]}")
        cursor.execute(f"delete from desempenio where id = {claves[4]}")
    conexion.commit()
    conexion.close()

def crear_cartas(id, pp):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        data = [
            (id, pp, 'Carta Presentacion', 'Activa'),
            (id, pp, 'Carta Aceptacion', 'Activa'),
            (id, pp, 'Carta Constancia', 'Activa')
        ]
        query = "INSERT INTO cartas (codEstudiante, codPPP, nombre, estado) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query, data)
    conexion.commit()
    conexion.close()


def crear_informe(code):
    conexion = obtener_conexion()
    claves=[]
    with conexion.cursor() as cursor:
        cursor.execute(
            "insert into informeinicialestudiante(estuIniEstudiante)"
            " VALUES (%s)",
            (code,)
        )
        id_generado = cursor.lastrowid
        cursor.execute(
            "insert into plantrabajo(codInfTrabajo)"
            " VALUES (%s)",
            (id_generado,)
        )
        claves.append(id_generado)
        cursor.execute(
            "insert into informefinalestudiante(estuFinEstudiante)"
            " VALUES (%s)",
            (code,)
        )
        id_generado = cursor.lastrowid
        claves.append(id_generado)
        cursor.execute(
            "insert into informeinicialempresa(estuIniEmpresa)"
            " VALUES (%s)",
            (code,)
        )
        id_generado = cursor.lastrowid
        claves.append(id_generado)
        
        cursor.execute(
            "insert into informefinalempresa(estuFinEmpresa)"
            " VALUES (%s)",
            (code,)
        )
        id_generado = cursor.lastrowid
        claves.append(id_generado)
        cursor.execute(
            "insert into desempenio(estuDesempenio)"
            " VALUES (%s)",
            (code,)
        )
        id_generado = cursor.lastrowid
        claves.append(id_generado)
    conexion.commit()
    conexion.close()
    return claves

def obtener_informes():
    conexion = obtener_conexion()
    informes = []
    with conexion.cursor() as cursor:
        cursor.execute(""" SELECT pp.numeroPPP,pp.iniPPP,pp.finPPP,pp.horas,es.id,
                        ii.fechaIniEstudiante,ii.estaIniEstudiante,ii.id,
                        fi.fechaInfFinEstudiante,fi.estaFinEstudiante,fi.id,
                        ie.fechaInfIniEmpresa,ie.estaIniEmpresa,ie.id,
                        fe.fechaInfFinEmpresa,fe.estaFinEmpresa,fe.id,
                        de.fechaInfDesempenio,de.estaDesempenio,de.id,pp.id from estudiante as es
                        INNER join ppp as pp on pp.codEstPPP=es.id
                        INNER join informeinicialestudiante as ii on ii.id=pp.codinformeinicialEst
                        INNER join informefinalestudiante as fi on fi.id=pp.codinformefinalEst
                        INNER join informeinicialempresa as ie on ie.id=pp.codinformeinicialEmp
                        INNER join informefinalempresa as fe on fe.id=pp.codinformefinalEmp
                        INNER join desempenio as de on de.id=pp.codFichaDesempenio where pp.estPPP='Pendiente'""")
        informes = cursor.fetchall()
    conexion.close()
    return informes

def obtener_ppp_estudiante(code,numero):
    conexion = obtener_conexion()
    ppp= []
    with conexion.cursor() as cursor:
        cursor.execute(
            "select pp.* from ppp as pp inner join estudiante as es "
            f" on es.id=pp.codestppp where es.id={code} and pp.numeroppp={numero}",
        )
        ppp=cursor.fetchall()
    conexion.close()
    return ppp

def obtener_ppp_estudiante(id):
    conexion = obtener_conexion()
    ppp= []
    with conexion.cursor() as cursor:
        cursor.execute(
            "select pp.* from ppp as pp inner join estudiante as es "
            f" on es.id=pp.codestppp where pp.id={id}",
        )
        ppp=cursor.fetchone()
    conexion.close()
    return ppp

def actualizar_ppp(id,codSemIniPPP,codSemFinPPP,horas,iniPPP,finPPP,codLinPPP,arePPP,codDocentePPP):

    conexion = obtener_conexion()
    if int(horas) > 260:
        horas = 260
    with conexion.cursor() as cursor:
        cursor.execute("update ppp set codSemIniPPP=%s,codSemFinPPP=%s,horas=%s,horas_pendientes=(horas_requeridas-%s),iniPPP=%s,finPPP=%s,codLinPPP=%s,arePPP=%s,codDocentePPP=%s"
                    f" where id = {id}",(codSemIniPPP,codSemFinPPP,horas,horas,iniPPP,finPPP,codLinPPP,arePPP,codDocentePPP))
    conexion.commit()
    conexion.close()
    


def transaccion_ppp(id):
    conexion = obtener_conexion()
    ppp = []
    with conexion.cursor() as cursor:
        cursor.execute("select pp.horas_pendientes,es.id,ii.estaIniEstudiante,fi.estaFinEstudiante, "
                        "ie.estaIniEmpresa,fe.estaFinEmpresa,de.estaDesempenio from ppp pp inner join "
                        "estudiante es on es.id = pp.codEstPPP inner join informeinicialestudiante ii on ii.id = pp.codinformeinicialEst "
                        "inner join informefinalestudiante fi on fi.id = pp.codinformefinalEst inner join informeinicialempresa ie on ie.id = pp.codinformeinicialEmp "
                        "inner join informefinalempresa fe on fe.id = pp.codinformefinalEmp inner join desempenio de on de.id = pp.codFichaDesempenio "
                        "where pp.id = %s",(id,))
    ppp = cursor.fetchone()
    conexion.close()
    return ppp

def cambiar_ppp(id,nombre):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update ppp set estPPP=%s where id = %s",(nombre,id))
    conexion.commit()
    conexion.close()