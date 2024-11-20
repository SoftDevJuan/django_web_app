document.addEventListener('DOMContentLoaded', function() {
    console.log("El JS de notificaciones ha cargado.");

    function validarTurnos() {
        var url = `/validar_turnos_proceso/?user=${user_id}`;
        if(user_id != 'None'){
            fetch(url)
            .then(response => response.json())  
            .then(data => {
                data.forEach(turno => {
                    var diferenciaMinutos = turno.diferencia_minutos;
                    
                    console.log(`Diferencia en minutos para el turno ${turno.turno}: ${diferenciaMinutos}`);

                    if (diferenciaMinutos > 90) {
                        console.log(`Turno ${turno.turno} ha superado los 90 minutos. Verificando permisos de notificación...`);

                        if (Notification.permission === 'granted') {
                            console.log("Permiso concedido para notificaciones. Mostrando notificación...");
                            const notification = new Notification('Turno pendiente', {
                                body: `El turno ${turno.turno} ha estado en proceso por más de 90 minutos y debe ser completado.`,
                                icon:  '/static/icon/CCLLetras.png'
                            });

                            notification.onclick = function() {
                                window.open('/ratificacion/conciliador/');
                            };


                        } else if (Notification.permission !== 'denied') {
                            console.log("Solicitando permiso para notificaciones...");
                            Notification.requestPermission().then(permission => {
                                if (permission === 'granted') {
                                    console.log("Permiso concedido después de solicitarlo. Mostrando notificación...");
                                    const notification = new Notification('Turno pendiente', {
                                        body: `El turno ${turno.turno} ha estado en proceso por más de 120 minutos y debe ser completado.`,
                                        icon: '/static/icon/CCLLetras.png'
                                    });

                                    notification.onclick = function() {
                                        window.open('/ratificacion/conciliador/');
                                    };


                                }else{
                                    alert("No has habilitado las notificaciones. Por favor, activa las notificaciones para recibir alertas sobre tus turnos pendientes.");
                                }
                            });
                        } else {
                            console.log("Permiso para notificaciones denegado o no disponible.");
                            alert("No has habilitado las notificaciones. Por favor, activa las notificaciones para recibir alertas sobre tus turnos pendientes.");
                            Notification.requestPermission().then(permission => {
                                if (permission === 'granted') {
                                    console.log("Permiso concedido después de solicitarlo. Mostrando notificación...");
                                    const notification = new Notification('Turno pendiente', {
                                        body: `El turno ${turno.turno} ha estado en proceso por más de 120 minutos y debe ser completado.`,
                                        icon:  '/static/icon/CCLLetras.png'
                                    });


                                    notification.onclick = function() {
                                        window.open('/ratificacion/conciliador/');
                                    };


                                }else{
                                    alert("No has habilitado las notificaciones. Por favor, activa las notificaciones para recibir alertas sobre tus turnos pendientes.");
                                }
                            });
                        }
                    }
                });
            })
            .catch(error => console.error('Error al obtener los turnos:', error));
        }else{
            console.log("Nececitas Iniciar Sesión")
        }
        
    }

    setInterval(validarTurnos, 30000);  
});
