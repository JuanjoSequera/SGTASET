const btnEliminacion = document.querySelectorAll(".btnEliminacion");

(function () {

    // notificacionSwal(document.title, 'tablero listados con éxito', 'success', 'OK');
    
    
    /*
    btnEliminacion.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const confrmacion = confirm('seguro de eliminar esta fila?');
            if (!confrmacion) {
                e.preventDefault();
            }
        });
    });
    */
        btnEliminacion.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            Swal.fire({
                title: "¿Estás seguro?",
                showCancelButton: true,
                confirmButtonText: 'Eliminar',
                confirmButtonColor: "#d33",
                backdrop: true,
                showLoaderOnConfirm: true,
                preConfirm: () => {
                    location.href = e.target.href;
                },
                allowOutsideClick: () => false,
                allowEscapekey: () => false,
            })
        });
    });

})();


    // Obtenemos el input del salario
const inputSalario = document.getElementById('txtSalario');

    // Función para agregar separador de miles
function addThousandsSeparator(inputSalario) {
    num = inputSalario
    return num.toLocaleString("es-US");
}


