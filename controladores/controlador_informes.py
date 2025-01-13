from bd import obtener_conexion

def obtener_informe_inicial(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"select * from informeinicialestudiante where id={id} ")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_informe_final(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"select * from informefinalestudiante where id={id} ")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_informe_inicial_empresa(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"select * from informeinicialempresa where id={id} ")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_informe_final_empresa(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"select * from informefinalempresa where id={id} ")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_desempenio(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"select * from desempenio where id={id} ")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_plan(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f"select * from plantrabajo where codInfTrabajo={id}")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def guardar_caracteristica(codDesempenio, nomCaracteristica, escalaSeleccionada, caracteristica_id=None):
    conexion = obtener_conexion()
    
    with conexion.cursor() as cursor:
        if caracteristica_id:
            cursor.execute("""
                UPDATE Caracteristicas
                SET codDesempenio = %s, nomCaracteristica = %s, escala_seleccionada = %s
                WHERE id = %s
            """, (codDesempenio, nomCaracteristica, escalaSeleccionada, caracteristica_id))
        else:
            cursor.execute("""
                INSERT INTO Caracteristicas (codDesempenio, nomCaracteristica, escala_seleccionada)
                VALUES (%s, %s, %s)
            """, (codDesempenio, nomCaracteristica, escalaSeleccionada))

    conexion.commit()
    conexion.close()

def obtener_caracteristicas_por_informe(codDesempenio):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id, nomCaracteristica, escala_seleccionada 
            FROM Caracteristicas 
            WHERE codDesempenio = %s
        """, (codDesempenio,))
        caracteristicas = cursor.fetchall()
    conexion.close()
    return caracteristicas


def guardar_informeIE(semestre,empresa,responsable,objetivos,fechaI,fechaF,filenameE,filenameR,docente,observaciones,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update informeinicialestudiante set codSemIniEstudiante=%s, empIniEstudiante=%s, resIniEstudiante=%s, "
                       "aceptacionEmpresa=%s, iniIniEstudiante=%s, finIniEstudiante=%s, firEstIniEstudiante=%s, "
                       "firResIniEstudiante=%s, codDocente=%s, obseIniEstudiante=%s where id = %s",
                       (semestre,empresa,responsable,objetivos,fechaI,fechaF,filenameE,filenameR,docente,observaciones,id))
    conexion.commit()
    conexion.close()

def guardar_plan(semTrabajo , iniTrabajo , finTrabajo , actTrabajo ,horTrabajo,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE  plantrabajo  SET semTrabajo=%s, iniTrabajo=%s, finTrabajo=%s, actTrabajo=%s, horTrabajo=%s WHERE codInfTrabajo=%s",
                       (semTrabajo , iniTrabajo , finTrabajo , actTrabajo ,horTrabajo,id))
    conexion.commit()
    conexion.close()

def guardar_informeFE(emprFinEstudiante,intFinEstudiante,descAreFinEstudiante,descLabFinEstudiante,conFinEstudiante,recFinEstudiante,bibFinEstudiante,aneFinEstudiante,codDocente,observaciones,infraestfisica,infraesttecno,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update informefinalestudiante set emprFinEstudiante=%s,intFinEstudiante=%s,descAreFinEstudiante=%s,"
                       " descLabFinEstudiante=%s,conFinEstudiante=%s,recFinEstudiante=%s,bibFinEstudiante=%s,aneFinEstudiante=%s,codDocente=%s,obseFinEstudiante=%s, infraestfisica=%s, infraesttecno=%s where id = %s",
                       (emprFinEstudiante,intFinEstudiante,descAreFinEstudiante,descLabFinEstudiante,conFinEstudiante,recFinEstudiante,bibFinEstudiante,aneFinEstudiante,codDocente,observaciones,infraestfisica,infraesttecno,id))
    conexion.commit()
    conexion.close()

def guardar_informeIEm(empIniEmpresa,resIniEmpresa,iniIniEmpresa,finIniEmpresa,aceIniEmpresa,aceAnexoIniEmpresa,labIniEmpresa,selFirResIniEmpresa,observaciones,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update informeinicialempresa set empIniEmpresa=%s,resIniEmpresa=%s,iniIniEmpresa=%s,finIniEmpresa=%s,"
                       " aceIniEmpresa=%s,aceAnexoIniEmpresa=%s,labIniEmpresa=%s,selFirResIniEmpresa=%s, obseIniEmpresa=%s where id = %s",
                       (empIniEmpresa,resIniEmpresa,iniIniEmpresa,finIniEmpresa,aceIniEmpresa,aceAnexoIniEmpresa,labIniEmpresa,selFirResIniEmpresa,observaciones,id))
    conexion.commit()
    conexion.close()

def guardar_informeFEm(empFinEmpresa,respFinEmpresa,iniFinEmpresa,finFinEmpresa,objFinEmpresa,horFinEmpresa,resFinEmpresa,otrFinEmpresa,selFirResFinEmpresa,observaciones,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update informefinalempresa set empFinEmpresa=%s,respFinEmpresa=%s,iniFinEmpresa=%s,finFinEmpresa=%s, "
                       " objFinEmpresa=%s,horFinEmpresa=%s,resFinEmpresa=%s,otrFinEmpresa=%s,selFirResFinEmpresa=%s, obseFinEmpresa=%s where id = %s",
                       (empFinEmpresa,respFinEmpresa,iniFinEmpresa,finFinEmpresa,objFinEmpresa,horFinEmpresa,resFinEmpresa,otrFinEmpresa,selFirResFinEmpresa,observaciones,id))
    conexion.commit()
    conexion.close()

def guardar_desempenio(empDesempenio,respDesempenio,areDesempenio,resuDesempenio,iniDesempenio,finDesempenio,conDesempenio,firRepDesempenio,codDocente,id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update desempenio set empDesempenio=%s,respDesempenio=%s,areDesempenio=%s,resuDesempenio=%s,iniDesempenio=%s, "
                       "finDesempenio=%s,conDesempenio=%s,firRepDesempenio=%s,codDocente=%s WHERE id=%s",
                       (empDesempenio,respDesempenio,areDesempenio,resuDesempenio,iniDesempenio,finDesempenio,conDesempenio,firRepDesempenio,codDocente,id))
    conexion.commit()
    conexion.close()

def editar_estado_inicialE(id,estado,obs):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update informeinicialestudiante set estaIniEstudiante= %s,obseIniEstudiante=%s where id=%s",
                       (estado,obs,id))
    conexion.commit()
    conexion.close()

def editar_estado_finalE(id,estado,obs):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update informefinalestudiante set estaFinEstudiante= %s,obseFinEstudiante=%s where id=%s",
                       (estado,obs,id))
    conexion.commit()
    conexion.close()

def editar_estado_inicialEm(id,estado,obs):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update informeinicialempresa set estaIniEmpresa = %s,obseIniEmpresa=%s where id=%s",
                       (estado,obs,id))
    conexion.commit()
    conexion.close()

def editar_estado_finalEm(id,estado,obs):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update informefinalempresa set estaFinEmpresa= %s,obseFinEmpresa=%s where id=%s",
                       (estado,obs,id))
    conexion.commit()
    conexion.close()

def editar_estado_desempenio(id,estado,obs):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("update desempenio set estaDesempenio= %s,obseDesempenio=%s where id=%s",
                       (estado,obs,id))
    conexion.commit()
    conexion.close()

def obtener_informe_inicial_para_generar_pdf(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(f'''SELECT 
                            i.id,
                            s.nomsemestre AS semestre,
                            e.razsocempresa AS empresa,
                            r.apenomresponsable AS responsable,
                            i.aceptacionEmpresa AS aceptacion,
                            i.iniIniEstudiante AS fecha_inicio,
                            i.finIniEstudiante AS fecha_termino,
                            i.firEstIniEstudiante AS firma_estudiante,
                            i.firResIniEstudiante AS firma_responsable,
                            r.carResponsable AS cargo,
                            est.apeNomEstudiante AS nombre_estudiante,
                            i.laboresPracticante AS labores,
                            est.codUniEstudiante AS codigo
                        FROM 
                            informeinicialestudiante i
                        INNER JOIN 
                            semestreacademico s ON i.codSemIniEstudiante = s.id
                        INNER JOIN 
                            empresa e ON i.empIniEstudiante = e.id
                        INNER JOIN 
                            responsable r ON i.resIniEstudiante = r.id
                        INNER JOIN 
                            estudiante est ON i.estuIniEstudiante  = est.id
                        WHERE i.id={id} ''')
        
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_informe_final_estudiante_para_generar_pdf(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select esc.nomEscuela,es.apeNomEstudiante,em.razSocEmpresa,fi.fechaInfFinEstudiante,fi.intFinEstudiante, "
                        "fi.descAreFinEstudiante,fi.descLabFinEstudiante,fi.conFinEstudiante,fi.recFinEstudiante,fi.bibFinEstudiante, "
                        "fi.aneFinEstudiante, fi.infraestfisica, fi.infraesttecno from informefinalestudiante fi inner JOIN estudiante es on es.id = fi.estuFinEstudiante "
                        "inner join escuelaprofesional esc on esc.id=es.codEscEstudiante inner join empresa em "
                        f"on em.id=fi.emprFinEstudiante where fi.id={id}")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_informe_inicial_empresa_para_generar_pdf(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select esc.nomEscuela,es.apeNomEstudiante,em.razSocEmpresa,fi.fechaInfIniEmpresa, "
                        "re.apeNomResponsable,fi.iniIniEmpresa,fi.finIniEmpresa,fi.aceIniEmpresa, "
                        "fi.aceAnexoIniEmpresa,fi.labIniEmpresa,fi.selFirResIniEmpresa, re.carResponsable "
                        "from informeinicialempresa fi inner JOIN estudiante es on es.id = fi.estuIniEmpresa "
                        "inner join escuelaprofesional esc on esc.id=es.codEscEstudiante inner join empresa em "
                        f"on em.id=fi.empIniEmpresa inner join responsable re on re.id=fi.resIniEmpresa where fi.id={id}")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_informe_final_empresa_para_generar_pdf(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select esc.nomEscuela,es.apeNomEstudiante,em.razSocEmpresa,fi.fechaInfFinEmpresa,re.apeNomResponsable, "
                        "fi.iniFinEmpresa,fi.finFinEmpresa,fi.objFinEmpresa,fi.horFinEmpresa,fi.resFinEmpresa, "
                        "fi.otrFinEmpresa,fi.selFirResFinEmpresa, re.carResponsable "
                        "from informefinalempresa fi inner JOIN estudiante es on es.id = fi.estuFinEmpresa "
                        "inner join escuelaprofesional esc on esc.id=es.codEscEstudiante inner join empresa em "
                        f"on em.id=fi.empFinEmpresa inner join responsable re on re.id=fi.respFinEmpresa where fi.id={id}")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def obtener_desempenio_generar_pdf(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("select es.apeNomEstudiante,esc.nomEscuela,fi.iniDesempenio,fi.finDesempenio,fi.areDesempenio, "
						"em.razSocEmpresa,em.dirEmpresa,re.apeNomResponsable,re.corResponsable,fi.firRepDesempenio, "
                        "fi.resuDesempenio,fi.conDesempenio,fi.fechaInfDesempenio "
                        "from desempenio fi inner JOIN estudiante es on es.id = fi.estuDesempenio "
                        "inner join escuelaprofesional esc on esc.id=es.codEscEstudiante inner join empresa em "
                        f"on em.id=fi.empDesempenio inner join responsable re on re.id=fi.respDesempenio where fi.id={id}")
        informe = cursor.fetchone()
    cursor.close()
    return informe

def eliminar_caracteristica(id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM caracteristicas WHERE id = %s", (id,))
    conexion.commit()
    conexion.close()
