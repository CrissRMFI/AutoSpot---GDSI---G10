import { useEffect, useState } from "react";
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
                {solicitudes.map((solicitud, index) => (
                  <tr
                    key={`${solicitud.tipo}-${solicitud.recurso_id}`}
                    className="border-t border-autospot-border align-top"
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
                ))}
              </tbody>
            </table>
          </div>

          {/* Lista de cards solo para mobile */}
          <ul className="flex flex-col gap-4 md:hidden">
            {solicitudes.map((solicitud, index) => (
              <li
                key={`${solicitud.tipo}-${solicitud.recurso_id}`}
                className="rounded-2xl border border-autospot-border bg-autospot-white p-5 shadow-[0_12px_30px_rgba(15,23,42,0.04)]"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                      #{index + 1} · {formatearFecha(solicitud.fecha_solicitud)}
                    </p>
                    <p className="mt-1 break-words font-display text-base font-bold text-autospot-black">
                      {solicitud.resumen}
                    </p>
                  </div>
                  <span
                    className={`inline-flex shrink-0 items-center rounded-full border px-2.5 py-1 text-xs font-bold ${claseChipTipo(solicitud.tipo)}`}
                  >
                    {etiquetaTipo(solicitud.tipo)}
                  </span>
                </div>
                <p className="mt-3 break-words text-sm text-autospot-muted">
                  {solicitud.usuario_email}
                </p>
                <p className="mt-1 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                  Estado: <span className="text-autospot-black">{solicitud.estado}</span>
                </p>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
};

export default SolicitudesDocumentacionPage;
