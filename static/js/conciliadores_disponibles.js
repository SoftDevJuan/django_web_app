function cargarTurnos() {
    fetch('/ver_quien_esta_disponible')
        .then(response => response.json()) 
        .then(data => {
            console.log('la data de los disponibles :' , data);
            const conciliadores = data.conciliadores;
            actualizarTabla(conciliadores);
            const h2Conteo = document.getElementById("conteo-disponibles");
            if(h2Conteo){
                h2Conteo.innerText = conteo_disponibles(conciliadores);
            }

            const h2Pendientes = getElementById('turnos-pendientes');
            if(h2Pendientes){
                h2Pendientes.innerText = data.pendientes;
            }
        })
        .catch(error => console.error('Error al cargar los turnos:', error));
}



var conteo_disponibles = function(conciliadores){
    var conteo = 0;
    conciliadores.forEach(conciliador => {
        if(conciliador.proceso.includes("No Tiene")){
            conteo += 1;
        }
    })
    return conteo;
}


function actualizarTabla(conciliadores) {
    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '';   

    conciliadores.forEach(conciliador => {
        const row = document.createElement('tr');

            const blocktd = document.createElement('td');
            const btnblock = document.createElement('button')

            if(conciliador.bloqueo){
                btnblock.className = 'btn btn-danger';
                btnblock.textContent = 'Desbloquear Conciliador';
            }else{
                btnblock.className = 'btn btn-success';
                btnblock.textContent = 'Bloquear Conciliador';
            }
            btnblock.id = conciliador.id

             // Añadir el evento de clic al botón
            btnblock.addEventListener('click', () => {
                cambiarBloqueo(conciliador.id, conciliador.bloqueo);
            });
            

            blocktd.appendChild(btnblock);
            row.appendChild(blocktd);


            const turnoCell = document.createElement('td');
            const icon = document.createElement('i');
            icon.classList.add('fa-solid', 'fa-check', 'blue-icon');
            turnoCell.textContent = conciliador.nombre;
            
            
            if(conciliador.proceso.includes("No Tiene")){
                row.appendChild(turnoCell);
            }else{
                row.id = "no-disponible";
                turnoCell.appendChild(icon);
                row.appendChild(turnoCell);
            }

            // Celda de documentación
            const docCell = document.createElement('td');
            docCell.textContent = conciliador.sala;
            row.appendChild(docCell);
            
            
            // Celda de estatus
            const statusCell = document.createElement('td');
            statusCell.textContent = conciliador.proceso;
            row.appendChild(statusCell);



            // Celda de observaciones
            const observacionCell = document.createElement('td');
            observacionCell.textContent = conciliador.observaciones;
            row.appendChild(observacionCell);
            

            // Añadir fila a la tabla
            tableBody.appendChild(row);
        
    });
}





document.addEventListener('DOMContentLoaded', function() {
    cargarTurnos();
    setInterval(cargarTurnos, 1000);  
});// DOM

cargarTurnos();

function cambiarBloqueo(id, bloqueoActual) {
    console.log("el id", id)
    console.log("bloqueo: ", bloqueoActual)
    if (bloqueoActual == true) {
        console.log("lo convierte a false")
        bloqueoActual = false;
    } else if (bloqueoActual == false) {
        console.log("lo convierte a true")
        bloqueoActual = true;
    }
    console.log("bloqueo: ", bloqueoActual)

    fetch('/bloquear_conciliador/',{
        method : 'POST',
        headers : {
            'Content-Type' : 'application/json'
        },
        body : JSON.stringify({
            'user_id' : id,
            'bloqueo' : bloqueoActual
        })
    })
    .then( response => {
        if(!response.ok){
            console.log("fallo al cambiar bloqueo")
        }else{
            console.log("bloqueo con exito")
        }
    })
}