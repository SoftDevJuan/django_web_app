document.addEventListener('DOMContentLoaded', function() {
    const personas = [];

    const llamarTurno = document.getElementById('llamar-turno');
    const reLlamar = document.getElementById('re-llamar');
    const terminarBtn = document.getElementById('terminar-btn');
    const verTurnosDiv = document.getElementById('verturnos');
    const inputRazonSocial = document.getElementById('razonSocial');
    var modal = document.getElementById("mesaModal");
    var span = document.getElementsByClassName("close")[0];
    var usarMesaBtn = document.getElementById("usarMesa");
    var mesaSelect = document.getElementById("mesaSelect");
    var btnMesa = document.getElementById("mesa");
    var iniciarbtn = document.getElementById('iniciar-asesoria');
    var metricasbtn = document.getElementById('metricas');
    var cancelarbtn = document.getElementById('regresar-turno');
    var confirmarCancelacion = document.getElementById('confirmar-cancelacion');
    var numeroMesa = null;
    var idMesa = null;
    var idTurno = null;
    const tiempoDuracion = document.getElementById("tiempo");


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
        setInterval(actualizarConteo, 1000);
    }
    

    metricasbtn.addEventListener('click', function(){
        window.location.href = '/ratificacion_metricas_dashboard/'
    });



    function obtener_fuentes_de_trabajo(){
        fetch('/fuentes_de_trabajo/')
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
                    const datalist = document.getElementById("razonSocialList");
                    data.forEach(item => {
                        const option = document.createElement("option");
                        option.value = item.razon_social;
                        datalist.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error al obtener las fuentes de trabajo:', error);
            });
        }
            



    // Función que inicia la asesoría en el sistema
    function iniciarAsesoria(asesor, personasTotal, registro, turno, area, mesa) {
        
        const datosInico = {
            conciliador_id: asesor,
            mesa: mesa,
            turno: turno,
            area: area,
            cantidad_personas: personasTotal,
            registro: registro
        };

        console.log("estos serian los datos para iniciar: ", datosInico);
        const urlinciarasesoria = '/iniciar_ratificacion/';

        fetch(urlinciarasesoria, {
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

    // Función para terminar una asesoría
    function terminarAsesoria(dataToSend) {
        const urlDataSend = '/terminar_ratificacion/'; 

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



    // Consulta para indicar al asesor qué mesa tiene asignada actualmente
    var mesaurl = `/miMesa?usuario=${username}`;
    fetch(mesaurl)
        .then(response => response.json())
        .then(data => {
            btnMesa.textContent = `Mesa #${data.numero_mesa}`;
            numeroMesa = data.numero_mesa;
            idMesa = data.id_mesa;
            console.log("el id de la mesa es :", idMesa);

            // Validar si el asesor tiene un turno abierto sin concluir
            var urlvalidarabiertos =`/validar_turnos_abiertos_rati?user=${user_id}`;
            return fetch(urlvalidarabiertos);
        })
        .then(response => response.json())
        .then(data => {
            console.log("se supone que el turmo abierto: ", data);
            if (data.turno && data.turno !== 'none') {
                iniciarbtn.click();
            }
        })
        .catch(error => {
            console.log('Error al obtener la mesa del usuario', error);
            btnMesa.textContent = 'Mesa #';
        });

    // Consulta para indicar al asesor cuántos turnos quedan por atender
    function contadorTurnos() {
        fetch('/obtener_turnos_ratis')
            .then(response => {
                if (!response.ok) {
                    alert('Aun no hay turnos disponibles.');
                    location.reload();
                }
                return response.json();
            })
            .then(datos => {
                const turnos_pendientes = datos.filter(turno => turno.status === 'PEN');
                const count = turnos_pendientes.length;
                verTurnosDiv.textContent = `Turnos Pendientes: ${count}`;
            })
            .catch(error => {
                verTurnosDiv.textContent = error.message;
            });
    }

    // Iniciar el contador de turnos y actualizar turnos cada segundo
    contadorTurnos();
    setInterval(contadorTurnos, 15000);




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



    

    // funcion para notifcar en pantalla al turno que ha sido llamado
    reLlamar.addEventListener('click', function() {
        console.log("se re lllama");
        const url = 'cambiar_status_notificacion_rati/';
        const textoTurno = $('#turno-numero').text();
        const data = {
            turno_id: idTurno,
            notificacion: false
        };

        reLlamar.disabled = true;
        reLlamar.style.backgroundColor = 'orange';
        reLlamar.style.cursor = 'not-allowed';
        reLlamar.textContent = 'Espere...';

        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cambiar el estado de la notificación');
            }
            return response.json();
        })
        .catch(error => {
            console.error('Error:', error);
        })
        .finally(() => {
            setTimeout(() => {
                reLlamar.disabled = false;
                reLlamar.style.backgroundColor = '';
                reLlamar.style.cursor = '';
                reLlamar.textContent = 'Volver a llamar';
            }, 10000); // 10 segundos
        });
    });



/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Función para terminar una asesoría
    terminarBtn.addEventListener('click', function() {
        let dataToSend = {
            general: {},
            detalles: []
        };
        
        const turno = document.getElementById('turno-numero');
        const textoTurno = turno ? turno.textContent : null;
        const selectElement = document.getElementById('razonSocial');
        const selectedOption = selectElement ? selectElement.value : null;
        const textFieldElement = document.getElementById('observaciones-text');
        const textFieldValue = textFieldElement ? textFieldElement.value : null;
        const personasDivs = document.querySelectorAll('#personas-lista .persona');
        const folio_sinacol = document.getElementById('folio-sinacol');
    
    
    
        registro_ciudadano = personas[0].registro;
        var nuevoStatus = 'FIN';
        dataToSend.general = {
            turno_id: idTurno,
            observaciones: textFieldValue,
            registro : registro_ciudadano,
        };
    
        terminarAsesoria(dataToSend);
    
        const url = 'cambiar_status_rati/';
        const datos = {
            turno_id: idTurno,
            registro: registro_ciudadano,
            nuevoStatus: nuevoStatus,
            mesa: numeroMesa,
            user: user_id,
            
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
                alert('Aun no hay turnos disponibles');
                location.reload();
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
        reLlamar.style.display = 'none';
        llamarTurno.disabled = false;
        personas.length = 0;
        location.reload();

        
    });
    
    
    

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    // Método para llamar al siguiente turno, cambiar su estado a proceso e iniciar la asesoría en el sistema
    iniciarbtn.addEventListener('click', function() {
        const turnos_cards = document.getElementsByClassName('turno-board-cards'); // Selecciona los elementos con la clase 'turno-board-cards'

            // Itera sobre la colección HTML y oculta cada elemento
            for (let i = 0; i < turnos_cards.length; i++) {
                turnos_cards[i].style.display = 'none';
            }
        personas.length = 0;
        var url_llamar = `llamar_turno_ratis?mesa=${numeroMesa}&user=${user_id}`;
        fetch(url_llamar)
            .then(async response => {
                if (!response.ok) {
                    return response.json().then(error => {
                        alert(error.error);
                        location.reload();
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
                            documento_1: ciudadano.documento_1,
                            documento_2: ciudadano.documento_2,
                            documento_3: ciudadano.documento_3,
                            documento_4: ciudadano.documento_4,
                            documento_5: ciudadano.documento_5,
                            documento_6: ciudadano.documento_6
                        });
                    });
    
                    idTurno = data.id;
                    const personasLista = document.getElementById('personas-lista');
                    var turno_text = data.turno;
                    
                    if(turno_text.includes("-")){
                        folio_solicitud = data.turno.split("-")[1];
                        turno_text = data.turno.split("-")[0];
                    }
                    document.getElementById('turno-numero').textContent = turno_text;
                    personasLista.innerHTML = ''; 
    
                    personas.forEach(persona => {
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
                        personaNombre.id = `nombre${persona.id_persona}`;
    
                        const personaExito = document.createElement('label');
                        personaExito.className = 'persona-exito';
                        personaExito.textContent = ' - Concluye con éxito: ';
    
                        const radioSi = document.createElement('input');
                        radioSi.type = 'radio';
                        radioSi.name = `exito-${persona.id_persona}`;
                        radioSi.value = 'si';
                        radioSi.className = 'radio-si';
    
                        const labelSi = document.createElement('label');
                        labelSi.className = 'label-si';
                        labelSi.textContent = 'Sí';
    
                        const radioNo = document.createElement('input');
                        radioNo.type = 'radio';
                        radioNo.name = `exito-${persona.id_persona}`;
                        radioNo.value = 'no';
                        radioNo.className = 'radio-no';
    
                        const labelNo = document.createElement('label');
                        labelNo.className = 'label-no';
                        labelNo.textContent = 'No';
    
                        const radioOtro = document.createElement('input');
                        radioOtro.type = 'radio';
                        radioOtro.name = `exito-${persona.id_persona}`;
                        radioOtro.value = 'Otra Area';
                        radioOtro.className = 'radio-otro';
    
                        const labelOtro = document.createElement('label');
                        labelOtro.className = 'label-otro';
                        labelOtro.textContent = 'Otra Area';
                        
                        const imagenesContainer = document.createElement('div');
                        imagenesContainer.className = 'imagenes-container';

                        if(imgURL1 != '' && imgURL1 != ''){
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
                            imgPDF.id = `${persona.nombre}`;
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

                            adjuntosDiv.appendChild(imgPDF)
                            imagenesContainer.appendChild(adjuntosDiv);

                            
                        personaDiv.appendChild(personaNombre);
                        /*personaDiv.appendChild(personaExito);
                        personaDiv.appendChild(radioSi);
                        personaDiv.appendChild(labelSi);
                        personaDiv.appendChild(radioNo);
                        personaDiv.appendChild(labelNo);
                        personaDiv.appendChild(radioOtro);
                        personaDiv.appendChild(labelOtro);*/
                        personaDiv.appendChild(imagenesContainer);
                        personasLista.appendChild(personaDiv);

                        const storedValue = localStorage.getItem(`exito-${persona.id_persona}`);
                        if (storedValue) {
                            const radioSelected = personaDiv.querySelector(`input[name="exito-${persona.id_persona}"][value="${storedValue}"]`);
                            if (radioSelected) {
                                radioSelected.checked = true;
                            }
                        }
                    
                        // Evento para guardar la selección en localStorage cuando cambia el radio button
                        personaDiv.addEventListener('change', function() {
                            const radioValue = personaDiv.querySelector(`input[name='exito-${persona.id_persona}']:checked`)?.value;
                            if (radioValue) {
                                localStorage.setItem(`exito-${persona.id_persona}`, radioValue);
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
    
                    const selectRazon = document.getElementById('razonSocial');
                    const labelRazon = document.getElementById('label-razon');
                    obtener_fuentes_de_trabajo();
    
                    var turnoActual = document.querySelector('.turno-actual');
                    turnoActual.style.display = 'block';

                    var observaciones = document.querySelector('.observaciones');
                    observaciones.style.display = 'block';
                    llamarTurno.disabled = true;
                    btnMesa.disabled = true;
                    reLlamar.disabled = true;
                    iniciarbtn.disabled = true;
                    //cancelarbtn.disabled = true;
                    terminarBtn.style.display = 'block';
                    //selectRazon.style.display = 'block';
                    //labelRazon.style.display = 'block';
                    tiempoDuracion.style.display = 'block';
                    console.log("toda la data: ", data);
                    console.log("datetime: ", data.hora_inicio);
                    conteo_tiempo(data.hora_inicio);

                    
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
                
    
                iniciarAsesoria(user_id, cantidadPersonas, registro_ciudadano, data.id, 3, idMesa);
                

                console.log('en asesro, el id :', idTurno);
                const nuevoStatus = 'PRO';
                const url = 'cambiar_status_rati/';
                const datos = {
                    turno_id: idTurno,
                    registro: registro_ciudadano,
                    nuevoStatus: nuevoStatus,
                    mesa: numeroMesa,
                    user : user_id
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
                        alert('Aun no hay turnos disponibles');
                        location.reload();
                    }
                    return response.json();
                });
    
                area = data.area;
            })
            .catch(error => {
                alert(error.message);
                location.reload();
            });

            modalCancelar = document.getElementById('cancelarModal');
            const h2Element = modalCancelar.querySelector('h2');
            if (h2Element) {
                h2Element.style.color = 'black'; 
            }

            cancelarbtn.onclick = function() {
                console.log("si le dio click")
                modalCancelar.style.display = "block";
            };
        
            window.onclick = function(event) {
                if (event.target == modalCancelar) {
                    modalCancelar.style.display = "none";
                }
            };
    });



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////7///////
    confirmarCancelacion.addEventListener('click', function() {
        var turno = document.getElementById('turno-numero');
        
        const nuevoStatus = 'PEN';
        const url = 'cambiar_status_rati/';
        const datos = {
            turno_id: idTurno,
            nuevoStatus: nuevoStatus,
            mesa: numeroMesa,
            user: user_id
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
                alert('Aun no hay turnos disponibles');
                location.reload();
            }
            return response.json();
        });
        alert('Listo.');
        modalCancelar.style.display = 'none';
        location.reload();
    });

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////7///////

    
    llamarTurno.addEventListener('click', function() {
        const turnos_cards = document.getElementsByClassName('turno-board-cards'); 

            for (let i = 0; i < turnos_cards.length; i++) {
                turnos_cards[i].style.display = 'none';
            }
        personas.length = 0;
        var url_llamar = `llamar_turno_ratis?mesa=${numeroMesa}&user=${user_id}`;
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
                console.log("en la data", data);
                if (data) {
                    if(data.error){
                        alert("Este Turno tiene mas de 1 persona trabajadora.")
                        location.reload();
                        return;
                        
                    }else{
                    data.datosCiudadanos.forEach(ciudadano => {
                        personas.push({
                            id_persona : ciudadano.id_ciudadano,
                            nombre: ciudadano.nombre,
                            registro: data.registro,
                            area: data.area,
                            documento_1: ciudadano.documento_1,
                            documento_2: ciudadano.documento_2
                        });
                    });
    
                    console.log(personas[0]);
                    idTurno = data.id;
                    var turno_text = data.turno;
                    if(turno_text.includes("-")){
                        folio_solicitud = data.turno.split("-")[1];
                        turno_text = data.turno.split("-")[0];
                    }
                    const personasLista = document.getElementById('personas-lista');
                    document.getElementById('turno-numero').textContent = turno_text;
                    personasLista.innerHTML = ''; // Limpiar la lista de personas
    
                    var turnoActual = document.querySelector('.turno-actual');
                    turnoActual.style.display = 'block';
                    llamarTurno.disabled = true;
                    btnMesa.disabled = true;
                    reLlamar.style.display = 'block';
                    iniciarbtn.style.display = 'block';
                    cancelarbtn.style.display = 'block';
                    var option = document.getElementById('razonSocial');
                    var labelRazon = document.getElementById('label-razon');
                    labelRazon.style.display = 'none';
                    option.style.display = 'none';
                }
    
                const turno = document.getElementById('turno-numero');
                turno.style.display = 'flex';
                turno.style.justifyContent = 'center';
                turno.style.alignItems = 'center';
                turno.style.fontSize = '300px'; 
                const textoTurno = turno.textContent;
                const registro_ciudadano = personas[0].registro;
                area = personas[0].area;
                const cantidadPersonas = personas.length;
    
                const nuevoStatus = 'NOT';
                const notificacion_nueva = false;
                const url = 'cambiar_status_rati/';
                const datos = {
                    turno_id: idTurno,
                    registro: registro_ciudadano,
                    nuevoStatus: nuevoStatus,
                    mesa: numeroMesa,
                    user: user_id,
                    notificacion : notificacion_nueva
                };
    
                console.log("los datos", datos);
                fetch(url, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(datos)
                })
                .then(response => {
                    if (!response.ok) {
                        console.log('Aaun no hay turnos disponibles');
                        //location.reload();
                    }
                    return response.json();
                });
    
                area = data.area;
            }
            })
            .catch(error => {
                alert(error.message);
                location.reload();
            });

            modalCancelar = document.getElementById('cancelarModal');
            const h2Element = modalCancelar.querySelector('h2');
            if (h2Element) {
                h2Element.style.color = 'black'; 
            }

            cancelarbtn.onclick = function() {
                console.log("si le dio click")
                modalCancelar.style.display = "block";
            };
        
            window.onclick = function(event) {
                if (event.target == modalCancelar) {
                    modalCancelar.style.display = "none";
                }
            };
    });

});

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////7///////

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

window.onclick = function(event) {
    if (event.target == modalCancelar) {
        modalCancelar.style.display = "none";
    }
};