import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useNotificaciones } from "../hooks/useNotificaciones";

const formatearFechaCorta = (iso) => {
  if (!iso) return "";
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return "";
  const ahora = new Date();
  const diffMs = ahora.getTime() - fecha.getTime();
  const diffMin = Math.round(diffMs / 60000);
  if (diffMin < 1) return "Recién";
  if (diffMin < 60) return `${diffMin} min`;
  const diffH = Math.round(diffMin / 60);
  if (diffH < 24) return `${diffH} h`;
  const diffD = Math.round(diffH / 24);
  if (diffD < 7) return `${diffD} d`;
  return fecha.toLocaleDateString("es-AR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};

const IconoVehiculo = (props) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M5 17H3v-5l2-5h14l2 5v5h-2" />
    <circle cx="7.5" cy="17.5" r="1.5" />
    <circle cx="16.5" cy="17.5" r="1.5" />
    <path d="M5 12h14" />
  </svg>
);

const IconoConductor = (props) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <rect x="3" y="5" width="18" height="14" rx="2" />
    <circle cx="9" cy="11" r="2" />
    <path d="M5 17c.5-2 2-3 4-3s3.5 1 4 3" />
    <path d="M14 9h5M14 13h5M14 16h3" />
  </svg>
);

const presentacionItem = (item) => {
  const tipo = item?.raw?.tipo;
  if (
    item.fuente === "NOTIFICACION_USUARIO" &&
    tipo === "VEHICULO_DOCUMENTACION_PENDIENTE"
  ) {
    return {
      label: "Documentación",
      Icono: IconoVehiculo,
      iconoBg: "bg-[#fef3c7] text-[#92400e]",
      acento: "bg-[#92400e]",
    };
  }
  if (item.fuente === "NOTIFICACION_USUARIO" && tipo === "VEHICULO_HABILITADO") {
    return {
      label: "Habilitado",
      Icono: IconoVehiculo,
      iconoBg: "bg-[#dcfce7] text-[#166534]",
      acento: "bg-[#166534]",
    };
  }
  if (item.fuente === "NOTIFICACION_USUARIO" && tipo === "VEHICULO_RECHAZADO") {
    return {
      label: "Rechazado",
      Icono: IconoVehiculo,
      iconoBg: "bg-[#fee2e2] text-[#b42318]",
      acento: "bg-[#b42318]",
    };
  }
  if (
    item.fuente === "NOTIFICACION_USUARIO" &&
    tipo === "RESERVA_PENDIENTE_VERIFICACION"
  ) {
    return {
      label: "Reserva",
      Icono: IconoConductor,
      iconoBg: "bg-[#dbeafe] text-[#1d4ed8]",
      acento: "bg-[#1d4ed8]",
    };
  }
  if (item.fuente === "NOTIFICACION_USUARIO" && tipo === "CHECKIN_PENDIENTE") {
    return {
      label: "Check-in",
      Icono: IconoConductor,
      iconoBg: "bg-[#fef3c7] text-[#92400e]",
      acento: "bg-[#92400e]",
    };
  }
  if (
    item.fuente === "NOTIFICACION_USUARIO" &&
    (tipo === "CHECKIN_APROBADO" || tipo === "CHECKIN_RECHAZADO")
  ) {
    return {
      label: tipo === "CHECKIN_APROBADO" ? "Check-in aprobado" : "Check-in rechazado",
      Icono: IconoVehiculo,
      iconoBg:
        tipo === "CHECKIN_APROBADO"
          ? "bg-[#dcfce7] text-[#166534]"
          : "bg-[#fee2e2] text-[#b42318]",
      acento: tipo === "CHECKIN_APROBADO" ? "bg-[#166534]" : "bg-[#b42318]",
    };
  }
  if (item.fuente === "NOTIFICACION_USUARIO" && tipo === "ALQUILER_INICIADO") {
    return {
      label: "Alquiler iniciado",
      Icono: IconoVehiculo,
      iconoBg: "bg-[#dcfce7] text-[#166534]",
      acento: "bg-[#166534]",
    };
  }
  if (item.fuente === "NOTIFICACION_USUARIO" && tipo === "RESERVA_APROBADA") {
    return {
      label: "Reserva aprobada",
      Icono: IconoConductor,
      iconoBg: "bg-autospot-black text-white",
      acento: "bg-autospot-black",
    };
  }
  if (item.fuente === "NOTIFICACION_USUARIO" && tipo === "RESERVA_RECHAZADA") {
    return {
      label: "Reserva rechazada",
      Icono: IconoConductor,
      iconoBg: "bg-autospot-cream text-autospot-muted border border-autospot-border",
      acento: "bg-autospot-muted",
    };
  }
  if (item.fuente === "NOTIFICACION_USUARIO" && tipo === "AUTO_DEVUELTO") {
    return {
      label: "Recepción",
      Icono: IconoVehiculo,
      iconoBg: "bg-[#fef3c7] text-[#92400e]",
      acento: "bg-[#92400e]",
    };
  }
  if (
    item.fuente === "NOTIFICACION_USUARIO" &&
    tipo === "CHECKOUT_PENDIENTE_CONFIRMACION"
  ) {
    return {
      label: "Checkout",
      Icono: IconoConductor,
      iconoBg: "bg-[#dbeafe] text-[#1d4ed8]",
      acento: "bg-[#1d4ed8]",
    };
  }
  if (
    item.fuente === "NOTIFICACION_USUARIO" &&
    (tipo === "CHECKOUT_CONFIRMADO" || tipo === "CHECKOUT_RECHAZADO")
  ) {
    return {
      label: tipo === "CHECKOUT_CONFIRMADO" ? "Confirmado" : "Rechazado",
      Icono: IconoVehiculo,
      iconoBg:
        tipo === "CHECKOUT_CONFIRMADO"
          ? "bg-[#dcfce7] text-[#166534]"
          : "bg-[#fee2e2] text-[#b42318]",
      acento: tipo === "CHECKOUT_CONFIRMADO" ? "bg-[#166534]" : "bg-[#b42318]",
    };
  }
  if (item.fuente === "SOLICITUD_DOCUMENTACION" && tipo === "VEHICULO") {
    return {
      label: "Vehículo",
      Icono: IconoVehiculo,
      iconoBg: "bg-[#dbeafe] text-[#1d4ed8]",
      acento: "bg-[#1d4ed8]",
    };
  }
  if (item.fuente === "SOLICITUD_DOCUMENTACION" && tipo === "CONDUCTOR") {
    return {
      label: "Conductor",
      Icono: IconoConductor,
      iconoBg: "bg-[#fef3c7] text-[#92400e]",
      acento: "bg-[#92400e]",
    };
  }
  return {
    label: "Notificación",
    Icono: IconoVehiculo,
    iconoBg: "bg-autospot-cream text-autospot-muted",
    acento: "bg-autospot-muted",
  };
};

const NotificacionesBell = ({ tonoClaro = false }) => {
  const navigate = useNavigate();
  const {
    itemsResumen,
    total,
    cargando,
    error,
    refrescar,
    marcarVista,
    hayMasItems,
    rutaVerTodas,
    textoVerTodas,
  } = useNotificaciones();

  const [abierto, setAbierto] = useState(false);
  const contenedorRef = useRef(null);
  const notificacionesVistasRef = useRef(new Set());

  useEffect(() => {
    if (!abierto) return undefined;

    const onClickFuera = (event) => {
      if (!contenedorRef.current) return;
      if (!contenedorRef.current.contains(event.target)) {
        setAbierto(false);
      }
    };
    const onEsc = (event) => {
      if (event.key === "Escape") setAbierto(false);
    };

    document.addEventListener("mousedown", onClickFuera);
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("mousedown", onClickFuera);
      document.removeEventListener("keydown", onEsc);
    };
  }, [abierto]);

  useEffect(() => {
    if (!abierto || cargando || itemsResumen.length === 0) return;

    itemsResumen.forEach((item) => {
      const notificacionId = item?.raw?.id;
      if (item.fuente !== "NOTIFICACION_USUARIO" || !notificacionId) return;
      if (
        [
          "RESERVA_PENDIENTE_VERIFICACION",
          "AUTO_DEVUELTO",
          "CHECKOUT_PENDIENTE_CONFIRMACION",
          "CHECKOUT_RECHAZADO",
        ].includes(item.raw.tipo)
      ) {
        return;
      }
      if (notificacionesVistasRef.current.has(notificacionId)) return;

      notificacionesVistasRef.current.add(notificacionId);
      void marcarVista(item, { ocultarLocalmente: false }).then((ok) => {
        if (!ok) {
          notificacionesVistasRef.current.delete(notificacionId);
        }
      });
    });
  }, [abierto, cargando, itemsResumen, marcarVista]);

  const toggle = () => {
    const proximo = !abierto;
    setAbierto(proximo);
    if (proximo) {
      refrescar();
    }
  };

  const colorBoton = tonoClaro
    ? "border-white/20 bg-white/[0.06] text-white hover:bg-white/[0.12]"
    : "border-autospot-border bg-white text-autospot-black hover:border-autospot-accent hover:text-autospot-accent";

  const irAItem = async (item) => {
    setAbierto(false);
    await marcarVista(item);
    navigate(item.href);
  };

  return (
    <div ref={contenedorRef} className="relative">
      <button
        type="button"
        onClick={toggle}
        aria-expanded={abierto}
        aria-label={
          total > 0
            ? `Tenés ${total} notificación${total === 1 ? "" : "es"}`
            : "Sin notificaciones"
        }
        className={`relative inline-flex h-10 w-10 items-center justify-center rounded-full border transition ${colorBoton}`}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="h-5 w-5"
          aria-hidden="true"
        >
          <path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
        </svg>
        {total > 0 && (
          <span className="absolute -right-1 -top-1 flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-autospot-accent px-1 text-[10px] font-bold leading-none ring-2 ring-autospot-cream !text-white">
            {total > 9 ? "9+" : total}
          </span>
        )}
      </button>

      {abierto && (
        <>
          {/* Overlay mobile para cerrar al tocar afuera */}
          <button
            type="button"
            tabIndex={-1}
            aria-hidden="true"
            onClick={() => setAbierto(false)}
            className="fixed inset-0 z-[90] cursor-default bg-autospot-black/30 backdrop-blur-[2px] sm:hidden"
          />

          <div
            role="dialog"
            aria-label="Notificaciones"
            className="fixed left-3 right-3 top-[4.5rem] z-[100] flex max-h-[70vh] flex-col overflow-hidden rounded-xl border border-autospot-border bg-autospot-white text-autospot-black shadow-[0_16px_40px_rgba(15,23,42,0.18)] sm:absolute sm:left-auto sm:right-0 sm:top-auto sm:mt-2 sm:max-h-[26rem] sm:w-[22rem]"
          >
            <header className="flex items-center justify-between border-b border-autospot-border px-4 py-2.5">
              <p className="font-display text-sm font-bold tracking-[-0.02em] text-autospot-black">
                Notificaciones
              </p>
              {total > 0 && (
                <span className="text-[11px] font-bold text-autospot-muted">
                  {total} nueva{total === 1 ? "" : "s"}
                </span>
              )}
            </header>

            <div className="flex justify-center overflow-y-auto">
              {cargando ? (
                <div className="flex justify-center py-6">
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-autospot-border border-t-autospot-accent"></div>
                </div>
              ) : error ? (
                <p className="px-4 py-6 text-center text-xs font-bold text-[#b42318]">
                  {error}
                </p>
              ) : itemsResumen.length === 0 ? (
                <div className="px-4 py-8 text-cente">
                  <p className="text-sm font-bold text-autospot-black">
                    Todo al día
                  </p>
                  <p className="mt-0.5 text-[11px] text-autospot-muted">
                    Sin notificaciones nuevas.
                  </p>
                </div>
              ) : (
                <div className="flex flex-col p-2 w-full">
                  {itemsResumen.map((item) => {
                    const { label, Icono, iconoBg } = presentacionItem(item);
                    return (
                      <div key={item.id} className="">
                        <button
                          type="button"
                          onClick={() => irAItem(item)}
                          className="flex w-full items-center gap-3 px-4 mb-1.5 text-left transition hover:bg-[#fafaf9]"
                        >
                          <span
                            className={`inline-flex h-4 w-9 shrink-0 items-center justify-center rounded-full ${iconoBg}`}
                            aria-hidden="true"
                          >
                            <Icono className="h-4 w-4" />
                          </span>

                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between gap-2">
                              <p className="truncate text-[13px] font-bold leading-tight text-autospot-black">
                                {item.detalle}
                              </p>
                              <span className="shrink-0 text-[10px] font-bold text-autospot-muted">
                                {formatearFechaCorta(item.fecha)}
                              </span>
                            </div>
                            <p className="mt-0.5 truncate text-[11px] text-autospot-muted">
                              {label} · {item.sujeto}
                            </p>
                          </div>
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {rutaVerTodas && (itemsResumen.length > 0 || hayMasItems) && (
              <footer className="border-t border-autospot-border bg-[#fafaf9] px-4 py-2 text-center">
                <Link
                  to={rutaVerTodas}
                  onClick={() => setAbierto(false)}
                  className="text-[11px] font-bold !text-autospot-accent hover:underline"
                >
                  {textoVerTodas}
                </Link>
              </footer>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default NotificacionesBell;
