console.log("se carga el js notificacion de audiencias")
var audiencia_id = "";
var justificacion = "";

function reproducirAudio() {
    console.log("si entro a reproducir");
    var audio = new Audio(audioPathNotificacion);
    audio.play().then(() => {
        console.log("Reproduciendo audio...");
    }).catch((error) => {
        console.error("Error al reproducir el audio: ", error);
    });
}


function validarAudiencias() {
    var url = `/validar_audiencias_proceso/?user=${user_id}`;
    
    if (user_id != 'None') {
        fetch(url)
            .then(response => response.json())  
            .then(data => {
                console.log(data);

                if (data.message.includes("si audiencia")) {
                    
                        if(data.audiencia_id){
                            audiencia_id = data.audiencia_id;
                            console.log("obtiene la audiencia", audiencia_id)
                
                        var url1 = `/validar_si_justifico/?user=${user_id}&audiencia=${audiencia_id}`;
                        fetch(url1)
                            .then(response => response.json())
                            .then(data => {
                                console.log("justifico?: ",data)
                                if (data.message){
                                    console.log("si lo cuenta");
    
                                }else{
                                    console.log("no lo cuenta");
                                    if (Notification.permission === 'granted') {
                                        mostrarNotificacion(data);
                                    } else if (Notification.permission !== 'denied') {
                                        Notification.requestPermission().then(permission => {
                                            if (permission === 'granted') {
                                                mostrarNotificacion();
                                                
                                            }
                                        });
                                    }
                                }
                            });
                        }    

                }else{
                    console.log("hay que meterle una notificacion tambien")
                    audiencia_id = "none";
                    var url1 = `/validar_si_justifico/?user=${user_id}`;
                    fetch(url1)
                        .then(response => response.json())
                        .then(data => {
                            console.log("justifico?: ",data)
                            if (data.message){
                                console.log("si lo cuenta");

                            }else{
                                console.log("no lo cuenta");
                                if (Notification.permission === 'granted') {
                                    mostrarNotificacion(data);
                                } else if (Notification.permission !== 'denied') {
                                    Notification.requestPermission().then(permission => {
                                        if (permission === 'granted') {
                                            mostrarNotificacion();
                                            
                                        }
                                    });
                                }
                            }
                        });
                }
            })
            .catch(error => console.error('Error al obtener los turnos:', error));
    } else {
        console.log("Necesitas Iniciar Sesión");
    }
}



function mostrarNotificacion() {
    const title = 'Actualmente No Tienes Audiencia';
    const options = {
        body: `¿Deseas llamar un turno de Ratificaciones?`,
        icon: '/static/icon/CCLLetras.png',
        requireInteraction: true,
        
    };

    const notification = new Notification(title, options);

    reproducirAudio();


    notification.onclick = function(event) {
        event.preventDefault();
        window.open('/ratificacion/conciliador/');
    };

    
    notification.onclose = function() {
        localStorage.setItem('mostrarPrompt', 'true');
        localStorage.setItem('user_id', user_id);
        localStorage.setItem('audiencia_id', audiencia_id);
        window.open('/ratificacion/conciliador/','_blank');
        console.log("el id de la audiencia: ",audiencia_id)
    };
}

window.addEventListener('load', function() {

    if (localStorage.getItem('mostrarPrompt') === 'true') {
        const user_id = localStorage.getItem('user_id');
        const audiencia_id = localStorage.getItem('audiencia_id');
        mostrarCuadroDialogoMotivo(user_id, audiencia_id);
    }
});

function mostrarCuadroDialogoMotivo(user_id, audiencia_id) {
    const motivo = prompt("Si por ahora no puedes tomar turnos de Ratificación, explica el motivo:");
    if (motivo) {
        console.log("Motivo:", motivo);
        const datos = {
            audiencia: audiencia_id,
            user: user_id,
            mensaje: motivo,
        };
        console.log(datos);

        fetch('/actualizar_justificacion/', {
            method: 'POST',
            headers: {
                'Content-type': 'application/json'
            },
            body: JSON.stringify(datos)
        }).then(response => {
            if (!response.ok) {
                throw new Error('Error al guardar motivo.');
            }
            localStorage.removeItem('mostrarPrompt');
            localStorage.removeItem('user_id');
            localStorage.removeItem('audiencia_id');

        }).catch(error => {
            console.error("Error:", error);
        });
    } else {
        console.log("No se proporcionó un motivo.");
    }
}

document.addEventListener('DOMContentLoaded', function() {
    setInterval(validarAudiencias, 50000);  
});



window.addEventListener('load', function() {
    if (localStorage.getItem('mostrarPrompt') === 'true') {
        //mostrarCuadroDialogoMotivo();
        localStorage.removeItem('mostrarPrompt');
    }
});


