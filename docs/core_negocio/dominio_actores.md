# AutoSpot - Core de Negocio y Dominio

## 1. Vision Arquitectonica del Producto
AutoSpot es una plataforma de intermediacion (Logistica) que automatiza el alquiler de vehiculos. 
**Diferenciador tecnico principal:** A diferencia de un modelo P2P tradicional, la plataforma integra una red de **estaciones fisicas** que garantizan la estandarizacion, entrega y seguridad del activo, operando como un sistema "llave en mano" con apertura digital y sin contacto entre las partes.

## 2. Actores del Sistema y Entidades (Personas)

### Actor 1: Conductor (Perfil Consumidor - ej. Mateo, Valeria)
*   **Rol en el sistema:** Usuario que contrata un activo para movilidad temporal.
*   **Requisitos de Dominio y Logica:**
    *   **Geolocalizacion:** El motor de busqueda debe priorizar y filtrar activos por proximidad geografica a la ubicacion del conductor.
    *   **Self-Service / Keyless:** El flujo de retiro debe ser instantaneo y manejado desde el dispositivo movil, interactuando unicamente con la Estacion y nunca con el duenio.
    *   **Filtros Estrictos:** Requiere segmentacion por caracteristicas booleanas o de capacidad (ej: `pets_friendly`, tamanio del baul).

### Actor 2: Propietario / Flotillero (Perfil Inversor - ej. Roberto, Anastacia)
*   **Rol en el sistema:** Usuario que suministra uno o multiples activos a la plataforma para generar rentabilidad.
*   **Requisitos de Dominio y Logica:**
    *   **Relacion 1:N (Flotas):** Un Propietario puede tener asociados multiples Activos en la base de datos y requiere metricas unificadas.
    *   **Cero contacto P2P:** Restriccion estricta de arquitectura; el sistema bloquea cualquier interaccion directa entre Propietario y Conductor.
    *   **Cadena de Evidencia:** El propietario depende de un registro inmutable de imagenes (Check-in / Check-out) para auditar el estado fisico de su unidad.

### Actor 3: Operador de Estacion / Auditor (Perfil Back-Office - ej. Julian, Ricardo)
*   **Rol en el sistema:** Empleado de la empresa logistica encargado de auditar identidades y certificar el estado de los vehiculos.
*   **Requisitos de Dominio y Logica:**
    *   **Cola de Validacion (KYC):** Acceso a un dashboard con solicitudes pendientes. Tiene la autoridad para aplicar una transicion de estado binaria (Aprobar / Rechazar) sobre la documentacion del Conductor.
    *   **Transacciones agiles:** El proceso de Check-in/Check-out de un activo debe resolverse con minima friccion en la UI, permitiendo anexar notas o "detalles discrecionales" al registro inmutable del vehiculo.

## 3. Lenguaje Ubicuo (Glosario Restrictivo)
*El agente de IA debe utilizar estrictamente estos terminos en el codigo fuente, base de datos y endpoints:*
*   **Activo / Vehiculo:** Reemplaza al termino generico "auto".
*   **Contratacion / Operacion:** Reemplaza a "reserva" o "alquiler".
*   **Estacion / Operador:** Entidad fisica y perfil encargado del intercambio logistico.
*   **Check-in / Check-out:** Proceso formal y documentado de entrega y recepcion del Activo.