document.addEventListener("DOMContentLoaded", function(event) {
    var video = document.getElementById('video');
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err) {
            console.log("An error occurred: " + err);
        });

    var recognitionForm = document.getElementById('recognitionForm');
    recognitionForm.addEventListener('submit', function(event) {
        event.preventDefault();

        var canvas = document.getElementById('canvas');
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        var imageDataURL = canvas.toDataURL('image/png');

        fetch('http://localhost:5002/recognition', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                imagen_facial: imageDataURL.split(',')[1]
            })
        }).then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Reconocimiento facial exitoso: " + data.message);
                displayAlumnoInfo(data.data);
            } else {
                alert("Reconocimiento facial fallido: " + data.message);
            }
        })
        .catch(error => {
            console.error(error);
            alert("Error en la comunicación con el servidor.");
        });
    });

    function displayAlumnoInfo(alumno) {
        const infoDiv = document.getElementById('alumnosInfo');
        const imgDiv = document.getElementById('imagenPersona');
        infoDiv.style.display = 'block'; 
    
        const nombreArchivo = `${alumno.nombre}_${alumno.apellido}.png`;
        const imagePath = `http://localhost:5002/images_alumnos/${nombreArchivo}`;
    
        infoDiv.innerHTML = `<p><strong>Nombre:</strong> ${alumno.nombre}</p>
                             <p><strong>Apellido:</strong> ${alumno.apellido}</p>
                             <p><strong>Género:</strong> ${alumno.genero}</p>
                             <p><strong>Edad:</strong> ${alumno.edad}</p>
                             <p><strong>Nacionalidad:</strong> ${alumno.nacionalidad}</p>
                             <p><strong>CURP:</strong> ${alumno.curp}</p>
                             <p><strong>Escuela de aplicación de examen:</strong> ${alumno.APLescuela}</p>
                             <p><strong>Turno de aplicación de examen:</strong> ${alumno.APLturno}</p>
                             <p><strong>Tipo de Examen:</strong> ${alumno.tipoexa}</p>`;
        imgDiv.innerHTML = `<img src="${imagePath}" alt="Fotografía de ${alumno.nombre} ${alumno.apellido}" style="width:200px;height:auto;">`;
        console.log(`Imagen cargada desde: ${imagePath}`);
    }
});
