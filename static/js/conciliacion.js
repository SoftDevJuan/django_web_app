let notificacionActiva = false;
let expedientesLlamados = new Set();

function reproducirNotificacion(turnospeach) {
    if (notificacionActiva) {
        console.log('Esperar a que termine la notificación anterior');
        return false;
    } else {
        notificacionActiva = true;
        if (!reproducirNotificacion.audio) {
            reproducirNotificacion.audio = new Audio(audioPath);
            reproducirNotificacion.audio.playbackRate = 1;
            const notificacionTimeout = setTimeout(() => {
                console.log('Tiempo de notificación excedido');
                notificacionActiva = false;
                reproducirNotificacion.audio = null;
            }, 20000);
            reproducirNotificacion.audio.onended = function() {
                clearTimeout(notificacionTimeout);
                reproducirNotificacion.audio = null;
                speak(turnospeach)
                    .then(() => {
                        notificacionActiva = false;
                    })
                    .catch(error => {
                        console.error('Error en speak:', error);
                        notificacionActiva = false;
                    });
            };
            reproducirNotificacion.audio.onerror = function() {
                reproducirNotificacion.audio = null;
                notificacionActiva = false;
            };
            reproducirNotificacion.audio.playbackRate = 1;
            reproducirNotificacion.audio.play().catch((error) => {
                console.error('Error al reproducir el audio:', error);
                clearTimeout(notificacionTimeout);
                reproducirNotificacion.audio = null;
                notificacionActiva = false;
            });
        }
    }
    return true;
}

function enviarDatosExpediente(data) {
    const url = '/api/actualizar_datos_expediente/'; // Asegúrate de que esta URL sea correcta

    fetch(url, {
        method: 'PATCH', // o 'POST', dependiendo de lo que tu servidor espere
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    }).then(response => response.json())
    .then(data => {
        console.log('Datos actualizados con éxito:', data);
        actualizarUI(data);
    })
    .catch(error => console.error('Error al enviar datos:', error));
}

function speak(text) {
    return new Promise((resolve, reject) => {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'es-US';
            utterance.pitch = 1;
            utterance.rate = 1.1;
            utterance.onend = resolve;
            window.speechSynthesis.speak(utterance);
        } else {
            reject(alert('Lo siento, tu navegador no soporta la API Web Speech'));
        }
    });
}

function llamarExpediente(button) {
    const row = button.closest('tr');
    const horario = row.children[0].textContent;
    const solicitante = row.children[1].textContent;
    const citado = row.children[2].textContent;
    const expediente = row.children[3].textContent;
    const conciliador = row.children[4].textContent;
    const sala = row.children[5].textContent;
    const estado = row.children[6].querySelector('.circle').classList.contains('green') ? 'Activo' : 'Inactivo';
    
    const turnospeach = `Turno: ${expediente}, favor de pasar a la sala ${sala}`;

    if (reproducirNotificacion(turnospeach)) {
        enviarDatosExpediente({ horario, solicitante, citado, expediente, conciliador, sala, estado });
        expedientesLlamados.add(expediente); // Marcar el expediente como llamado
    }
}

document.addEventListener('DOMContentLoaded', function() {
    let userInteracted = false;

    // Función para actualizar el reloj
    function updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const timeString = `${hours}:${minutes}:${seconds}`;
        document.getElementById('clock').textContent = timeString;
    }
    setInterval(updateClock, 1000);
    updateClock(); // Llamada inicial

    // Registrar la interacción del usuario
    document.addEventListener('click', function() {
        userInteracted = true;
    });
});

function actualizarUI(data) {
    // Asumiendo que la API devuelve los datos necesarios para actualizar la UI
    document.getElementById('info-sala').textContent = data.sala;
    document.getElementById('info-expediente').textContent = data.expediente;
    document.getElementById('info-conciliador').textContent = data.conciliador;
    document.getElementById('info-solicitante').textContent = data.solicitante;
    document.getElementById('info-citado').textContent = data.citado;
}

function reproducirSonido(audioPath) {
    if (audioPath) {
        new Audio(audioPath).play().catch(error => {
            console.error('Error reproduciendo el sonido: ', error);
        });
    }
}

function actualizarInfoExpediente(data) {
    document.getElementById('info-sala').textContent = data.sala;
    document.getElementById('info-expediente').textContent = data.expediente;
    document.getElementById('info-conciliador').textContent = data.conciliador;
    document.getElementById('info-solicitante').textContent = data.solicitante;
    document.getElementById('info-citado').textContent = data.citado;

    // Reproducir el sonido
    reproducirSonido(audioPath);
}

function obtenerNotificaciones() {
    $.ajax({
        url: '/obtener-notificaciones/',
        method: 'GET',
        success: function(data) {
            if ($.isEmptyObject(data)) {
                console.log('No hay notificaciones pendientes');
                return;
            }

            // Actualizar la información del expediente y reproducir el sonido
            actualizarInfoExpediente(data);
        },
        error: function(error) {
            console.error('Error obteniendo las notificaciones: ', error);
        }
    });
}

// Llamar a la función obtenerNotificaciones cada 10 segundos
setInterval(obtenerNotificaciones, 10000);
obtenerNotificaciones(); // Llamada inicial
