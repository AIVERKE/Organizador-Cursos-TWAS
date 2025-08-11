document.addEventListener('DOMContentLoaded', () => {
  // Este objeto debe venir desde el backend o un fetch()
  // Por ahora es un ejemplo simulado de cómo se recibiría
  const asistencias = {
    manana: {
      lunes: true,
      martes: false,
      miercoles: true,
      jueves: false,
      viernes: true
    },
    tarde: {
      lunes: false,
      martes: true,
      miercoles: false,
      jueves: true,
      viernes: false
    }
  };

  const celdas = document.querySelectorAll('td[data-turno][data-dia]');

  celdas.forEach(celda => {
    const turno = celda.dataset.turno;
    const dia = celda.dataset.dia;

    const estado = asistencias?.[turno]?.[dia] ?? false;
    actualizarEstiloCelda(celda, estado);
  });
});

function actualizarEstiloCelda(celda, estado) {
  celda.classList.remove('asistencia-si', 'asistencia-no');
  celda.classList.add(estado ? 'asistencia-si' : 'asistencia-no');
  celda.textContent = estado ? '✔' : '✘';
}
