(function () {
    const btnEliminacion = document.querySelectionAll(".btnEliminacion");

    btnEliminacion.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const confrmacion = confirm('seguro de eliminar el curso?');
            if (!confrmacion) {
                e.preventDefault();
            }
        });
    });

})();

