var captura = 0;
var video = document.createElement("video");
var canvasElement = document.getElementById("canvas");
var canvas = canvasElement.getContext("2d");
var loadingMessage = document.getElementById("loadingMessage");
var outputContainer = document.getElementById("output");
var outputMessage = document.getElementById("outputMessage");
var outputData = document.getElementById("outputData");





function drawLine(begin, end, color) {
canvas.beginPath();
canvas.moveTo(begin.x, begin.y);
canvas.lineTo(end.x, end.y);
canvas.lineWidth = 4;
canvas.strokeStyle = color;
canvas.stroke();
}

// Use facingMode: environment to attemt to get the front camera on phones
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(function(stream) {
video.srcObject = stream;
video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
video.play();
requestAnimationFrame(tick);
});

function tick() {
loadingMessage.innerText = "⌛ Loading video..."
if (video.readyState === video.HAVE_ENOUGH_DATA) {
    loadingMessage.hidden = true;
    canvasElement.hidden = false;
    outputContainer.hidden = false;

    canvasElement.height = video.videoHeight;
    canvasElement.width = video.videoWidth;
    canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);
    var imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height);
    var code = jsQR(imageData.data, imageData.width, imageData.height, {
    inversionAttempts: "dontInvert",
    });
    if (code&&captura!=1) {
    drawLine(code.location.topLeftCorner, code.location.topRightCorner, "#0a1f8f");
    drawLine(code.location.topRightCorner, code.location.bottomRightCorner, "#0a1f8f");
    drawLine(code.location.bottomRightCorner, code.location.bottomLeftCorner, "#0a1f8f");
    drawLine(code.location.bottomLeftCorner, code.location.topLeftCorner, "#0a1f8f");
    
    outputMessage.hidden = true;
    outputData.parentElement.hidden = false;
    outputData.innerText = code.data;
    $infoQR = code.data;
    document.getElementById('info').value = $infoQR;
    captura=1;
    video.pause();
    $('#lector').hide();
    $('#carga').show();
    $('#info').val($infoQR);
    $('#texto_carga').text("Cargando, espere un momento porfavor...");
    //$('#lectorQR').submit();
    $('#lectorQR').trigger('submit');
    }
}
requestAnimationFrame(tick);
}