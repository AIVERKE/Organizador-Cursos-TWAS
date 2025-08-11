const asistencias = {};

document.addEventListener('DOMContentLoaded', () => {   /*Espera que la página se cargue completamente antes de ejecutar el código.*/
  const celdas = document.querySelectorAll('td[data-turno][data-dia]');

  celdas.forEach(celda => {
    const turno = celda.dataset.turno;
    const dia = celda.dataset.dia;

    // Estado inicial: false
    if (!asistencias[turno]) asistencias[turno] = {};
    asistencias[turno][dia] = false;
    actualizarEstiloCelda(celda, false);

    celda.addEventListener('click', () => {
      asistencias[turno][dia] = !asistencias[turno][dia];
      actualizarEstiloCelda(celda, asistencias[turno][dia]);
      console.log(asistencias); // Para pruebas
    });
  });
});

function actualizarEstiloCelda(celda, estado) {
  celda.classList.remove('asistencia-si', 'asistencia-no');
  celda.classList.add(estado ? 'asistencia-si' : 'asistencia-no');
  celda.textContent = estado ? '✔' : '✘';
}
