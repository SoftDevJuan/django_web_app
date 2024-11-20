function crearTabla(data) {
    var data = data.data;
    var ciudadanos = data.ciudadanos;
    var solicitudes = data.solicitudes;
    var folio_solicitud = data.solicitudes[0].folio_solicitud;
    var cantidadPartes = ciudadanos.length;
    var tipo_solicitud = "Ratificación con Convenio";
    var registro = data.ciudadanos[0].registro;
    console.log("los datos: ", data);

    var contenido = '<form id="uploadForm">';

    // Tabla de información de solicitud
    contenido +='<h1>Datos cargados correctamente</h1>'
    contenido += '<table class="table-info">';
    contenido += '<thead><tr><th colspan="3" class="th-title">Información de Solicitud</th></tr>';
    contenido += '<tr>';
    contenido += '<th>Folio Solicitud</th>';
    //contenido += '<th>Tipo de Solicitud</th>';
    contenido += '<th>Cantidad de Partes</th>';
    contenido += '</tr></thead>';
    contenido += '<tbody>';
    contenido += '<tr>';
    contenido += '<td>' + folio_solicitud + '</td>';
    //contenido += '<td>' + tipo_solicitud + '</td>';
    contenido += '<td>' + cantidadPartes + '</td>';
    contenido += '</tr>';
    contenido += '</tbody>';
    contenido += '</table>';


     // Tabla de fuentes de trabajo
    contenido += '<table class="table-info">';
    //contenido += '<thead><tr><th colspan="5" class="th-title">Fuentes</th></tr>';
    contenido += '<tr>';
    contenido += '<th>Fuente</th>';
    contenido += '<th>Tipo Persona</th>';
    contenido += '<th>Municipio</th>';
    contenido += '</tr></thead>';
    contenido += '<tbody>';

    ciudadanos.forEach(function (ciudadano) {
        var nombre = ciudadano.nombre;
        var tipo_persona = ciudadano.tipo_persona;
        var tipo_persona_sin_acentos = eliminarAcentos(tipo_persona.toLowerCase());
        var municipio = ciudadano.municipio;
        var idCiudadano = ciudadano.id;
        

        if(tipo_persona_sin_acentos.includes("soy persona juridica empleadora") && nombre.startsWith("Fuente:")){ 
            contenido += '<td>' + nombre + '</td>';
            contenido += '<td>' + tipo_persona + '</td>';
            contenido += '<td>' + municipio + '</td>';
            contenido += '</tr>';;
        }
        
    });

    contenido += '</tbody></table>';


    // Tabla de ciudadanos
    contenido += '<table class="table-solicitantes">';
   // contenido += '<thead><tr><th colspan="5" class="th-title">Ciudadanos</th></tr>';
    contenido += '<tr>';
    contenido += '<th>Asistencia</th>';
    contenido += '<th>Nombre</th>';
    contenido += '<th>Sexo</th>';
    contenido += '<th>Tipo Persona</th>';
    contenido += '<th>Municipio</th>';
    contenido += '<th>Acciones</th>';
    contenido += '</tr></thead>';
    contenido += '<tbody>';

    ciudadanos.forEach(function (ciudadano) {
        var nombre = ciudadano.nombre;
        var sexo = ciudadano.sexo;
        var tipo_persona = ciudadano.tipo_persona;
        var tipo_persona_sin_acentos = eliminarAcentos(tipo_persona.toLowerCase());
        var municipio = ciudadano.municipio;
        var idCiudadano = ciudadano.id;
        var checkboxId = "ciudadano-" + idCiudadano;
        var asistencia = solicitudes.some(solicitud => solicitud.id_ciudadano === idCiudadano && solicitud.asistencia);
        var checkedAttribute = asistencia ? 'disabled checked' : '';

        if(tipo_persona_sin_acentos.includes("soy persona juridica empleadora") && nombre.startsWith("Fuente:")){

        }
        else{
        contenido += asistencia ? '<tr class="row-asistencia">' : '<tr id="' + checkboxId + '">';
        contenido += '<td><input type="checkbox" onchange="mostrarMensaje(\'' + checkboxId + '\')" id="checkbox-' + checkboxId + '" ' + checkedAttribute + '></td>'; 
        contenido += '<td>' + nombre + '</td>';
        contenido += '<td>' + sexo + '</td>';
        contenido += '<td>' + tipo_persona + '</td>';
        contenido += '<td>' + municipio + '</td>';
        contenido += '<td> <button type="button" id="eliminar-ciudadano' + idCiudadano +'" class="btn btn-danger">Eliminar</button></td>';
        contenido += '</tr>';
        contenido += '<td colspan="5" id="identificacion-' + checkboxId + '" hidden></td>';
        }
    });
    

    contenido += '</tbody></table>';
    
    verificarTurno(registro).then(estadoTurno => {
        if (estadoTurno.existe) {
            if (estadoTurno.estado !== 'PEN') {
                if(estadoTurno.estado == 'PRO' || estadoTurno.estado == 'NOT'){
                    contenido += `<br><br><div class="alert alert-success" role="alert">El turno ${estadoTurno.turno} ya esta siendo atendido.</div>`;
                }else{
                    contenido += `<br><br><div class="alert alert-warning" role="alert">El turno ${estadoTurno.turno} ya no esta siendo atendido.</div>`;
                    contenido += '<br><br><button type="button" id="boton_asignar_turno" class="btn btn-warning" data-bs-toggle="modal" data-bs-target="#assignTurnModal">Generar Otro Turno</button>';
                }

            } else {
                // Botón para agregar un nuevo ciudadano
                contenido += '<br><button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCitizenModal" onclick="limpiarModal()">Agregar Ciudadano</button>';
                contenido += `<br><br><h1>Turno: ${estadoTurno.turno} <button class="btn btn-warning" onclick="seEquivoco(${estadoTurno.id})">Cancelar este turno</button></h1> `;
            }
        } else {
            contenido += '<button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addCitizenModal" onclick="limpiarModal()">Agregar Ciudadano</button>';
            contenido += '<br><br><button type="button" id="boton_asignar_turno" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#assignTurnModal">Asignar Turno</button>';

        }

    contenido += '</form>';

    

    // Modal para agregar un nuevo ciudadano
    contenido += `
    <div class="modal fade" id="addCitizenModal" tabindex="-1" aria-labelledby="addCitizenModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="addCitizenModalLabel">Agregar Ciudadano</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="addCitizenForm" action="/registrar_adicional/" method="POST">
                        <div class="mb-3">
                            <label for="nombre" class="form-label">Nombre</label>
                            <input type="text" class="form-control" id="nombre" name="nombre" required>
                            <ul id="lista-sugerencias"></ul>
                            <img id="imagen-sugerencia" src="" alt="ine" style="display: none; width: 200px; height: auto;"/>
                        </div>
                        <div class="mb-3">
                            <label for="sexo" class="form-label">Sexo</label>
                            <select class="form-select" id="sexo" name="sexo" required>
                                <option value="" disabled selected>Selecciona una opción</option>
                                <option value="Masculino">Masculino</option>
                                <option value="Femenino">Femenino</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="tipo_persona" class="form-label">Tipo de Persona</label>
                            <select class="form-select" id="tipo_persona" name="tipo_persona" required>
                                <option value="" disabled selected>Selecciona una opción</option>
                                <option value="Soy Persona Trabajadora">Soy trabajador</option>
                                <option value="Soy Persona Fisica Empleadora">Soy dueño de una empresa</option>
                                <option value="Soy Persona Juridica Empleadora">Soy representante legal de la empresa</option>
                                <option value="Soy Persona de Confianza">Soy persona de confianza</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="municipio" class="form-label">Municipio</label>
                            <input type="text" class="form-control" id="municipio" name="municipio" required>
                            <input type="hidden" class="form-control" id="registro" name="registro" value="${registro}" required>
                            <input type="hidden" class="form-control" id="folio" name="folio" value="${folio_solicitud}" required>
                            <input type="hidden" class="form-control" id="codigo" name="codigo">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    <button type="submit" class="btn btn-primary" form="addCitizenForm" data-bs-dismiss="modal">Guardar</button>
                </div>
            </div>
        </div>
    </div>`;

         // Modal para asignar turno
        contenido += `
        <div class="modal fade" id="assignTurnModal" tabindex="-1" aria-labelledby="assignTurnModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header"> 
                        <h5 class="modal-title" id="assignTurnModalLabel">Asignar Turno</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="assignTurnForm">
                            <div class="mb-3">
                                <label for="area" class="form-label">Área</label>
                                <select class="form-select" id="area" name="area" required>
                                    <option value="" disabled selected>Selecciona un área</option>
                                    <option value="ratificacion">Ratificación</option>
                                    <option value="ratificacion con cita">Ratificación con Cita</option>
                                    <option value="ratificacion preferente">Ratificación Preferente</option>
                                    <option value="asesoria">Asesoria Juridica</option>
                                    <option value="asesoria con cita">Asesoria Juridica con Cita</option>
                                    <option value="asesoria preferente">Asesoria Juridica Preferente</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="prefijo" class="form-label">Turno</label>
                                <input type="text" class="form-control" id="prefijo" name="prefijo" value="${folio_solicitud}" readonly>
                            </div>
                            <input type="hidden" id="registro" name="registro" value="${registro}" required>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="submit" class="btn btn-primary" onclick="asignarTurno()" data-bs-dismiss="modal">Asignar Turno</button>
                    </div>
                </div>
            </div>
        </div>`;


    $('#contenedor_datos_procesados').html(contenido);
});
}

async function verificarTurno(registro) {
    try {
        let response = await fetch('/verificar_estado_turno/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ registro: registro })
        });
        let data = await response.json();
        return data; // Retornamos toda la respuesta (incluyendo si el turno existe y su estado)
    } catch (error) {
        console.error('Error al verificar el estado del turno:', error);
        return { estado: 'PEN', existe: false }; // En caso de error
    }
}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


const csrftoken = getCookie('csrftoken');


function asignarTurno() {
    var registro = document.getElementById('registro').value;
    var area = document.getElementById('area').value;
    var folio = document.getElementById('prefijo').value;

    if (area === "" || folio === "") {
        alert("Por favor selecciona un área y verifica el folio.");
        return;
    }

    $.ajax({
        url: '/asignar_turno_folio/',
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'registro': registro,
            'folio': folio,
            'area': area  // Asegúrate de enviar el área
        },
        success: function(response) {
            alert(response.message);
    
            // Actualizar botones
            $('#boton_asignar_turno').replaceWith(`
                <br><h1>Turno: ${response.turno}</h1>
                <button class="btn btn-warning" onclick="seEquivoco(${response.id})"> Cancelar este turno</button>
            `);
        },
        error: function(xhr, status, error) {
            var response = JSON.parse(xhr.responseText);
            alert(response.error || 'Ha ocurrido un error inesperado.');
        }
    });
}

function actualizarCodigosCiudadanos() {
    var registro = document.getElementById('registro').value;

    $.ajax({
        url: '/actualizar_codigos_ciudadanos/',
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'registro': registro,
        },
        success: function(response) {
            console.log('Códigos de ciudadanos actualizados correctamente');
            //location.reload(); // Recargar la página para reflejar los cambios
        },
        error: function(error) {
            console.log('Error al actualizar los códigos de ciudadanos. Por favor, intenta nuevamente.');
        }
    });
}



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function limpiarModal(){
    console.log("comienza a limpiar el modal")
    setTimeout(() =>{
        input_nombre = document.getElementById('nombre');
        input_municipio = document.getElementById('municipio');
        select_sexo = document.getElementById('sexo');
        select_tipo_persona = document.getElementById('tipo_persona')
        foto = document.getElementById('imagen-sugerencia');

        input_nombre.value ="";
        input_municipio.value = "";
        select_sexo.value = "";
        select_tipo_persona.value = "";
        if(foto){
            foto.src = "";
            foto.style.display = 'none';
        }
        
        iniciarAutocompletado();
    },200);

    
}

function iniciarAutocompletado() {
    console.log("inicia autocompletado");
    var inputNombre = document.getElementById('nombre');
    
    inputNombre.addEventListener('input', function() {
        var query = this.value;
        if (query.length > 2) {  
            $.ajax({
                url: "/buscar_ciudadano_autocompletar/", 
                data: { 'q': query },
                dataType: 'json',
                success: function(data) {
                    
                    mostrarSugerencias(data); 
                },
                error: function(xhr, status, error) {
                    console.log('Error en la búsqueda: ' + error);
                }
            });
        }
    });
}




function mostrarSugerencias(data) {
    var listaSugerencias = $('#lista-sugerencias');
    listaSugerencias.empty();

    data.forEach(function(item) {
        listaSugerencias.append('<li class="sugerencia" data-nombre="' + item.nombre + '" data-sexo="' + item.sexo + '" data-tipo_persona="' + item.tipo_persona + '" data-municipio="' + item.municipio + '" data-codigo="' + item.codigo + '" data-imagen="' + item.ine + '">' + item.nombre + '</li>');
    });
}

$(document).on('click', '#lista-sugerencias .sugerencia', function() {
    var nombre = $(this).data('nombre');
    var sexo = $(this).data('sexo');
    var tipo_persona = $(this).data('tipo_persona');
    var municipio = $(this).data('municipio');
    var codigo = $(this).data('codigo');
    var imagenUrl = $(this).data('imagen');

    if(sexo.startsWith('m')|| sexo.startsWith('M') ){
        sexo = 'Masculino';
    } else if(sexo.startsWith('f')|| sexo.startsWith('F')){
        sexo = 'Femenino';
    }

    // Completar el formulario
    completarFormulario({
        nombre: nombre,
        sexo: sexo,
        tipo_persona: eliminarAcentos(tipo_persona),
        municipio: municipio,
        codigo: codigo
    });

    // Mostrar la imagen
    var imagenSugerencia = $('#imagen-sugerencia');
    if (imagenUrl) {
        imagenSugerencia.attr('src', imagenUrl);
        imagenSugerencia.show();
    } else {
        imagenSugerencia.hide();
    }

    // Limpiar la lista de sugerencias
    $('#lista-sugerencias').empty();
});

function completarFormulario(datos) {
    $('#nombre').val(datos.nombre);
    $('#sexo').val(datos.sexo);
    $('#tipo_persona').val(datos.tipo_persona);
    $('#municipio').val(datos.municipio);
    $('#codigo').val(datos.codigo);
}




///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

async function llamarFuncion(c, s, f) {
    try {
        const response = await ajaxPost("/registro/ratificaciones/folio/insertar_ciudadanos/", {
            c: c,
            s: s,
            f: f
        });

        return response;

    } catch (error) {
        console.error('Error:', error);
        throw error; 
    }
}



document.addEventListener('DOMContentLoaded', function () {
    // Asigna el evento a un contenedor presente en el DOM, como el body
    document.body.addEventListener('click', function (event) {
        // Verifica si el elemento que disparó el evento es el botón que abre el modal
        if (event.target.matches('button[data-bs-target="#addCitizenModal"]')) {
            setTimeout(() => {
                const addCitizenForm = document.getElementById('addCitizenForm');
                
                if (addCitizenForm) {
                    addCitizenForm.addEventListener('submit', async function (event) {
                        console.log("Formulario interceptado");
                        event.preventDefault();  // Esto previene la redirección por defecto

                        const formData = new FormData(addCitizenForm);
                        const csrfToken = getCookie('csrftoken');

                        try {
                            const response = await fetch(addCitizenForm.action, {
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': csrfToken
                                },
                                body: formData
                            });

                            if (response.ok) {
                                const data = await response.json();
                                agregarCiudadanoATabla(data);
                                
                                
                            } else {
                                console.error('Error:', response.statusText);
                                alert('Hubo un error al registrar el ciudadano.');
                            }
                        } catch (error) {
                            console.error('Error:', error);
                            alert('Hubo un error al registrar el ciudadano.');
                        }
                    });
                } else {
                    console.error('El formulario no se encontró en el DOM');
                }
            }, 100); // Espera de 100ms para asegurarse que el modal esté en el DOM
        }
    });
});





function agregarCiudadanoATabla(ciudadano) {
    var checkboxId = "ciudadano-" + ciudadano.id;
    if(!ciudadano.asistencia){
        var asistencia = false;
    }
    else{
        asistencia = ciudadano.asistencia;
    }
     // Los nuevos ciudadanos no tendrán asistencia registrada inicialmente
    var checkedAttribute = asistencia ? 'disabled checked' : '';

    var contenido = asistencia ? '<tr class="row-asistencia">' : '<tr id="' + checkboxId + '">';
    contenido += '<td><input type="checkbox" onchange="mostrarMensaje(\'' + checkboxId + '\')" id="checkbox-' + checkboxId + '" ' + checkedAttribute + '></td>';
    contenido += '<td>' + ciudadano.nombre + '</td>';
    contenido += '<td>' + ciudadano.sexo + '</td>';
    contenido += '<td>' + ciudadano.tipo_persona + '</td>';
    contenido += '<td>' + ciudadano.municipio + '</td>';
    contenido += '<td> <button type="button" id="eliminar-ciudadano' + ciudadano.id +'" class="btn btn-danger">Eliminar</button></td>';
    contenido += '</tr>';
    contenido += '<td colspan="5" id="identificacion-' + checkboxId + '" hidden></td>';

    document.querySelector('.table-solicitantes tbody').innerHTML += contenido;
}





document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', async function(event) {
        if (event.target && event.target.matches('button[id^="eliminar-ciudadano"]')) {
            event.preventDefault(); // Prevenir la recarga de página

            const idCiudadano = event.target.id.replace('eliminar-ciudadano', '');
            const row = document.getElementById(`ciudadano-${idCiudadano}`);
            
            if (confirm('¿Estás seguro de que deseas eliminar a este ciudadano?')) {
                try {
                    const response = await fetch(`/eliminar_ciudadano_ratis/${idCiudadano}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    if (response.ok) {
                        if (row) {
                            row.remove(); // Eliminar la fila de la tabla
                        }
                        alert('Ciudadano eliminado con éxito.');
                    } else {
                        alert('Hubo un error al intentar eliminar al ciudadano.');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Hubo un error al intentar eliminar al ciudadano.');
                }
            }
        }
    });
});

function eliminarAcentos(texto) {
    return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}




function seEquivoco(id_turno) {
    if (confirm('¿Deseas remover este turno?')) {
        var url = `/cancelar_turno_recepcion/${id_turno}/`;
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // Si necesitas enviar datos
            }
        })
        .then(response => {
            if (response.ok) {
                alert('Se canceló con éxito');
            } else {
                alert('Hubo un error al cancelar el turno');
            }
        })
        .catch(error => {
            alert('Hubo un error de red: ' + error.message);
        });
    }
}


