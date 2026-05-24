import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getSolicitudesDocumentacion } from "../api/solicitudesApi";

const formatearFecha = (iso) => {
  if (!iso) return "—";
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return iso;
  return fecha.toLocaleString("es-AR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const etiquetaTipo = (tipo) => {
  if (tipo === "VEHICULO") return "Vehículo";
  if (tipo === "CONDUCTOR") return "Conductor";
  return tipo;
};

const claseChipTipo = (tipo) => {
  if (tipo === "VEHICULO") {
    return "bg-[#eff6ff] text-[#1d4ed8] border-[#bfdbfe]";
  }
  if (tipo === "CONDUCTOR") {
    return "bg-[#fef3c7] text-[#92400e] border-[#fde68a]";
  }
  return "bg-autospot-cream text-autospot-muted border-autospot-border";
};

const SolicitudesDocumentacionPage = () => {
  const [solicitudes, setSolicitudes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [searchParams] = useSearchParams();
  const focusParam = searchParams.get("focus") || "";
  const itemRefs = useRef(new Map());

  useEffect(() => {
    const fetchSolicitudes = async () => {
      try {
        const data = await getSolicitudesDocumentacion();
        setSolicitudes(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error(err);
        const status = err?.response?.status;
        if (status === 401) {
          setError("Tu sesión expiró. Iniciá sesión nuevamente.");
        } else if (status === 403) {
          setError("No tenés permisos para ver las solicitudes.");
        } else {
          setError(
            "No pudimos cargar las solicitudes. Intentá de nuevo en unos minutos.",
          );
        }
      } finally {
        setCargando(false);
      }
    };
    fetchSolicitudes();
  }, []);

  const claveFocus = useMemo(() => focusParam, [focusParam]);

  useEffect(() => {
    if (!claveFocus || cargando) return;
    const nodo = itemRefs.current.get(claveFocus);
    if (nodo) {
      nodo.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [claveFocus, cargando, solicitudes]);

  const obtenerClave = (solicitud) =>
    `${solicitud.tipo}:${solicitud.recurso_id}`;

  const obtenerUrlDetalle = (solicitud) =>
    `/admin/solicitudes-documentacion/${solicitud.tipo}/${solicitud.recurso_id}`;

  const esItemDestacado = (solicitud) =>
    claveFocus && obtenerClave(solicitud) === claveFocus;

  const registrarRef = (clave) => (nodo) => {
    if (nodo) {
      itemRefs.current.set(clave, nodo);
    } else {
      itemRefs.current.delete(clave);
    }
  };

  return (
    <>
      <div className="mb-6 flex min-w-0 flex-col gap-2 sm:flex-row sm:items-end sm:justify-between px-2">
        <div className="min-w-0">
          <p className="mb-1 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Cola de revisión
          </p>
          <h1 className="font-display text-2xl font-black leading-[1.1] tracking-[-0.04em] text-autospot-black break-words sm:text-4xl">
            Solicitudes de documentación
          </h1>
          <p className="mt-1 max-w-2xl text-xs sm:text-sm leading-relaxed text-autospot-muted">
            Listado de trámites pendientes ordenado por fecha de ingreso (más
            antiguos primero), para asegurar atención equitativa.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318] mx-2">
          {error}
        </div>
      )}

      {cargando ? (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent"></div>
        </div>
      ) : solicitudes.length === 0 ? (
        <div className="rounded-[22px] border border-dashed border-autospot-border bg-white/70 px-5 py-10 text-center mx-2">
          <p className="font-display text-lg font-bold text-autospot-black">
            No hay trámites pendientes
          </p>
          <p className="mt-2 text-sm text-autospot-muted">
            Cuando ingresen nuevas solicitudes, aparecerán acá.
          </p>
        </div>
      ) : (
        <div className="w-full px-2">
          {/* 
            TABLA: Oculta por defecto (hidden) en celulares, 
            visible como bloque de tabla a partir de pantallas medianas (md:block)
          */}
          <div className="hidden md:block overflow-hidden rounded-2xl border border-autospot-border bg-autospot-white shadow-[0_12px_30px_rgba(15,23,42,0.04)]">
            <table className="w-full text-left text-sm">
              <thead className="bg-[#f9fafb] text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                <tr>
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Tipo</th>
                  <th className="px-4 py-3">Usuario</th>
                  <th className="px-4 py-3">Detalle</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3">Ingreso</th>
                  <th className="px-4 py-3">Acción</th>
                </tr>
              </thead>
              <tbody>
                {solicitudes.map((solicitud, index) => {
                  const clave = obtenerClave(solicitud);
                  const destacado = esItemDestacado(solicitud);
                  return (
                    <tr
                      key={`${solicitud.tipo}-${solicitud.recurso_id}`}
                      ref={registrarRef(clave)}
                      className={`border-t border-autospot-border align-top transition ${destacado ? "bg-[#fff7ed] ring-2 ring-autospot-accent" : "hover:bg-gray-50/50"}`}
                    >
                      <td className="px-4 py-3 font-bold text-autospot-muted">
                        {index + 1}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold ${claseChipTipo(solicitud.tipo)}`}
                        >
                          {etiquetaTipo(solicitud.tipo)}
                        </span>
                      </td>
                      <td className="px-4 py-3 break-words text-autospot-black">
                        {solicitud.usuario_email}
                      </td>
                      <td className="px-4 py-3 text-autospot-black">
                        {solicitud.resumen}
                      </td>
                      <td className="px-4 py-3 text-autospot-muted">
                        {solicitud.estado}
                      </td>
                      <td className="px-4 py-3 text-autospot-muted">
                        {formatearFecha(solicitud.fecha_solicitud)}
                      </td>
                      <td className="px-4 py-3">
                        <Link
                          to={obtenerUrlDetalle(solicitud)}
                          className="inline-flex whitespace-nowrap rounded-full bg-autospot-accent px-4 py-2 text-xs font-bold !text-white transition hover:bg-[#5a1420]"
                        >
                          Ver documentación
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* 
            LISTA MOBILE: Grid de 1 columna para celulares, 
            se oculta por completo en pantallas grandes (md:hidden)
          */}
          <ul className="flex w-full flex-col gap-4 md:hidden">
            {solicitudes.map((solicitud, index) => {
              const clave = obtenerClave(solicitud);
              const destacado = esItemDestacado(solicitud);
              const inicial = (solicitud.usuario_email || "?")
                .charAt(0)
                .toUpperCase();
              const esVehiculo = solicitud.tipo === "VEHICULO";
              const avatarClase = esVehiculo
                ? "bg-[#eff6ff] text-[#1d4ed8]"
                : "bg-[#fef3c7] text-[#92400e]";

              return (
                <li
                  key={`${solicitud.tipo}-${solicitud.recurso_id}`}
                  ref={registrarRef(clave)}
                  className={`overflow-hidden rounded-2xl border bg-autospot-white shadow-sm transition ${
                    destacado
                      ? "border-autospot-accent ring-2 ring-autospot-accent bg-[#fff7ed]"
                      : "border-autospot-border"
                  }`}
                >
                  <div className="p-5">
                    {/* Encabezado de la Card: Avatar + Información principal */}
                    <div className="flex items-center gap-3 border-b border-autospot-border pb-3">
                      <span
                        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-base font-bold ${avatarClase}`}
                      >
                        {inicial}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-xs font-bold text-autospot-black">
                          {solicitud.usuario_email}
                        </p>
                        <p className="mt-0.5 text-[11px] font-medium text-autospot-muted">
                          Posición: #{index + 1} en la cola
                        </p>
                      </div>
                      <span
                        className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold ${claseChipTipo(solicitud.tipo)}`}
                      >
                        {etiquetaTipo(solicitud.tipo)}
                      </span>
                    </div>

                    {/* Detalles del trámite en formato formulario responsivo */}
                    <div className="mt-4 space-y-3 text-xs">
                      <div>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-autospot-muted block mb-0.5">
                          Recurso / Detalle
                        </span>
                        <p className="font-semibold text-autospot-black break-words">
                          {solicitud.resumen}
                        </p>
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-autospot-muted block mb-0.5">
                            Fecha Ingreso
                          </span>
                          <p className="font-medium text-autospot-black">
                            {formatearFecha(solicitud.fecha_solicitud)}
                          </p>
                        </div>
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-autospot-muted block mb-0.5">
                            Estado Actual
                          </span>
                          <p className="font-medium text-autospot-black">
                            {solicitud.estado}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Acción principal de la Card */}
                    <div className="mt-5">
                      <Link
                        to={obtenerUrlDetalle(solicitud)}
                        className="inline-flex w-full justify-center rounded-xl bg-autospot-accent py-2.5 text-xs font-bold !text-white transition hover:bg-[#5a1420] shadow-sm"
                      >
                        Revisar Documentación
                      </Link>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </>
  );
};

export default SolicitudesDocumentacionPage;
