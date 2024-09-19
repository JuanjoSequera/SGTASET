

const notificacionSwal = (titleTex, text, icon, confirmButtonText) => {
        swal.fire({
        titleText: titleTex,
        text: text,
        icon: icon,
        showConfirmButtonText: confirmButtonText,
    })
}
