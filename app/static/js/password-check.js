const new_password = document.getElementById('new_password');
const confirm_password = document.getElementById('confirm_password');
const mensaje = document.getElementById('mensaje');

function verificarPassword() {
    if (confirm_password.value === new_password.value && new_password.value !== "") {
        mensaje.textContent = '✅ Las contraseñas coinciden';
        mensaje.className = 'mensaje correcto';
    } else {
        mensaje.textContent = '❌ Las contraseñas no coinciden';
        mensaje.className = 'mensaje incorrecto';
    }
}

new_password.addEventListener('input', verificarPassword);
confirm_password.addEventListener('input', verificarPassword);
