//
fetch('/api/v1/proyecto/allActive')
    .then(response => response.json())
    .then(data => {
        // Procesar la lista de proyectos
        const proyectos = data.data;

        console.log(proyectos);
    })
    .catch(error => console.error('Error al realizar la solicitud:', error));
