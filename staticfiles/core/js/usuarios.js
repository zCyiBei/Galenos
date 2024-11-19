$(document).ready(function() {

  // Asignar placeholders para ayudar a los usuarios
  $('#id_username').attr('placeholder', 'Ej: JuanR');
  $('#id_first_name').attr('placeholder', 'Ej: Juan');
  $('#id_last_name').attr('placeholder', 'Ej: Riveros');
  $('#id_email').attr('placeholder', 'Ej: juanr@ss.com');
  $('#id_rut').attr('placeholder', 'Ej: 11111111-1 (sin puntos y con guión)');
  $('#id_direccion').attr('placeholder', 'Calle, n° casa o edificio, n° departamento o piso\n'
    + 'localidad o ciudad, código postal o de área\n'
    + 'estado o provincia, ciudad, país');

  // Cambiar el texto del combo de Tipo de usuario por "Seleccione un tipo de usuario"
  var select = document.querySelector('select[name="tipo_usuario"]');
  if (select) {
      var defaultOption = select.querySelector('option[value=""]');
      if (defaultOption) {
          defaultOption.text = "Seleccione un tipo de usuario";
      }
  }

  // Agregar una validación por defecto para que la imagen la exija como campo obligatorio
  $.extend($.validator.messages, {
    required: "Este campo es requerido",
  });

  // Configuración de validación del formulario
  $('#form-usuarios').validate({ 
      rules: {
        'username': {
          required: true,
        },
        'tipo_usuario': {
          required: true,
          inList: ['Cliente', 'Administrador'],
        },
        'first_name': {
          required: true,
          soloLetras: true,
        },
        'last_name': {
          required: true,
          soloLetras: true,
        },
        'email': {
          required: true,
          emailCompleto: true,
        },
        'rut': {
          required: true,
          rutChileno: true,
        },
        'direccion': {
          required: true,
        },
      },
      messages: {
        'username': {
          required: 'Debe ingresar un nombre de usuario',
        },
        'tipo_usuario': {
          required: 'Debe ingresar un tipo de usuario',
          inList: 'Debe ingresar un tipo de usuario válido',
        },
        'first_name': {
          required: 'Debe ingresar su nombre',
          soloLetras: "El nombre sólo puede contener letras y espacios en blanco",
        },
        'last_name': {
          required: 'Debe ingresar sus apellidos',
          soloLetras: "Los apellidos sólo pueden contener letras y espacios en blanco",
        },
        'email': {
          required: 'Debe ingresar su correo',
          emailCompleto: 'El formato del correo no es válido',
        },
        'rut': {
          required: 'Debe ingresar su RUT',
          rutChileno: 'El formato del RUT no es válido',
        },
        'direccion': {
          required: 'Debe ingresar su dirección',
        },
      },
      errorElement: 'div', // Utiliza un elemento <div> para los mensajes de error
      errorClass: 'invalid-feedback', // Aplica la clase de Bootstrap para los mensajes de error
      errorPlacement: function(error, element) {
          error.appendTo(element.parent()); // Inserta el mensaje de error después del elemento padre
      },
      highlight: function(element, errorClass, validClass) {
          $(element).addClass('is-invalid'); // Aplica la clase de Bootstrap para resaltar errores
      },
      unhighlight: function(element, errorClass, validClass) {
          $(element).removeClass('is-invalid'); // Quita la clase de Bootstrap cuando se corrige el error
      }
  });

  $('#id_generar_password').click(function() {
    // Ejemplo de acción al hacer clic en un elemento
    $("#change_password_indicator").val("Nuevo valor del campo");
    $("#change_password_username").val("Nuevo valor del campo");
  });

});
