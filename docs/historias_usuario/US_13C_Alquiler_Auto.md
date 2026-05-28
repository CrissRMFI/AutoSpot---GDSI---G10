# US 13C: Alquiler de auto

**Sprint:** 4
**Actor:** Conductor
**Prioridad:** Baja
**Estimación:** 5

## Descripción
**Como** conductor,
**quiero** procesar el pago de mi alquiler a través de un ente financiero externo,
**para** formalizar el vínculo contractual y asegurar la disponibilidad exclusiva del auto.

## Criterios de Aceptación

### CA 1
**Dado que** se ha definido un alquiler con un costo determinado,
**cuando** el usuario inicia el proceso de pago,
**entonces** debe suministrar al ente externo el monto exacto calculado para la operación.

### CA 2
**Dado que** la transacción se procesa externamente,
**cuando** el ente informa un rechazo, insuficiencia de fondos o el usuario interrumpe la operación,
**entonces** el sistema debe liberar la disponibilidad del activo.
