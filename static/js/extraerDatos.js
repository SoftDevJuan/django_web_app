function encontrarMunicipio(domicilios) {
    if (Array.isArray(domicilios)) {
        for (var i = 0; i < domicilios.length; i++) {
            if (domicilios[i].municipio) {
                return domicilios[i].municipio;
            }
        }
    }
    return "Municipio no disponible";
}

function obtenerCitados(d){
    var objSolicitados = d.Respuesta.data.solicitados;
    var tipo_solicitud_id = d.Respuesta.data.tipo_solicitud_id;
    citados = {};

  
    Object.keys(objSolicitados).forEach(function(key, index) {
        var persona = objSolicitados[key];
        var parte = {};
        var tipo_persona = "";

        if(tipo_solicitud_id === 3 || tipo_solicitud_id === 2){
            tipo_persona = "Soy Persona Trabajadora";
        }else if (tipo_solicitud_id === 1){

            if(persona.tipo_persona_id === 1){
                tipo_persona = "Soy Persona Física Empleadora";
            }else {
                tipo_persona = "Soy Persona Jurídica Empleadora";
            }
        }
    


        if (persona.tipo_persona_id === 1) {
            parte['nombreCompleto'] = persona.nombre + " " + persona.primer_apellido + " " + persona.segundo_apellido;
            var municipio = encontrarMunicipio(persona.domicilios || []);
            parte['municipio'] = municipio;
        } else {
            parte['nombreComercial'] = persona.nombre_comercial;
            var municipio = encontrarMunicipio(persona.domicilios || []);
            parte['municipio'] = municipio;
        }
        parte['sexo'] = persona.genero_id;
        parte['tipo_persona'] = tipo_persona;
        
        citados['Citados' + index] = parte;
    });
    return citados;
}

function folioSolicitud(d){
    var folio = d.Respuesta.data.folio;
    var anio = d.Respuesta.data.anio;
    folioCompleto = folio + "/" + anio;
    return folioCompleto;
}

function obtenerSolicitantes(d){
    var objSolicitantes = d.Respuesta.data.solicitantes;
    var tipo_solicitud_id = d.Respuesta.data.tipo_solicitud_id;
    solicitantes = {};

    
    Object.keys(objSolicitantes).forEach(function(key, index) {
        var persona = objSolicitantes[key];
        var parte = {};
        var tipo_persona_id = persona.tipo_persona_id;
        var tipo_parte_id = persona.tipo_parte_id;
        var tipo_persona = "";

        if(tipo_solicitud_id === 3 || tipo_solicitud_id === 2){
            if(persona.tipo_persona_id === 1){
                tipo_persona = "Soy Persona Física Empleadora";
            }else {
                tipo_persona = "Soy Persona Jurídica Empleadora";
            }
        }else if (tipo_solicitud_id === 1){
            tipo_persona = "Soy Persona Trabajadora";
        }
        

        if (persona.tipo_persona_id === 1) {
            parte['nombreCompleto'] = persona.nombre + " " + persona.primer_apellido + " " + persona.segundo_apellido;
            var municipio = encontrarMunicipio(persona.domicilios || []);
            parte['municipio'] = municipio;
        } else {
            parte['nombreComercial'] = persona.nombre_comercial;
            var municipio = encontrarMunicipio(persona.domicilios || []);
            parte['municipio'] = municipio;
        }
        parte['sexo'] = persona.genero_id;
        parte['tipo_persona'] = tipo_persona;
        
        solicitantes['Solicitante' + index] = parte;
    });
    return solicitantes;
}

function obtenerTipoSolicitud(d){
    var objTipoSolicitud = d.Respuesta.data.tipo_solicitud;
    tipo_solicitud = objTipoSolicitud['nombre'];
    return tipo_solicitud;
}