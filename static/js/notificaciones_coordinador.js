console.log("se carga el js de notificaciones para coordinadores")
var conciliadores = "";
var turnos = "";

function reproducirAudio() {
    console.log("si entro a reproducir");
    var audio = new Audio(audioPathNotificacion);
    audio.play().then(() => {
        console.log("Reproduciendo audio...");
    }).catch((error) => {
        console.error("Error al reproducir el audio: ", error);
    });
}


function validarDisponibles() {
    var url = `/conciliadores_disponibles_notificacion/?user=${user_id}`;
    
    if (user_id != 'None') {
        fetch(url)
            .then(response => response.json())  
            .then(data => {
                console.log(data);
                if(data.conciliadores && data.turnos){
                    conciliadores = data.conciliadores;
                    turnos = data.turnos;

                    if (Notification.permission === 'granted') {
                        mostrarNotificacionSinOptions(data);
                    } else if (Notification.permission !== 'denied') {
                        Notification.requestPermission().then(permission => {
                            if (permission === 'granted') {
                                mostrarNotificacionSinOptions();             
                            }
                        });
                    }
                }
                
                
                });
    } else {
        console.log("Necesitas Iniciar Sesión");
    }
}



function mostrarNotificacionSinOptions() {
    const title = `Turnos Pendientes: ${turnos}`;
    const options = {
        body: `Conciliadores Disponibles: ${conciliadores}`,
        icon: '/static/icon/CCLLetras.png',
        
        
    };

    const notification = new Notification(title, options);

    reproducirAudio();


    notification.onclick = function(event) {
        event.preventDefault();
        window.open('/conciliadores_disponibles/');
    };
}

document.addEventListener('DOMContentLoaded', function() {
    setInterval(validarDisponibles, 600000);  
});


