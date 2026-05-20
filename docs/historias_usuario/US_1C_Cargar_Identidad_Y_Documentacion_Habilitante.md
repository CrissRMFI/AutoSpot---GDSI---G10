# US 1C: Cargar de identidad y documentación habilitante

**Sprint:** 2
**Actor:** Conductor
**Prioridad:** Alta

## Descripcion
**Como** Conductor registrado en la plataforma
**quiero** cargar mi documentación habilitante (licencia de conducir)
**para** poder contratar Activos en AutoSpot.

La US 1U cubre los datos de identidad básicos (DNI, nombre, apellido y fotos del DNI).
Esta US incorpora la documentación específica que habilita al Conductor a operar un
Activo: la licencia de conducir, sus fotos y los datos de vigencia.

## Criterios de Aceptacion

### CA 1
**Dado que** tengo una cuenta creada y mis datos personales registrados,
**cuando** cargo número de licencia, categoría, fecha de emisión y fecha de vencimiento,
**entonces** mi documentación habilitante queda registrada en la plataforma.

### CA 2
**Dado que** tengo una cuenta creada,
**cuando** subo foto del frente y dorso de mi licencia de conducir,
**entonces** la documentación habilitante queda asociada a mi Conductor.

### CA 3
**Dado que** tengo una cuenta creada,
**cuando** intento guardar la documentación habilitante con un campo obligatorio
omitido, vacío o inválido (por ejemplo, vencimiento anterior a la fecha de emisión),
**entonces** el registro no se realiza y se informa el error.

### CA 4
**Dado que** ya cargué mi documentación habilitante,
**cuando** intento volver a registrarla,
**entonces** el sistema rechaza el segundo registro y me ofrece actualizarla en su
lugar.

### CA 5
**Dado que** ya cargué mi documentación habilitante,
**cuando** la actualizo (renovación, cambio de categoría, re-subida de fotos),
**entonces** el sistema persiste los nuevos datos y conserva la asociación con mi
Conductor.

## Diseño

### Backend
- Tabla nueva `documentacion_habilitante_conductor` con FK a `usuarios.id` (1:1).
- Endpoints:
  - `GET  /usuarios/{usuario_id}/documentacion-habilitante`
  - `PUT  /usuarios/{usuario_id}/documentacion-habilitante`
  - `PUT  /usuarios/{usuario_id}/documentacion-habilitante/actualizar`
- Autenticación JWT. El `sub` del token debe coincidir con `usuario_id`.

### Frontend
- Página `/documentacion-habilitante` (protegida).
- Tarjeta en el Dashboard que dirija al formulario.

### Estado inicial
- `estado_validacion = "PENDIENTE_VALIDACION"` (Operador de Estación valida en
  historias futuras).
