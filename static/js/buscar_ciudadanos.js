function openModal(turnoId, area) {
    document.getElementById('modal').style.display = 'block';
    document.getElementById('turno-id-add').value = turnoId;
    document.getElementById('turno-id-remove').value = turnoId;
    document.querySelector('input[name="area"]').value = area;
    document.querySelector('input[name="area-remove"]').value = area;
    document.getElementById('search-add').value = '';
    document.getElementById('results-add').innerHTML = '';
    document.getElementById('results-remove').innerHTML = '';

    searchCiudadanoAdd();  // Para añadir ciudadanos
    searchCiudadanoRemove();  // Para quitar ciudadanos
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

function searchCiudadanoAdd() {
    let query = document.getElementById('search-add').value;

    if (query.length < 2) {
        return;
    }

    fetch(`/buscar_ciudadano_turno/?q=${query}`)
        .then(response => response.json())
        .then(data => {
            let results = document.getElementById('results-add');
            results.innerHTML = ''; // Limpiar resultados anteriores

            data.forEach(ciudadano => {
                let divAdd = document.createElement('div');
                divAdd.innerHTML = `<input type="radio" onclick="selectCiudadano('${ciudadano.nombre}', '${ciudadano.id}')" name="ciudadano_id" value="${ciudadano.id}"> ${ciudadano.nombre}`;
                results.appendChild(divAdd);
            });
        });
}

function selectCiudadano(nombre, id) {
    // Actualiza el campo de texto con el nombre del ciudadano seleccionado
    document.querySelector('input[name="nombre_seleccionado"]').value = nombre;
    // Actualiza el valor del campo oculto con el ID del ciudadano seleccionado
    document.querySelector('input[name="ciudadano_id"]').value = id;
}

function searchCiudadanoRemove() {
    let turnoId = document.getElementById('turno-id-remove').value;
    let area = document.querySelector('input[name="area-remove"]').value;

    fetch(`/obtener_ciudadanos_en_turno/?turno_id=${turnoId}&area=${area}`)
        .then(response => response.json())
        .then(data => {
            let resultsRemove = document.getElementById('results-remove');
            resultsRemove.innerHTML = ''; // Limpiar resultados anteriores

            data.forEach(ciudadano => {
                let divRemove = document.createElement('div');
                divRemove.innerHTML = `<input type="radio" onclick="selectCiudadano('${ciudadano.nombre}', '${ciudadano.id}')" name="ciudadano_id" value="${ciudadano.id}"> ${ciudadano.nombre}`;
                resultsRemove.appendChild(divRemove);
            });
        });
}

function searchTable() {
    // Obtener el valor del input de búsqueda
    var input = document.getElementById("search-input");
    var filter = input.value.toLowerCase();
    
    // Obtener la tabla y sus filas
    var table = document.getElementById("turnos-table");
    var rows = table.getElementsByTagName("tr");

    // Recorrer las filas de la tabla y ocultar las que no coincidan con la búsqueda
    for (var i = 1; i < rows.length; i++) { // Empieza en 1 para saltar el encabezado
        var turno = rows[i].getElementsByTagName("td")[0].textContent.toLowerCase();
        var area = rows[i].getElementsByTagName("td")[1].textContent.toLowerCase();
        var nombres = rows[i].getElementsByTagName("td")[4].textContent.toLowerCase();
        
        // Comparar con el texto de búsqueda
        if (turno.includes(filter) || area.includes(filter) || nombres.includes(filter)) {
            rows[i].style.display = ""; // Mostrar la fila
        } else {
            rows[i].style.display = "none"; // Ocultar la fila
        }
    }
}

