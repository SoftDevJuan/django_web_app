function cargarTurnos() {
    fetch('/turnos_auxiliares')
        .then(response => response.json()) 
        .then(data => {
            console.log('la data de los auxiliares :' , data);
            const turnos = data.turnos;
            actualizarTabla(turnos); 
        })
        .catch(error => console.error('Error al cargar los turnos:', error));
}

// Función para actualizar el estado del turno en el servidor
function actualizarEstado(turnoId, div) {
    fetch('/actualizar_estado/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            
        },
        body: JSON.stringify({ turno_id: turnoId, estado_revisado: true })  
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const turnoActualizado = {
                id: turnoId,
                estado_revisado: true
            };
            actualizarEstadoDOM(turnoActualizado, div);
        } else {
            console.error('Error al actualizar el estado del turno');
        }
    })
    .catch(error => {
        console.error('Error en la petición:', error);
    });
}


function llamar_a_revision(turnoId){
    var enviar = {turno_id: turnoId, nuevo_status: 'NOT'};
    fetch('/cambiar_status_rati/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            
        },
        body: JSON.stringify(enviar)  // Enviar True para actualizar
    })
    .then(response => response.json())
    .then(data => {
        if (data) {
            console.log(data)
        } else {
            console.error('Error al actualizar el estado del turno');
        }
    })
    .catch(error => {
        console.error('Error en la petición:', error);
    });
}


function cancelar_turno(turnoId){
    var enviar = {turno_id: turnoId, nuevo_status: 'CAN'};
    fetch('/cambiar_status_rati/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            
        },
        body: JSON.stringify(enviar)  // Enviar True para actualizar
    })
    .then(response => response.json())
    .then(data => {
        if (data) {
            console.log(data)
        } else {
            console.error('Error al actualizar el estado del turno');
        }
    })
    .catch(error => {
        console.error('Error en la petición:', error);
    });
}



// Función para actualizar el estado visual en el DOM
function actualizarEstadoDOM(turno, div) {
    // Limpiar el contenido previo del div
    div.innerHTML = '';

    // Crear el botón "Revisado / No revisado"
    const buttonRevisado = document.createElement('button');
    buttonRevisado.classList.add('btn', turno.estado_revisado ? 'btn-success' : 'btn-primary', 'btn-sm', 'fw-bold');
    buttonRevisado.textContent = turno.estado_revisado ? 'Revisado' : 'No revisado';
    buttonRevisado.dataset.turnoId = turno.id;
    div.appendChild(buttonRevisado);

    // Solo crear el botón "Llamar" si el estado_revisado es false
    if (!turno.estado_revisado) {
        const buttonLlamar = document.createElement('button');
        buttonLlamar.classList.add('btn', 'btn-warning', 'btn-sm', 'ms-2', 'fw-bold');
        buttonLlamar.textContent = 'Llamar';
        buttonLlamar.dataset.turnoId = turno.id;
        div.appendChild(buttonLlamar);

        // Evento de clic para el botón "Llamar"
        buttonLlamar.addEventListener('click', function () {
            llamar_a_revision(turno.id);
        });
    }
    buttonRevisado.addEventListener('click', function () {
        actualizarEstado(turno.id, div);
    });

}



function cancelaciones(turno, div) {
    // Limpiar el contenido previo del div
    div.innerHTML = '';

    // Crear el botón "Revisado / No revisado"
    const buttonCancelar = document.createElement('button');
    buttonCancelar.classList.add('btn', 'btn-danger', 'btn-sm', 'fw-bold');
    buttonCancelar.textContent = "Cancelar Turno";
    buttonCancelar.id = `${turno.id}`
    buttonCancelar.dataset.turnoId = turno.id;
    div.appendChild(buttonCancelar);
    
    buttonCancelar.addEventListener('click', function () {
        const confirmar = confirm("¿Estás seguro de que deseas cancelar el turno?");
        if(confirmar){
            cancelar_turno(turno.id);
        }
        
    });
    
}




function actualizarTabla(turnos) {
    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '';   

    turnos.forEach(turno => {
        if (turno.status !== 'CAN' && turno.status !== 'FIN') {
            const row = document.createElement('tr');

            // Celda de turno
            const turnoCell = document.createElement('td');
            turnoCell.textContent = turno.turno;
            row.appendChild(turnoCell);

            // Celda de documentación
            const docCell = document.createElement('td');
            const div = document.createElement('div');
            div.classList.add('d-flex', 'justify-content-center');
            row.appendChild(docCell);
            
            actualizarEstadoDOM(turno, div);  // Llamada para agregar los botones al DOM

            docCell.appendChild(div);

            // Celda de estatus
            const statusCell = document.createElement('td');
            if (turno.status === 'PEN') {
                statusCell.textContent = 'Por atender';
            } else if (turno.status === 'NOT') {
                statusCell.textContent = 'Llamando';
                statusCell.classList.add('td-llamando');
            } else if (turno.status === 'PRO') {
                statusCell.textContent = 'En proceso';
                statusCell.classList.add('td-en-proceso');
            }
            row.appendChild(statusCell);

            // Celda de conciliador
            const conciliadorCell = document.createElement('td');
            conciliadorCell.textContent = turno.usuario ? `${turno.usuario}` : 'Por asignar';
            row.appendChild(conciliadorCell);

            // Celda de personas
            const personasCell = document.createElement('td');
            personasCell.textContent = turno.personas_count;
            row.appendChild(personasCell);

            // celda cancelar
            const cancelarCell = document.createElement('td');
            const divCan = document.createElement('div')
            divCan.classList.add('d-flex', 'justify-content-center');
            
            cancelaciones(turno, divCan)
            cancelarCell.appendChild(divCan)
            row.appendChild(cancelarCell)
            
            // Añadir fila a la tabla
            tableBody.appendChild(row);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    cargarTurnos();
    setInterval(cargarTurnos, 1000);  
});// DOM

cargarTurnos();