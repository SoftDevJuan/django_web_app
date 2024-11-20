
document.addEventListener('DOMContentLoaded', function() {
    const personas = [];
    const terminarBtn = document.getElementById('terminar-btn');
    var modal = document.getElementById("mesaModal");
    var span = document.getElementsByClassName("close")[0];
    var usarMesaBtn = document.getElementById("usarMesa");
    var mesaSelect = document.getElementById("mesaSelect");
    var btnMesa = document.getElementById("mesa");
    var iniciarbtn = document.getElementById('iniciar-ratificacion');
    var confirmarCancelacion = document.getElementById('confirmar-cancelacion');
    var retrocederbtn = document.getElementById('retroceder');
    var numeroMesa = null;
    var idMesa = null;
    var idTurno = null;
    var idUser = null;
    const tiempoDuracion = document.getElementById("tiempo");

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function conteo_tiempo(inicio) {
    const fechaInicio = new Date(inicio);
    function actualizarConteo() {
        const ahora = new Date(); 
        const diferencia = ahora - fechaInicio; 

        
        const horas = Math.floor(diferencia / (1000 * 60 * 60));
        const minutos = Math.floor((diferencia % (1000 * 60 * 60)) / (1000 * 60));
        const segundos = Math.floor((diferencia % (1000 * 60)) / 1000);

        
        const horasFormateadas = horas.toString().padStart(2, "0");
        const minutosFormateados = minutos.toString().padStart(2, "0");
        const segundosFormateados = segundos.toString().padStart(2, "0");

        tiempoDuracion.textContent = `Tiempo de atención: ${horasFormateadas}:${minutosFormateados}:${segundosFormateados}`;
    }
    setInterval(actualizarConteo, 15000);
}

            
    // Función que inicia la conciliadororía en el sistema
    function iniciar_conciliacion(conciliador, personasTotal, registro, turno, area, mesa) {
        
        const datosInico = {
            conciliador_id: conciliador,
            mesa: mesa,
            turno: turno,
            area: area,
            cantidad_personas: personasTotal,
            registro: registro
        };

        console.log("estos serian los datos para iniciar: ", datosInico);
        const urlinciarconciliacion = '/iniciarConciliacion/';
        console.log(urlinciarconciliacion);

        fetch(urlinciarconciliacion, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosInico)
        })
        .then(response => response.json())
        .then(data => { 
            console.log(data)
        })
        .catch(error => {
            console.log(error.message);
        });
    }
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Función para terminar una conciliacion
    function terminar_conciliacion(dataToSend) {
        const urlDataSend = '/terminarConciliacion/'; 

        fetch(urlDataSend, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSend)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al enviar los datos');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            var texto_tiempo = tiempoDuracion.textContent;
            console.log(texto_tiempo);
            alert(data.mensaje + texto_tiempo);
        })
        .catch(error => {
            console.error('Error:', error);
        });
        
    }
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Consulta para indicar al concciliador qué mesa tiene asignada actualmente
    var mesaurl = `/miMesaRati?usuario=${username}`;
    console.log("el username: " , username);
    var urlvalidarabiertos =`/validar_turnos_abiertosRati?user=${username}`;
    fetch(mesaurl)
        .then(response => response.json())
        .then(data => {
            btnMesa.textContent = data.numero_mesa;
            numeroMesa = data.numero_mesa;
            idMesa = data.id_mesa;

            
            return fetch(urlvalidarabiertos);
        })
        .then(response => response.json())
        .then(data => {
            if (data.turno && data.turno !== 'none') {
                iniciarbtn.click();
            }
        })
        .catch(error => {
            console.log('Error al obtener la mesa del usuario', error);
            btnMesa.textContent = 'Mesa #';
        });
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Funciones para seleccionar una mesa de trabajo
    btnMesa.onclick = function() {
        modal.style.display = "block";
    };

    span.onclick = function() {
        modal.style.display = "none";
    };

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Funciones para el modal de selección de mesa
    usarMesaBtn.onclick = function() {
        numeroMesa = mesaSelect.value;
        if (!numeroMesa) {
            alert("Por favor, selecciona un número de mesa.");
            return;
        }
        fetch('/asignarMesaRati/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conciliador: username,
                mesa: numeroMesa
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                modal.style.display = "none";
                location.reload();
            } else {
                alert("Hubo un error al asignar la mesa. " + data.error);
            }
        })
        .catch(error => {
            alert("Hubo un error al asignar la mesa. " + error);
        });
    };
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Función para terminar una conciliacion
    terminarBtn.addEventListener('click', function() {
        let dataToSend = {
            general: {},
            detalles: []
        };
        
        const turno = document.getElementById('turno-numero');
        const textoTurno = turno ? turno.textContent : null;
        //const selectElement = document.getElementById('razonSocial');
        //const selectedOption = selectElement ? selectElement.value : null;
        const textFieldElement = document.getElementById('observaciones-text');
        //const textFieldValue = textFieldElement ? textFieldElement.value : "N/A";
        const personasDivs = document.querySelectorAll('#personas-lista .persona');
        //const folio_sinacol_solicitud = document.getElementById('folio-sinacol-solicitud');

        
    
        // Verificar si algún radio con valor 'Pago en Sitio' está seleccionado
        let algunSiSeleccionado = false;
        personasDivs.forEach((personaDiv) => {
            const radioSi = personaDiv.querySelector(`input[name^="exito-"][value="Convenio Pago"]:checked`); 
            if (radioSi) {
                algunSiSeleccionado = true;
            }
        });
    
        
    
        registro_ciudadano = personas[0].registro;
        var nuevoStatus = 'FIN';
        
        // Datos generales de la conciliacion
        dataToSend.general = {
            turno: idTurno,
            registro : registro_ciudadano,
        };
        
        // Datos específicos de cada persona en la conciliacion
        let valid = true;
        personasDivs.forEach((personaDiv) => {
            
            const personaNombreElement = personaDiv.querySelector('.persona-nombre');
            if (!personaNombreElement) {
                console.error('persona-nombre element not found');
                valid = false;
                return;
            }
            const personaNombre = personaNombreElement.textContent;
            const persona = personas.find(persona => persona.nombre === personaNombre);
            if (!persona) {
                console.error(`Persona with name ${personaNombre} not found in personas array`);
                valid = false;
                return;
            }
            const personaId = persona.id_persona;
        
            dataToSend.detalles.push({
                id_ciudadano: personaId,
            });
            
            
        });
        
        console.log('Data to send:', dataToSend);
        terminar_conciliacion(dataToSend);
    
        const url = 'cambiar_statusRati/';
        const datos = {
            turno: idTurno,
            registro: registro_ciudadano,
            nuevoStatus: nuevoStatus,
            mesa: numeroMesa
        };
    
        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datos)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('No se encontraron turnos');
            }
            return response.json();
        });
    
        // Clear the HTML data
        const personasLista = document.getElementById('personas-lista');
        while (personasLista.firstChild) {
            personasLista.removeChild(personasLista.firstChild);
        }
    
        var turnoActual = document.querySelector('.turno-actual');
        turnoActual.style.display = 'none';
        var observaciones = document.querySelector('.observaciones');
        observaciones.style.display = 'none';
        terminarBtn.style.display = 'none';
        personas.length = 0;
        //location.reload();

        
    });
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    // Método para llamar al siguiente turno, cambiar su estado a proceso e iniciar la conciliación en el sistema
    iniciarbtn.addEventListener('click', function() {
        const turnos_cards = document.getElementsByClassName('turno-board-cards'); // Selecciona los elementos con la clase 'turno-board-cards'

            // Itera sobre la colección HTML y oculta cada elemento
            for (let i = 0; i < turnos_cards.length; i++) {
                turnos_cards[i].style.display = 'none';
            }
        personas.length = 0;
        var url_llamar = `llamar_turnoRati?user=${username}`;
        fetch(url_llamar)
            .then(async response => {
                if (!response.ok) {
                    return response.json().then(error => {
                        throw new Error(error.error);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    data.datosCiudadanos.forEach(ciudadano => {
                        personas.push({
                            id_persona : ciudadano.id_ciudadano,
                            nombre: ciudadano.nombre,
                            registro: data.registro,
                            area: data.area,
                            tipo_persona :  ciudadano.tipo_persona,
                            documento_1: ciudadano.documento_1,
                            documento_2: ciudadano.documento_2,
                            documento_3: ciudadano.documento_3,
                            documento_4: ciudadano.documento_4,
                            documento_5: ciudadano.documento_5,
                            documento_6: ciudadano.documento_6
                        });
                    });
    
                    console.log(personas[0]);
                    idTurno = data.id;
                    const personasLista = document.getElementById('personas-lista');
                    document.getElementById('turno-numero').textContent = data.turno;
                    personasLista.innerHTML = ''; // Limpiar la lista de personas
    
                    personas.forEach(persona => {

                        console.log("el tipo de persona:" , persona.tipo_persona);
                        const imgURL1 = persona.documento_1 ? `${persona.documento_1}` : '';
                        const imgURL2 = persona.documento_2 ? `${persona.documento_2}` : '';
                        const imgURL3 = persona.documento_3 ? `${persona.documento_3}` : '';
                        const imgURL4 = persona.documento_4 ? `${persona.documento_4}` : '';
                        const imgURL5 = persona.documento_5 ? `${persona.documento_5}` : '';
                        const imgURL6 = persona.documento_6 ? `${persona.documento_6}` : '';

                        const personaDiv = document.createElement('div');
                        const adjuntosDiv = document.createElement('div');
                        adjuntosDiv.className ='adjuntos';
                        personaDiv.className = 'persona';
                        
                        const personaNombre = document.createElement('span');
                        personaNombre.className = 'persona-nombre';
                        personaNombre.textContent = persona.nombre;

                        if(persona.tipo_persona.includes("Trabajadora")){
                            var tipop = "Trabajador";
                        }else if (persona.tipo_persona.includes("Empleador")){
                            tipop = "Empleador";
                        }else if (persona.tipo_persona.includes("Confianza")){
                            tipop = "Invitado";
                        }

                        const personaTipo = document.createElement('span');
                        personaTipo.className = 'persona-tipo';
                        personaTipo.textContent = tipop;

                        personaDiv.appendChild(personaTipo);
                        personaDiv.appendChild(personaNombre);
                        


                        const imagenesContainer = document.createElement('div');
                        imagenesContainer.className = 'imagenes-container';

                        if(imgURL1 != '' && imgURL2 != ''){
                            console.log('no hay testigos');
                            if (imgURL1) {
                                const imagen1 = document.createElement('img');
                                imagen1.src = imgURL1;
                                imagen1.alt = 'Imagen 1';
                                imagen1.className = 'imagen-persona';
                                imagenesContainer.appendChild(imagen1);
                            }
        
                            if (imgURL2) {
                                const imagen2 = document.createElement('img');
                                imagen2.src = imgURL2;
                                imagen2.alt = 'Imagen 2';
                                imagen2.className = 'imagen-persona';
                                imagenesContainer.appendChild(imagen2);
                            }
                            
                        }else{
                            if (imgURL3) {
                                const imagen3 = document.createElement('img');
                                imagen3.src = imgURL3;
                                imagen3.alt = 'INE testigo 1 frontal';
                                imagen3.className = 'imagen-persona';
                                imagenesContainer.appendChild(imagen3);
                            }
        
                            if (imgURL4) {
                                const imagen4 = document.createElement('img');
                                imagen4.src = imgURL4;
                                imagen4.alt = 'INE testigo 1 trasera ';
                                imagen4.className = 'imagen-persona';
                                imagenesContainer.appendChild(imagen4);
                            }
                            if (imgURL5) {
                                const imagen5 = document.createElement('img');
                                imagen5.src = imgURL5;
                                imagen5.alt = 'INE testigo 2 frontal';
                                imagen5.className = 'imagen-persona';
                                imagenesContainer.appendChild(imagen5);
                            }
        
                            if (imgURL6) {
                                const imagen6 = document.createElement('img');
                                imagen6.src = imgURL6;
                                imagen6.alt = 'INE testigo 2 trasera';
                                imagen6.className = 'imagen-persona';
                                imagenesContainer.appendChild(imagen6);
                            }
                        }
                        
                        const imgPDF = document.createElement('img');
                            imgPDF.src = '/static/icon/descargar-en-pdf.png';
                            imgPDF.alt = 'PDF icon';
                            imgPDF.className = 'img-pdf';
                            imgPDF.id = `${persona.nombre}${persona.registro}`;
                            imgPDF.addEventListener('click', () => {
                                imgPDF.style.opacity = "0.5";  
                                imgPDF.style.cursor = "wait";
                                if(imgURL1 && imgURL2){
                                    convertirYDescargarPDF(imgURL1, imgURL2, `${persona.nombre}`);
                                }else{
                                    convertirYDescargarPDF(imgURL3, imgURL4, `testigo1`);
                                    convertirYDescargarPDF(imgURL5, imgURL6, `testigo2`);
                                }

                                setTimeout(() => {
                                    imgPDF.style.opacity = "1"; 
                                    imgPDF.style.cursor = "pointer";
                                }, 5000);
                                
                            });

                            const textoDescargar = document.createElement('p');
                            textoDescargar.textContent = 'Descargar Identificacion PDF';
                            textoDescargar.className = 'descargar-pdf-id';

                            adjuntosDiv.appendChild(imgPDF);
                            adjuntosDiv.appendChild(textoDescargar);
                            imagenesContainer.appendChild(adjuntosDiv);
                            
                        
                        personaDiv.appendChild(imagenesContainer);
                        personasLista.appendChild(personaDiv);

                        const storedValue = localStorage.getItem(`exito-${persona.nombre}`);
                        if (storedValue) {
                            const radioSelected = personaDiv.querySelector(`input[name="exito-${persona.nombre}"][value="${storedValue}"]`);
                            if (radioSelected) {
                                radioSelected.checked = true;
                            }
                        }
                    
                        // Evento para guardar la selección en localStorage cuando cambia el radio button
                        personaDiv.addEventListener('change', function() {
                            const radioValue = personaDiv.querySelector(`input[name='exito-${persona.nombre}']:checked`)?.value;
                            if (radioValue) {
                                localStorage.setItem(`exito-${persona.nombre}`, radioValue);
                            }
                        });

                    });
                    
                    var modal = document.getElementById('myModal');
                    var modalImg = document.getElementById('modalImg');
                    var imagenes = document.querySelectorAll('.imagen-persona');
                    imagenes.forEach(function(imagen) {
                        imagen.addEventListener('click', function() {
                            modal.style.display = 'block';
                            modalImg.src = this.src;
                        });
                    });
                    window.onclick = function(event) {
                        if (event.target == modal) {
                            modal.style.display = 'none';
                        }
                    };
    
                
    
                    var turnoActual = document.querySelector('.turno-actual');
                    turnoActual.style.display = 'block';

                    var observaciones = document.querySelector('.observaciones');
                    observaciones.style.display = 'block';
                    btnMesa.disabled = true;
                    iniciarbtn.disabled = true;
                    terminarBtn.style.display = 'block';
                    //reloj.style.display = 'block'
                    //selectRazon.style.display = 'block';
                    //labelRazon.style.display = 'block';  
                    tiempoDuracion.style.display = 'block';
                    console.log("toda la data: ", data);
                    console.log("datetime: ", data.hora_inicio);
                    conteo_tiempo(data.inicio);                 
                }
    
                const turno = document.getElementById('turno-numero');
                const textoTurno = turno.textContent;
                turno.style.fontSize = "";
                const turnoH2 = document.getElementById('turno-id');
                turnoH2.style.display = 'flex';
                turnoH2.style.justifyContent = 'center';
                turnoH2.style.alignItems = 'center';
                const registro_ciudadano = personas[0].registro;
                area = personas[0].area;
                const cantidadPersonas = personas.length;
                    
                iniciar_conciliacion(user_id, cantidadPersonas, registro_ciudadano, data.id, 1, idMesa);
                    
                const nuevoStatus = 'PRO';
                const url = 'cambiar_statusRati/';
                const datos = {
                    turno: idTurno,
                    registro: registro_ciudadano,
                    nuevoStatus: nuevoStatus,
                    mesa: numeroMesa
                };
    
                fetch(url, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(datos)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('No se encontraron turnos');
                    }
                    return response.json();
                });
    
                area = data.area;
            })
            .catch(error => {
                alert(error.message);
            });
    });
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////7///////
    
    confirmarCancelacion.addEventListener('click', function() {
        var turno = document.getElementById('turno-numero');
        const textoTurno = turno.textContent;
        const registro_ciudadano = personas[0].registro;
        const nuevoStatus = 'CAN';
        const url = 'cambiar_statusRati/';
        const datos = {
            turno: idTurno,
            registro: registro_ciudadano,
            nuevoStatus: nuevoStatus,
            mesa: numeroMesa
        };

        console.log(datos);

        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datos)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('No se encontraron turnos');
            }
            return response.json();
        });
        alert('Cancelado.');
        modalCancelar.style.display = 'none';
        location.reload();
    });
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////7///////

retrocederbtn.addEventListener('click', function (){
    console.log('retroceder');
    const registro_ciudadano = personas[0].registro;
        const nuevoStatus = 'PEN';
        const url = 'cambiar_statusRati/';
        const datos = {
            turno: idTurno,
            registro: registro_ciudadano,
            nuevoStatus: nuevoStatus,
            mesa: numeroMesa
        };

        console.log(datos);

        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datos)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('No se encontraron turnos');
            }
            return response.json();
        });
        alert('Listo, el turno ahora esta en espera.');
        location.reload();

});

}); //domloaded
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function convertirYDescargarPDF(img1, img2, nombre_ciudadano) {
    // Función para extraer el nombre del archivo de la ruta
    function extractFileName(path) {
        return path.split('/').pop();
    }

    // Extraer nombres de archivos
    var fileName1 = extractFileName(img1);
    var fileName2 = extractFileName(img2);

    // Construir la URL con parámetros de consulta
    var url = new URL('/pdf_local/', window.location.origin);
    url.searchParams.append('img1', fileName1);
    url.searchParams.append('img2', fileName2);
    url.searchParams.append('nombre', nombre_ciudadano);

    // Realizar la solicitud fetch
    fetch(url)
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    // Mostrar alerta con el mensaje de error y paths
                    alert(`Error: ${data.error}\nPath imagen 1: ${data.image_path_front}\nPath imagen 2: ${data.image_path_back}`);
                    throw new Error(data.error);
                });
            }
            return response.blob();
        })
        .then(blob => {
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${nombre_ciudadano}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error:', error));
}



