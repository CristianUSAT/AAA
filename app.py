from flask import Flask, render_template, request, url_for , redirect, flash, jsonify, json, make_response,session,Response
import flask
import json
import os
from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, join_room, leave_room, emit
from werkzeug.utils import secure_filename
import requests
import hashlib
from hashlib import sha256
import random
from flask import g
import controladores.controlador_docente as controlador_docente
import controladores.controlador_estudiante as controlador_estudiante
import controladores.controlador_escuela as controlador_escuela
import controladores.controlador_administrador as controlador_administrador
import controladores.controlador_ppp as controlador_ppp
import controladores.controlador_facultad as controlador_facultad
import controladores.controlador_linea as controlador_linea
import controladores.controlador_chat as controlador_chat
import controladores.controlador_informes as controlador_informes
import controladores.controlador_empresa as controlador_empresa
import controladores.controlador_responsable as controlador_responsable
import controladores.controlador_plan as controlador_plan
import controladores.controlador_supervision as controlador_supervision
import controladores.controlador_semestre as controlador_semestre
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,PageBreak,ListFlowable,ListItem
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from io import BytesIO
import io
from datetime import datetime
from flask import send_file
from PIL import Image as PilImage
import controladores.controlador_horario as controlador_horario
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image,HRFlowable
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from xml.sax.saxutils import escape
from flask import send_file, flash, redirect
import io
import os


app = Flask(__name__)
app.debug = True
app.secret_key = 'ChamosMarlon'
jwt = JWTManager(app)
socketio = SocketIO(app)
UPLOAD_FOLDER = os.path.abspath('static/media/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Decorador para proteger rutas específicas por rol
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in allowed_roles:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Middleware global para verificar autenticación
@app.before_request
def verificar_autenticacion():
    rutas_publicas = ['/login', '/procesos-login', '/static', '/', ]
    if request.path not in rutas_publicas and 'role' not in session:
        return redirect(url_for('login'))

def ordenar(dir):
    sort = ['asc','desc']
    if dir == sort[0]:
        next_dir = sort[1]
    else:
        next_dir = sort[0]
    return next_dir

def obtener_lista(estudiantes, page, per_page,next_dir,columna):
    start = (page - 1) * per_page
    end = start + per_page
    estudiantes_paginados = estudiantes[start:end]
    if next_dir == 'asc':
        estudiantes_paginados = sorted(estudiantes_paginados, key=lambda x: x[columna])
    else:
        estudiantes_paginados = sorted(estudiantes_paginados, key=lambda x: x[columna], reverse=True)
    
    total_pages = (len(estudiantes) + per_page - 1) // per_page
    return estudiantes_paginados, total_pages

@app.route('/')
def inicio():
    return render_template('index.html')

@app.context_processor
def rol_usuario():
    username = request.cookies.get('username')
    token = request.cookies.get('token')
    docente = controlador_docente.obtener_docente(username)
    estudiante = controlador_estudiante.obtener_estudiante(username)
    administrador = controlador_administrador.obtener_administrador(username)
    
    if username:
        if docente and token == docente[5]:
            g.rol = 2
            g.user = docente[1]
            return dict(rol=2, user=docente[1])
        if estudiante and token == estudiante[9]:
            g.rol = 1
            g.user = estudiante[2]
            return dict(rol=1, user=estudiante[2])
        if administrador and token == administrador[4]:
            g.rol = 3
            g.user = administrador[1]
            return dict(rol=3, user=administrador[1])
    g.rol = 0
    return dict(rol=0)

@app.context_processor
def cargar_usuarios():
    user = request.cookies.get('username')
    if user:
        docente = controlador_docente.obtener_docente(user)
        estudiante = controlador_estudiante.obtener_estudiante(user)
        valor=[]
        if estudiante:
            valor = controlador_chat.buscar_mensajes('idEstudiante',estudiante[0],estudiante[2])
            docentes = controlador_chat.obtener_docentes(estudiante[0])
            if docentes:
                return {'lista_docentes': docentes,'valor':valor}
        elif docente:
            valor = controlador_chat.buscar_mensajes('idDocente',docente[0],docente[1])
            estudiantes = controlador_chat.obtener_estudiantes(docente[0])
            if estudiantes:
                return {'lista_estudiantes': estudiantes,'valor':valor}
    return {}

@app.route('/login')
def login():
    username = request.cookies.get('username')
    token = request.cookies.get('token')
    
    # Verifica si el usuario está autenticado
    if username and token:
        docente = controlador_docente.obtener_docente(username)
        estudiante = controlador_estudiante.obtener_estudiante(username)
        administrador = controlador_administrador.obtener_administrador(username)
        
        if (docente and token == docente[5]) or \
           (estudiante and token == estudiante[9]) or \
           (administrador and token == administrador[4]):
            # Si hay una sesión activa, redirige al logout
            return redirect('/logout')
    
    # Si no hay sesión activa, muestra el formulario de login
    return render_template('login.html')

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.set_cookie('token', '', expires=0)
    resp.set_cookie("username", '', expires=0)
    session.pop('role', None)
    session.clear()
    return resp

@app.route('/procesos-login', methods=["POST"])
def proceso_login():
    user = request.form["usuario"]
    con = request.form["contraseña"]
    usuarioD = controlador_docente.verificar_usuario(user,con)
    usuarioE = controlador_estudiante.verificar_usuario(user,con)
    usuarioA = controlador_administrador.verificar_usuario(user,con)
    mensaje = "Error en validacion"
    if usuarioD or usuarioE or usuarioA:
        t = hashlib.new('sha256')
        entale = random.randint(1,1024)
        strEntale = str(entale)
        t.update(bytes(strEntale, encoding = 'utf-8'))
        token = t.hexdigest()
        if usuarioD:
            session['role'] = 'docente'
            create_access_token(identity=user, additional_claims={"role": 'docente'})
            resp = make_response(redirect("/inicio-docente"))
            controlador_docente.actualizar_token(user,token)
        elif usuarioE:
            session['role'] = 'estudiante'
            resp = make_response(redirect("/inicio-estudiante"))
            controlador_estudiante.actualizar_token(user,token)
        elif usuarioA:
            session['role'] = 'admin'
            create_access_token(identity=user, additional_claims={"role": 'admin'})
            resp = make_response(redirect("/inicio-administrador"))
            controlador_administrador.actualizar_token(user,token)
        resp.set_cookie("username", user)
        resp.set_cookie('token', token)
        return resp
    else:
        return render_template('login.html',mensaje=mensaje)
    
@socketio.on('iniciar')
def iniciar_bandeja():
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            join_room(str(estudiante[0])+'999')
        elif docente:
            join_room(str(docente[0])+'999')


@app.route('/inicio-docente')
@role_required(['docente'])
def inicioDocente():
    return render_template('vistaDocente.html')
    
@app.route('/inicio-estudiante')
@role_required(['estudiante'])
def inicioEstudiante():
    return render_template('vistaEstudiante.html')

@app.route('/inicio-administrador')
@role_required(['admin'])
def inicioAdministrador():
    return render_template('vistaAdministrador.html')



@app.route('/misDatos')
@role_required(['estudiante'])
def misDatos():
    try:
        user = request.cookies.get('username') 
        estudiante = controlador_estudiante.obtener_estudiante(user)  
         
        if estudiante:
            nombre = 'GESTIONAR PPP'
            titulo = 'Mis datos Personales'
            return render_template('misDatos.html', titulo=titulo,nombre=nombre, estudiante=estudiante)
        else:
            flash("Estudiante no encontrado", "danger")
            
    except Exception as e:
        print(e)
        flash("Ocurrió un error al cargar el estudiante", "danger")
        


@app.route('/listaEscuela')
@role_required(['docente','admin'])
def listaEscuela():
    dir = request.args.get('dir','asc',type=str)
    error_message = session.pop('error_message', None)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)
    facultad = request.args.get('nomFacultad','0',type=str)
    nombre = 'MÓDULO ACADÉMICO'
    titulo= 'Gestionar escuelas'
    buscar = request.args.get('escuela','0',type=str)
    name='escuela'
    escuelas = controlador_escuela.obtener_escuelas(facultad,buscar)
    facultades = controlador_facultad.obtener_facultades(buscar)
    per_page = 8
    page = request.args.get('page', 1, type=int)

    escuelas_paginados, total_pages = obtener_lista(escuelas,page,per_page,next_dir,columna)
    return render_template('ListaEscuela.html',nombre=nombre,lista = escuelas_paginados,facultades=facultades, facultad=facultad,
                           next_dir=next_dir,titulo=titulo, total_pages=total_pages, page=page, buscar=buscar, name=name,error_message=error_message)

@app.route('/listaSemestre')
@role_required(['docente','admin'])
def listaSemestre():
    dir = request.args.get('dir','asc',type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)
    nombre = 'MÓDULO ACADÉMICO'
    titulo= 'Gestionar semestre'
    buscar = request.args.get('semestre','0',type=str)
    name='semestre'
    semestres = controlador_semestre.obtener_semestres(buscar)
    per_page = 8
    page = request.args.get('page', 1, type=int)

    semestre, total_pages = obtener_lista(semestres,page,per_page,next_dir,columna)
    return render_template('ListaSemestre.html',nombre=nombre,lista = semestre,next_dir=next_dir,titulo=titulo,
                             total_pages=total_pages, page=page, buscar=buscar, name=name)



@app.route('/listaFacultad')
@role_required(['docente','admin'])
def listaFacultad():
    dir = request.args.get('dir','asc',type=str)
    error_message = session.pop('error_message', None)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)
    nombre = 'MÓDULO ACADÉMICO'
    titulo= 'Gestionar facultades'
    buscar = request.args.get('facultad','0',type=str)
    facultades = controlador_facultad.obtener_facultades(buscar)
    name='facultad'
    per_page = 8
    page = request.args.get('page', 1, type=int)

    facultades_paginados, total_pages = obtener_lista(facultades,page,per_page,next_dir,columna)
    return render_template('ListaFacultad.html',nombre=nombre,lista = facultades_paginados,
                           next_dir=next_dir,titulo=titulo, total_pages=total_pages, page=page, buscar=buscar, name=name, error_message=error_message)

@app.route('/listaLinea')
@role_required(['docente','admin'])
def listaLinea():
    error_message = session.pop('error_message', None)
    dir = request.args.get('dir','asc',type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)
    escuela = request.args.get('nomEscuela','0',type=str)
    nombre = 'MÓDULO PPP'
    titulo= 'Gestionar línea de desarrollo'
    buscar = request.args.get('linea','0',type=str)
    linea = controlador_linea.obtener_lineas(escuela, buscar)
    name ='linea'
    escuelas = controlador_escuela.obtener_escuelasa(buscar)

    per_page = 8
    page = request.args.get('page', 1, type=int)

    linea_paginados, total_pages = obtener_lista(linea,page,per_page,next_dir,columna)
    return render_template('ListaLinea.html',nombre=nombre,lista = linea_paginados,escuelas=escuelas,escuela=escuela,
                                next_dir=next_dir,titulo=titulo, total_pages=total_pages, page=page,buscar=buscar, name=name, error_message=error_message)

@app.route('/listaPlan')
@role_required(['docente','admin'])
def listaPlan():
    dir = request.args.get('dir','asc',type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)
    escuela = request.args.get('nomEscuela','0',type=str)
    nombre = 'MÓDULO ACADÉMICO'
    titulo= 'Gestionar plan de estudio'
    buscar = request.args.get('plan','0',type=str)
    plan = controlador_plan.obtener_plans(escuela, buscar)
    name ='plan'
    escuelas = controlador_escuela.obtener_escuelasa(buscar)
    per_page = 8
    page = request.args.get('page', 1, type=int)
    plan_paginados, total_pages = obtener_lista(plan,page,per_page,next_dir,columna)
    return render_template('ListaPlan.html',nombre=nombre,plan = plan_paginados,escuelas=escuelas,escuela=escuela,
                                next_dir=next_dir,titulo=titulo, total_pages=total_pages, page=page,buscar=buscar, name=name)

@app.route('/listaEstudiante')
@role_required(['docente','admin'])
def listaEstudiante():
    try:
        error_message = session.pop('error_message', None)
        dir = request.args.get('dir','asc',type=str)
        next_dir = ordenar(dir)
        columna = request.args.get('columna',2,type=int)
        escuela = request.args.get('nomEscuela','0',type=str)
        buscar = request.args.get('estudiante','0',type=str)
        nombre = 'MÓDULO ACADÉMICO'
        titulo= 'Gestionar estudiantes'
        estudiantes = controlador_estudiante.obtener_estudiantes(escuela,buscar)
        escuelas = controlador_escuela.obtener_escuelas('0','0')
        name='estudiante'

        per_page = 8
        page = request.args.get('page', 1, type=int)

        estudiantes_paginados, total_pages = obtener_lista(estudiantes,page,per_page,next_dir,columna)
        return render_template('ListaEstudiante.html',nombre=nombre,lista = estudiantes_paginados,escuelas=escuelas,escuela=escuela,
                            next_dir=next_dir,titulo=titulo, total_pages=total_pages, page=page,buscar=buscar, name=name,error_message=error_message)
    except Exception as e:
        return 'Error en validacion' + e
    
@app.route('/listaPPP')
@role_required(['docente','admin'])
def listaPPP():
    dir = request.args.get('dir','asc',type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)
    escuela = request.args.get('nomEscuela','0',type=str)
    buscar = request.args.get('estudiante','0',type=str)
    nombre = 'MÓDULO PPP'
    titulo= 'Gestionar prácticas pre-profesionales'
    name='estudiante'
    estudiantes = controlador_estudiante.obtener_estudiantes(escuela,buscar)
    escuelas = controlador_escuela.obtener_escuelas('0','0')
    ppp = controlador_ppp.obtener_informes()
    tipo=[['Informe inicial estudiante',5],['Informe final estudiante',8],['Informe inicial empresa',11],
        ['Informe final empresa',14],['Ficha de desempeño',17]]
    per_page = 8
    page = request.args.get('page', 1, type=int)

    estudiantes_paginados, total_pages = obtener_lista(estudiantes,page,per_page,next_dir,columna)

    return render_template('ListaPPP.html',nombre=nombre,lista=estudiantes_paginados,titulo=titulo,escuela=escuela,tipo=tipo,
                        escuelas=escuelas,ppp=ppp,page=page,total_pages=total_pages, next_dir=next_dir,buscar=buscar, name=name)

@app.route('/lista-supervision')
@role_required(['docente', 'admin'])
def listaSuper():
    error_message = session.pop('error_message', None)
    dir = request.args.get('dir', 'asc', type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna', 2, type=int)
    buscar = request.args.get('estudiante', '0', type=str)
    escuelas = controlador_escuela.obtener_escuelasa(buscar)
    nombre = 'MÓDULO PPP'
    titulo = 'Gestionar supervisiones'
    name = 'estudiante'
    escuela = request.args.get('nomEscuela','0',type=str)
    estudiantes = controlador_estudiante.obtener_estudiantes(escuela, buscar)

    # Obtener lista de PPP para cada estudiante sin duplicados
    lista_ppp = controlador_supervision.obtener_lista_ppp()

    # Convertir cada tupla de PPP en un diccionario
    lista_ppp_dict = []
    for ppp in lista_ppp:
        ppp_dict = {
            'ppp_id': ppp[0],
            'numeroPPP': ppp[1],
            'iniPPP': ppp[2],
            'finPPP': ppp[3],
            'horas': ppp[4],
            'estudiante_id': ppp[5]
        }
        # Agregar supervisiones para el PPP específico
        ppp_dict['supervisiones'] = controlador_supervision.obtener_supervisiones_por_ppp(ppp_dict['ppp_id'])
        lista_ppp_dict.append(ppp_dict)

    per_page = 8
    page = request.args.get('page', 1, type=int)

    # Paginación de la lista de estudiantes
    estudiantes_paginados, total_pages = obtener_lista(estudiantes, page, per_page, next_dir, columna)

    return render_template('ListaSuper.html', nombre=nombre, lista=estudiantes_paginados, titulo=titulo,
                           ppp_lista=lista_ppp_dict, page=page, total_pages=total_pages, next_dir=next_dir, buscar=buscar, name=name, escuelas=escuelas, escuela=escuela, error_message=error_message)



@app.route('/supervisiones')
@role_required(['docente', 'admin'])
def lista_supervisiones():
    error_message = session.pop('error_message', None)
    supervisiones = controlador_supervision.obtener_supervisiones()
    return render_template('ListaSuper.html', supervisiones=supervisiones, error_message=error_message)

@app.route('/supervisiones/nueva/<int:superEstu>/<int:superPPP>', methods=['GET', 'POST'])
@role_required(['docente', 'admin'])
def nueva_supervision(superEstu,superPPP):
    error_message = session.pop('error_message', None)

    if request.method == 'POST':
        fecha = datetime.now().date()
        hora = datetime.now().time()
        superEmpr = request.form['superEmpr']
        ubicacion = request.form['ubicacion']
        responsable = request.form['responsable']
        area_desempenio = request.form['area_desempenio']
        funciones = request.form['funciones']
        observaciones = request.form['observaciones']
        firmaEstu = request.files.get('firmaEstu')
        firmaDoce = request.files.get('firmaDoce')
        firmaJefe = request.files.get('firmaJefe')
        
        
        # Llama a la función para crear la supervisión
        controlador_supervision.crear_supervision(
            int(superEstu), int(superPPP), fecha, hora, superEmpr, ubicacion, responsable, area_desempenio,
            funciones, observaciones, firmaEstu, firmaJefe, firmaDoce
        )
        
        # Redirige a la lista de supervisiones
        return redirect(url_for('listaSuper'))
    
    empresas = controlador_supervision.obtener_empresas()
    responsables = controlador_supervision.obtener_responsables()
    estudiantes = controlador_supervision.obtener_estudiantes()

    return render_template('NuevaSupervision.html', empresa=empresas, responsable=responsables, superEstu=superEstu, superPPP=superPPP, estudiantes=estudiantes, error_message=error_message)



@app.route('/supervisiones/editar/<int:id>', methods=['GET', 'POST'])
@role_required(['docente', 'admin'])
def editar_supervision(id):
    error_message = session.pop('error_message', None)
    superEstu = request.args.get('superEstu')
    superPPP = request.args.get('superPPP')
    supervisioon = controlador_supervision.obtener_supervision(id)
    
    if request.method == 'POST':
        # Usa los nombres de campo correctos
        superEmpr = request.form['superEmpr']  # Campo para la empresa
        ubicacion = request.form['ubicacion']  # Campo para la ubicación
        area_desempenio = request.form['area_desempenio']
        responsable = request.form['responsable']  # Campo para el responsable
        funciones = request.form['funciones']
        observaciones = request.form['observaciones']
        firmaEstu = request.files.get('firmaEstu')
        firmaDoce = request.files.get('firmaDoce')
        firmaJefe = request.files.get('firmaJefe')

                # Manejo de archivos de firmas (nuevo o existente)
        if firmaEstu and firmaEstu.filename != '':
            firmaEstu_path = controlador_supervision.guardar_archivo(firmaEstu, 'static/uploads/firmas')
        else:
            firmaEstu_path = supervisioon[11]  # Mantén la firma actual

        if firmaJefe and firmaJefe.filename != '':
            firmaJefe_path = controlador_supervision.guardar_archivo(firmaJefe, 'static/uploads/firmas')
        else:
            firmaJefe_path = supervisioon[12]

        if firmaDoce and firmaDoce.filename != '':
            firmaDoce_path = controlador_supervision.guardar_archivo(firmaDoce, 'static/uploads/firmas')
        else:
            firmaDoce_path = supervisioon[13]

        
        controlador_supervision.actualizar_supervision(
            id, superEmpr, ubicacion, area_desempenio, responsable,
            funciones, observaciones, firmaEstu_path, firmaJefe_path, firmaDoce_path
        )
        
        return redirect(url_for('listaSuper'))
    
    empresas = controlador_supervision.obtener_empresas()
    responsables = controlador_supervision.obtener_responsables()
    estudiantes = controlador_supervision.obtener_estudiantes()
    
    return render_template(
        'EditarSupervision.html', supervisioon=supervisioon, id=id,
        superEstu=superEstu, superPPP=superPPP, empresa=empresas, responsable=responsables, estudiantes=estudiantes, error_message=error_message
    )

@app.route('/caracteristica/eliminar/<int:id>', methods=['POST'])
@role_required(['docente', 'admin'])
def eliminar_caracteristica(id):
    try:
        controlador_informes.eliminar_caracteristica(id)  
        return jsonify({"success": True, "message": "Característica eliminada con éxito"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/supervisiones/eliminar/<int:id>', methods=['POST'])
@role_required(['docente', 'admin'])
def eliminar_supervision(id):
    controlador_supervision.eliminar_supervision(id)
    return redirect(url_for('listaSuper'))

@app.route('/supervisiones/ver/<int:id>', methods=['GET'])
@role_required(['docente', 'admin'])
def ver_supervision(id):
    error_message = session.pop('error_message', None)
    supervision = controlador_supervision.obtener_supervision(id)
    empresas = controlador_supervision.obtener_empresas()
    responsables = controlador_supervision.obtener_responsables()
    estudiantes = controlador_supervision.obtener_estudiantes()
    if supervision:
        return render_template('VerSupervision.html', supervision=supervision, empresas=empresas, responsable=responsables, estudiantes=estudiantes, error_message=error_message)
    else:
        return redirect(url_for('listaSuper'))

@app.route('/lista-informes')
def listarInformes():
    nombre = 'GESTIONAR PPP'
    username = request.cookies.get('username')
    estudiante = controlador_estudiante.obtener_estudiante(username)
    elemento=[]
    elemento.append(estudiante[0])
    titulo= 'Gestionar Documentos'
    ppp = controlador_ppp.obtener_informes()
    tipo=[['Informe inicial estudiante',5],['Informe final estudiante',8],['Informe inicial empresa',11],
          ['Informe final empresa',14],['Ficha de desempeño',17]]
    return render_template('ListaRegistroPPP.html',nombre=nombre,ppp=ppp,titulo=titulo,elemento=elemento, tipo=tipo)

@app.route('/editar/<string:tipo>/<int:id>/<int:idE>')
@role_required(['estudiante','admin','docente'])
def editar(id,tipo,idE):
    if tipo == 'Informe inicial estudiante':
        return editar_inicialE(id,idE)
    if tipo == 'Informe final estudiante':
        return editar_finalE(id,idE)
    if tipo == 'Informe inicial empresa':
        return editar_inicialEm(id,idE)
    if tipo == 'Informe final empresa':
        return editar_finalEm(id,idE)
    if tipo == 'Ficha de desempeño':
        return editar_desempenio(id,idE)
    return redirect('/lista-informes')

def editar_inicialE(id,idE):
    if idE==0:
        user = request.cookies.get('username')
        estudiante = controlador_estudiante.obtener_estudiante(user)
        empresa = controlador_estudiante.obtenerEmpresa(estudiante[0])
        responsable = controlador_responsable.obtener_responsables_por_estudiante(estudiante[0])
    else:
        empresa = controlador_estudiante.obtenerEmpresa(idE)
        responsable = controlador_responsable.obtener_responsables_por_estudiante(idE)

    print(session['role'])
    semestre = controlador_docente.obtener_semestres()
    docentes = controlador_docente.obtener_docentes()
    informe = controlador_informes.obtener_informe_inicial(id)
    plan = controlador_informes.obtener_plan(id)
    semanas_trabajo = (plan[2] or '').split(',')
    inicios_trabajo = (plan[3] or '').split(',')
    fines_trabajo = (plan[4] or '').split(',')
    actividades = (plan[5] or '').split(',')
    horas = (plan[6] or '').split(',')
    plan_trabajo = zip(semanas_trabajo, inicios_trabajo, fines_trabajo, actividades, horas)
    print(plan_trabajo)
    return render_template('InformeInicialEstudiante.html',informe=informe,semestres=semestre,plan=plan_trabajo,
                           empresa=empresa,responsable=responsable,docentes=docentes)

def editar_finalE(id,idE):
    if idE==0:
        user = request.cookies.get('username')
        estudiante = controlador_estudiante.obtener_estudiante(user)
        empresa = controlador_estudiante.obtenerEmpresa(estudiante[0])
    else:
        empresa = controlador_estudiante.obtenerEmpresa(idE)
    docentes = controlador_docente.obtener_docentes()
    informe = controlador_informes.obtener_informe_final(id)
    return render_template('InformeFinalEstudiante.html',informe=informe,empresa=empresa,docentes=docentes)

def editar_inicialEm(id,idE):
    if idE==0:
        user = request.cookies.get('username')
        estudiante = controlador_estudiante.obtener_estudiante(user)
        empresa = controlador_estudiante.obtenerEmpresa(estudiante[0])
        responsable = controlador_responsable.obtener_responsables_por_estudiante(estudiante[0])
    else:
        empresa = controlador_estudiante.obtenerEmpresa(idE)
        responsable = controlador_responsable.obtener_responsables_por_estudiante(idE)
    informe = controlador_informes.obtener_informe_inicial_empresa(id)
    return render_template('InformeInicialEmpresa.html',informe=informe,empresa=empresa,responsable=responsable)

def editar_finalEm(id,idE):
    if idE==0:
        user = request.cookies.get('username')
        estudiante = controlador_estudiante.obtener_estudiante(user)
        empresa = controlador_estudiante.obtenerEmpresa(estudiante[0])
        responsable = controlador_responsable.obtener_responsables_por_estudiante(estudiante[0])
    else:
        empresa = controlador_estudiante.obtenerEmpresa(idE)
        responsable = controlador_responsable.obtener_responsables_por_estudiante(idE)
    informe = controlador_informes.obtener_informe_final_empresa(id)
    return render_template('InformeFinalEmpresa.html',informe=informe,empresa=empresa,responsable=responsable)

def editar_desempenio(id,idE):
    if idE==0:
        user = request.cookies.get('username')
        estudiante = controlador_estudiante.obtener_estudiante(user)
        empresas = controlador_estudiante.obtenerEmpresa(estudiante[0])
        responsables = controlador_responsable.obtener_responsables_por_estudiante(estudiante[0])
    else:
        empresas = controlador_estudiante.obtenerEmpresa(idE)
        responsables = controlador_responsable.obtener_responsables_por_estudiante(idE)
    informe = controlador_informes.obtener_desempenio(id)
    docentes = controlador_docente.obtener_docentes()
    caracteristicas = controlador_informes.obtener_caracteristicas_por_informe(id)
    return render_template('desempenio.html',informe=informe,empresas=empresas,responsables=responsables,docentes=docentes,caracteristicas=caracteristicas)


@app.route('/guardar-inicial-estudiante/<int:id>',methods=["POST"])
@role_required(['estudiante','admin','docente'])
def guardar_inicialE(id):
    iforme = controlador_informes.obtener_informe_inicial(id)
    semestre = request.form["codSemIniEstudiante"]
    empresa = request.form["empIniEstudiante"]
    responsable = request.form["resIniEstudiante"]
    aceptacion = request.form["aceptacionEmpresa"]
    docente = request.form["docente"]
    fechaI = request.form["iniIniEstudiante"]
    fechaF = request.form["finIniEstudiante"]
    firmaE = request.files['firEstIniEstudiante']
    observaciones = request.form["observaciones"]

    if firmaE.filename != '':
        filenameE = secure_filename(firmaE.filename)
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameE)
        firmaE.save(ruta_completa)
    else:
        filenameE = iforme[8]
    firmaR = request.files['firResIniEstudiante']
    if firmaR.filename != '':
        filenameR = secure_filename(firmaR.filename)
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameR)
        firmaR.save(ruta_completa)  
    else:
        filenameR = iforme[9]
    
    controlador_informes.guardar_informeIE(semestre,empresa,responsable,aceptacion,fechaI,fechaF,filenameE,filenameR,docente,observaciones,id)
    semanas_trabajo = request.form.getlist("semTrabajo[]")
    inicios_trabajo = request.form.getlist("iniTrabajo[]")
    fines_trabajo = request.form.getlist("finTrabajo[]")
    actividades = request.form.getlist("actTrabajo[]")
    horas = request.form.getlist("horTrabajo[]")
    semanas_str = ",".join(semanas_trabajo)
    inicios_str = ",".join(inicios_trabajo)
    fines_str = ",".join(fines_trabajo)
    actividades_str = ",".join(actividades)
    horas_str = ",".join(horas)
    controlador_informes.guardar_plan(semanas_str,inicios_str,fines_str,actividades_str,horas_str,id)
    flash("Informe inicial del estudiante registrado correctamente", "success")
    if session['role'] == 'estudiante':
        return redirect('/lista-informes')
    else:
        return redirect('/listaPPP')
    

@app.route('/guardar-final-estudiante/<int:id>',methods=["POST"])
@role_required(['estudiante','admin','docente'])
def guardar_finalE(id):
    iforme = controlador_informes.obtener_informe_final(id)
    empresa = request.form["emprFinEstudiante"]
    introduccion = request.form["intFinEstudiante"]
    descripcion = request.form["descAreFinEstudiante"]
    labores = request.form["descLabFinEstudiante"]
    conclusiones = request.form["conFinEstudiante"]
    recomendaciones = request.form["recFinEstudiante"]
    biblio = request.form["bibFinEstudiante"]
    docente = request.form["docente"]
    observaciones = request.form["observaciones"]
    infraestfisica = request.form["infraestfisica"]
    infraesttecno = request.form["infraesttecno"]

    anexo = request.files['aneFinEstudiante']

    if anexo.filename != '':
        filename = secure_filename(anexo.filename)
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        anexo.save(ruta_completa)
    else:
        filename = iforme[9]
    controlador_informes.guardar_informeFE(empresa,introduccion,descripcion,labores,conclusiones,recomendaciones,biblio,filename,docente,observaciones,infraestfisica,infraesttecno,id)
    flash("Informe final del estudiante registrado correctamente", "success")
    if session['role'] == 'estudiante':
        return redirect('/lista-informes')
    else:
        return redirect('/listaPPP')

@app.route('/guardar-inicial-empresa/<int:id>',methods=["POST"])
@role_required(['estudiante','admin','docente'])
def guardar_inicialEm(id):
    iforme = controlador_informes.obtener_informe_inicial_empresa(id)
    empresa = request.form["empIniEmpresa"]
    responsable = request.form["resIniEmpresa"]
    finicio = request.form["iniIniEmpresa"]
    fin = request.form["finIniEmpresa"]
    aceptacion = request.form["aceIniEmpresa"]
    labores = request.form["labIniEmpresa"]
    sellos = request.files['selFirResIniEmpresa']
    observaciones = request.form["observaciones"]

    if sellos.filename != '':
        filenameSellos = secure_filename(sellos.filename)
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameSellos)
        sellos.save(ruta_completa)
    else:
        filenameSellos = iforme[9]
    anexo = request.files['aceAnexoIniEmpresa']
    if anexo.filename != '':
        filenameAnexo = secure_filename(anexo.filename)
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameAnexo)
        anexo.save(ruta_completa)
    else:
        filenameAnexo = iforme[7]

    controlador_informes.guardar_informeIEm(empresa,responsable,finicio,fin,aceptacion,filenameAnexo,labores,filenameSellos,observaciones,id)
    flash("Informe inicial de la empresa registrado correctamente", "success")
    if session['role'] == 'estudiante':
        return redirect('/lista-informes')
    else:
        return redirect('/listaPPP')

@app.route('/guardar-final-empresa/<int:id>',methods=["POST"])
@role_required(['estudiante','admin','docente'])
def guardar_finalEm(id):
    iforme = controlador_informes.obtener_informe_final_empresa(id)
    empresa = request.form["empFinEmpresa"]
    responsable = request.form["respFinEmpresa"]
    finicio = request.form["iniFinEmpresa"]
    fin = request.form["finFinEmpresa"]
    obj = request.form["objFinEmpresa"]
    hora = request.form["horFinEmpresa"]
    resp = request.form["resFinEmpresa"]
    otro = request.form["otrFinEmpresa"]
    sellos = request.files['selFirResFinEmpresa']
    observaciones = request.form["observaciones"]

    if sellos.filename != '':
        filenameSellos = secure_filename(sellos.filename)
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameSellos)
        sellos.save(ruta_completa)
    else:
        filenameSellos = iforme[10]
    controlador_informes.guardar_informeFEm(empresa,responsable,finicio,fin,obj,hora,resp,otro,filenameSellos,observaciones,id)
    flash("Informe final de la empresa registrado correctamente", "success")
    if session['role'] == 'estudiante':
        return redirect('/lista-informes')
    else:
        return redirect('/listaPPP')

@app.route('/guardar-desempenio/<int:id>', methods=["GET", "POST"])
@role_required(['estudiante', 'admin', 'docente'])
def guardar_desempenio(id):
    # Obtener datos iniciales
    iforme = controlador_informes.obtener_desempenio(id)
    caracteristicas_existentes = controlador_informes.obtener_caracteristicas_por_informe(id)
    print("Características obtenidas:", caracteristicas_existentes)
    if request.method == "POST":
        # Procesar los datos del formulario
        empresa = request.form["empDesempenio"]
        responsable = request.form["respDesempenio"]
        ini = request.form["iniDesempenio"]
        fin = request.form["finDesempenio"]
        docente = request.form["docente"]
        area = request.form["areDesempenio"]
        resultados = request.form["resuDesempenio"]
        conclu = request.form["conDesempenio"]
        
        # Procesar el archivo de firma si existe
        sellos = request.files['firRepDesempenio']
        if sellos.filename != '':
            filenameSellos = secure_filename(sellos.filename)
            ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameSellos)
            sellos.save(ruta_completa)
        else:
            filenameSellos = iforme[9]

        # Guardar o actualizar el informe de desempeño
        controlador_informes.guardar_desempenio(
            empresa, responsable, area, resultados, ini, fin, conclu, filenameSellos, docente, id
        )
        
        # Obtener las características seleccionadas
        nom_caracteristicas = request.form.getlist("nomCaracteristica[]")
        escalas = [request.form.get(f"escala_{i+1}") for i in range(len(nom_caracteristicas))]

        # Guardar o actualizar cada característica
        for idx, (nom, escala) in enumerate(zip(nom_caracteristicas, escalas)):
            if idx < len(caracteristicas_existentes):
                # Actualizar característica existente
                caracteristica_id = caracteristicas_existentes[idx][0]  
                controlador_informes.guardar_caracteristica(id, nom, escala, caracteristica_id)
            else:
                # Insertar nueva característica
                controlador_informes.guardar_caracteristica(id, nom, escala)
        flash("Desempeño registrado correctamente", "success")
        # Redirigir según el rol
        if session['role'] == 'estudiante':
            return redirect('/lista-informes')
        else:
            return redirect('/listaPPP')
    
    # Si el método es GET, renderizar el formulario
    return render_template(
        "editar_desempenio.html", 
        iforme=iforme, 
        caracteristicas=caracteristicas_existentes
    )




@app.route('/enviar-informe/<string:tipo>/<int:id>')
@role_required(['estudiante','admin'])
def enviar_informe(tipo,id):
    if tipo == 'Informe inicial estudiante':
        controlador_informes.editar_estado_inicialE(id,'Enviado','')
    if tipo == 'Informe final estudiante':
        controlador_informes.editar_estado_finalE(id,'Enviado','')
    if tipo == 'Informe inicial empresa':
        controlador_informes.editar_estado_inicialEm(id,'Enviado','')
    if tipo == 'Informe final empresa':
        controlador_informes.editar_estado_finalEm(id,'Enviado','')
    if tipo == 'Ficha de desempeño':
        controlador_informes.editar_estado_desempenio(id,'Enviado','')
    return redirect('/lista-informes')

@app.route('/aceptar-informe/<string:tipo>/<int:id>')
@role_required(['estudiante','docente','admin'])
def aceptar_informe(tipo,id):
    if tipo == 'Informe inicial estudiante':
        controlador_informes.editar_estado_inicialE(id,'Aceptado','')
    if tipo == 'Informe final estudiante':
        controlador_informes.editar_estado_finalE(id,'Aceptado','')
    if tipo == 'Informe inicial empresa':
        controlador_informes.editar_estado_inicialEm(id,'Aceptado','')
    if tipo == 'Informe final empresa':
        controlador_informes.editar_estado_finalEm(id,'Aceptado','')
    if tipo == 'Ficha de desempeño':
        controlador_informes.editar_estado_desempenio(id,'Aceptado','')
    return redirect('/listaPPP')

@app.route('/rechazar-informe/<string:tipo>/<int:id>',methods=['POST'])
@role_required(['docente','admin'])
def rechazar_informe(tipo,id):
    obs = request.form["observacion"]
    if tipo == 'Informe inicial estudiante':
        controlador_informes.editar_estado_inicialE(id,'Rechazado',obs)
    if tipo == 'Informe final estudiante':
        controlador_informes.editar_estado_finalE(id,'Rechazado',obs)
    if tipo == 'Informe inicial empresa':
        controlador_informes.editar_estado_inicialEm(id,'Rechazado',obs)
    if tipo == 'Informe final empresa':
        controlador_informes.editar_estado_finalEm(id,'Rechazado',obs)
    if tipo == 'Ficha de desempeño':
        controlador_informes.editar_estado_desempenio(id,'Rechazado',obs)
    return redirect('/listaPPP')

#metodo para agregar archivos
""" archivo = request.files['imagen']
    if archivo.filename != '':
        filename = secure_filename(archivo.filename)
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(ruta_completa) """


@app.route('/agregar-estudiante',methods=["POST"])
@role_required(['docente','admin'])
def agregarEstudiante():
    try:
        codigo=request.form["codigo"]
        nombres=request.form["nombres"]
        numero=request.form["numero"]
        correo=request.form["correo"]
        escuela=request.form["escuela"]
        contra=request.form["contra"]
        dni=request.form["dni"]
        estado=request.form.get('estado')
        if estado is not None:
            estado=1
        else:
            estado=0
        id = controlador_estudiante.agregar_estudiante(codigo,nombres,escuela,dni,numero,correo,estado,contra)
        claves = controlador_ppp.crear_informe(id)
        ppp=controlador_ppp.crear_ppp(id,claves[0],claves[1],claves[2],claves[3],claves[4])
        controlador_ppp.crear_cartas(id,ppp)
        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error
        session['error_message'] = 'Error agregar estudiante, use valores validos, evite duplicar valores de otros estudiantes'
        return redirect(request.referrer)

@app.route('/crear_ppp/<int:id>')
@role_required(['docente','admin'])
def crear_ppp(id):
    claves = controlador_ppp.crear_informe(id)
    ppp=controlador_ppp.crear_ppp(id,claves[0],claves[1],claves[2],claves[3],claves[4])
    controlador_ppp.crear_cartas(id,ppp)
    flash('PPP creada correctamente','success')
    return redirect(request.referrer)

@app.route('/eliminar_ppp/<int:id>',methods=["POST"])
@role_required(['docente','admin'])
def eliminar_ppp(id):
    controlador_ppp.eliminar_ppp(id)
    flash('PPP eliminada correctamente','success')
    return redirect(request.referrer)


@app.route('/editar-estudiante',methods=["POST"])
@role_required(['docente','admin'])
def editar_estudiante():
    try:
        id = request.form["idEstudiante"]
        codigo=request.form["codigo"]
        nombres=request.form["nombres"]
        numero=request.form["numero"]
        correo=request.form["correo"]
        escuela=request.form["escuela"]
        contra=request.form["contra"]
        dni=request.form["dni"]
        estado=request.form.get('estado')
        if estado is not None:
            estado=1
        else:
            estado=0
        controlador_estudiante.modificarEstudiante(codigo,nombres,escuela,dni,numero,correo,estado,contra,id)
        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error
        session['error_message'] = 'Error modificar estudiante, use valores validos'
        return redirect(request.referrer)

@app.route('/editar-semestre',methods=["POST"])
@role_required(['docente','admin'])
def editar_semestre():
    id = request.form["idSemestre"]
    codigo = request.form["codigoSemestre"]
    ini = request.form["fechaI"]
    fin = request.form["fechaF"]
    estado = request.form.get('estadoSemestre')
    if estado is not None:
        estado=1
    else:
        estado=0
    controlador_semestre.modificarSemestre(codigo,ini,fin,estado,id)
    return redirect(request.referrer)

@app.route('/agregar-semestre',methods=["POST"])
@role_required(['docente','admin'])
def agregar_semestre():
    codigo = request.form["codigoSemestre"]
    ini = request.form["fechaI"]
    fin = request.form["fechaF"]
    estado = request.form.get('estadoSemestre')
    if estado is not None:
        estado=1
    else:
        estado=0
    controlador_semestre.agregarSemestre(codigo,ini,fin,estado)
    return redirect(request.referrer)

@app.route('/eliminarsemestre/<int:id>',methods=["POST"])
def eliminarSemestre(id):
    try:
        
        controlador_semestre.eliminarSemestre(id)
        flash("Semestre eliminada correctamente", "success")
        return redirect(request.referrer)
    except Exception as e:
            session['error_message'] = 'Error al eliminar semestre.'
            flash("Hubo un error al eliminar la semestre, tiene datos relacionados", "error")
            return redirect(request.referrer)


@app.route('/agregar-escuela',methods=["POST"])
@role_required(['docente','admin'])
def agregarEscuela():
    try:
        nombre=request.form["nombre"]
        estado=request.form.get("estado")
        facultad=request.form["facultad"]
        if estado is not None:
            estado=1
        else:
            estado=0
        controlador_escuela.agregar_escuela(nombre,estado,facultad)
        flash("Escuela guardada correctamente", "success")
        return redirect(request.referrer)
    except Exception as e:
        session['error_message'] = 'Error al agregar escuela. Por favor, revise los datos e intente nuevamente.'
        flash("Hubo un error al guardar la escuela, revise los datos e intente nuevamente", "error")
        return redirect(request.referrer)
@app.route('/modificar-escuela',methods=["POST"])
@role_required(['docente','admin'])
def modificarEscuela():
    try:
            id=request.form["id"]
            nombre=request.form["nomEscuela"]
            estado = request.form.get('estado', '0')
            facultad=request.form["facultad"]
            if estado is not None:
                estado=1
            else:
                estado=0
            controlador_escuela.modificarEscuela(id,nombre,estado,facultad)
            flash("Escuela editada correctamente.", "success")
            return redirect(request.referrer)
    except Exception as e:
        session['error_message'] = 'Error al agregar escuela. Por favor, revise los datos e intente nuevamente.'
        flash("Hubo un error al editar la escuela", "error")
        return redirect(request.referrer)

@app.route('/agregar-linea',methods=["POST"])
@role_required(['docente','admin'])
def agregarLinea():
    try:
        nombre=request.form["nombre"]
        estado=request.form["estado"]
        escuela=request.form["escuela"]
        if estado is not None:
            estado=1
        else:
            estado=0
        controlador_linea.agregar_linea(nombre,estado,escuela)
        flash("Linea de desarrollo agregada correctamente.", "success")
        return redirect(request.referrer)
    except Exception as e:
        session['error_message'] = 'Error al agregar linea de desarrollo. Por favor, revise los datos e intente nuevamente.'
        flash("Hubo un error al editar la escuela", "error")
        return redirect(request.referrer)
    
@app.route('/agregar-plan',methods=["POST"])
@role_required(['docente','admin'])
def agregarPlan():
    nombre=request.form["nombre"]
    creditos=request.form["creditos"]
    estado=request.form["estado"]
    escuela=request.form["escuela"]
    if estado is not None:
        estado=1
    else:
        estado=0
    controlador_plan.agregar_plan(nombre,creditos,estado,escuela)
    return redirect(request.referrer)

@app.route('/agregar-facultad',methods=["POST"])
@role_required(['docente','admin'])
def agregarFacultad():
    try:
        nombre=request.form["nombre"]
        estado = request.form.get('estado', '0')
        controlador_facultad.agregar_facultad(nombre,estado)
        flash("Facultad guardada correctamente", "success")
        return redirect(request.referrer)
    except Exception as e:
        session['error_message'] = 'Error al agregar facultad. Por favor, revise los datos e intente nuevamente.'
        flash("Hubo un error al guardar la facultad", "error")
        return redirect(request.referrer)


@app.route('/cambiar-estado/<int:estado>/<int:id>')
@role_required(['docente','admin'])
def cambiarEstEstudiante(estado,id):
    if estado:
        controlador_estudiante.modificarEstEstudiante(0,id)
    else:
        controlador_estudiante.modificarEstEstudiante(1,id)
    return redirect(request.referrer)

@app.route('/cambiar-estado-semestre/<int:estado>/<int:id>')
@role_required(['docente','admin'])
def cambiarEstSemestre(estado,id):
    if estado:
        controlador_semestre.modificarEstSemestre(0,id)
    else:
        controlador_semestre.modificarEstSemestre(1,id)
    return redirect(request.referrer)

@app.route('/eliminar-estudiante/<int:id>',methods=["POST"])
def eliminarEstudiante(id):
    controlador_estudiante.eliminarEstudiante(id)
    return redirect(request.referrer)

@app.route('/cambiar-estado-escuela/<int:estado>/<int:id>')
def cambiarEstEscuela(estado,id):
    try:
        if estado:
            controlador_escuela.modificarEstEscuela(0,id)
        else:
            controlador_escuela.modificarEstEscuela(1,id)
        return redirect(request.referrer)
    except Exception as e:
        session['error_message'] = 'Error al agregar escuela. Por favor, revise los datos e intente nuevamente.'
        return redirect(request.referrer)
@app.route('/eliminar-escuela/<int:id>',methods=["POST"])
def eliminarEscuela(id):
    try:
        controlador_escuela.eliminarEscuela(id)
        flash("Escuela eliminada correctamente", "sucess")
        return redirect(request.referrer)   
    except Exception as e:            
        session['error_message'] = 'Error al eliminar escuela. Por favor, verifique la escuela que desea eliminar.'           
        flash("Hubo un error al eliminar la escuela, tiene datos relacionados", "error")
        return redirect(request.referrer)
@app.route('/cambiar-estado-facultad/<int:estado>/<int:id>')
def cambiarEstFacultad(estado,id):
    try:
        if estado:
            controlador_facultad.modificarEstFacultad(0,id)
        else:
            controlador_facultad.modificarEstFacultad(1,id)
        return redirect(request.referrer)
    except Exception as e:
            session['error_message'] = 'Error al agregar escuela. Por favor, revise los datos e intente nuevamente.'
            return redirect(request.referrer)

@app.route('/cambiar-estado-docente/<int:estado>/<int:id>')
def cambiarEstDocente(estado,id):
    if estado:
        controlador_docente.modificarEstDocente(0,id)
    else:
        controlador_docente.modificarEstDocente(1,id)
    return redirect(request.referrer)


@app.route('/eliminarfacultad/<int:id>',methods=["POST"])
def eliminarFacultad(id):
    try:
        controlador_facultad.eliminarFacultad(id)
        flash("Facultad eliminada correctamente", "success")
        return redirect(request.referrer)
    except Exception as e:
            session['error_message'] = 'Error al eliminar facultad. Por favor, verifique la facultad que desea eliminar'
            flash("Hubo un error al eliminar la facultad, tiene datos relacionados", "error")
            return redirect(request.referrer)
    
@app.route('/cambiar-estado-linea/<int:estado>/<int:id>')
def cambiarEstLinea(estado,id):
    if estado:
        controlador_linea.modificarEstLinea(0,id)
    else:
        controlador_linea.modificarEstLinea(1,id)
    return redirect(request.referrer)

@app.route('/cambiar-estado-plan/<int:estado>/<int:id>')
def cambiarEstPlan(estado,id):
    if estado:
        controlador_plan.modificarEstPlan(0,id)
    else:
        controlador_plan.modificarEstPlan(1,id)
    return redirect(request.referrer)


@app.route('/eliminar-linea/<int:id>',methods=["POST"])
@role_required(['docente', 'admin'])
def eliminarLinea(id):
    controlador_linea.eliminarLinea(id)
    return redirect(request.referrer)

@app.route('/eliminar-plan/<int:id>',methods=["POST"])
def eliminarPlan(id):
    controlador_plan.eliminarPlan(id)
    return redirect(request.referrer)

@app.route('/modificar-linea', methods=["POST"])
@role_required(['docente', 'admin'])
def modificarLinea():
    id = request.form["id"]
    nombre = request.form["nombre"]
    escuela = request.form["escuela"]
    estado = 1 if "estado" in request.form else 0
    controlador_linea.actualizarLinea(id, nombre, estado, escuela)
    return redirect(request.referrer)

@app.route('/modificar-plan', methods=["POST"])
def modificarPlan():
    id = request.form["id"]
    nombre = request.form["nombre"]
    creditos = request.form["creditos"]
    escuela = request.form["escuela"]
    estado = 1 if "estado" in request.form else 0
    controlador_plan.actualizarPlan(id, nombre, creditos, estado, escuela)
    return redirect(request.referrer)


@socketio.on('mensaje_chat')
def recibir_mensaje(mensaje_chat,id):
    user = request.cookies.get('username')
    respuesta_procesar_form = []
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            sala = str(id)+'999'+str(estudiante[0])
            print(sala)
            respuesta_procesar_form=controlador_chat.procesar_form_chat(mensaje_chat,estudiante[0],id,estudiante[2])
        elif docente:
            sala = str(docente[0])+'999'+str(id)
            print(sala)
            respuesta_procesar_form=controlador_chat.procesar_form_chat(mensaje_chat,id,docente[0],docente[1])
    emit('mensaje_chat',{'lista_mensajes': respuesta_procesar_form},room=sala)

@socketio.on('cargar_bandeja')
def bandeja_entra(id,emisor):
    user = request.cookies.get('username')
    if user:
        bandeja = str(id)+'999'
    emit('cargar_bandeja',{'id':emisor},room=bandeja)

@socketio.on('obtener_chats')
def obtener_chats(id):
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            mensajes=controlador_chat.lista_mensajes_chat(estudiante[0],id)
            emisor=estudiante[2]
        elif docente:
            mensajes=controlador_chat.lista_mensajes_chat(id,docente[0])
            emisor=docente[1]
    emit('obtener_chats',{'mensajes': mensajes,'emisor':emisor})

@socketio.on('entrar_sala')
def entrar_sala(id):
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            sala = str(id)+'999'+str(estudiante[0])
            print(sala)
        elif docente:
            sala = str(docente[0])+'999'+str(id)
            print(sala)
        join_room(sala)

@socketio.on('salir_sala')
def sali_sala(id):
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            sala = str(estudiante[0])+'999'+str(id)
        elif docente:
            sala = str(docente[0])+'999'+str(id)
        leave_room(sala)

@socketio.on('generar_visto')
def visto(id):
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            controlador_chat.actualizar_visto(estudiante[0],id,estudiante[2])
        elif docente:
            controlador_chat.actualizar_visto(id,docente[0],docente[1])



#### EMPRESA ####

def obtener_lista2(lista, page, per_page, next_dir, columna, tipo_tabla):
    columnas_validas = {
        'empresa': ['id', 'razSocEmpresa', 'dirEmpresa', 'girEmpresa', 'repreEmpresa'],
        'responsable': ['id', 'codEstResponsable', 'codEmpResponsable', 'apeNomResponsable', 
                        'carResponsable', 'telResponsable', 'corResponsable', 'horResponsable', 'nombre_empresa']
    }

    if tipo_tabla not in columnas_validas:
        raise ValueError("Tipo de tabla no válido")

    columnas = columnas_validas[tipo_tabla]

    if columna < 1 or columna > len(columnas):
        raise ValueError("Columna no válida para ordenación")

    columna_a_ordenar = columnas[columna - 1]
    columna_indices = {col: idx for idx, col in enumerate(columnas)}
    index_columna = columna_indices[columna_a_ordenar]

    lista_ordenada = sorted(lista, key=lambda x: x[index_columna], reverse=(next_dir == 'desc'))

    start = (page - 1) * per_page
    end = start + per_page
    lista_paginada = lista_ordenada[start:end]

    total_pages = len(lista) // per_page + (1 if len(lista) % per_page > 0 else 0)

    return lista_paginada, total_pages






@app.route('/listaEmpresas', methods=["GET", "POST"])
@role_required(['estudiante','admin','docente'])
def listaEmpresas():
    error_message = session.pop('error_message', None)
    dir = request.args.get('dir','asc',type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)
    
    buscar = request.args.get('empresa','0',type=str)
    nombre = 'GESTIONAR PPP'
    username = request.cookies.get('username')
    estudiante = controlador_estudiante.obtener_id_estudiante(username)
    titulo = 'Gestionar empresa'
    lista = controlador_estudiante.obtener_empresa2(estudiante,buscar)
    numero = 1

    name = 'empresa'

    # Paginación
    per_page = 8
    page = request.args.get('page', 1, type=int)

    empresas_paginados, total_pages = obtener_lista(lista, page, per_page, next_dir, columna)


    # Obtener todas las empresas
    empresas = controlador_empresa.obtener_empresas_no_vinculadas(estudiante)


    if request.method == "POST":
        empresa_id = request.form.get("empresa_id")
        
        # Relacionar la empresa con el estudiante
        controlador_empresa.agregar_empresa_estudiante(estudiante, empresa_id)
        flash("Empresa asociada exitosamente", "success")
        return redirect(request.referrer)

    return render_template('ListaEmpresa.html', nombre=nombre, lista=empresas_paginados, titulo=titulo, 
                           numero=numero, estudiante=estudiante, page=page, total_pages=total_pages, 
                           next_dir=next_dir, name=name, empresas=empresas,buscar=buscar, error_message=error_message)


@app.route('/agregarEmpresa', methods=["POST"])
@role_required(['estudiante','admin'])
def agregarEmpresa():
    try:
        username = request.cookies.get('username')
        estudiante = controlador_estudiante.obtener_id_estudiante(username)
        razSocEmpresa = request.form.get("razSocEmpresa")  
        dirEmpresa = request.form.get("dirEmpresa")   
        girEmpresa = request.form.get("girEmpresa")         
        repreEmpresa = request.form.get("repreEmpresa")  
        canTraEmpresa = request.form.get("canTraEmpresa")  
        visEmpresa = request.form.get("visEmpresa")  
        misEmpresa = request.form.get("misEmpresa")       
        orgEmpresa = request.files.get("orgEmpresa")   

        if orgEmpresa and orgEmpresa.filename != '':
            filenameOrganigrama = secure_filename(orgEmpresa.filename)
            ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameOrganigrama)
            orgEmpresa.save(ruta_completa)
        else:
            filenameOrganigrama = None

        id_generado = controlador_empresa.agregar_empresa(
            estudiante,
            razSocEmpresa,
            dirEmpresa,
            girEmpresa,
            repreEmpresa,
            canTraEmpresa,
            visEmpresa,
            misEmpresa,
            filenameOrganigrama
        )

        # Mensaje de éxito
        # flash("Empresa agregada exitosamente", "success")

        if id_generado:
            flash("Empresa agregada exitosamente", "success")
        else:
            flash("Error al agregar la empresa", "danger")

        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error
        flash("Error al agregar empresa. Por favor, revise los datos e intente nuevamente.", "danger")
        session['error_message'] = 'Error al agregar empresa. Por favor, revise los datos e intente nuevamente.'
        return redirect(request.referrer)



@app.route('/modificarEmpresa', methods=["POST"])
def modificarEmpresa():
    try:
        id = request.form["id"]
        razSocEmpresa = request.form["razSocEmpresa"]
        dirEmpresa = request.form["dirEmpresa"]
        girEmpresa = request.form["girEmpresa"]
        repreEmpresa = request.form["repreEmpresa"]
        canTraEmpresa = request.form["canTraEmpresa"]
        visEmpresa = request.form["visEmpresa"]
        misEmpresa = request.form["misEmpresa"]
        
        # Obtener la imagen actual de la empresa
        nombre_imagen_actual = controlador_empresa.obtener_imagen_actual(id)

        # Si se sube una nueva imagen
        orgEmpresa = request.files.get("orgEmpresa")

        if orgEmpresa and orgEmpresa.filename != '':
            # Si hay una nueva imagen, eliminar la antigua
            if nombre_imagen_actual and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen_actual)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen_actual))
            
            # Guardar la nueva imagen
            filenameOrganigrama = secure_filename(orgEmpresa.filename)
            ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameOrganigrama)
            orgEmpresa.save(ruta_completa)
            nuevo_nombre_imagen = filenameOrganigrama
        else:
            # Si no se sube una nueva imagen, mantener la actual
            nuevo_nombre_imagen = nombre_imagen_actual

        # Actualizar la empresa en la base de datos
        controlador_empresa.actualizar_empresa(
            id, razSocEmpresa, dirEmpresa, girEmpresa, 
            repreEmpresa, canTraEmpresa, visEmpresa, misEmpresa, 
            nuevo_nombre_imagen
        )
        flash("Empresa modificada exitosamente", "success")
        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error
        session['error_message'] = 'Error al modificar empresa. Por favor, revise los datos e intente nuevamente.'
        return redirect(request.referrer)


@app.route('/eliminar-empresa/<int:id>', methods=["POST"])
def eliminarEmpresa(id):
    try:
        # Obtener el nombre de la imagen actual de la empresa
        nombre_imagen = controlador_empresa.obtener_imagen_actual(id)

        # Eliminar la imagen de la carpeta de uploads si existe
        if nombre_imagen and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))

        # Eliminar la empresa de la base de datos
        controlador_empresa.eliminar_empresa(id)
        flash("Empresa eliminada", "success")
        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error
        flash('Error al eliminar empresa: No se puede eliminar porque está relacionada con algún estudiante.', 'danger')
        session['error_message'] = 'Error al eliminar empresa.'
        return redirect(request.referrer)
    

@app.route('/eliminar-rel-empresa/<int:id>', methods=["POST"])
def eliminarRelEmpresa(id):
    try:
        # Eliminar la relación de la empresa con los estudiantes en la base de datos
        controlador_empresa.eliminar_relacion_empresa_estudiante(id)
        flash("Relación de empresa con estudiantes eliminada", "success")
    except Exception as e:
        # Mensaje de error
        flash('Error al eliminar relación de empresa con estudiantes: ' + str(e), 'danger')
        
    return redirect(request.referrer)





@app.route('/listarEmpresas', methods=["GET", "POST"])
@role_required(['estudiante', 'admin'])
def listarEmpresas():
    error_message = session.pop('error_message', None)
    username = request.cookies.get('username')
    estudiante = controlador_estudiante.obtener_id_estudiante(username)
    
    # Obtener todas las empresas
    empresas = controlador_empresa.obtener_empresas()

    print("Empresas obtenidas:", empresas)

    if request.method == "POST":
        empresa_id = request.form.get("empresa_id")
        
        # Relacionar la empresa con el estudiante
        controlador_empresa.agregar_empresa_estudiante(estudiante, empresa_id)
        flash("Empresa asociada exitosamente", "success")
        return redirect(request.referrer)

    return render_template('ListaEmpresa.html', empresas=empresas, error_message=error_message)



########################



#########   EMPRESA DOCENTE  ############

@app.route('/listaEmpresasDoc', methods=["GET"])
@role_required(['admin','docente'])
def listaEmpresasDoc():
    error_message = session.pop('error_message', None)
    dir = request.args.get('dir','asc',type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)
    
    buscar = request.args.get('empresa','0',type=str)
    nombre = 'MÓDULO PPP'
    username = request.cookies.get('username')
    estudiante = controlador_estudiante.obtener_id_estudiante(username)
    titulo = 'Gestionar empresa'
    lista = controlador_empresa.obtener_empresasDoc2(buscar)
    numero = 1

    name = 'empresa'

    # Paginación
    per_page = 8
    page = request.args.get('page', 1, type=int)

    empresas_paginados, total_pages = obtener_lista(lista, page, per_page, next_dir, columna)

    return render_template('ListaEmpresa.html', nombre=nombre, lista=empresas_paginados, titulo=titulo, 
                           numero=numero, estudiante=estudiante, page=page, total_pages=total_pages, 
                           next_dir=next_dir, name=name,buscar=buscar, error_message=error_message)


@app.route('/agregarEmpresaDoc', methods=["POST"])
@role_required(['docente', 'admin'])
def agregarEmpresaDoc():
    try:
        razSocEmpresa = request.form.get("razSocEmpresa")  
        dirEmpresa = request.form.get("dirEmpresa")   
        girEmpresa = request.form.get("girEmpresa")         
        repreEmpresa = request.form.get("repreEmpresa")  
        canTraEmpresa = request.form.get("canTraEmpresa")  
        visEmpresa = request.form.get("visEmpresa")  
        misEmpresa = request.form.get("misEmpresa")       
        orgEmpresa = request.files.get("orgEmpresa")   

        if orgEmpresa and orgEmpresa.filename != '':
            filenameOrganigrama = secure_filename(orgEmpresa.filename)
            ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], filenameOrganigrama)
            orgEmpresa.save(ruta_completa)
        else:
            filenameOrganigrama = None

        id_generado = controlador_empresa.agregar_empresa_simple(
            razSocEmpresa,
            dirEmpresa,
            girEmpresa,
            repreEmpresa,
            canTraEmpresa,
            visEmpresa,
            misEmpresa,
            filenameOrganigrama
        )

        if id_generado:
            flash("Empresa agregada exitosamente", "success")
        else:
            flash("Error al agregar la empresa", "danger")

        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error
        flash("Error al agregar empresa. Por favor, revise los datos e intente nuevamente.", "danger")
        session['error_message'] = 'Error al agregar empresa. Por favor, revise los datos e intente nuevamente.'
        return redirect(request.referrer)

#########################################


####### EMPRESAS REPORTE #########

@app.route('/listarEmpresasReporte', methods=["GET", "POST"])
@role_required(['docente', 'admin'])
def listarEmpresasReporte():
    error_message = session.pop('error_message', None)
    
    nombre = 'MÓDULO PPP'  
    empresas = controlador_empresa.obtener_empresas_con_cantidad_estudiantes()
    
    return render_template('reporteEstudiantesxEmpresa.html', empresas=empresas, nombre=nombre, error_message=error_message)



##################################


###### Horario ########

@app.route('/horario')
@role_required(['estudiante','admin'])
def horario():
    try:
        user = request.cookies.get('username')
        estudiante_id = controlador_estudiante.obtener_id_estudiante(user)
        horarios = controlador_horario.obtener_horarios_por_estudiante(estudiante_id)

        # Imprimir los horarios en la terminal
        print("Horarios enviados al frontend:", horarios)

        nombre = 'GESTIONAR PPP'
        titulo = 'Mis datos Personales'
        return render_template('horarios.html', titulo=titulo, nombre=nombre, horarios=horarios)    

    except Exception as e:
        print(e)
        return redirect(request.referrer)


@app.route('/guardarHorario', methods=["POST"])
def guardar_horario():
    try:
        data = request.get_json()  
        horarios_seleccionados = data.get("horariosSeleccionados", [])
        
        username = request.cookies.get('username')
        estudiante_id = controlador_estudiante.obtener_id_estudiante(username)

        if not horarios_seleccionados:
            controlador_horario.eliminar_horario(estudiante_id)
            return jsonify({"message": "Horarios eliminados correctamente"}), 200

        print(horarios_seleccionados)

        controlador_horario.eliminar_horario(estudiante_id)

        for horario in horarios_seleccionados:
            dia = horario.get("dia")
            hora = horario.get("hora")

            if not dia or not hora:
                flash("Error: Datos de horario incompletos", "error")
                return jsonify({"error": "Datos de horario incompletos"}), 400

            controlador_horario.agregar_horario(estudiante_id, dia, hora)

        flash("Horarios guardados correctamente", "success")
        return jsonify({"message": "Horarios guardados correctamente"}), 200

    except Exception as e:
        flash(f"Error al guardar los horarios: {str(e)}", "error")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/obtener_horario/<int:estudiante_id>')
def obtener_horario(estudiante_id):
    try:

        horarios = controlador_horario.obtener_horarios_por_estudiante(estudiante_id)
        return jsonify({'horarios': horarios})

    except Exception as e:
        print("Error al obtener horarios:", e)
        return jsonify({'error': str(e)}), 500




########################

#### RESPONSABLE ####

@app.route('/listaResponsables', methods=["GET", "POST"] )
@role_required(['estudiante', 'admin','docente'])
def listaResponsables():
    error_message = session.pop('error_message', None)
    dir = request.args.get('dir','asc',type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)

    buscar = request.args.get('responsable','0',type=str)
    nombre = 'GESTIONAR PPP'
    username = request.cookies.get('username')
    estudiante = controlador_estudiante.obtener_id_estudiante(username)
    empresas = controlador_empresa.obtener_empresas_por_estudiante(estudiante)
    titulo = 'Gestionar responsable'
    lista = controlador_responsable.obtener_responsables_por_estudiante2(estudiante,buscar)
    numero = 1

    name ='responsable'
 
    # Paginación
    per_page = 8
    page = request.args.get('page', 1, type=int)

    responsables_paginados, total_pages = obtener_lista(lista, page, per_page, next_dir, columna)

    # Obtener los responsables no vinculados segun empresa
    responsables = controlador_responsable.obtener_responsables_por_empresa2(estudiante)

    if request.method == "POST":
        responsable = request.form.get("responsable_id")
        
        # Relacionar la empresa con el estudiante
        controlador_responsable.agregar_relacion_estudiante_responsable(estudiante, responsable)
        flash("Responsable asociado exitosamente", "success")
        return redirect(request.referrer)


    return render_template('ListaResponsable.html', nombre=nombre, lista=responsables_paginados, titulo=titulo, 
                           numero=numero, estudiante=estudiante, empresas=empresas, page=page, total_pages=total_pages, 
                           next_dir=next_dir, name=name, error_message=error_message,responsables=responsables)





@app.route('/agregarResponsable', methods=["POST"])
def agregarResponsable():
    try:
        username = request.cookies.get('username')
        estudiante = controlador_estudiante.obtener_id_estudiante(username)
        
        codEmpResponsable = request.form.get("codEmpResponsable")  
        apeNomResponsable = request.form.get("apeNomResponsable")   
        carResponsable = request.form.get("carResponsable")         
        telResponsable = request.form.get("telResponsable")  
        corResponsable = request.form.get("corResponsable")  
        horResponsable = request.form.get("horResponsable")  
        
        # Agregar el responsable a la tabla Responsable
        responsable_id = controlador_responsable.agregar_responsable(
            codEmpResponsable,
            apeNomResponsable,
            carResponsable,
            telResponsable,
            corResponsable,
            horResponsable
        )
        
        # Crear la relación entre el estudiante y el responsable
        controlador_responsable.agregar_relacion_estudiante_responsable(estudiante, responsable_id)

        flash('Responsable agregado exitosamente.', 'success')
        
        return redirect(request.referrer)  
    except Exception as e:
        # Mensaje de error
        flash('Error al agregar responsable. Por favor, revise los datos e intente nuevamente.', 'danger')
        session['error_message'] = 'Error al agregar responsable. Por favor, revise los datos e intente nuevamente.'
        return redirect(request.referrer)


@app.route('/modificarResponsable', methods=["POST"])
def modificarResponsable():
    try:
        id = request.form["id"]

        codEmpResponsable = request.form["codEmpResponsable"]
        apeNomResponsable = request.form["apeNomResponsable"]
        carResponsable = request.form["carResponsable"]
        telResponsable = request.form["telResponsable"]
        corResponsable = request.form["corResponsable"]
        horResponsable = request.form["horResponsable"]

        controlador_responsable.actualizar_responsable(
            id, codEmpResponsable, apeNomResponsable, 
            carResponsable, telResponsable, corResponsable, horResponsable
        )
        flash('Responsable modificado exitosamente.', 'success')
        return redirect(request.referrer)
    except Exception as e:
        flash('Error al modificar responsable. Por favor, revise los datos e intente nuevamente.', 'danger')
        return redirect(request.referrer)


##########Facultad

@app.route('/modificarFacultad', methods=["POST"])
def modificarFacultad():
    try:
        id = request.form["id"]  
        nomFacultad = request.form["nomFacultad"]
        estado = 1 if request.form.get('estado') else 0

        controlador_facultad.actualizarFacultad(
            nomFacultad, estado, id
        )
        flash("Facultad editada correctamente.", "sucess")
        return redirect(request.referrer)
    except Exception as e:
        session['error_message']= 'Error al modificar la facultad. Por favor, revise los datos e intente nuevamente'
        flash("Error al editar la facultad, revise los datos e intente nuevamente", "error")
        return redirect(request.referrer)


@app.route('/eliminarResponsable/<int:id>', methods=["POST"])
def eliminarResponsable(id):
    try:
        controlador_responsable.eliminar_responsable(id)
        flash('Responsable eliminado exitosamente.', 'success')
        return redirect(request.referrer)
    except Exception as e:
        flash('Error al eliminar responsable: No se puede eliminar porque está relacionada con algún estudiante.', 'danger')
        return redirect(request.referrer)


@app.route('/eliminarRelResponsable/<int:id>', methods=["POST"])
def eliminarRelResponsable(id):
    try:
        # Eliminar solo la relación en la tabla intermedia
        controlador_responsable.eliminar_relacion_estudiante_responsable(id)
        
        flash('Relación con el responsable eliminada exitosamente.', 'success')
        return redirect(request.referrer)
    except Exception as e:
        flash('Error al eliminar relación con el responsable. Por favor, intente nuevamente.', 'danger')
        return redirect(request.referrer)



##############


######### RESPONSABLE DOCENTE/ADMIN ################

@app.route('/listaResponsablesDoc')
@role_required(['docente', 'admin'])
def listaResponsablesDoc():
    error_message = session.pop('error_message', None)
    dir = request.args.get('dir','asc',type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna',2,type=int)

    buscar = request.args.get('responsable','0',type=str)
    nombre = 'MÓDULO PPP'

    empresas = controlador_empresa.obtener_empresas()  # Obtener todas las empresas
    titulo = 'Gestionar responsable'
    lista = controlador_responsable.obtener_todos_responsables(buscar)  # Obtener todos los responsables sin filtrar por estudiante
    numero = 1
    responsables = {}
    name = 'responsable'


    # Paginación
    per_page = 8
    page = request.args.get('page', 1, type=int)

    responsables_paginados, total_pages = obtener_lista(lista, page, per_page, next_dir, columna)

    return render_template('ListaResponsable.html', nombre=nombre, lista=responsables_paginados, titulo=titulo, 
                           numero=numero, empresas=empresas, page=page, total_pages=total_pages, 
                           next_dir=next_dir, name=name, error_message=error_message,responsables=responsables)


@app.route('/agregarResponsableDoc', methods=["POST"])
def agregarResponsableDoc():
    try:
        username = request.cookies.get('username')
        
        codEmpResponsable = request.form.get("codEmpResponsable")  
        apeNomResponsable = request.form.get("apeNomResponsable")   
        carResponsable = request.form.get("carResponsable")         
        telResponsable = request.form.get("telResponsable")  
        corResponsable = request.form.get("corResponsable")  
        horResponsable = request.form.get("horResponsable")  
        
        # Agregar el responsable a la tabla Responsable
        controlador_responsable.agregar_responsable(
            codEmpResponsable,
            apeNomResponsable,
            carResponsable,
            telResponsable,
            corResponsable,
            horResponsable
        )
        

        flash('Responsable agregado exitosamente.', 'success')
        
        return redirect(request.referrer)  
    except Exception as e:
        # Mensaje de error
        flash('Error al agregar responsable. Por favor, revise los datos e intente nuevamente.', 'danger')
        session['error_message'] = 'Error al agregar responsable. Por favor, revise los datos e intente nuevamente.'
        return redirect(request.referrer)

#################################################

@app.route('/relacionEmpresaResponsable')
@role_required(['docente','admin'])
def relacionEmpresaResponsable():
    try:
        error_message = session.pop('error_message', None)
        dir = request.args.get('dir','asc',type=str)
        next_dir = ordenar(dir)
        columna = request.args.get('columna',2,type=int)
        escuela = request.args.get('nomEscuela','0',type=str)
        buscar = request.args.get('estudiante','0',type=str)
        nombre = 'MÓDULO PPP'
        titulo= 'Relacionar empresa y responsable'
        estudiantes = controlador_estudiante.obtener_estudiantes(escuela,buscar)
        escuelas = controlador_escuela.obtener_escuelas('0','0')
        name='estudiante'

        per_page = 8
        page = request.args.get('page', 1, type=int)

        estudiantes_paginados, total_pages = obtener_lista(estudiantes,page,per_page,next_dir,columna)
        return render_template('relacionEmpresaResponsable.html',nombre=nombre,lista = estudiantes_paginados,escuelas=escuelas,escuela=escuela,
                            next_dir=next_dir,titulo=titulo, total_pages=total_pages, page=page,buscar=buscar, name=name,error_message=error_message)
    except Exception as e:
        return 'Error en validacion' + e

@app.route('/relacionEmpresa/<int:estudiante_id>')
@role_required(['docente', 'admin'])
def relacionEmpresa(estudiante_id):
    try:
        nombre = 'MÓDULO PPP'
        empresas_relacionadas, empresas_no_relacionadas = controlador_estudiante.obtenerEmpresasPorEstudiante(estudiante_id)
        return render_template('relacionEmpresa.html', estudiante_id=estudiante_id, empresas_relacionadas=empresas_relacionadas, empresas_no_relacionadas=empresas_no_relacionadas, nombre=nombre)
    except Exception as e:
        return f'Error al obtener las empresas: {e}'


@app.route('/relacionResponsable/<int:estudiante_id>', endpoint='relacionResponsable')
@role_required(['docente', 'admin'])
def relacionResponsable(estudiante_id):
    try:
        nombre = 'MÓDULO PPP'
        print(f"Estudiante ID recibido: {estudiante_id}")
        responsables_relacionados, responsables_no_relacionados = controlador_estudiante.obtenerResponsablesPorEstudiante(estudiante_id)
        return render_template('relacionResponsable.html', estudiante_id=estudiante_id, responsables_relacionados=responsables_relacionados, responsables_no_relacionados=responsables_no_relacionados,nombre=nombre)
    except Exception as e:
        print(f'Error al obtener los responsables: {e}')
        return f'Error al obtener los responsables: {e}'





@app.route('/asociar_empresa', methods=['POST'])
@role_required(['docente', 'admin'])
def asociar_empresa():
    estudiante_id = request.form['estudiante_id']
    empresa_id = request.form['empresa_id']
    try:

        controlador_estudiante.asociar_empresa(estudiante_id, empresa_id)
        flash('Empresa agregada exitosamente.', 'success')

        return redirect(url_for('relacionEmpresa', estudiante_id=estudiante_id))
    except Exception as e:
        flash('Error al agregar empresa.', 'error')
        return redirect(url_for('relacionEmpresa', estudiante_id=estudiante_id))


@app.route('/desasociar_empresa', methods=['POST'])
@role_required(['docente', 'admin'])
def desasociar_empresa():
    estudiante_id = request.form['estudiante_id']
    empresa_id = request.form['empresa_id']
    try:
        controlador_estudiante.desasociar_empresa(estudiante_id, empresa_id)
        flash('Se elimino la relación exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar la relación con empresa. Uno o mas responsables de la empresa estan relacionados con el estudiante', 'error')
    return redirect(url_for('relacionEmpresa', estudiante_id=estudiante_id))



@app.route('/asociar_responsable', methods=['POST'])
@role_required(['docente', 'admin'])
def asociar_responsable():
    estudiante_id = request.form['estudiante_id']
    responsable_id = request.form['responsable_id']
    try:
        controlador_estudiante.asociar_responsable(estudiante_id, responsable_id)
        flash('Responsable agregado exitosamente.', 'success')
    except Exception as e:
        flash('Error al agregar el responsable.', 'error')
    return redirect(url_for('relacionResponsable', estudiante_id=estudiante_id))


@app.route('/desasociar_responsable', methods=['POST'])
@role_required(['docente', 'admin'])
def desasociar_responsable():
    estudiante_id = request.form['estudiante_id']
    responsable_id = request.form['responsable_id']
    try:
        controlador_estudiante.desasociar_responsable(estudiante_id, responsable_id)
        flash('Se elimino la relación exitosamente.', 'success')
    except Exception as e:
        flash('Error al eliminar la relación con responsable', 'error')
    return redirect(url_for('relacionResponsable', estudiante_id=estudiante_id))





####################################################




@app.route('/generar-pdf-informe/<string:tipo>/<int:id>')
@role_required(['estudiante','admin','docente'])
def generar_pdf_informe(id,tipo):
    if tipo == 'Informe inicial estudiante':
        return generar_pdf_informe_inicial(id)
    if tipo == 'Informe final estudiante':
        return descargar_pdf_final_estudiante(id)
    if tipo == 'Informe inicial empresa':
        return descargar_pdf_inicial_empresa(id)
    if tipo == 'Informe final empresa':
        return descargar_pdf_final_empresa(id)
    if tipo == 'Ficha de desempeño':
        return descargar_desempenio(id)


def generar_pdf_informe_inicial(id):
    try:
        informe = controlador_informes.obtener_informe_inicial_para_generar_pdf(id)
        plan = controlador_informes.obtener_plan(id)
        datos = {
            "semestre": str(informe[1]),
            "empresa": str(informe[2]),
            "responsable": str(informe[3]),
            "aceptacion": str(informe[4]),
            "fecha_inicio": informe[5],
            "fecha_termino": informe[6],
            "firma_estudiante": os.path.join(app.config['UPLOAD_FOLDER'], informe[7]) if informe[7] else None,
            "firma_responsable": os.path.join(app.config['UPLOAD_FOLDER'], informe[8]) if informe[8] else None,
            "cargo": informe[9],
            "nombre_estudiante": informe[10],
            "labores": informe[11],
            "codigo": informe[12],
            "semanas_trabajo":plan[2].split(','),
            "inicios_trabajo":plan[3].split(','),
            "fines_trabajo":plan[4].split(','),
            "actividades":plan[5].split(','),
            "horas":plan[6].split(',')
        }

        pdf_buffer = generar_pdf(datos)

        # Asegurarse de que el buffer esté en el inicio
        pdf_buffer.seek(0)

        # Usar send_file para retornar el archivo PDF
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="informe_inicial_estudiante.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        flash('Faltan datos para generar pdf','error')
        return redirect(request.referrer)

def generar_pdf(datos):
    try:
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        content = []
        
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        title_style.alignment = 1
        content.append(Paragraph("INFORME INICIAL SOBRE PRÁCTICAS PRE PROFESIONALES", title_style))
        content.append(Paragraph("(ELABORADO POR EL ESTUDIANTE)", title_style))
        content.append(Spacer(1, 24))

        # Agregar el contenido detallado

        content.append(Paragraph("1. Nombres y apellidos del estudiante:", styles["Heading4"]))
        content.append(Paragraph(datos["nombre_estudiante"], styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("2. Código del estudiante:", styles["Heading4"]))
        content.append(Paragraph(datos["codigo"], styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("3. Semestre Académico:", styles["Heading4"]))
        content.append(Paragraph(datos["semestre"], styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("4. Empresa/Institución donde se realizará la práctica:", styles["Heading4"]))
        content.append(Paragraph(datos["empresa"], styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("5. Persona de la Empresa/Institución responsable de la práctica:", styles["Heading4"]))
        content.append(Paragraph(datos["responsable"], styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("6. Cargo que ocupa:", styles["Heading4"]))
        content.append(Paragraph(datos["cargo"], styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("7. Objetivos de la práctica:", styles["Heading4"]))

        # Saltos de linea
        aceptacion_lines = datos["aceptacion"].split('\n')
        for line in aceptacion_lines:
            content.append(Paragraph(line, styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("8. Fecha de inicio de la práctica:", styles["Heading4"]))
        content.append(Paragraph(datos["fecha_inicio"].strftime("%d/%m/%Y"), styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("9. Fecha de término de la práctica:", styles["Heading4"]))
        content.append(Paragraph(datos["fecha_termino"].strftime("%d/%m/%Y"), styles["BodyText"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph("10. Plan de trabajo:", styles["Heading4"]))

        semanas_trabajo = datos["semanas_trabajo"]  # Lista de semanas
        inicios_trabajo = datos["inicios_trabajo"]  # Lista de fechas de inicio
        fines_trabajo = datos["fines_trabajo"]  # Lista de fechas de fin
        actividades = datos["actividades"]  # Lista de actividades
        horas = datos["horas"]  # Lista de horas

        table_data = []
        table_data.append(["N° de semana", "Fecha de inicio", "Fecha de fin", "Actividades a realizar", "N° de horas"])
        for semana, inicio, fin, actividad, hora in zip(semanas_trabajo, inicios_trabajo, fines_trabajo, actividades, horas):
            table_data.append([semana, inicio, fin, actividad, hora])

        plan_table = Table(table_data)
        
        # Estilo de la tabla
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris para la cabecera
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco para la cabecera
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación centrada
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),  # Fuente negrita para todo
            ('FONTSIZE', (0, 0), (-1, -1), 12),  # Aumentar el tamaño de la fuente a 12
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Bordes de la tabla
            ('BOTTOMPADDING', (0, 0), (-1, 0), 18),  # Más espacio en el fondo de las celdas
            ('TOPPADDING', (0, 0), (-1, -1), 18),  # Más espacio en la parte superior
            ('LEFTPADDING', (0, 0), (-1, -1), 17),  # Más espacio a la izquierda
            ('RIGHTPADDING', (0, 0), (-1, -1), 17),  # Más espacio a la derecha
            ('ROWHEIGHT', (0, 0), (-1, -1), 25),  # Aumentar la altura de las filas
        ])

        plan_table.setStyle(table_style)

        # Agregar la tabla a los contenidos del PDF
        content.append(plan_table)

        content.append(Paragraph("11. Fecha y firma del estudiante y del responsable de la Empresa/Institución", styles["Heading4"]))
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        content.append(Paragraph(fecha_actual, styles["BodyText"]))
        content.append(Spacer(1, 12))

        # Verificar si las firmas existen y luego agregar las imágenes
        firma_estudiante_path = datos["firma_estudiante"]
        firma_responsable_path = datos["firma_responsable"]
        firma_estudiante_path = reducir_resolucion(firma_estudiante_path)
        firma_responsable_path = reducir_resolucion(firma_responsable_path)

        if firma_estudiante_path and firma_responsable_path:
            try:
                firma_table_data = [
                    [Image(firma_estudiante_path, width=150, height=80),"",
                    Image(firma_responsable_path, width=150, height=80)],
                    [f"Firma estudiante: {datos['nombre_estudiante']}","","Firma de la Empresa/Institución"]
                ]
                
                firma_table = Table(firma_table_data, colWidths=[150,15,150], rowHeights=[80, 30])
                firma_table.setStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TEXTCOLOR', (0, 1), (-1, 1), colors.gray),
                    ('SIZE', (0, 1), (-1, 1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),    # Espaciado a la izquierda de cada celda
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),   # Espaciado a la derecha de cada celda
                    ('TOPPADDING', (0, 0), (-1, -1), 12),     # Espaciado en la parte superior de cada celda
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ])
                content.append(firma_table)
            except Exception as e:
                print(f"Ocurrió un error al cargar las imágenes: {e}")
        

        pdf.build(content)
        buffer.seek(0)
        return buffer  # Retornar el buffer para send_file
    except Exception as e:
        flash('Faltan datos para generar pdf','error')
        return redirect(request.referrer)





def descargar_pdf_final_estudiante(id):
    try:
        # Buffer para crear el PDF en memoria
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=letter)
        detalle = []
        styles = getSampleStyleSheet()

        # Estilos de encabezado
        header_style = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, fontSize=14)
        header_style2 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontSize=12)
        normal_style = ParagraphStyle(name='Normal', parent=styles['Normal'], fontSize=11, spaceAfter=10,leading=15)
        normal_style2 = ParagraphStyle(name='Normal', parent=styles['Normal'], fontSize=11, spaceAfter=10, leftIndent=35)
        section_title_style = ParagraphStyle(name='SectionTitle', alignment=0, fontSize=12, fontName="Helvetica-Bold", spaceAfter=10, spaceBefore=20)
        sub_section_style = ParagraphStyle(name='SubSectionTitle', alignment=0, fontSize=12, fontName="Helvetica-Bold", spaceAfter=10, leftIndent=15)
        sub_section_style2 = ParagraphStyle(name='SubSectionTitle', alignment=0, fontSize=12, fontName="Helvetica-Bold", spaceAfter=5, leftIndent=25)
        # Obtener datos del informe
        informe = controlador_informes.obtener_informe_final_estudiante_para_generar_pdf(id)
        if not informe:
            raise ValueError("No se encontró el informe.")
        
        # Obtener datos de la empresa relacionada
        empresa = controlador_empresa.obtener_empresa_por_nombre(informe[2])

        # Imagen y encabezado
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], 'usat_doc.jpg')
        imagen = Image(imagen_path, width=250, height=250)
        header1 = Paragraph("INFORME FINAL ESTUDIANTE DE PRÁCTICAS PRE PROFESIONALES", header_style)
        detalle.append(imagen)
        detalle.append(Spacer(1, 20))
        detalle.append(header1)

        # Información inicial
        fecha = informe[3].strftime('%Y-%m-%d')
        header2 = Paragraph(f"ESCUELA PROFESIONAL DE {(informe[0]).upper()}", header_style2)
        header3 = Paragraph(f"NOMBRE Y APELLIDOS DEL ESTUDIANTE:<br/> {informe[1]}", header_style2)
        header4 = Paragraph(f"NOMBRE DE LA INSTITUCIÓN:<br/> {informe[2]}", header_style2)
        header5 = Paragraph(f"FECHA DE ENTREGA DEL INFORME:<br/> {fecha}", header_style2)
        detalle.extend([header2, Spacer(1, 20), header3, header4, header5])

        # Salto de página después de la imagen y la información inicial para el índice
        detalle.append(PageBreak())

        # Índice Estático
        index_title = Paragraph("ÍNDICE", header_style2)
        detalle.append(index_title)
        detalle.append(Spacer(1, 10))

        # Agregar el índice
        style_level_0 = ParagraphStyle(
            'Level0', parent=styles['Normal'], fontSize=12, spaceAfter=5)

        style_level_1 = ParagraphStyle(
            'Level1', parent=styles['Normal'], fontSize=12, leftIndent=20, spaceAfter=5)

        style_level_2 = ParagraphStyle(
            'Level2', parent=styles['Normal'], fontSize=12, leftIndent=40, spaceAfter=5)

        style_level_3 = ParagraphStyle(
            'Level3', parent=styles['Normal'], fontSize=12, leftIndent=60, spaceAfter=5)

        # Lista de elementos del índice con sus respectivos niveles de sangría
        index_items = [
            ("Introducción", 0),
            ("1. Descripción de la institución", 0),
            ("1.1. Datos de la Institución", 1),
            ("1.1.1. Razón Social", 2),
            ("1.1.2. Dirección", 2),
            ("1.1.3. Giro de la Institución", 2),
            ("1.1.4. Representante Legal de la Institución", 2),
            ("1.1.5. Cantidad de Trabajadores", 2),
            ("1.2. Visión", 1),
            ("1.3. Misión", 1),
            ("1.4. Infraestructura", 1),
            ("1.4.1. Infraestructura física", 2),
            ("1.4.2. Infraestructura tecnológica", 2),
            ("1.5. Organigrama", 1),
            ("2. Labores desarrolladas por el estudiante", 0),
            ("2.1. Descripción del área de trabajo y relaciones laborales", 1),
            ("2.2. Descripción de las labores realizadas", 1),
            ("3. Conclusiones", 0),
            ("4. Recomendaciones", 0),
            ("5. Bibliografía", 0),
            ("Anexos", 0),
        ]

        # Añadir los elementos del índice con los estilos correspondientes
        for item, level in index_items:
            if level == 0:
                style = style_level_0
            elif level == 1:
                style = style_level_1
            elif level == 2:
                style = style_level_2
            elif level == 3:
                style = style_level_3
            
            index_paragraph = Paragraph(item, style)
            detalle.append(index_paragraph)
            detalle.append(Spacer(1, 5))

        # Salto de página después del índice
        detalle.append(PageBreak())

        # Contenido principal (sin espaciado extra entre títulos y subtítulos)
        lista_contenido = [
            Paragraph("Introducción", section_title_style),
            Paragraph(f"{informe[4].replace('\n', '<br />')}", normal_style),
            Paragraph("1. Descripción de la institución", section_title_style),
            Paragraph("1.1. Datos de la Institución", sub_section_style),
            Paragraph("1.1.1. Razón Social", sub_section_style2),
            Paragraph(f"{empresa[1]}", normal_style2),
            Paragraph("1.1.2. Dirección", sub_section_style2),
            Paragraph(f"{empresa[2]}", normal_style2),
            Paragraph("1.1.3. Giro de la Institución", sub_section_style2),
            Paragraph(f"{empresa[3]}", normal_style2),
            Paragraph("1.1.4. Representante Legal de la Institución", sub_section_style2),
            Paragraph(f"{empresa[4]}", normal_style2),
            Paragraph("1.1.5. Cantidad de Trabajadores", sub_section_style2),
            Paragraph(f"{empresa[5]}", normal_style2),
            Paragraph("1.2. Visión", sub_section_style),
            Paragraph(f"{empresa[6].replace('\n', '<br />')}", normal_style2),
            Paragraph("1.3. Misión", sub_section_style),
            Paragraph(f"{empresa[7]}", normal_style2),
            Paragraph("1.4. Infraestructura", sub_section_style),
            Paragraph("1.4.1. Infraestructura física", sub_section_style2),
            Paragraph(f"{informe[11].replace('\n', '<br />')}", normal_style2),
            Paragraph("1.4.2. Infraestructura tecnológica", sub_section_style2),
            Paragraph(f"{informe[12].replace('\n', '<br />')}", normal_style2),
            Paragraph("1.5. Organigrama", sub_section_style),
            Spacer(1, 20),
        ]

        organigrama_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{empresa[8]}')
        if os.path.exists(organigrama_path):
            organigrama = Image(organigrama_path, width=350, height=350)
            lista_contenido.append(organigrama)
            lista_contenido.append(Spacer(1, 20))

        # Continuar con el resto del contenido
        lista_contenido.extend([
            Paragraph("2. Labores desarrolladas por el estudiante", section_title_style),
            Paragraph("2.1. Descripción del área de trabajo y relaciones laborales", sub_section_style),
            Paragraph(f"{informe[5].replace('\n', '<br />')}", normal_style2),
            Paragraph("2.2. Descripción de las labores realizadas", sub_section_style),
            Paragraph(f"{informe[6].replace('\n', '<br />')}", normal_style2),
            Paragraph("3. Conclusiones", section_title_style),
            Paragraph(f"{informe[7].replace('\n', '<br />')}", normal_style),
            Paragraph("4. Recomendaciones", section_title_style),
            Paragraph(f"{informe[8].replace('\n', '<br />')}", normal_style),
            Paragraph("5. Bibliografía", section_title_style),
            Paragraph(f"{informe[9].replace('\n', '<br />')}", normal_style),
            Paragraph("Anexos", section_title_style),
        ])
        detalle.extend(lista_contenido)

        # Agregar anexos
        anexos_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{informe[10]}')
        if os.path.exists(anexos_path):
            anexos = Image(anexos_path, width=400, height=400)
            detalle.append(anexos)
            detalle.append(Spacer(1, 20))

        # Crear el PDF
        doc.build(detalle)

       
        # Enviar el archivo
        buff.seek(0)
        return send_file(buff, as_attachment=True, download_name=f"informe_final_estudiante_{informe[1]}.pdf", mimetype='application/pdf')

    except Exception as e:
        flash(f"Error al generar el PDF: {str(e)}", "error")
        return redirect(request.referrer)





def reducir_resolucion(imagen_path, max_width=800):
    imagen = PilImage.open(imagen_path)  # Cambiado a PilImage
    # Redimensionar solo si la imagen es más ancha que el máximo permitido
    if imagen.width > max_width:
        proporcion = max_width / float(imagen.width)
        altura_nueva = int((float(imagen.height) * proporcion))
        # Usar el filtro LANCZOS para una reducción de calidad alta
        imagen = imagen.resize((max_width, altura_nueva), PilImage.LANCZOS)
        imagen.save(imagen_path, optimize=True, quality=85)  # Guardar con compresión
    return imagen_path

def descargar_pdf_inicial_empresa(id):
    try:
        # Buffer para crear el PDF en memoria
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=60)
        detalle = []
        styles = getSampleStyleSheet()

        # Estilos de encabezado
        header_style = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, fontSize=14)
        header_style2 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontSize=12)
        header_style3 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=2, spaceAfter=20, fontSize=20)
        header_style4 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=0, spaceAfter=15, fontSize=12)
        header_style5 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, spaceAfter=15, fontSize=14)
        informe = controlador_informes.obtener_informe_inicial_empresa_para_generar_pdf(id)
        # Imagen y encabezado
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], 'usat_doc.jpg')
        imagen = Image(imagen_path, width=250, height=250)
        header1 = Paragraph("INFORME INICIAL EMPRESA DE PRACTICAS PRE PROFESIONALES", header_style)
        detalle.append(imagen)
        detalle.append(Spacer(1, 20))
        detalle.append(header1)

        # Estilos de párrafo
        my_style = ParagraphStyle(name='MyStyle', parent=styles['Normal'], fontSize=11, textColor='black', alignment=0, spaceAfter=10)
        my_style1 = ParagraphStyle(name='MyStyle', parent=styles['Normal'], fontSize=11, textColor='black', alignment=TA_JUSTIFY, spaceAfter=10)

        
        if informe:
            
            fecha = informe[3].strftime('%Y-%m-%d')
            # Agregar contenido al PDF según los datos obtenidos
            header2 = Paragraph(f"ESCUELA PROFESIONAL DE {(informe[0]).upper()}", header_style2)
            header3 = Paragraph(f"NOMBRE Y APELLIDOS DEL ESTUDIANTE:<br/> {informe[1]}", header_style2)
            header4 = Paragraph(f"NOMBRE DE LA INSTITUCIÓN:<br/> {informe[2]}", header_style2)
            header5 = Paragraph(f"FECHA DE ENTREGA DEL INFORME:<br/> {fecha}", header_style2)
            detalle.extend([header2, Spacer(1, 20), header3, header4, header5, PageBreak()])

            anexos_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{informe[8]}')
            anexos = Image(anexos_path,width=560,height=500)
            firma_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{informe[10]}')
            firma = Image(firma_path,width=200,height=150)
            # Contenido adicional
            
            fecha_actual = datetime.now().strftime('%Y-%m-%d')  

            lista_contenido = [
                Paragraph("INFORME INICIAL SOBRE PRÁCTICAS PRE PROFESIONALES", ParagraphStyle(name='SectionTitle', alignment=1, fontSize=16, fontName="Helvetica-Bold", spaceAfter=20)),
                Paragraph("(ELABORADO POR LA EMPRESA/INSTITUCIÓN)", ParagraphStyle(name='SectionTitle', alignment=1, fontSize=16, fontName="Helvetica-Bold", spaceAfter=30)),
                Paragraph("1. Nombre de la Empresa/Institución", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15)),
                Paragraph(f"{informe[2]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("2. Persona de la Empresa/Institución responsable de la práctica", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15)),
                Paragraph(f"{informe[4]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("3. Cargo que ocupa", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15)),
                Paragraph(f"{informe[11]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("4. Nombres y apellidos y del estudiante", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15)),
                Paragraph(f"{informe[1]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("5. Fecha de inicio de la práctica", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15)),
                Paragraph(f"{informe[5]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("6. Fecha de término de la práctica", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15)),
                Paragraph(f"{informe[6]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("7. Aceptación por parte de la Empresa/Institución para la realización de la práctica y compromiso para atender al estudiante durante toda la ejecución", 
                          ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15,leading=15)),
                Paragraph(f"{informe[7].replace('\n', '<br />')}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10,leading=16)),
                Paragraph("8. Labores del practicante", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15)),
                Paragraph(f"{informe[9].replace('\n', '<br />')}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10,leading=16)),
                PageBreak(),
                Paragraph("9. Fecha, firma del responsable y sello de la Empresa/Institución", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10, spaceBefore=15)),
                Paragraph(f"Fecha del informe: {fecha_actual}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),
            ]
            detalle.extend(lista_contenido)
            detalle.append(firma)
            detalle.append(Paragraph(f"{informe[4]}", ParagraphStyle(name='NormalText', alignment=TA_CENTER, fontSize=12, spaceAfter=10)))
            detalle.append(PageBreak())
            detalle.append(Paragraph("Carta de aceptacion", ParagraphStyle(name='CenteredBold', alignment=1, fontSize=14, fontName="Helvetica-Bold",spaceAfter=10)))
            detalle.append(anexos)
            detalle.append(PageBreak())


        # Crear PDF y enviar como respuesta
        doc.build(detalle)
        buff.seek(0)
        return send_file(buff, as_attachment=True, download_name=f"informe_inicial_empresa_{informe[1]}.pdf", mimetype='application/pdf')
    except Exception as e:
        flash('Faltan datos para generar pdf','error')
        return redirect(request.referrer)

def descargar_pdf_final_empresa(id):
    try:

        # Buffer para crear el PDF en memoria
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=60)
        detalle = []
        styles = getSampleStyleSheet()
        # Estilos de encabezado
        header_style = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, fontSize=14)
        header_style2 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontSize=12)
        header_style3 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=2, spaceAfter=20, fontSize=20)
        header_style4 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=0, spaceAfter=15, fontSize=12)
        header_style5 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, spaceAfter=15, fontSize=14)
        normal_style = ParagraphStyle(name='NormalText', fontSize=12, fontName="Helvetica",spaceAfter=10)
        informe = controlador_informes.obtener_informe_final_empresa_para_generar_pdf(id)
        # Imagen y encabezado
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], 'usat_doc.jpg')
        imagen = Image(imagen_path, width=250, height=250)
        header1 = Paragraph("INFORME FINAL EMPRESA DE PRACTICAS PRE PROFESIONALES", header_style)
        detalle.append(imagen)
        detalle.append(Spacer(1, 20))
        detalle.append(header1)

        # Estilos de párrafo
        my_style = ParagraphStyle(name='MyStyle', parent=styles['Normal'], fontSize=11, textColor='black', alignment=0, spaceAfter=10)
        my_style1 = ParagraphStyle(name='MyStyle', parent=styles['Normal'], fontSize=11, textColor='black', alignment=TA_JUSTIFY, spaceAfter=10)

        
        if informe:        
            fecha = informe[3].strftime('%Y-%m-%d')
            # Agregar contenido al PDF según los datos obtenidos
            header2 = Paragraph(f"ESCUELA PROFESIONAL DE {(informe[0]).upper()}", header_style2)
            header3 = Paragraph(f"NOMBRE Y APELLIDOS DEL ESTUDIANTE:<br/> {informe[1]}", header_style2)
            header4 = Paragraph(f"NOMBRE DE LA INSTITUCIÓN:<br/> {informe[2]}", header_style2)
            header5 = Paragraph(f"FECHA DE ENTREGA DEL INFORME:<br/> {fecha}", header_style2)
            detalle.extend([header2, Spacer(1, 20), header3, header4, header5, PageBreak()])

            firma_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{informe[11]}')
            firma = Image(firma_path,width=200,height=150)
            # Contenido adicional
            fecha_actual = datetime.now().strftime('%Y-%m-%d')  

            lista_contenido = [
                Paragraph("INFORME FINAL SOBRE PRÁCTICAS PRE PROFESIONALES", ParagraphStyle(name='SectionTitle', alignment=1, fontSize=16, fontName="Helvetica-Bold", spaceAfter=20)),
                Paragraph("(ELABORADO POR LA EMPRESA/INSTITUCIÓN)", ParagraphStyle(name='SectionTitle', alignment=1, fontSize=16, fontName="Helvetica-Bold", spaceAfter=20)),
                Paragraph("1. Nombre de la Empresa/Institución", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10)),
                Paragraph(f"{informe[0]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("2. Persona de la Empresa/Institución responsable de la práctica", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10)),
                Paragraph(f"{informe[4]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("3. Cargo que ocupa", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10)),
                Paragraph(f"{informe[12]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("4. Nombres y apellidos y del estudiante", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10)),
                Paragraph(f"{informe[1]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("5. Fecha de inicio de la práctica", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10)),
                Paragraph(f"{informe[5]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("6. Fecha de término de la práctica", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10)),
                Paragraph(f"{informe[5]}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10)),
                Paragraph("7. Valoración sobre el trabajo realizado por el estudiante", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10)),
                Paragraph("- Cumplimiento de los objetivos:", ParagraphStyle(name='NormalText', alignment=0, fontSize=12, fontName="Helvetica",spaceAfter=10,leftIndent=15)),
                Paragraph(f"{informe[7].replace('\n', '<br />')}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10,leftIndent=25,leading=16)),
                Paragraph("- Cumplimiento del total de horas planificadas:", ParagraphStyle(name='NormalText', alignment=0, fontSize=12, fontName="Helvetica",spaceAfter=10,leftIndent=15)),
                Paragraph(f"{informe[8].replace('\n', '<br />')}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10,leftIndent=25,leading=16)),
                Paragraph("- Responsabilidad (disciplina, puntualidad, horarios, relaciones humanas, etc.):", ParagraphStyle(name='NormalText', alignment=0, fontSize=12, fontName="Helvetica",spaceAfter=10,leftIndent=15)),
                Paragraph(f"{informe[9].replace('\n', '<br />')}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10,leftIndent=25,leading=16)),
                Paragraph("- Algún otro aspecto de interés:", ParagraphStyle(name='NormalText', alignment=0, fontSize=12, fontName="Helvetica",spaceAfter=10,leftIndent=15)),
                Paragraph(f"{informe[10].replace('\n', '<br />')}", ParagraphStyle(name='NormalText', fontSize=12,spaceAfter=10,leftIndent=25,leading=16)),
                PageBreak(),
                Paragraph("8. Fecha, firma del responsable y sello de la Empresa/Institución", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=12, fontName="Helvetica-Bold",spaceAfter=10)),
                Paragraph(f"Fecha del informe: {fecha_actual}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),
            ]
            detalle.extend(lista_contenido)
            detalle.append(firma)
            detalle.append(Paragraph(f"{informe[2]}", ParagraphStyle(name='NormalText', alignment=TA_CENTER, fontSize=12, spaceAfter=10)))
            detalle.append(PageBreak())

        # Crear PDF y enviar como respuesta
        doc.build(detalle)
        buff.seek(0)
        return send_file(buff, as_attachment=True, download_name=f"informe_final_empresa_{informe[1]}.pdf", mimetype='application/pdf')
    except Exception as e:
        flash('Faltan datos para generar pdf','error')
        return redirect(request.referrer)

def descargar_desempenio(id):
    try:
        # Buffer para crear el PDF en memoria
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=60)
        detalle = []
        styles = getSampleStyleSheet()
        
        # Estilos de encabezado
        header_style = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, fontSize=14)
        header_style2 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontSize=12)
        header_style3 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=2, spaceAfter=20, fontSize=20)
        header_style4 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=0, spaceAfter=15, fontSize=12)
        header_style5 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, spaceAfter=15, fontSize=14)

        # Obtener los datos del informe
        informe = controlador_informes.obtener_desempenio_generar_pdf(id)
        caracteristicas = controlador_informes.obtener_caracteristicas_por_informe(id)

        # Imagen y encabezado
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], 'usat_doc.jpg')
        imagen = Image(imagen_path, width=250, height=250)
        header1 = Paragraph("INFORME INICIAL EMPRESA DE PRACTICAS PRE PROFESIONALES", header_style)
        detalle.append(imagen)
        detalle.append(Spacer(1, 20))
        detalle.append(header1)

        # Estilos de párrafo
        my_style = ParagraphStyle(name='MyStyle', parent=styles['Normal'], fontSize=11, textColor='black', alignment=0, spaceAfter=10)
        my_style1 = ParagraphStyle(name='MyStyle', parent=styles['Normal'], fontSize=11, textColor='black', alignment=TA_JUSTIFY, spaceAfter=10)

        # Ejemplo de cómo obtener datos (esto se debe reemplazar con la consulta real)
        if informe:
            fecha = informe[12].strftime('%Y-%m-%d')
            # Agregar contenido al PDF según los datos obtenidos
            header2 = Paragraph(f"ESCUELA PROFESIONAL DE {(informe[1]).upper()}", header_style2)
            header3 = Paragraph(f"NOMBRE Y APELLIDOS DEL ESTUDIANTE:<br/> {informe[0]}", header_style2)
            header4 = Paragraph(f"NOMBRE DE LA INSTITUCIÓN:<br/> {informe[5]}", header_style2)
            header5 = Paragraph(f"FECHA DE ENTREGA DEL INFORME:<br/> {fecha}", header_style2)
            detalle.extend([header2, Spacer(1, 20), header3, header4, header5, PageBreak()])

            # Imagen de la firma
            firma_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{informe[9]}')
            firma = Image(firma_path, width=200, height=100) 

            # Sección de resultados
            lista_contenido = [
                Paragraph("<u>Ficha de Evaluación del Desempeño del</u>", ParagraphStyle(name='SectionTitle', alignment=1, fontSize=14, fontName="Helvetica-Bold", spaceAfter=18)),
                Paragraph("<u>Prácticas Pre Profesionales</u>", ParagraphStyle(name='SectionTitle', alignment=1, fontSize=14, fontName="Helvetica-Bold", spaceAfter=18)),
                Paragraph("La Universidad Católica Santo Toribio de Mogrovejo (USAT) agradece la valiosa colaboracién de su Institución en la formaciån profesional de los estudiantes de nuestra casa de estudios.", ParagraphStyle(name='NormalText', fontSize=12, leading=13, alignment=TA_JUSTIFY)),
                Paragraph("El objetivo de esta evaluación es recoger información sobre el desempeño de nuestros estudiantes durante el periodo de prácticas pre profesionales. En tal sentido, le agradeceremos responderlade manera objetiva, ya que su opinion nos ayudará a mejorar el nivel de las Prácticas Pre profesionales que son requisito para la titulación de nuestros estudiantes.", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10, leading=13,alignment=TA_JUSTIFY)),
                Spacer(1, 12),  
                HRFlowable(width="100%", thickness=1, color="black", lineCap='round', spaceBefore=1, spaceAfter=1),
                Spacer(1, 12),  
                Paragraph("DATOS GENERALES", ParagraphStyle(name='SectionTitle', alignment=1, fontSize=13, fontName="Helvetica-Bold", spaceAfter=18)),
                
                Paragraph(f"<i><b>Nombres y apellidos del estudiante: </b></i>{informe[0]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),
                
                Paragraph(f"<i><b>Escuela Profesional: </b></i>{informe[1]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),
                
                Paragraph(f"<i><b>Periodo de prácticas: </b></i>Del {informe[2]} Al {informe[3]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),
                
                Paragraph(f"<i><b>Área de desempeño del estudiante: </b></i>{informe[4]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),

                Paragraph(f"<i><b>Nombre de la Empresa (Centro de prácticas): </b></i>{informe[5]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),

                Paragraph(f"<i><b>Dirección de la empresa: </b></i>{informe[6]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),

                Paragraph(f"<i><b>Nombre del responsable de la empresa: </b></i>{informe[7]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),

                Paragraph(f"<i><b>Correo electrónico del responsable de la empresa: </b></i>{informe[8]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)),
                Spacer(1, 12),  
                HRFlowable(width="100%", thickness=1, color="black", lineCap='round', spaceBefore=1, spaceAfter=1),
                Spacer(1, 12),  
            ]
            detalle.extend(lista_contenido)

            # Conclusiones (se añadirá después de la tabla)
            detalle.append(Spacer(1, 20))
            detalle.append(Paragraph("Conclusiones", ParagraphStyle(name='CenteredBold', alignment=0, fontSize=14, fontName="Helvetica-Bold", spaceAfter=10)))
            detalle.append(Paragraph(f"{informe[11]}", ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10)))

            # Insertar la tabla de características
            if caracteristicas:
                            data = [
                ["Características a evaluar", "Escala", "", "", ""],  # Primera fila
                ["", "Deficiente", "Regular", "Bueno", "Muy bueno"],  # Segunda fila
            ]

            for c in caracteristicas:
                try:
                    # Nombre de la característica y escala seleccionada
                    nom_caracteristica = c[1]  # Nombre de la característica
                    escala_seleccionada = c[2]  # Escala seleccionada

                    # Agregar una fila con la característica y las escalas
                    row = [
                        nom_caracteristica,
                        "X" if escala_seleccionada == "Deficiente" else "",
                        "X" if escala_seleccionada == "Regular" else "",
                        "X" if escala_seleccionada == "Bueno" else "",
                        "X" if escala_seleccionada == "Muy Bueno" else "",
                    ]
                    data.append(row)
                except IndexError as e:
                    print(f"Error al acceder a los elementos en caracteristicas: {e}")

            # Crear la tabla
            table = Table(data, colWidths=[3 * inch, inch, inch, inch, inch])

            # Estilo de la tabla
            table.setStyle(TableStyle([
                ('SPAN', (0, 0), (0, 1)),  # Combinar celdas de "Características a evaluar"
                ('SPAN', (1, 0), (-1, 0)),  # Combinar celdas de "Escala"
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris para la primera fila
                ('BACKGROUND', (0, 1), (-1, 1), colors.grey),  # Fondo gris claro para la segunda fila
                ('TEXTCOLOR', (0, 1), (-1, 1), colors.whitesmoke),  # Texto blanco para la segunda fila
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco para la primera fila
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinear texto al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Negrita en la primera fila
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espaciado inferior en la primera fila
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Bordes de la tabla
            ]))

            # Añadir la tabla al contenido del PDF
            detalle.append(Spacer(1, 20))  # Espaciado antes de la tabla
            detalle.append(table)  # Insertar la tabla

            detalle.append(Spacer(1, 20))
            detalle.append(Paragraph("Firma", ParagraphStyle(name='CenteredBold', alignment=1, fontSize=14, fontName="Helvetica-Bold", spaceAfter=10)))
            detalle.append(firma)
            detalle.append(PageBreak())

        # Crear PDF y enviar como respuesta
        doc.build(detalle)
        buff.seek(0)
        
        return send_file(buff, as_attachment=True, download_name=f"ficha_desempenio_{informe[0]}.pdf", mimetype='application/pdf')

    except Exception as e:
        flash('Faltan datos para generar pdf', 'error')
        return redirect(request.referrer)


@app.route('/guardar-ppp/<int:id>', methods=["POST"])
def guardar_ppp(id):
    try:
        semestreI = request.form["semestreI"]
        semestrF = request.form["semestreF"]
        horas = request.form["horas"]
        ini = request.form["iniPPP"]
        fin = request.form["finPPP"]
        linea = request.form["linea"]
        area = request.form["arePPP"]
        docente = request.form["docente"]
        
        # Actualizar la PPP
        controlador_ppp.actualizar_ppp(id, semestreI, semestrF, horas, ini, fin, linea, area, docente)
        
        # Mensaje de éxito
        flash('PPP guardado exitosamente', 'success')
        
        # Redirigir según el rol del usuario
        if session['role'] == 'estudiante':
            return redirect('/lista-informes')
        else:
            return redirect('/listaPPP')
    except Exception as e:
        # Mensaje de error
        session['error_message'] = 'Error al guardar PPP. Por favor, revise los datos e intente nuevamente.'
        return redirect(request.referrer)



#### DOCENTE ####

@app.route('/listaDocentes')
def listaDocentes():
    error_message = session.pop('error_message', None)
    dir = request.args.get('dir', 'asc', type=str)
    next_dir = ordenar(dir)
    columna = request.args.get('columna', 2, type=int)

    nombre = 'MÓDULO PERSONAL'

    buscar = request.args.get('docente','0',type=str)
    titulo = 'Gestionar docente'
    lista = controlador_docente.obtener_docentes2(buscar)
    numero = 1

    name = 'docente'

    per_page = 8
    page = request.args.get('page', 1, type=int)

    docentes_paginados, total_pages = obtener_lista(lista, page, per_page, next_dir, columna)


    return render_template('ListaDocente.html', nombre=nombre, lista=docentes_paginados, titulo=titulo, numero=numero,
                             page=page, total_pages=total_pages, next_dir=next_dir, name=name,buscar=buscar, error_message=error_message)



@app.route('/agregarDocente', methods=["POST"])
def agregarDocente():
    try:
        apeNomDocente = request.form.get("apeNomDocente")
        dniDocente = request.form.get("dniDocente")
        corDocente = request.form.get("corDocente")
        estDocente = request.form.get('estDocente', '0')
        passDocente = request.form.get("passDocente")

        controlador_docente.agregar_docente(
            apeNomDocente,
            dniDocente,
            corDocente,
            estDocente,
            passDocente
        )
        flash("Docente agregado exitosamente", "success")
        return redirect(request.referrer)
    except ValueError as ve:
        error_type, error_msg = ve.args
        if error_type == "duplicate_entry":
            if "dniDocente" in error_msg:
                flash("Error: El DNI ya está registrado", "danger")
            elif "corDocente" in error_msg:
                flash("Error: El correo electrónico ya está registrado", "danger")
            else:
                flash("Error: Datos duplicados", "danger")
        else:
            flash("Error al agregar docente", "danger")
        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error genérico
        flash("Error al agregar docente", "danger")
        return redirect(request.referrer)

@app.route('/modificarDocente', methods=["POST"])
def modificarDocente():
    try:
        id = request.form["id"]
        apeNomDocente = request.form["apeNomDocente"]
        dniDocente = request.form["dniDocente"]
        corDocente = request.form["corDocente"]

        estDocente = 1 if request.form.get('estado') else 0
        passDocente = request.form["passDocente"]

        controlador_docente.actualizar_docente(
            id, apeNomDocente, dniDocente, corDocente, estDocente, passDocente
        )
        flash("Docente actualizado exitosamente", "success")
        return redirect(request.referrer)
    except ValueError as ve:
        error_type, error_msg = ve.args
        if error_type == "duplicate_entry":
            if "dniDocente" in error_msg:
                flash("Error: El DNI ya está registrado", "danger")
            elif "corDocente" in error_msg:
                flash("Error: El correo electrónico ya está registrado", "danger")
            else:
                flash("Error: Datos duplicados", "danger")
        else:
            flash("Error al modificar docente", "danger")
        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error genérico
        session['error_message'] = 'Error al modificar docente. Por favor, revise los datos e intente nuevamente.'
        return redirect(request.referrer)



@app.route('/eliminarDocente/<int:id>', methods=["POST"])
def eliminarDocente(id):
    try:
        controlador_docente.eliminar_docente(id)
        flash("Docente eliminado", "success")
        return redirect(request.referrer)
    except Exception as e:
        # Mensaje de error
        flash("Error al eliminar docente", "danger")
        session['error_message'] = 'Error al eliminar docente. '
        return redirect(request.referrer)

@app.route('/editar_ppp/<int:id>')
def editarPPP(id):
    error_message = session.pop('error_message', None)
    ppp = controlador_ppp.obtener_ppp_estudiante(id)
    semestre = controlador_docente.obtener_semestres()
    linea = controlador_linea.obtener_lineas('0','0')
    docente = controlador_docente.obtener_docentes()
    return render_template('editarPPP.html',ppp=ppp,semestre=semestre,linea=linea,docente=docente, error_message=error_message)


#TRANSACCION

@app.route('/rechazar_ppp/<int:id>/<int:idE>')
def rechazar_ppp(id,idE):
    controlador_ppp.cambiar_ppp(id,'Rechazada')
    controlador_estudiante.modificarEstEstudiante(1,idE)
    claves = controlador_ppp.crear_informe(idE)
    ppp=controlador_ppp.crear_ppp(idE,claves[0],claves[1],claves[2],claves[3],claves[4])
    controlador_ppp.crear_cartas(idE,ppp)
    flash("PPP rechazada, generando una nueva", "success")
    return redirect(request.referrer)

@app.route('/transaccion/<int:id>/<int:idE>')
def transaccion(id,idE):
    ppp = controlador_ppp.transaccion_ppp(id)
    if ppp:
        for valor in ppp[2:7]:
            if valor != 'Aceptado':
                flash("Faltan documentos por aceptar", "error")
                return redirect(request.referrer)
    if ppp[0] > 0:
        claves = controlador_ppp.crear_informe(idE)
        pp=controlador_ppp.crear_ppp(idE,claves[0],claves[1],claves[2],claves[3],claves[4])
        print('ESTIANTE: ',pp)
        controlador_ppp.crear_cartas(idE,pp)
        flash("Faltan horas para completar PPP, generando nueva PPP", "warning")
        controlador_estudiante.modificarEstEstudiante(1,idE)
    else:
        flash("PPP aceptada, cambiando estado de estudiante", "success")
        controlador_estudiante.modificarEstEstudiante(0,idE)
    controlador_ppp.cambiar_ppp(id,'Aceptado')
    return redirect(request.referrer)


#####################

#####################REPORTES#################

@app.route('/reporte_cantidad_linea')
@role_required(['docente', 'admin'])
def reporte_lineas():
    try:
        dir = request.args.get('dir', 'asc', type=str)
        next_dir = ordenar(dir)
        columna = request.args.get('columna', 1, type=int)
        per_page = 8
        page = request.args.get('page', 1, type=int)

        nombre = "MÓDULO PPP"
        titulo = "Reporte cantidad de PPPs por línea de desarrollo y estado"
        datos_reporte = controlador_linea.reporteCantidadPorLinea()

        print("Datos obtenidos del reporte:", datos_reporte)  # Depuración

        datos_paginados, total_pages = obtener_lista_reporte(datos_reporte, page, per_page, next_dir, columna)

        return render_template(
            'reporteCantidadLineaEstado.html',
            nombre=nombre,
            datosReporte=datos_paginados,
            titulo=titulo,
            total_pages=total_pages,
            page=page,
            next_dir=next_dir,
            enumerate=enumerate
        )
    except Exception as e:
        return f"Error al cargar el reporte: {e}"





def obtener_lista_reporte(lista, page, per_page, dir, columna):
    try:

        lista_ordenada = sorted(lista, key=lambda x: x[columna - 1], reverse=(dir == 'desc'))
        

        total_items = len(lista_ordenada)
        total_pages = (total_items + per_page - 1) // per_page
        inicio = (page - 1) * per_page
        fin = inicio + per_page

        return lista_ordenada[inicio:fin], total_pages
    except Exception as e:
        raise ValueError(f"Error al procesar la lista para la paginación: {e}")
    
# AUXILIARES
def recibir_mensajeA(mensaje_chat,id):
    user = request.cookies.get('username')
    respuesta_procesar_form = []
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            sala = str(id)+'999'+str(estudiante[0])
            respuesta_procesar_form=controlador_chat.procesar_form_chat(mensaje_chat,estudiante[0],id,estudiante[2])
        elif docente:
            sala = str(id)+'999'+str(docente[0])
            respuesta_procesar_form=controlador_chat.procesar_form_chat(mensaje_chat,id,docente[0],docente[1])
    emit('mensaje_chat',{'lista_mensajes': respuesta_procesar_form},room=sala)

def bandeja_entraA(id,emisor):
    user = request.cookies.get('username')
    if user:
        bandeja = str(id)+'999'
    emit('cargar_bandeja',{'id':emisor},room=bandeja)

def obtener_chatsA(id):
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            mensajes=controlador_chat.lista_mensajes_chat(estudiante[0],id)
            emisor=estudiante[2]
        elif docente:
            mensajes=controlador_chat.lista_mensajes_chat(id,docente[0])
            emisor=docente[1]
    emit('obtener_chats',{'mensajes': mensajes,'emisor':emisor})

def entrar_salaA(id):
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            sala = str(estudiante[0])+'999'+str(id)
        elif docente:
            sala = str(docente[0])+'999'+str(id)
        join_room(sala)

def sali_salaA(id):
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            sala = str(estudiante[0])+'999'+str(id)
        elif docente:
            sala = str(docente[0])+'999'+str(id)
        leave_room(sala)

def vistoA(id):
    user = request.cookies.get('username')
    if user:
        estudiante = controlador_estudiante.obtener_estudiante(user)
        docente = controlador_docente.obtener_docente(user)
        if estudiante:
            controlador_chat.actualizar_visto(estudiante[0],id,estudiante[2])
        elif docente:
            controlador_chat.actualizar_visto(id,docente[0],docente[1])

def descargar_pdf_final_estudianteA(id):
    try:
        # Buffer para crear el PDF en memoria
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=letter)
        detalle = []
        styles = getSampleStyleSheet()

        # Estilos de encabezado
        header_style = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, fontSize=14)
        header_style2 = ParagraphStyle(name='Header', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontSize=12)
        normal_style = ParagraphStyle(name='Normal', parent=styles['Normal'], fontSize=11, spaceAfter=10,leading=15)
        normal_style2 = ParagraphStyle(name='Normal', parent=styles['Normal'], fontSize=11, spaceAfter=10, leftIndent=35)
        section_title_style = ParagraphStyle(name='SectionTitle', alignment=0, fontSize=12, fontName="Helvetica-Bold", spaceAfter=10, spaceBefore=20)
        sub_section_style = ParagraphStyle(name='SubSectionTitle', alignment=0, fontSize=12, fontName="Helvetica", spaceAfter=5, leftIndent=15)
        # Obtener datos del informe
        informe = controlador_informes.obtener_informe_final_estudiante_para_generar_pdf(id)
        if not informe:
            raise ValueError("No se encontró el informe.")
        
        # Obtener datos de la empresa relacionada
        empresa = controlador_empresa.obtener_empresa_por_nombre(informe[2])

        # Imagen y encabezado
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], 'usat_doc.jpg')
        imagen = Image(imagen_path, width=250, height=250)
        header1 = Paragraph("INFORME FINAL ESTUDIANTE DE PRÁCTICAS PRE PROFESIONALES", header_style)
        detalle.append(imagen)
        detalle.append(Spacer(1, 20))
        detalle.append(header1)

        # Información inicial
        fecha = informe[3].strftime('%Y-%m-%d')
        header2 = Paragraph(f"ESCUELA PROFESIONAL DE {(informe[0]).upper()}", header_style2)
        header3 = Paragraph(f"NOMBRE Y APELLIDOS DEL ESTUDIANTE:<br/> {informe[1]}", header_style2)
        header4 = Paragraph(f"NOMBRE DE LA INSTITUCIÓN:<br/> {informe[2]}", header_style2)
        header5 = Paragraph(f"FECHA DE ENTREGA DEL INFORME:<br/> {fecha}", header_style2)
        detalle.extend([header2, Spacer(1, 20), header3, header4, header5])

        # Salto de página después de la imagen y la información inicial para el índice
        detalle.append(PageBreak())

        # Índice Estático
        index_title = Paragraph("ÍNDICE", header_style2)
        detalle.append(index_title)
        detalle.append(Spacer(1, 10))

        # Agregar el índice
        index_items = [
            "Introducción",
            "Descripción de la institución",
            "1.1 Razón Social",
            "1.2 Dirección",
            "1.3 Giro de la Institución",
            "1.4 Representante Legal de la Institución",
            "1.5 Cantidad de Trabajadores",
            "1.6 Visión",
            "1.7 Misión",
            "1.8 Organigrama",
            "2. Labores desarrolladas por el estudiante",
            "3. Conclusiones",
            "4. Recomendaciones",
            "5. Bibliografía",
            "Anexos"
        ]

        for item in index_items:
            index_paragraph = Paragraph(item, normal_style)
            detalle.append(index_paragraph)
            detalle.append(Spacer(1, 5))

        # Salto de página después del índice
        detalle.append(PageBreak())

        # Contenido principal (sin espaciado extra entre títulos y subtítulos)
        lista_contenido = [
            Paragraph("Introducción", section_title_style),
            Paragraph(f"{informe[4].replace('\n', '<br />')}", normal_style),
            Paragraph("1. Descripción de la institución", section_title_style),
            Paragraph(f"{informe[6].replace('\n', '<br />')}", normal_style),
            Paragraph("1.1. Razón Social", sub_section_style),
            Paragraph(f"{empresa[1]}", normal_style2),
            Paragraph("1.2. Dirección", sub_section_style),
            Paragraph(f"{empresa[2]}", normal_style2),
            Paragraph("1.3. Giro de la Institución", sub_section_style),
            Paragraph(f"{empresa[3]}", normal_style2),
            Paragraph("1.4. Representante Legal de la Institución", sub_section_style),
            Paragraph(f"{empresa[4]}", normal_style2),
            Paragraph("1.5. Cantidad de Trabajadores", sub_section_style),
            Paragraph(f"{empresa[5]}", normal_style2),
            Paragraph("1.6. Visión", sub_section_style),
            Paragraph(f"{empresa[6]}", normal_style2),
            Paragraph("1.7. Misión", sub_section_style),
            Paragraph(f"{empresa[7]}", normal_style2),
            Paragraph("1.8. Organigrama", sub_section_style),
            Spacer(1, 20),
        ]

        organigrama_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{empresa[8]}')
        if os.path.exists(organigrama_path):
            organigrama = Image(organigrama_path, width=350, height=350)
            lista_contenido.append(organigrama)
            lista_contenido.append(Spacer(1, 20))

        # Continuar con el resto del contenido
        lista_contenido.extend([
            Paragraph("2. Labores desarrolladas por el estudiante ", section_title_style),
            Paragraph(f"{informe[6].replace('\n', '<br />')}", normal_style),
            Paragraph("3. Conclusiones", section_title_style),
            Paragraph(f"{informe[7].replace('\n', '<br />')}", normal_style),
            Paragraph("4. Recomendaciones", section_title_style),
            Paragraph(f"{informe[8].replace('\n', '<br />')}", normal_style),
            Paragraph("5. Bibliografía", section_title_style),
            Paragraph(f"{informe[9].replace('\n', '<br />')}", normal_style),
            Paragraph("Anexos", section_title_style),
        ])
        detalle.extend(lista_contenido)

        # Agregar anexos
        anexos_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{informe[10]}')
        if os.path.exists(anexos_path):
            anexos = Image(anexos_path, width=400, height=400)
            detalle.append(anexos)
            detalle.append(Spacer(1, 20))

        # Crear el PDF
        doc.build(detalle)

       
        # Enviar el archivo
        buff.seek(0)
        return send_file(buff, as_attachment=True, download_name=f"informe_final_estudiante_{informe[1]}.pdf", mimetype='application/pdf')

    except Exception as e:
        flash(f"Error al generar el PDF: {str(e)}", "error")
        return redirect(request.referrer)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
