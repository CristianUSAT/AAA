-- Tabla Administrador
CREATE TABLE Administrador(
    id int PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150),
    correo VARCHAR(150),
    contraseña VARCHAR(150),
    token VARCHAR(255)
);

-- Tabla Facultad
CREATE TABLE Facultad(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nomFacultad VARCHAR(150) UNIQUE,
    estFacultad BOOLEAN
);

-- Tabla EscuelaProfesional
CREATE TABLE EscuelaProfesional(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nomEscuela VARCHAR(150) UNIQUE ,
    estEscuela BOOLEAN ,
    codFacEscuela INT ,
    FOREIGN KEY (codFacEscuela) REFERENCES Facultad(id) 
);

-- Tabla SemestreAcademico
CREATE TABLE SemestreAcademico(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nomSemestre VARCHAR(150) UNIQUE ,
    iniSemestre DATE ,
    finSemestre DATE ,
    estSemestre BOOLEAN 
);

-- Tabla PlanEstudio
CREATE TABLE PlanEstudio(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nomPlan VARCHAR(150) UNIQUE ,
    crePlan INT ,
    estPlan BOOLEAN ,
    codEscPlan INT ,
    FOREIGN KEY (codEscPlan) REFERENCES EscuelaProfesional(id) ON DELETE CASCADE
);

-- Tabla Estudiante
CREATE TABLE Estudiante (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codUniEstudiante VARCHAR(150) UNIQUE,
    apeNomEstudiante VARCHAR(150),
    codEscEstudiante INT,
    dniEstudiante VARCHAR(150) UNIQUE,
    telEstudiante VARCHAR(150) UNIQUE,
    corUniEstudiante VARCHAR(150) UNIQUE,
    estEstudiante BOOLEAN,
    passEstudiante VARCHAR(150),
    token VARCHAR(255),
    FOREIGN KEY (codEscEstudiante) REFERENCES EscuelaProfesional(id) ON DELETE CASCADE
);

-- Tabla Horario
CREATE TABLE Horario (
    idHorario INT PRIMARY KEY AUTO_INCREMENT,
    idEstudiante INT,
    dia ENUM('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'),
    hora int,
    FOREIGN KEY (idEstudiante) REFERENCES estudiante(id) ON DELETE CASCADE,
    UNIQUE KEY (idEstudiante, dia, hora) 
);

-- Tabla Docente
CREATE TABLE Docente (
    id INT PRIMARY KEY AUTO_INCREMENT,
    apeNomDocente VARCHAR(150) ,
    dniDocente VARCHAR(150) UNIQUE,
    corDocente VARCHAR(150) UNIQUE,
    estDocente BOOLEAN,
    token VARCHAR(255),
    passDocente VARCHAR(150) 
);

-- Tabla Escala
CREATE TABLE Escala (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nomEscala VARCHAR(150) UNIQUE ,
    estEscala BOOLEAN 
);

-- Tabla LineaDesarrollo
CREATE TABLE LineaDesarrollo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nomArea VARCHAR(150) UNIQUE ,
    estArea BOOLEAN ,
    codEscArea INT ,
    FOREIGN KEY (codEscArea) REFERENCES EscuelaProfesional(id) 
);

-- Tabla Empresa
CREATE TABLE Empresa (
    id INT PRIMARY KEY AUTO_INCREMENT,
    razSocEmpresa VARCHAR(150),
    dirEmpresa VARCHAR(150),
    girEmpresa VARCHAR(150),
    repreEmpresa VARCHAR(150),
    canTraEmpresa INT,
    visEmpresa TEXT,
    misEmpresa TEXT,
    orgEmpresa TEXT
);

-- Tabla intermedia para relacionar Empresa y Estudiante
CREATE TABLE EmpresaEstudiante (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empresaId INT,
    estudianteId INT,
    FOREIGN KEY (empresaId) REFERENCES Empresa(id),
    FOREIGN KEY (estudianteId) REFERENCES Estudiante(id)
);

-- Tabla Responsable
CREATE TABLE Responsable (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codEmpResponsable INT,
    apeNomResponsable VARCHAR(150),
    carResponsable VARCHAR(150),
    telResponsable VARCHAR(150),
    corResponsable VARCHAR(150),
    horResponsable VARCHAR(150),
    FOREIGN KEY (codEmpResponsable) REFERENCES Empresa(id)
);

-- Tabla intermedia para relacionar Estudiante y Responsable
CREATE TABLE EstudianteResponsable (
    id INT PRIMARY KEY AUTO_INCREMENT,
    estudianteId INT,
    responsableId INT,
    FOREIGN KEY (estudianteId) REFERENCES Estudiante(id),
    FOREIGN KEY (responsableId) REFERENCES Responsable(id)
);

-- Tabla InformeInicialEstudiante
CREATE TABLE InformeInicialEstudiante (
    id INT PRIMARY KEY AUTO_INCREMENT,
    estuIniEstudiante INT , 
    codSemIniEstudiante INT null,
    empIniEstudiante INT null,
    resIniEstudiante INT null,
    aceptacionEmpresa TEXT,
    iniIniEstudiante DATE ,
    finIniEstudiante DATE ,
    firEstIniEstudiante TEXT ,
    firResIniEstudiante TEXT ,
    estaIniEstudiante VARCHAR(150) ,
    obseIniEstudiante TEXT,
    codDocente INT null,
    fechaIniEstudiante DATETIME DEFAULT CURRENT_TIMESTAMP ,
    laboresPracticante TEXT,
    FOREIGN KEY (estuIniEstudiante) REFERENCES Estudiante(id) ON DELETE CASCADE,
    FOREIGN KEY (codSemIniEstudiante) REFERENCES SemestreAcademico(id) ON DELETE CASCADE,
    FOREIGN KEY (empIniEstudiante) REFERENCES Empresa(id) ON DELETE CASCADE,
    FOREIGN KEY (resIniEstudiante) REFERENCES Responsable(id) ON DELETE CASCADE,
    FOREIGN KEY (codDocente) REFERENCES Docente(id) ON DELETE CASCADE
);

-- Tabla PlanTrabajo
CREATE TABLE PlanTrabajo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codInfTrabajo INT ,
    semTrabajo text ,
    iniTrabajo text ,
    finTrabajo text ,
    actTrabajo text ,
    horTrabajo text ,
    FOREIGN KEY (codInfTrabajo) REFERENCES InformeInicialEstudiante(id) ON DELETE CASCADE
);

-- Tabla InformeInicialEmpresa
CREATE TABLE InformeInicialEmpresa (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empIniEmpresa INT null,
    resIniEmpresa INT null,
    estuIniEmpresa INT ,
    iniIniEmpresa DATE ,
    finIniEmpresa DATE ,
    aceIniEmpresa TEXT ,
    aceAnexoIniEmpresa TEXT ,
    labIniEmpresa TEXT ,
    selFirResIniEmpresa TEXT ,
    fechaInfIniEmpresa DATETIME DEFAULT CURRENT_TIMESTAMP ,
    estaIniEmpresa VARCHAR(150) ,
    obseIniEmpresa TEXT,
    FOREIGN KEY (empIniEmpresa) REFERENCES Empresa(id) ON DELETE CASCADE,
    FOREIGN KEY (resIniEmpresa) REFERENCES Responsable(id) ON DELETE CASCADE,
    FOREIGN KEY (estuIniEmpresa) REFERENCES Estudiante(id) ON DELETE CASCADE
);

-- Tabla InformeFinalEstudiante
CREATE TABLE InformeFinalEstudiante (
    id INT PRIMARY KEY AUTO_INCREMENT,
    emprFinEstudiante INT null,
    estuFinEstudiante INT ,
    intFinEstudiante TEXT ,
    descAreFinEstudiante TEXT ,
    descLabFinEstudiante TEXT ,
    conFinEstudiante TEXT ,
    recFinEstudiante TEXT ,
    bibFinEstudiante TEXT ,
    aneFinEstudiante TEXT ,
    fechaInfFinEstudiante DATETIME DEFAULT CURRENT_TIMESTAMP ,
    estaFinEstudiante VARCHAR(150) ,
    obseFinEstudiante TEXT,
	codDocente INT null,
    infraestfisica TEXT,
    infraesttecno TEXT,
    FOREIGN KEY (emprFinEstudiante) REFERENCES Empresa(id) ON DELETE CASCADE,
    FOREIGN KEY (estuFinEstudiante) REFERENCES Estudiante(id) ON DELETE CASCADE,
	FOREIGN KEY (codDocente) REFERENCES Docente(id) ON DELETE CASCADE
);

-- Tabla InformeFinalEmpresa
CREATE TABLE InformeFinalEmpresa (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empFinEmpresa INT null,
    respFinEmpresa INT null,
    estuFinEmpresa INT ,
    iniFinEmpresa DATE ,
    finFinEmpresa DATE ,
    objFinEmpresa TEXT ,
    horFinEmpresa TEXT ,
    resFinEmpresa TEXT ,
    otrFinEmpresa TEXT ,
    selFirResFinEmpresa TEXT ,
    fechaInfFinEmpresa DATETIME DEFAULT CURRENT_TIMESTAMP ,
    estaFinEmpresa VARCHAR(150) ,
    obseFinEmpresa TEXT,
    FOREIGN KEY (empFinEmpresa) REFERENCES Empresa(id) ON DELETE CASCADE,
    FOREIGN KEY (respFinEmpresa) REFERENCES Responsable(id) ON DELETE CASCADE,
    FOREIGN KEY (estuFinEmpresa) REFERENCES Estudiante(id) ON DELETE CASCADE
);

-- Tabla Desempenio
CREATE TABLE Desempenio (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empDesempenio INT ,
    respDesempenio INT ,
    estuDesempenio INT ,
    areDesempenio VARCHAR(150) ,
    resuDesempenio TEXT ,
    iniDesempenio DATE ,
    finDesempenio DATE ,
    conDesempenio TEXT ,
    firRepDesempenio TEXT ,
    estaDesempenio VARCHAR(150) ,
    obseDesempenio VARCHAR(150) ,
	codDocente INT ,
    fechaInfDesempenio DATETIME DEFAULT CURRENT_TIMESTAMP ,
    FOREIGN KEY (empDesempenio) REFERENCES Empresa(id) ON DELETE CASCADE,
    FOREIGN KEY (respDesempenio) REFERENCES Responsable(id) ON DELETE CASCADE,
    FOREIGN KEY (estuDesempenio) REFERENCES Estudiante(id) ON DELETE CASCADE,
	FOREIGN KEY (codDocente) REFERENCES Docente(id) ON DELETE CASCADE
);

-- Tabla TablaCaracteristicas
CREATE TABLE Caracteristicas (
    id INT PRIMARY KEY AUTO_INCREMENT,
	nomCaracteristica VARCHAR(150), -- Nombre de la característica evaluada
    escala_seleccionada ENUM('Deficiente', 'Regular', 'Bueno', 'Muy Bueno'), 
    codDesempenio INT ,
    FOREIGN KEY (codDesempenio) REFERENCES Desempenio(id) ON DELETE CASCADE
);
-- PPP
CREATE TABLE PPP (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codEstPPP INT ,
    codSemIniPPP INT null,
    codSemFinPPP INT null,
    horas_requeridas INT,
    horas_pendientes INT,
    horas INT,
    iniPPP DATE ,
    finPPP DATE ,
    codLinPPP INT null,
    arePPP VARCHAR(150) ,
    estPPP VARCHAR(150) ,
    obsPPP VARCHAR(150) ,
    codDocentePPP INT null,
    numeroPPP int,
    codinformeinicialEst int null,
    codinformefinalEst int null,
    codinformeinicialEmp int null,
    codinformefinalEmp int null,
    codFichaDesempenio int null,
    FOREIGN KEY (codEstPPP) REFERENCES Estudiante(id) ON DELETE CASCADE,
    FOREIGN KEY (codSemIniPPP) REFERENCES SemestreAcademico(id) ON DELETE CASCADE,
    FOREIGN KEY (codSemFinPPP) REFERENCES SemestreAcademico(id) ON DELETE CASCADE,
    FOREIGN KEY (codLinPPP) REFERENCES LineaDesarrollo(id) ON DELETE CASCADE,
    FOREIGN KEY (codDocentePPP) REFERENCES Docente(id) ON DELETE CASCADE,
    FOREIGN KEY (codinformeinicialEst) REFERENCES InformeInicialEstudiante(id) ON DELETE CASCADE,
    FOREIGN KEY (codinformefinalEst) REFERENCES InformeFinalEstudiante(id) ON DELETE CASCADE,
    FOREIGN KEY (codinformeinicialEmp) REFERENCES InformeInicialEmpresa(id) ON DELETE CASCADE,
    FOREIGN KEY (codinformefinalEmp) REFERENCES InformeFinalEmpresa(id) ON DELETE CASCADE,
    FOREIGN KEY (codFichaDesempenio) REFERENCES Desempenio(id) ON DELETE CASCADE
);
-- Cartas
CREATE TABLE Cartas(
    id int PRIMARY KEY AUTO_INCREMENT,
    fechaRegistro DATE DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50),
    nombre VARCHAR(255),
    codEstudiante int null,
    codPPP int null,
    enlace VARCHAR(255),
    FOREIGN KEY (codEstudiante) REFERENCES Estudiante(id) ON DELETE CASCADE,
    FOREIGN KEY (codPPP) REFERENCES PPP(id) ON DELETE CASCADE
);

CREATE TABLE mensajes(
    id int PRIMARY KEY AUTO_INCREMENT,
    texto text,
    fechaEnvio DATE DEFAULT CURRENT_TIMESTAMP,
    hora time DEFAULT CURRENT_TIME,
    estado char(1),
    idEstudiante int null,
    idDocente int null,
    emisor VARCHAR(100),
    FOREIGN KEY (idEstudiante) REFERENCES Estudiante(id) ON DELETE CASCADE,
    FOREIGN KEY (idDocente) REFERENCES Docente(id) ON DELETE CASCADE
);

CREATE TABLE super(
    id int PRIMARY KEY AUTO_INCREMENT,
    superEstu int,
    superPPP int,
    superEmpr int,
    funciones text,
    observaciones text,
    firmaEstu VARCHAR(255),
    firmaDoce VARCHAR(255),
    firmaJefe VARCHAR(255),
    fecha date,
    hora time,
    ubicacion text,
    numero int,
    area_desempenio text,
    responsable int,
    FOREIGN KEY (superEstu) REFERENCES Estudiante(id) ON DELETE CASCADE,
    FOREIGN KEY (superPPP) REFERENCES PPP(id) ON DELETE CASCADE,
    FOREIGN KEY (superEmpr) REFERENCES Empresa(id) ON DELETE CASCADE,
    FOREIGN KEY (responsable) REFERENCES Responsable(id) ON DELETE CASCADE
);
