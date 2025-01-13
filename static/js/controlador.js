const mensajeInput = document.querySelector("#mensaje");

mensajeInput.focus();

const socket = io();

nombreactual = document.getElementById('nombre').textContent;

document.addEventListener('DOMContentLoaded', async ()=>{
    socket.emit('iniciar');
});

function enviarDatos(idD) {
    socket.emit("obtener_chats", idD);
    socket.emit("entrar_sala", idD);
    const divContent = document.querySelector("#textos");
    const user = document.createElement('div');
    user.setAttribute('id','user')
    user.setAttribute('data-id',idD)
    user.hidden=true
    divContent.appendChild(user)
    const destino = document.querySelectorAll('.formulario-usuarios');
    destino.forEach(elemento=>{
        elemento.addEventListener("click",()=>{
            const hijo = elemento.querySelector('.a .b');
            hijo.classList.remove('fw-bold');
            const id = elemento.getAttribute('data-id');
            socket.emit('generar_visto',id);
        });
    });
}

socket.on("obtener_chats", (data) => {
    const datos = data.mensajes
    const divContent = document.querySelector("#textos");
    datos.forEach(elemento=>{
        const mensajeDiv = document.createElement('div');
        mensajeDiv.className = 'd-flex flex-column mb-3 p-3 border rounded';
        if (data.emisor===elemento[7]) {
            mensajeDiv.style.backgroundColor='#e1f7d5';
            mensajeDiv.classList.add('ms-5');
        }
        else{
            mensajeDiv.style.backgroundColor='#d1e7fd';
            mensajeDiv.classList.add('me-5');
        }
        // Contenido del mensaje
        mensajeDiv.innerHTML = `
            <div class="d-flex justify-content-between">
                <span class="fw-bold" id="user" data-id="${elemento[6]}" >${elemento[7]}</span>
                <span class="text-muted small">${elemento[2]}</span>
            </div>
            <p class="mb-1">${elemento[1]}</p>
            <div class="text-end small">
                <span class="text-primary">${elemento[3]}</span>
            </div>
        `;
        divContent.appendChild(mensajeDiv);
    });
    bajarMira();
});


const form_chat = document.querySelector("#formulario_chat");

if (form_chat) {
    form_chat.addEventListener("submit", async (event) => {
        event.preventDefault();
        const idD = document.querySelector('#user').getAttribute('data-id')
        // Verificar si viene algun mensaje
        if (mensajeInput && mensajeInput.value.trim() === "") {
            mensajeInput.style.border = "1px solid #ffb2a0";
            return; // Detener el envío del formulario
        }
        //limpio el border del input mensaje
        mensajeInput.style.border = "";
        socket.emit("mensaje_chat", mensajeInput.value, idD);
        mensajeInput.value = "";
    });
}
socket.on("mensaje_chat", (data) => {
    const id = document.querySelector('#user').getAttribute('data-id')
    socket.emit('cargar_bandeja',id,data.emisor);
    const datos = data.lista_mensajes;
    const divContent = document.querySelector("#textos");
    const mensajeDiv = document.createElement('div');
    mensajeDiv.className = 'd-flex flex-column mb-3 p-3 border rounded';
    nombre = document.getElementById('nombre').textContent;
    if (nombre.trim() == datos[7].trim()) {
        mensajeDiv.style.backgroundColor='#e1f7d5';
        mensajeDiv.classList.add('ms-5');
    }
    else{
        mensajeDiv.style.backgroundColor='#d1e7fd';
        mensajeDiv.classList.add('me-5');
    }
    // Contenido del mensaje
    mensajeDiv.innerHTML = `
        <div class="d-flex justify-content-between">
                <span class="fw-bold" id="user" data-id="${datos[6]}" >${datos[7]}</span>
                <span class="text-muted small">${datos[2]}</span>
            </div>
            <p class="mb-1">${datos[1]}</p>
            <div class="text-end small">
                <span class="text-primary">${datos[3]}</span>
            </div>
    `;
    divContent.appendChild(mensajeDiv);
    bajarMira();
});


socket.on('cargar_bandeja',(data)=>{
    let bandeja = document.getElementById('bandeja');
    let canvas = document.getElementById('offcanvasMensajeria');
    if (!canvas.classList.contains('show')) {
        bandeja.className='bi-envelope-exclamation-fill me-2';
    }
    let emisor = String(data.id);
    const elemento = document.querySelector(`.formulario-usuarios[data-id="${emisor}"]`);
    const hijo = elemento.children[0];
    hijo.children[0].classList.add('fw-bold');
    const padre = elemento.parentNode;
    padre.prepend(elemento);
}
);

function bajarMira() {
    const chatWindow = document.querySelector('.offcanvas-body');
    chatWindow.scrollTop = chatWindow.scrollHeight;
};
function mostrarPantallaMensajes(remitente) {
    // Mostrar la pantalla de mensajes y ocultar la lista de remitentes
    const lista = document.querySelectorAll('#listaRemitentes');
    const pantalla = document.querySelectorAll('#pantallaMensajes');
    lista.forEach(elemento => {
        elemento.style.display = 'none';
    });
    pantalla.forEach(elemento => {
        elemento.style.display = 'block';
    });
    // Actualizar el nombre del remitente
    document.querySelectorAll('.nombreRemitente').forEach(clase => {
        clase.textContent = remitente
    }
    );
    bajarMira();
}

function volverAListaRemitentes() {
    // Volver a la lista de remitentes y ocultar la pantalla de mensajes
    const id = document.querySelector('#user').getAttribute('data-id');

    socket.emit('salir_sala',id);
    const divContent = document.querySelector("#textos");
    divContent.innerHTML="";
    const lista = document.querySelectorAll('#listaRemitentes');
    const pantalla = document.querySelectorAll('#pantallaMensajes');
    lista.forEach(elemento => {
        elemento.style.display = 'block';
    });
    pantalla.forEach(elemento => {
        elemento.style.display = 'none';
    });
}

function limpiar() {
    let bandeja = document.getElementById('bandeja');
    bandeja.className = 'bi-envelope-fill me-2';
}