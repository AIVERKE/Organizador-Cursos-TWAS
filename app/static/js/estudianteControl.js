function mostrarSeccion(seccion) {
  const datos = document.getElementById('seccion-datos');
  const iframe = document.getElementById('seccion-iframe');

  datos.style.display = (seccion === 'datos') ? 'block' : 'none';
  iframe.style.display = (seccion === 'iframe') ? 'block' : 'none';

  const enlaces = document.querySelectorAll('.menu a');
  enlaces.forEach(e => e.classList.remove('activo'));
  if (seccion === 'datos') {
    enlaces[0].classList.add('activo');
  }
}

function mostrarIframe(url, elemento) {
  document.getElementById('seccion-datos').style.display = 'none';
  const iframe = document.getElementById('seccion-iframe');
  // iframe.src = `/templates/Estudiante/${url}`;
  iframe.src = url;

  iframe.style.display = 'block';

  const enlaces = document.querySelectorAll('.menu a');
  enlaces.forEach(e => e.classList.remove('activo'));
  if (elemento) {
    elemento.classList.add('activo');
  }
}

// Mostrar datos por defecto al cargar
window.onload = () => mostrarSeccion('datos');
