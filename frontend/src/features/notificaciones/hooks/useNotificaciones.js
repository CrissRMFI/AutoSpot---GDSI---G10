import { useEffect, useState } from "react";
import { useAuth } from "../../auth/hooks/useAuth";
import { getSolicitudesDocumentacion } from "../../admin/api/solicitudesApi";

const MAX_ITEMS_DROPDOWN = 5;

/**
 * Hook que centraliza las notificaciones del usuario autenticado.
 *
 * Por ahora solo el rol ADMIN recibe notificaciones (cola de solicitudes de
 * documentación pendientes — US 1R y 2R). El hook está pensado para crecer:
 * cuando otras US agreguen notificaciones para CLIENTE/PROPIETARIO se pueden
 * concatenar acá manteniendo el mismo contrato.
 */
export const useNotificaciones = () => {
  const { usuario, estaAutenticado } = useAuth();
  const rol = (usuario?.rol || "").toUpperCase();
  const debeConsultarSolicitudes = estaAutenticado && rol === "ADMIN";

  const [estado, setEstado] = useState({
    solicitudes: [],
    cargando: false,
    error: "",
  });
  const [contadorRefresco, setContadorRefresco] = useState(0);

  useEffect(() => {
    if (!debeConsultarSolicitudes) {
      // No consultamos: dejamos solo notificaciones aplicables a este rol.
      let cancelado = false;
      Promise.resolve().then(() => {
        if (cancelado) return;
        setEstado({ solicitudes: [], cargando: false, error: "" });
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

    getSolicitudesDocumentacion()
      .then((data) => {
        if (cancelado) return;
        setEstado({
          solicitudes: Array.isArray(data) ? data : [],
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
  }, [debeConsultarSolicitudes, contadorRefresco]);

  const refrescar = () => {
    setContadorRefresco((valor) => valor + 1);
  };

  const { solicitudes, cargando, error } = estado;

  const items = solicitudes.map((solicitud) => ({
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

  return {
    items,
    itemsResumen: items.slice(0, MAX_ITEMS_DROPDOWN),
    total: items.length,
    cargando,
    error,
    refrescar,
    hayMasItems: items.length > MAX_ITEMS_DROPDOWN,
    rutaVerTodas:
      rol === "ADMIN" ? "/admin/solicitudes-documentacion" : null,
  };
};
