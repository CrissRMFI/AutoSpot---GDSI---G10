# Historias de Usuario — AutoSpot

## Sprint 1

| Sprint    | US  | Título                                       | Estimación | Implementada |
| --------- | --- | -------------------------------------------- | ---------- | :----------: |
| 1         | 1U  | Registro datos personales                    | 2          |      ✅      |
| 1         | 2U  | Inicio de sesión del usuario                 | 2          |      ✅      |
| 1         | 3U  | Finalización de sesión del usuario           | 2          |      ✅      |
| 1         | 4U  | Gestión y actualización de perfil de usuario | 3          |      ✅      |
| 1         | 5U  | Registrarse con mail y contraseña            | 2          |      ✅      |
| 1         | 1D  | Cargar características y fotos del auto      | 3          |      ✅      |
| 1         | 5D  | Definir precio del auto                      | 1          |      ✅      |
| **TOTAL** |     |                                              | **15**     |              |

## Sprint 2

| Sprint    | US  | Título                                               | Estimación | Implementada |
| --------- | --- | ---------------------------------------------------- | ---------- | :----------: |
| 2         | 2D  | Cargar documentación del auto                        | 3          |      ✅      |
| 2         | 3D  | Editar características y fotos del auto              | 3          |      ✅      |
| 2         | 4D  | Visualización de estado de solicitud de habilitación | 2          |      ✅      |
| 2         | 7D  | Actualización de precio del auto                     | 3          |      ✅      |
| 2         | 9D  | Habilitar/deshabilitar auto en el momento            | 2          |      ✅      |
| 2         | 1C  | Cargar de identidad y documentación habilitante      | 3          |      ✅      |
| 2         | 4C  | Visualización y selección de estación                | 3          |      ✅      |
| **TOTAL** |     |                                                      | **19**     |              |

## Sprint 3 — reorganizado para mostrar el flujo end-to-end

Se promueven 3 US del Sprint 4 original (**14C**, **5R**, **6R**) para que el flujo end-to-end quede visible al cerrar este sprint.

| Orden     | US  | Título                                                         | Estimación | Implementada | Habilita / Notas                                                                                                                                                                                             |
| --------- | --- | -------------------------------------------------------------- | ---------- | :----------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1         | 1R  | Solicitudes de documentación                                   | 3          |      ❌      | Cola de solicitudes (vehículos + conductores en `EN_REVISION`) **+ acción aprobar/rechazar con motivo**. Endpoint backend nuevo. **Desbloquea ciclo del propietario** (sus autos pueden pasar a HABILITADO). |
| 2         | 2R  | Priorización cronológica de las solicitudes                    | 2          |      ❌      | Ordena la cola de 1R por fecha de envío (más antiguas primero).                                                                                                                                              |
| 3         | 9C  | Visualización de ficha técnica y galería del auto              | 3          |      ❌      | Página de detalle pública (cliente ve datos del activo sin acciones de gestión). Incluye **listado público de autos disponibles** (necesario para llegar al detalle). **Desbloquea descubrimiento cliente.** |
| 4         | 5C  | Visualización por zona y orden alfabético — selección estación | 3          |      ❌      | Estaciones filtrables por zona/orden + listado de autos por estación.                                                                                                                                        |
| 5         | 2C  | Visualización de estado de solicitud de habilitación (cliente) | 2          |      ❌      | Cliente ve si su licencia fue Aprobada/Rechazada (consume la salida de 1R/2R aplicada a conductores). **Cierra loop del cliente para conducir.**                                                             |
| 6         | 7C  | Motor de filtrado de catálogo por características              | 3          |      ❌      | Filtros del catálogo (categoría, transmisión, mascotas, rango de precio). Refina sobre 9C + 5C.                                                                                                              |
| 7         | 3C  | Configuración del tiempo de alquiler                           | 2          |      ❌      | Formulario en el detalle del auto: fechas desde/hasta + cálculo de total. Prepara la reserva (14C).                                                                                                          |
| 8         | 14C | Obtener código de reserva                                      | 3          |      ❌      | **Promovida de Sprint 4.** Cliente confirma reserva → backend genera código único. Nueva entidad `Reserva` + estado `RESERVADO` en el vehículo.                                                              |
| 9         | 5R  | Verificar código de reserva                                    | 3          |      ❌      | **Promovida de Sprint 4.** Recepcionista busca/valida el código en su panel, ve datos del cliente y del auto.                                                                                                |
| 10        | 6R  | Entrega                                                        | 1          |      ❌      | **Promovida de Sprint 4.** Recepcionista marca la reserva como entregada. **Cierra el loop end-to-end visible.**                                                                                             |
| **TOTAL** |     |                                                                | **25**     |              |                                                                                                                                                                                                              |

### Notas y dependencias

- **Flujo end-to-end visible al cerrar Sprint 3:** propietario publica → carga documentación → **admin aprueba (NUEVO)** → cliente filtra estaciones → cliente explora catálogo → **cliente ve detalle del auto (NUEVO)** → cliente filtra → cliente elige tiempo → **cliente reserva (NUEVO)** → **recepcionista verifica código (NUEVO)** → **recepcionista entrega el auto (NUEVO)**.

## Sprint 4 — reducido tras promover 14C, 5R y 6R

| Sprint    | US  | Título                                            | Estimación | Implementada |
| --------- | --- | ------------------------------------------------- | ---------- | :----------: |
| 4         | 15C | Registro del estado inicial del activo (Check-in) | 2          |      ❌      |
| 4         | 11C | Suministro de información logística de retiro     | 2          |      ❌      |
| 4         | 3R  | Abrir documentación                               | 2          |      ✅      |
| 4         | 4R  | Notificación y Validar documentación              | 2          |      ❌      |
| **TOTAL** |     |                                                   | **8**      |              |

## Sprint 5

| Sprint    | US  | Título                                                       | Estimación | Implementada |
| --------- | --- | ------------------------------------------------------------ | ---------- | :----------: |
| 5         | 14D | Historial de clientes por auto                               | 3          |      ❌      |
| 5         | 7R  | Recepción                                                    | 3          |      ❌      |
| 5         | 8R  | Rellenar formulario de Checkout                              | 2          |      ❌      |
| 5         | 17C | Valoración cuantitativa del servicio                         | 3          |      ❌      |
| 5         | 10C | Suministro histórico de valoraciones y reputación del activo | 3          |      ❌      |
| **TOTAL** |     |                                                              | **14**     |              |

## Sprint 6

| Sprint    | US  | Título                           | Estimación | Implementada |
| --------- | --- | -------------------------------- | ---------- | :----------: |
| 6         | 8C  | Motor de filtrado por puntuación | 3          |      ❌      |
| 6         | 18C | Testimonio descriptivo           | 3          |      ❌      |
| 6         | 6D  | Recomendación de precio — IA     | 8          |      ❌      |
| **TOTAL** |     |                                  | **14**     |              |

## Sprint 7

| Sprint    | US  | Título                           | Estimación | Implementada |
| --------- | --- | -------------------------------- | ---------- | :----------: |
| 7         | 10R | Historial de autos               | 2          |      ❌      |
| 7         | 15D | Dashboard de ganancias generales | 3          |      ❌      |
| 7         | 16D | Dashboard de ganancias por auto  | 3          |      ❌      |
| 7         | 11R | Historial de conductores         | 2          |      ❌      |
| **TOTAL** |     |                                  | **10**     |              |
