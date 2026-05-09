# US 5D: Definir precio del auto

**Sprint:** 1
**Actor:** Propietario
**Prioridad:** Alta

## Descripcion
**Como** duenio de un auto recien registrado y habilitado,
**quiero** establecer el valor de la tarifa de alquiler por dia,
**para** que mi auto pueda empezar a generar ingresos.

## Criterios de Aceptacion

### CA 1
**Dado que** estoy configurando la tarifa, 
**cuando** ingreso un numero negativo o cero, 
**entonces** el sistema impide el guardado.

### CA 2
**Dado que** estoy en la pantalla de precios, 
**cuando** ingreso un valor, 
**entonces** el sistema muestra el "Precio sugerido" y el monto neto que recibire tras la comision.

### CA 3
**Dado que** el precio ingresado esta muy por fuera del promedio de la categoria, 
**cuando** intento confirmar, 
**entonces** el sistema muestra una advertencia sobre la posible baja demanda.

### CA 4
**Dado que** estoy definiendo la tarifa diaria del auto cuando el sistema cuenta con informacion de categoria, modelo o zona de operacion, 
**entonces** muestra un precio diario sugerido de referencia para orientar al propietario.
