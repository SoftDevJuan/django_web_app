
const numerosAtexto = {
    0: 'cero',
    1: 'uno',
    2: 'dos',
    3: 'tres',
    4: 'cuatro',
    5: 'cinco',
    6: 'seis',
    7: 'siete',
    8: 'ocho',
    9: 'nueve',
    10: 'diez',
    11: 'once',
    12: 'doce',
    13: 'trece',
    14: 'catorce',
    15: 'quince',
    16: 'dieciséis',
    17: 'diecisiete',
    18: 'dieciocho',
    19: 'diecinueve',
    20: 'veinte',
    21: 'veintiuno',
    22: 'veintidós',
    23: 'veintitrés',
    24: 'veinticuatro',
    25: 'veinticinco',
    26: 'veintiséis',
    27: 'veintisiete',
    28: 'veintiocho',
    29: 'veintinueve',
    30: 'treinta',
    31: 'treinta y uno',
    32: 'treinta y dos',
    33: 'treinta y tres',
    34: 'treinta y cuatro',
    35: 'treinta y cinco',
    36: 'treinta y seis',
    37: 'treinta y siete',
    38: 'treinta y ocho',
    39: 'treinta y nueve',
    40: 'cuarenta',
    41: 'cuarenta y uno',
    42: 'cuarenta y dos',
    43: 'cuarenta y tres',
    44: 'cuarenta y cuatro',
    45: 'cuarenta y cinco',
    46: 'cuarenta y seis',
    47: 'cuarenta y siete',
    48: 'cuarenta y ocho',
    49: 'cuarenta y nueve',
    50: 'cincuenta',
    51: 'cincuenta y uno',
    52: 'cincuenta y dos',
    53: 'cincuenta y tres',
    54: 'cincuenta y cuatro',
    55: 'cincuenta y cinco',
    56: 'cincuenta y seis',
    57: 'cincuenta y siete',
    58: 'cincuenta y ocho',
    59: 'cincuenta y nueve',
    60: 'sesenta',
    61: 'sesenta y uno',
    62: 'sesenta y dos',
    63: 'sesenta y tres',
    64: 'sesenta y cuatro',
    65: 'sesenta y cinco',
    66: 'sesenta y seis',
    67: 'sesenta y siete',
    68: 'sesenta y ocho',
    69: 'sesenta y nueve',
    70: 'setenta',
    71: 'setenta y uno',
    72: 'setenta y dos',
    73: 'setenta y tres',
    74: 'setenta y cuatro',
    75: 'setenta y cinco',
    76: 'setenta y seis',
    77: 'setenta y siete',
    78: 'setenta y ocho',
    79: 'setenta y nueve',
    80: 'ochenta',
    81: 'ochenta y uno',
    82: 'ochenta y dos',
    83: 'ochenta y tres',
    84: 'ochenta y cuatro',
    85: 'ochenta y cinco',
    86: 'ochenta y seis',
    87: 'ochenta y siete',
    88: 'ochenta y ocho',
    89: 'ochenta y nueve',
    90: 'noventa',
    91: 'noventa y uno',
    92: 'noventa y dos',
    93: 'noventa y tres',
    94: 'noventa y cuatro',
    95: 'noventa y cinco',
    96: 'noventa y seis',
    97: 'noventa y siete',
    98: 'noventa y ocho',
    99: 'noventa y nueve',
};



let notificacionActiva = false;
//let audioPath = 'ruta/a/tu/sonido.mp3'; // Reemplaza con la ruta real de tu archivo de audio

// Función para establecer el volumen del video
function setVolume(volumen) {
    var video = document.getElementById('videoccl');
    if (video) {
        video.volume = volumen;
    } else {
        console.error('Elemento de video no encontrado');
    }
}

// Función para reproducir la notificación
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
                // Restablecer el volumen del video al 100%
                setVolume(1);
            }, 20000);

            reproducirNotificacion.audio.onended = function() {
                clearTimeout(notificacionTimeout);
                reproducirNotificacion.audio = null;
                speak(turnospeach)
                    .then(() => {
                        notificacionActiva = false;
                        // Restablecer el volumen del video al 100%
                        setVolume(1);
                    })
                    .catch(error => {
                        console.error('Error en speak:', error);
                        notificacionActiva = false;
                        // Restablecer el volumen del video al 100%
                        setVolume(1);
                    });
            };

            reproducirNotificacion.audio.onerror = function() {
                reproducirNotificacion.audio = null;
                notificacionActiva = false;
                // Restablecer el volumen del video al 100%
                setVolume(1);
            };

            reproducirNotificacion.audio.play().catch((error) => {
                console.error('Error al reproducir el audio:', error);
                clearTimeout(notificacionTimeout);
                reproducirNotificacion.audio = null;
                notificacionActiva = false;
                // Restablecer el volumen del video al 100%
                setVolume(1);
            });
        }
    }
    return true;
}

// Función para llamar a un turno mediante voz sintética
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


function convertirNumeroATexto(numero) {
    if (numero < 10) {
        return numero.toString();
    }
    return numerosAtexto[numero] || numero.toString();
}


function verificarEstadoEnDOM() {
    const filas = document.querySelectorAll('#table-body tr');
    filas.forEach(fila => {
        const estado = fila.querySelector('td:nth-child(2)').textContent.trim();
        const turno = fila.querySelector('td:first-child').textContent.trim();
        const notificacion =  fila.querySelector('td:nth-child(5)').textContent; 
        const mesala = fila.querySelector('td:nth-child(3)').textContent.trim()
        const turnoId = fila.getAttribute('data-turno-id');
        console.log(turnoId,"el turno", turno ,"la notificacion: ", notificacion);



        if (estado === 'Llamando') {
            if (notificacionActiva) {
                console.log('Notificación en curso, se omite la actualización de turnos.');
                return;
            }
            let numero = parseInt(turno.substring(2));
            let numeroEnTexto = convertirNumeroATexto(numero);
            if (turno.includes("/")){
                var turnospeach = `Folio: ${turno.substring(0,2)} ${numeroEnTexto}, favor de pasar a la ${fila.querySelector('td:nth-child(3)').textContent.trim()}`;
            }else{
                turnospeach = `Turno: ${turno.substring(0,2)} ${numeroEnTexto}, favor de pasar a la ${fila.querySelector('td:nth-child(3)').textContent.trim()}`;
            }
            
            console.log(turnospeach);
            if(mesala == 'Por asignar'){
                console.log('cambia el texto de la notificacion');
                if (turno.includes("/")){
                    turnospeach = `Folio: ${turno.substring(0,2)} ${numeroEnTexto}, favor de pasar a revisión de documentos con los auxiliares}`;
                }else{
                    turnospeach = `Turno: ${turno.substring(0,2)} ${numeroEnTexto}, favor de pasar a revisión de documentos con los auxiliares}`;
                }
            
            }
            
            if (notificacion === 'False') {
                if (reproducirNotificacion(turnospeach)) {
                    const url = '/cambiar_status_notificacion/'; 
                    const data = {
                        turno_id: turnoId,
                        notificacion: true
                    };

                    console.log(data);
                    
                    fetch(url, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    }).catch(error => {
                        console.error('Error al actualizar el estado de la notificación:', error);
                    });
                    
                }
            }
        }
    });
    return true;

}

function recargarDOM(){
    console.log("se recargo la pagina");
    location.reload();
    console.log("se recargo la pagina");
}
// Llama a verificarEstadoEnDOM cada segundo
document.addEventListener('DOMContentLoaded', function () {
    console.log("inicio");
    //setInterval(verificarEstadoEnDOM, 1000);
    //setTimeout(recargarDOM, 7000);
    
    
    
});
