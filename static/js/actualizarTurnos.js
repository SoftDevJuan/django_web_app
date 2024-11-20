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


function convertirNumeroATexto(numero) {
    if (numero < 10) {
        return numero.toString();
    }
    return numerosAtexto[numero] || numero.toString();
}

let notificacionActiva = false;
let audioPlayer = null;

/*if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/js/sw.js').then(registration => {
        console.log('Service Worker registrado con éxito:', registration);
    }).catch(error => {
        console.log('Error al registrar el Service Worker:', error);
    });
} else {
    console.log('Service Worker no está soportado en este navegador.');
}*/


// Este método es para reproducir la alarma cuando se llama a un nuevo turno
function reproducirNotificacion(turnospeach) {
    console.log("comienza el proceso")
    if (notificacionActiva) {
        console.log('Esperar a que termine la notificacion anterior');
        return false;
    } else {
        notificacionActiva = true;
        if (!reproducirNotificacion.audio) {
            reproducirNotificacion.audio = new Audio(audioPath);
            reproducirNotificacion.audio.playbackRate = 1;

            // Establecer el volumen del video al 30% antes de reproducir la notificación
            setVolume(0.3);

            console.log('Se reduce el volumen al 30 %');

            const notificacionTimeout = setTimeout(() => {
                console.log('Tiempo de notificacion excedido');
                notificacionActiva = false;
                reproducirNotificacion.audio = null;
                
                setVolume(1);
            }, 20000);

            reproducirNotificacion.audio.onended = function() {

                console.log('Notificacion terminada');

                clearTimeout(notificacionTimeout);

                console.log('Se limpia tirme out');
                reproducirNotificacion.audio = null;

                console.log('Reproducir notificacion en null');
                speak(turnospeach)
                    .then((success) => {
                        console.log('Se intenta marcar variable en falso');
                        notificacionActiva = false;

                        setVolume(1);
                    })
                    .catch(error => {
                        console.log('Error al intentar marcar variable en falso');
                        console.error('Error en speak:', error);
                        notificacionActiva = false;
                        
                        setVolume(1);
                    });
                console.log('Sono notificacion hablada');

            };

            reproducirNotificacion.audio.onerror = function() {

                console.log('Error al reproducir el audio');
                reproducirNotificacion.audio = null;
                notificacionActiva = false;
                setVolume(1);
            };

            reproducirNotificacion.audio.play().catch((error) => {
                console.error('Error al reproducir el audio:', error);
                clearTimeout(notificacionTimeout);
                reproducirNotificacion.audio = null;
                notificacionActiva = false;
                setVolume(1);
            });
        }
    }
    console.log('Se retorno notificacion en true');
    return true;
}

// Este método es para llamar a un turno mediante voz sintética
function speak(text) {
    console.log('Se llamo a speak()');
    return new Promise((resolve, reject) => {
        console.log('Entrando a promesa de speak()');
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            console.log('Entrando a speechSynthesis(2)');
            utterance.lang = 'es-US';
            console.log('Entrando a speechSynthesis(3)');
            utterance.pitch = 1;
            utterance.rate = 1.1;
            console.log('Entrando a speechSynthesis(4)');
            utterance.onend = resolve(true);
            console.log('Entrando a speechSynthesis(5)');
            window.speechSynthesis.speak(utterance);
            console.log('Entrando a speechSynthesis(6)');

        } else {
            reject(alert('Lo siento, tu navegador no soporta la API Web Speech'));
        }
    });
}

function setVolume(volumen) {
    var video = document.getElementById('videoccl');
    if (video) {
        video.volume = volumen;
    } else {
        console.error('Elemento de video no encontrado');
    }
}

// Este método renderiza los turnos, valida su estado y notifica según sea necesario
function actualizarTurnos() {
    if (notificacionActiva) {
        console.log('Notificación en curso, se omite la actualización de turnos.');
        return;
    }
    $.getJSON('/obtener_turnos', function(data) {
        var turnoInner = $('.turno-inner');
        var turnoInnerP = $('.turno-inner-p');
        var turnoUltimo = $('.turno-inner-p-last'); // Div para el último turno con status "NOT"
        turnoInner.empty();
        turnoInnerP.empty();
        turnoUltimo.empty();

        if (data.length === 0) {
            turnoInnerP.append('<div class="turno-card"><span class="turno">No hay turnos</span><span class="sala"></span></div>');
            return;
        }

        var ultimoNotTurnoIndex = -1;
        $.each(data, function(index, turno) {
            if (turno.status === "NOT") {
                ultimoNotTurnoIndex = index;
            }
        });

        $.each(data, function(index, turno) {
            var nuevoTurno;
            if (turno.status === "NOT") {
                nuevoTurno = `
                    <div class="turno-card pro">
                        <div class="card-body">
                            <span class="turno">${turno.turno}</span>
                            <span class="sala">Mesa ${turno.mesa}</span>
                        </div>
                    </div>
                `;
                let numero = parseInt(turno.turno.substring(2));
                let numeroEnTexto = convertirNumeroATexto(numero);
                var turnospeach = `Turno: ${turno.turno.substring(0,2)} ${numeroEnTexto}, favor de pasar a la mesa ${turno.mesa}`;
                console.log(turnospeach);
                
                if (!turno.notificacion) {
                    console.log("se supone que aun no lo notifica")
                    if (reproducirNotificacion(turnospeach)) {
                        const url = 'cambiar_status_notificacion/';
                        const data = {
                            turno_id: turno.id,
                            notificacion: true
                        };
                        fetch(url, {
                            method: 'PATCH',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });
                    }
                }else{
                    console.log("se supone que ya lo nitifico")
                    const url = 'cambiar_status_notificacion/';
                        const data = {
                            turno_id: turno.id,
                            notificacion: true
                        };
                        fetch(url, {
                            method: 'PATCH',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });
                }

                if (index === ultimoNotTurnoIndex) {
                    turnoUltimo.append(nuevoTurno);
                } else {
                    turnoInnerP.append(nuevoTurno);
                }
            } else if (turno.status === "PEN"){
                nuevoTurno = `
                    <div class="turno-card">
                        <div class="card-body">
                            <span class="turno">${turno.turno}</span>
                            <span class="sala">Por atender</span>
                        </div>
                    </div>
                `;
                turnoInner.append(nuevoTurno);
            }
        });
    });
}

// Validar si la página se ha cargado y llamar actualizarTurnos cada segundo
$(document).ready(function() {
    actualizarTurnos();
    setInterval(actualizarTurnos, 3000);
});
