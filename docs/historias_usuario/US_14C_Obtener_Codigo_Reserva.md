# US 14C: Obtener código de reserva

**Sprint:** 4
**Actor:** Conductor
**Prioridad:** Alta

## Descripción
**Como** conductor,
**quiero** tener mi código de reserva en formato QR,
**para** efectuar el retiro físico del auto de manera segura y eficiente.

## Criterios de Aceptación

### CA 1
**Dado que** se ha confirmado la reserva de una unidad específica,
**cuando** se accede a los detalles de retiro,
**entonces** el sistema debe garantizar que la información suministrada corresponda estrictamente a la unidad y características pactadas originalmente.

### CA 2
**Dado que** no ingresé mi medio de pago,
**cuando** pago,
**entonces** se me informa que debo seleccionar un medio de pago.

### CA 3
**Dado que** el pago ha sido confirmado,
**cuando** el conductor se presenta para retirar el auto,
**entonces** el sistema debe generar una credencial única y temporal en formato QR que funcione como validación, permitiendo al personal autorizar la entrega del auto.
