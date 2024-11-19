// static/js/citas.js

document.addEventListener("DOMContentLoaded", function() {
  // Función para eliminar una cita
  const botonesEliminar = document.querySelectorAll('.eliminar-cita');

  botonesEliminar.forEach(function(boton) {
      boton.addEventListener('click', function(event) {
          event.preventDefault();  // Evita que se recargue la página al hacer clic
          const fila = boton.closest('tr');  // Encuentra la fila de la cita
          const citaId = fila.dataset.id;  // Obtiene el ID de la cita (debe estar en el data-id)

          // Aquí podrías enviar una solicitud al servidor para eliminar la cita
          // Por ahora, solo ocultamos la fila para simular que la cita fue eliminada
          fila.style.display = 'none';

          // Ejemplo de cómo podrías hacer una solicitud AJAX para eliminar la cita:
          fetch(`/eliminar_cita/${citaId}/`, {
              method: 'DELETE',
              headers: {
                  'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value  // CSRF token
              }
          }).then(response => {
              if (response.ok) {
                  alert('Cita eliminada');
              } else {
                  alert('Hubo un problema al eliminar la cita');
              }
          }).catch(error => {
              console.error('Error:', error);
              alert('Hubo un error al eliminar la cita');
          });
      });
  });

  // Función para cambiar el estado de una cita
  const botonesEstado = document.querySelectorAll('.cambiar-estado');

  botonesEstado.forEach(function(boton) {
      boton.addEventListener('click', function(event) {
          event.preventDefault();  // Evita que se recargue la página al hacer clic
          const fila = boton.closest('tr');  // Encuentra la fila de la cita
          const estadoActual = fila.querySelector('.estado-cita');  // Encuentra el estado actual
          const nuevoEstado = estadoActual.textContent === 'pendiente' ? 'confirmada' : 'pendiente';  // Cambia el estado

          // Actualiza el estado en la vista
          estadoActual.textContent = nuevoEstado;

          // Aquí podrías hacer una solicitud AJAX para actualizar el estado en el servidor
          const citaId = fila.dataset.id;  // Obtiene el ID de la cita

          fetch(`/actualizar_estado_cita/${citaId}/`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value  // CSRF token
              },
              body: JSON.stringify({ estado: nuevoEstado })
          }).then(response => {
              if (response.ok) {
                  alert(`Estado actualizado a ${nuevoEstado}`);
              } else {
                  alert('Hubo un problema al actualizar el estado');
              }
          }).catch(error => {
              console.error('Error:', error);
              alert('Hubo un error al actualizar el estado');
          });
      });
  });
});
