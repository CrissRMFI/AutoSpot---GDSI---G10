import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getAlquileresDeAuto } from "../api/historialAutosApi";

const PLACEHOLDER_AUTO =
  "data:image/svg+xml;charset=UTF-8," +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="160" height="120" viewBox="0 0 160 120"><rect width="160" height="120" fill="#f0ebe2"/><g fill="none" stroke="#b9b2a8" stroke-width="2"><path d="M30 78l10-26a6 6 0 015.6-4h48.8a6 6 0 015.6 4l10 26"/><path d="M22 78h116v14a4 4 0 01-4 4h-12a4 4 0 01-4-4v-4H42v4a4 4 0 01-4 4H26a4 4 0 01-4-4z"/><circle cx="46" cy="84" r="6"/><circle cx="114" cy="84" r="6"/></g></svg>`,
  );

const formatFecha = (valor) => {
  if (!valor) return "—";
  try {
    return new Date(valor).toLocaleString("es-AR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return valor;
  }
};

const estadoEstilo = (estado = "") => {
  const e = estado.toUpperCase();
  if (e.includes("CURSO") || e.includes("ACTIV") || e.includes("ENTREG")) {
    return "bg-[#e7f8ed] text-[#166534] border-[#bbf7d0]";
  }
  if (e.includes("FINALIZ") || e.includes("COMPLET") || e.includes("DEVUEL")) {
    return "bg-autospot-cream text-autospot-muted border-autospot-border";
  }
  if (e.includes("CANCEL") || e.includes("RECHAZ")) {
    return "bg-[#fef2f2] text-[#b42318] border-[#fecaca]";
  }
  return "bg-[#fff7ed] text-[#9a3412] border-[#fed7aa]";
};

const AdminAlquileresAutoPage = () => {
  const { vehiculoId } = useParams();
  const navigate = useNavigate();

  const [auto, setAuto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await getAlquileresDeAuto(vehiculoId);
        setAuto(data);
      } catch (err) {
        console.error(err);
        setError("No se pudieron cargar los alquileres de este vehículo.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [vehiculoId]);

  const movimientos = auto?.movimientos ?? [];

  return (
    <div className="w-full">
      <button
        onClick={() => navigate(-1)}
        className="mb-5 inline-flex items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Volver
      </button>

      <p className="mb-2 text-xs font-bold uppercase tracking-[0.12em] text-autospot-accent">
        Registro de alquileres
      </p>
      <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
        Alquileres del vehículo
      </h1>

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent" />
        </div>
      ) : error ? (
        <div className="mt-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
          {error}
        </div>
      ) : auto ? (
        <div className="mt-6 flex flex-col gap-6">
          {/* Encabezado del auto */}
          <div className="flex flex-col gap-5 rounded-3xl border border-autospot-border bg-white p-5 shadow-sm sm:flex-row sm:items-center">
            <img
              src={auto.foto_url || PLACEHOLDER_AUTO}
              onError={(e) => {
                e.currentTarget.src = PLACEHOLDER_AUTO;
              }}
              alt={`${auto.marca} ${auto.modelo}`}
              className="h-40 w-full shrink-0 rounded-2xl object-cover sm:h-28 sm:w-44"
            />
            <div className="min-w-0 flex-1">
              <h2 className="font-display text-2xl font-bold tracking-[-0.03em] text-autospot-black">
                {auto.marca} {auto.modelo}
              </h2>
              <div className="mt-2 flex flex-wrap gap-x-5 gap-y-1.5 text-sm text-autospot-muted">
                {auto.anio && <span>Año {auto.anio}</span>}
                {auto.patente && (
                  <span>
                    Patente{" "}
                    <span className="font-bold text-autospot-black">{auto.patente}</span>
                  </span>
                )}
                {auto.estacion && (
                  <span>
                    Estación{" "}
                    <span className="font-bold text-autospot-black">{auto.estacion}</span>
                  </span>
                )}
              </div>
            </div>
            <div className="shrink-0 rounded-2xl bg-autospot-cream px-5 py-3 text-center">
              <p className="font-display text-2xl font-black text-autospot-accent">
                {movimientos.length}
              </p>
              <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                Alquileres
              </p>
            </div>
          </div>

          {/* Lista de alquileres */}
          {movimientos.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-autospot-border bg-white/70 px-5 py-14 text-center">
              <p className="text-sm font-bold text-autospot-muted">
                Este vehículo no registra alquileres todavía.
              </p>
            </div>
          ) : (
            <>
              {/* Tabla (desktop) */}
              <div className="hidden overflow-hidden rounded-3xl border border-autospot-border bg-white shadow-sm md:block">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-autospot-border bg-autospot-cream/50 text-xs font-bold uppercase tracking-[0.06em] text-autospot-muted">
                    <tr>
                      <th className="px-5 py-3.5">Conductor</th>
                      <th className="px-5 py-3.5">Estado</th>
                      <th className="px-5 py-3.5">Estación retiro</th>
                      <th className="px-5 py-3.5">Inicio</th>
                      <th className="px-5 py-3.5">Fin</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-autospot-border/60">
                    {movimientos.map((mov) => (
                      <tr key={mov.id} className="transition hover:bg-autospot-cream/30">
                        <td className="px-5 py-4">
                          <p className="font-bold text-autospot-black">
                            {mov.conductor_nombre && mov.conductor_apellido
                              ? `${mov.conductor_nombre} ${mov.conductor_apellido}`
                              : mov.conductor_email}
                          </p>
                          {mov.conductor_nombre && (
                            <p className="text-xs text-autospot-muted">{mov.conductor_email}</p>
                          )}
                        </td>
                        <td className="px-5 py-4">
                          <span
                            className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold ${estadoEstilo(mov.estado)}`}
                          >
                            {mov.estado}
                          </span>
                        </td>
                        <td className="px-5 py-4 text-autospot-black">{mov.estacion_retiro}</td>
                        <td className="px-5 py-4 text-autospot-muted">{formatFecha(mov.fecha_inicio)}</td>
                        <td className="px-5 py-4 text-autospot-muted">{formatFecha(mov.fecha_fin)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Cards (mobile) */}
              <div className="flex flex-col gap-3 md:hidden">
                {movimientos.map((mov) => (
                  <div
                    key={mov.id}
                    className="rounded-2xl border border-autospot-border bg-white p-4 shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate font-bold text-autospot-black">
                          {mov.conductor_nombre && mov.conductor_apellido
                            ? `${mov.conductor_nombre} ${mov.conductor_apellido}`
                            : mov.conductor_email}
                        </p>
                        <p className="truncate text-xs text-autospot-muted">{mov.estacion_retiro}</p>
                      </div>
                      <span
                        className={`shrink-0 inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-bold ${estadoEstilo(mov.estado)}`}
                      >
                        {mov.estado}
                      </span>
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-2 border-t border-autospot-border/60 pt-3 text-xs">
                      <div>
                        <p className="font-bold uppercase tracking-[0.06em] text-autospot-muted">Inicio</p>
                        <p className="text-autospot-black">{formatFecha(mov.fecha_inicio)}</p>
                      </div>
                      <div>
                        <p className="font-bold uppercase tracking-[0.06em] text-autospot-muted">Fin</p>
                        <p className="text-autospot-black">{formatFecha(mov.fecha_fin)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      ) : null}
    </div>
  );
};

export default AdminAlquileresAutoPage;
