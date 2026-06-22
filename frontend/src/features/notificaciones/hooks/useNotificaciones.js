import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../../auth/hooks/useAuth";
import { getSolicitudesDocumentacion } from "../../admin/api/solicitudesApi";
import {
  getNotificaciones,
  marcarNotificacionVista,
} from "../api/notificacionesApi";

const MAX_ITEMS_DROPDOWN = 5;

/**
 * Hook que centraliza las notificaciones del usuario autenticado.
 *
 * El rol ADMIN recibe avisos derivados de la cola de solicitudes pendientes.
 * PROPIETARIO/CLIENTE consumen notificaciones persistidas propias y no vistas.
 */
export const useNotificaciones = () => {
  const { usuario, estaAutenticado } = useAuth();
  const rol = (usuario?.rol || "").toUpperCase();
  const debeConsultarSolicitudes = estaAutenticado && rol === "ADMIN";
  const debeConsultarNotificacionesUsuario = estaAutenticado;

  const [estado, setEstado] = useState({
    solicitudes: [],
    notificaciones: [],
    cargando: false,
    error: "",
  });
  const [contadorRefresco, setContadorRefresco] = useState(0);

  useEffect(() => {
    if (!estaAutenticado) {
      let cancelado = false;
      Promise.resolve().then(() => {
        if (cancelado) return;
        setEstado({
          solicitudes: [],
          notificaciones: [],
          cargando: false,
          error: "",
        });
      });
      return () => {
        cancelado = true;
      };
    }

    let cancelado = false;
    Promise.resolve().then(() => {
      if (cancelado) return;
      setEstado((previo) => ({ ...previo, cargando: true, error: "" }));
    });

    const consultaSolicitudes = debeConsultarSolicitudes
      ? getSolicitudesDocumentacion()
      : Promise.resolve([]);
    const consultaNotificaciones = debeConsultarNotificacionesUsuario
      ? getNotificaciones()
      : Promise.resolve([]);

    Promise.all([consultaSolicitudes, consultaNotificaciones])
      .then(([solicitudesData, notificacionesData]) => {
        if (cancelado) return;
        setEstado({
          solicitudes: Array.isArray(solicitudesData) ? solicitudesData : [],
          notificaciones: Array.isArray(notificacionesData)
            ? notificacionesData
            : [],
          cargando: false,
          error: "",
        });
      })
      .catch((err) => {
        if (cancelado) return;
        console.error(err);
        setEstado((previo) => ({
          ...previo,
          cargando: false,
          error: "No pudimos cargar tus notificaciones.",
        }));
      });

    return () => {
      cancelado = true;
    };
  }, [
    estaAutenticado,
    rol,
    debeConsultarSolicitudes,
    debeConsultarNotificacionesUsuario,
    contadorRefresco,
  ]);

  const refrescar = useCallback(() => {
    setContadorRefresco((valor) => valor + 1);
  }, []);

  const marcarVista = useCallback(async (item, opciones = {}) => {
    if (item?.fuente !== "NOTIFICACION_USUARIO" || !item.raw?.id) {
      return true;
    }

    const { ocultarLocalmente = true } = opciones;
    const notificacionId = item.raw.id;
    const esPersistente = [
      "VEHICULO_DOCUMENTACION_PENDIENTE",
      "RESERVA_PENDIENTE_VERIFICACION",
      "AUTO_DEVUELTO",
      "CHECKOUT_PENDIENTE_CONFIRMACION",
      "CHECKOUT_RECHAZADO",
      "CHECKIN_RECHAZADO",
      "ALQUILER_INICIADO",
    ].includes(item.raw.tipo);

    if (item.raw.tipo === "RESERVA_PENDIENTE_VERIFICACION") {
      return true;
    }

    if (ocultarLocalmente && !esPersistente) {
      setEstado((previo) => ({
        ...previo,
        notificaciones: previo.notificaciones.filter(
          (notificacion) => notificacion.id !== notificacionId,
        ),
      }));
    }

    try {
      await marcarNotificacionVista(notificacionId);
      return true;
    } catch (err) {
      console.error(err);
      refrescar();
      return false;
    }
  }, [refrescar]);

  const { solicitudes, notificaciones, cargando, error } = estado;

  const itemsSolicitudes = solicitudes.map((solicitud) => ({
    id: `solicitud:${solicitud.tipo}:${solicitud.recurso_id}`,
    fuente: "SOLICITUD_DOCUMENTACION",
    titulo:
      solicitud.tipo === "VEHICULO"
        ? "Nuevo vehículo en revisión"
        : "Nueva licencia de conducir",
    detalle: solicitud.resumen,
    sujeto: solicitud.usuario_email,
    fecha: solicitud.fecha_solicitud,
    href: `/admin/solicitudes-documentacion?focus=${encodeURIComponent(
      `${solicitud.tipo}:${solicitud.recurso_id}`,
    )}`,
    raw: solicitud,
  }));

  const hrefNotificacion = (notificacion) => {
    if (notificacion.tipo === "CHECKIN_PENDIENTE") {
      return "/admin/checkins/revision";
    }
    if (notificacion.tipo === "CHECKIN_RECHAZADO" && notificacion.recurso_id) {
      return `/usuario/reservas/${notificacion.recurso_id}/checkin`;
    }
    if (notificacion.tipo === "CHECKIN_APROBADO" && notificacion.recurso_id) {
      return `/usuario/alquileres?focus=${notificacion.recurso_id}`;
    }
    if (notificacion.tipo === "ALQUILER_INICIADO" && notificacion.recurso_id) {
      return `/vehiculos`;
    }
    if (notificacion.tipo === "AUTO_DEVUELTO" && notificacion.recurso_id) {
      return `/admin/recepcion?focus=${notificacion.recurso_id}`;
    }
    if (
      (notificacion.tipo === "CHECKOUT_CONFIRMADO" ||
        notificacion.tipo === "CHECKOUT_RECHAZADO") &&
      notificacion.recurso_id
    ) {
      return `/admin/recepcion?focus=${notificacion.recurso_id}`;
    }
    if (
      notificacion.tipo === "CHECKOUT_PENDIENTE_CONFIRMACION" &&
      notificacion.recurso_id
    ) {
      return `/usuario/alquileres?focus=${notificacion.recurso_id}`;
    }
    if (
      (notificacion.tipo === "RESERVA_PENDIENTE_VERIFICACION" ||
        notificacion.tipo === "RESERVA_EXPIRADA_ADMIN") &&
      notificacion.recurso_id
    ) {
      return `/admin/reservas/verificar?reservaId=${notificacion.recurso_id}`;
    }
    if (
      (notificacion.tipo === "RESERVA_APROBADA" ||
        notificacion.tipo === "RESERVA_RECHAZADA" ||
        notificacion.tipo === "RESERVA_EXPIRADA_CONDUCTOR") &&
      notificacion.recurso_id
    ) {
      return `/usuario/reservas?focus=${notificacion.recurso_id}`;
    }
    if (
      notificacion.tipo === "VEHICULO_DOCUMENTACION_PENDIENTE" &&
      notificacion.recurso_id
    ) {
      return `/vehiculos/${notificacion.recurso_id}/documentacion`;
    }
    if (
      notificacion.tipo === "CONDUCTOR_HABILITADO" ||
      notificacion.tipo === "CONDUCTOR_RECHAZADO"
    ) {
      return "/documentacion-habilitante";
    }
    if (notificacion.recurso_tipo === "REPORTE" && notificacion.recurso_id) {
      return `/admin/incidentes/${notificacion.recurso_id}`;
    }
    if (notificacion.recurso_tipo === "VEHICULO" && notificacion.recurso_id) {
      return `/vehiculos/${notificacion.recurso_id}/detalle`;
    }
    return "/dashboard";
  };

  const itemsUsuario = notificaciones.map((notificacion) => ({
    id: `notificacion:${notificacion.id}`,
    fuente: "NOTIFICACION_USUARIO",
    titulo: notificacion.titulo,
    detalle: notificacion.mensaje,
    sujeto:
      notificacion.recurso_tipo === "VEHICULO"
        ? "Tu vehículo"
        : notificacion.recurso_tipo === "RESERVA"
          ? "Reserva"
          : "AutoSpot",
    fecha: notificacion.created_at,
    href: hrefNotificacion(notificacion),
    raw: notificacion,
  }));

  const items = [...itemsSolicitudes, ...itemsUsuario];

  return {
    items,
    itemsResumen: items.slice(0, MAX_ITEMS_DROPDOWN),
    total: items.length,
    cargando,
    error,
    refrescar,
    marcarVista,
    hayMasItems: items.length > MAX_ITEMS_DROPDOWN,
    rutaVerTodas:
      rol === "ADMIN"
        ? "/admin/solicitudes-documentacion"
        : rol === "PROPIETARIO"
          ? "/vehiculos"
          : "/usuario/alquileres",
    textoVerTodas:
      rol === "ADMIN"
        ? "Ver todas las solicitudes →"
        : rol === "PROPIETARIO"
          ? "Ver mis vehículos →"
          : "Ver mis alquileres →",
  };
};
