import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
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
          setError("No pudimos cargar las solicitudes. Intentá de nuevo en unos minutos.");
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
      <div className="mb-6 flex min-w-0 flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Cola de revisión
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black break-words sm:text-4xl">
            Solicitudes de documentación
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-autospot-muted">
            Listado de trámites pendientes ordenado por fecha de ingreso (más
            antiguos primero), para asegurar atención equitativa.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
          {error}
        </div>
      )}

      {cargando ? (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent"></div>
        </div>
      ) : solicitudes.length === 0 ? (
        <div className="rounded-[22px] border border-dashed border-autospot-border bg-white/70 px-5 py-10 text-center">
          <p className="font-display text-lg font-bold text-autospot-black">
            No hay trámites pendientes
          </p>
          <p className="mt-2 text-sm text-autospot-muted">
            Cuando ingresen nuevas solicitudes, aparecerán acá.
          </p>
        </div>
      ) : (
        <>
          {/* Tabla solo para desktop */}
          <div className="hidden overflow-hidden rounded-2xl border border-autospot-border bg-autospot-white shadow-[0_12px_30px_rgba(15,23,42,0.04)] md:block">
            <table className="w-full text-left text-sm">
              <thead className="bg-[#f9fafb] text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                <tr>
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Tipo</th>
                  <th className="px-4 py-3">Usuario</th>
                  <th className="px-4 py-3">Detalle</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3">Ingreso</th>
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
                    className={`border-t border-autospot-border align-top transition ${destacado ? "bg-[#fff7ed] ring-2 ring-autospot-accent" : ""}`}
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
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Lista de cards solo para mobile */}
          <ul className="flex w-full flex-col gap-4 md:hidden">
            {solicitudes.map((solicitud, index) => {
              const clave = obtenerClave(solicitud);
              const destacado = esItemDestacado(solicitud);
              const inicial = (solicitud.usuario_email || "?")
                .charAt(0)
                .toUpperCase();
              const esVehiculo = solicitud.tipo === "VEHICULO";
              const avatarClase = esVehiculo
                ? "bg-[#1d4ed8] text-white"
                : "bg-[#92400e] text-white";
              return (
              <li
                key={`${solicitud.tipo}-${solicitud.recurso_id}`}
                ref={registrarRef(clave)}
                className={`overflow-hidden rounded-3xl border bg-autospot-white shadow-[0_18px_40px_rgba(15,23,42,0.06)] transition ${destacado ? "border-autospot-accent ring-2 ring-autospot-accent" : "border-autospot-border"}`}
              >
                {/* Banda de color superior */}
                <div
                  className={`h-1.5 w-full ${esVehiculo ? "bg-[#1d4ed8]" : "bg-[#92400e]"}`}
                  aria-hidden="true"
                />

                <div className="flex flex-col items-center px-6 pb-6 pt-7">
                  <span
                    className={`inline-flex h-16 w-16 items-center justify-center rounded-full text-xl font-bold shadow-[0_8px_20px_rgba(15,23,42,0.15)] ${avatarClase}`}
                    aria-hidden="true"
                  >
                    {inicial}
                  </span>

                  <span
                    className={`mt-4 inline-flex items-center rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-[0.1em] ${claseChipTipo(solicitud.tipo)}`}
                  >
                    {etiquetaTipo(solicitud.tipo)}
                  </span>

                  <p className="mt-3 break-words text-center font-display text-lg font-bold leading-tight tracking-[-0.02em] text-autospot-black">
                    {solicitud.resumen}
                  </p>

                  <p className="mt-1 break-all text-center text-xs text-autospot-muted">
                    {solicitud.usuario_email}
                  </p>

                  <div className="mt-5 grid w-full grid-cols-2 gap-3 border-t border-autospot-border pt-4">
                    <div className="text-center">
                      <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
                        Ingreso
                      </p>
                      <p className="mt-1 text-xs font-bold text-autospot-black">
                        {formatearFecha(solicitud.fecha_solicitud)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
                        Estado
                      </p>
                      <p className="mt-1 text-xs font-bold text-autospot-black">
                        {solicitud.estado}
                      </p>
                    </div>
                  </div>

                  <p className="mt-4 text-[10px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
                    #{index + 1} en la cola
                  </p>
                </div>
              </li>
              );
            })}
          </ul>
        </>
      )}
    </>
  );
};

export default SolicitudesDocumentacionPage;
