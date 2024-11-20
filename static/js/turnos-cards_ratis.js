function loadScript(url, callback) {
    var script = document.createElement("script");
    script.type = "text/javascript";
    if (script.readyState) {  // Solo para IE
        script.onreadystatechange = function() {
            if (script.readyState === "loaded" || script.readyState === "complete") {
                script.onreadystatechange = null;
                callback();
            }
        };
    } else {  // Para todos los demás navegadores
        script.onload = function() {
            callback();
        };
    }
    script.src = url;
    document.getElementsByTagName("head")[0].appendChild(script);
}

// Cargar jQuery si no está definido
if (typeof jQuery === "undefined") {
    loadScript("https://code.jquery.com/jquery-3.6.0.min.js", init);
} else {
    init();
}

// Tu función de inicialización
function init() {
    function actualizarTurnos() {
        $.getJSON('/obtener_turnos_ratis', function(data) {
            var turnoBoard = $('.turno-board-cards');
            turnoBoard.empty();
            if (data.length === 0) {
                turnoBoard.append('<div class="card"><div class="card-body"><span class="turno">No hay turnos</span><span class="sala"></span></div></div>');
                return;
            }
            $.each(data, function(index, turno) {
                var nuevoTurno;
                var turno_text = turno.turno;
                    if(turno_text.includes("-")){
                        folio_solicitud = turno.turno.split("-")[1];
                        turno_text = turno.turno.split("-")[0];
                    }
                if (turno.status === "PRO" || turno.status === "NOT") {
                    if(turno.mesa && turno.usuario){
                        nuevoTurno = '<div class="card pro"><div class="card-body"><span class="turno">Turno: ' + turno_text + '</span><span class="sala"> Mesa: ' + turno.mesa + '</span></div></div>';
                    }else{
                        nuevoTurno = '<div class="card rev"><div class="card-body"><span class="turno">Turno: ' + turno_text + '</span><span class="sala">Con los Auxiliares</span></div></div>';
                    }
                    
                } else if(turno.estado_revisado) {
                    nuevoTurno = '<div class="card listo"><div class="card-body"><span class="turno">Turno: ' + turno_text + '</span><span class="sala">Listo para llamar</span></div></div>';
                }else{
                    nuevoTurno = '<div class="card"><div class="card-body"><span class="turno">Turno: ' + turno_text + '</span><span class="sala">Pendiente revisión de documentos</span></div></div>';
                }

                turnoBoard.prepend(nuevoTurno);
            });
        });
    }

    // Ejecutar cuando la página esté completamente cargada
    $(document).ready(function() {
        actualizarTurnos();
        setInterval(actualizarTurnos, 1000);
    });
}