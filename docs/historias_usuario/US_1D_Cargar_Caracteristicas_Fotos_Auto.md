# US 1D: Cargar caracteristicas y fotos del auto

**Sprint:** 1
**Actor:** Propietario
**Prioridad:** Alta

## Descripcion
Como  duenio de auto,
quiero agregar las caracteristicas detalladas y subir fotos de mi auto,
para el registro del auto en la plataforma.

## Criterios de Aceptacion

### CA 1
**Dado que** estoy en el formulario de registro del auto, 
**cuando** intento guardar sin completar campos obligatorios (tipo de transmision, capacidad, marca, modelo, categoria, tipo de combustible, anio del auto, pets friendly, fotos), 
**entonces** el sistema muestra un error especifico y bloquea el guardado.

### CA 2
**Dado que** estoy ingresando el anio del auto, 
**cuando** ingreso un anio mayor al actual o menor al limite permitido, 
**entonces** el sistema arroja un error de validacion.

### CA 3
**Dado que** intento cargar una foto con formato invalido o tamanio superior al permitido 
**cuando** confirmo la carga, 
**entonces** el sistema rechaza el archivo e informa el motivo.

### CA 4
**Dado que** estoy registrando marca y modelo del auto, 
**cuando** la combinacion ingresada no exite, 
**entonces** el sistema impide continuar.

### CA 5
**Dado que** no cargo la cantidad minima de fotos requeridas (4, una de cada lado del auto), 
**cuando** intento enviar el auto a revision, 
**entonces** el sistema bloquea la solicitud.

### CA 6
**Dado que** complete todos los campos obligatorios correctamente, 
**cuando** hago clic en guardar,  
**entonces** la informacion del auto se guarda exitosamente.