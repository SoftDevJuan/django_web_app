//script para actiañizar el reloj cada segundo

function actualizarReloj(){
    const hoy = new Date();
    const dia = String(hoy.getDate()).padStart(2,'0');
    const mes = String(hoy.getMonth()).padStart(2,'0');
    const año = String(hoy.getFullYear());
    const horas = String(hoy.getHours()).padStart(2,'0');
    const minutos = String(hoy.getMinutes()).padStart(2,'0');
    const segundos = String(hoy.getSeconds()).padStart(2,'0');
    const semana = ['Domingo', 'Lunes', 'Martes','Miercoles','Jueves','Viernes','Sabado'];
    const mes_str = ['Enero', 'Febrero', 'Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
    const indexDia = hoy.getDay();
    const indexMes = hoy.getMonth();
    const nombreDia = semana[indexDia];
    const nombreMes = mes_str[indexMes]
    const fechaString = `${nombreDia} ${dia} de ${nombreMes} del ${año}`;
    const horaString = `${horas}:${minutos}:${segundos}`;
    document.getElementById('reloj').textContent = `${fechaString}, ${horaString} hrs.`
}

actualizarReloj();
setInterval(actualizarReloj, 1000);
