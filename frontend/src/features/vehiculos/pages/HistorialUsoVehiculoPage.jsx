import { useState, useEffect, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ChevronLeft,
  Star,
  CalendarClock,
  MessageSquareText,
  AlertTriangle,
  Users,
} from "lucide-react";
import { getDetalleVehiculo, getHistorialUsoVehiculo } from "../api/vehiculoService";
import LightboxGaleria from "../components/LightboxGaleria";

const formatFecha = (valor) =>
  valor
    ? new Date(valor).toLocaleString("es-AR", {
        dateStyle: "short",
        timeStyle: "short",
      })
    : "—";

const Estrellas = ({ puntaje }) => (
  <div className="flex text-[#eab308]">
    {Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${i < puntaje ? "fill-current" : "text-autospot-border"}`}
      />
    ))}
  </div>
);

const Resenia = ({ registro }) =>
  registro.puntaje || registro.resenia ? (
    <div>
      {registro.puntaje ? <Estrellas puntaje={registro.puntaje} /> : null}
      {registro.resenia ? (
        <span className="mt-1 block italic text-autospot-muted">
          "{registro.resenia}"
        </span>
      ) : (
        <span className="text-autospot-muted">Sin reseña</span>
      )}
    </div>
  ) : (
    <span className="text-autospot-muted">Sin reseña</span>
  );

/** Links a los reportes (check-in / check-out / incidencia) de un registro. */
const LinksReporte = ({ registro, vehiculoId }) => {
  const d = registro.detalles_reporte;
  if (!registro.tiene_reporte || !d) {
    return <span className="text-autospot-muted">Ninguna</span>;
  }
  const link = (texto) => (
    <Link
      to={`/vehiculos/${vehiculoId}/historial/reporte`}
      state={{ reporte: d }}
      className="block text-sm font-bold text-autospot-accent transition hover:underline"
    >
      {texto}
    </Link>
  );
  return (
    <div className="flex flex-col gap-1.5">
      {(d.descripcion_danios_checkin || d.motivo_rechazo_checkin) &&
        link("Reporte Check-in")}
      {(d.descripcion_danios_checkout || d.motivo_rechazo_checkout) &&
        link("Reporte Check-out")}
      {d.reporte_incidencia && link("Reporte de Incidencia")}
    </div>
  );
};

const Fotos = ({ urls, onAbrir }) =>
  urls && urls.length > 0 ? (
    <div className="flex flex-wrap gap-1.5">
      {urls.map((url, i) => (
        <button
          key={i}
          type="button"
          onClick={() => onAbrir(urls, i)}
          className="h-9 w-9 overflow-hidden rounded-md border border-autospot-border transition hover:border-autospot-accent hover:shadow-sm"
          title={`Ver foto ${i + 1}`}
        >
          <img src={url} alt={`Foto ${i + 1}`} className="h-full w-full object-cover" />
        </button>
      ))}
    </div>
  ) : (
    <span className="text-autospot-muted">—</span>
  );

const MetricaCard = ({ icono: Icono, valor, titulo }) => (
  <article className="rounded-lg border border-autospot-border bg-autospot-white p-4">
    <div className="flex items-center gap-3">
      <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#efe9df] text-autospot-accent">
        <Icono className="h-5 w-5" aria-hidden="true" />
      </span>
      <div className="min-w-0">
        <p className="text-2xl font-black leading-none text-autospot-black">{valor}</p>
        <p className="mt-1 text-xs font-bold uppercase tracking-[0.06em] text-autospot-muted">
          {titulo}
        </p>
      </div>
    </div>
  </article>
);

export const HistorialUsoVehiculoPage = () => {
  const { vehiculoId } = useParams();
  const [vehiculo, setVehiculo] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lightboxAbierto, setLightboxAbierto] = useState(false);
  const [fotosLightbox, setFotosLightbox] = useState([]);
  const [indiceLightbox, setIndiceLightbox] = useState(0);

  const abrirLightbox = (urls, index) => {
    setFotosLightbox(urls.map((url) => ({ url, lado: "EXTRA" })));
    setIndiceLightbox(index);
    setLightboxAbierto(true);
  };

  useEffect(() => {
    const fetchDatos = async () => {
      try {
        const [detalle, historialData] = await Promise.all([
          getDetalleVehiculo(vehiculoId),
          getHistorialUsoVehiculo(vehiculoId),
        ]);
        setVehiculo(detalle);
        setHistorial(historialData);
      } catch {
        setError("Ocurrió un error al cargar el historial del vehículo.");
      } finally {
        setLoading(false);
      }
    };
    fetchDatos();
  }, [vehiculoId]);

  const stats = useMemo(() => {
    const total = historial.length;
    const conPuntaje = historial.filter((r) => r.puntaje);
    const promedio = conPuntaje.length
      ? conPuntaje.reduce((s, r) => s + r.puntaje, 0) / conPuntaje.length
      : 0;
    return {
      total,
      promedio,
      resenias: historial.filter((r) => r.resenia).length,
      reportes: historial.filter((r) => r.tiene_reporte).length,
      conductores: new Set(historial.map((r) => r.conductor_nombre)).size,
    };
  }, [historial]);

  if (loading) {
    return (
      <section className="flex w-full justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent" />
      </section>
    );
  }

  if (error) {
    return (
      <section className="w-full py-16 text-center">
        <p className="text-lg font-bold text-[#b42318]">{error}</p>
      </section>
    );
  }

  return (
    <section className="w-full min-w-0 text-autospot-black">
      {/* HEADER */}
      <div className="mb-6">
        <Link
          to={`/vehiculos/${vehiculoId}/detalle`}
          className="mb-3 inline-flex items-center gap-2 rounded-full border border-autospot-border bg-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
        >
          <ChevronLeft className="h-4 w-4" />
          Volver al detalle
        </Link>
        <h1 className="text-3xl font-black leading-tight text-autospot-black sm:text-4xl">
          Historial de uso
        </h1>
        <p className="mt-1 text-sm font-semibold text-autospot-muted">
          {vehiculo?.marca} {vehiculo?.modelo} · {vehiculo?.patente || "Sin patente"}
          {vehiculo?.anio ? ` · ${vehiculo.anio}` : ""}
          {vehiculo?.kilometros != null
            ? ` · ${Number(vehiculo.kilometros).toLocaleString("es-AR")} km`
            : ""}
        </p>
      </div>

      {/* MÉTRICAS */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-5">
        <MetricaCard icono={CalendarClock} valor={stats.total} titulo="Alquileres" />
        <MetricaCard
          icono={Star}
          valor={stats.promedio ? stats.promedio.toFixed(1) : "—"}
          titulo="Calificación prom."
        />
        <MetricaCard
          icono={MessageSquareText}
          valor={stats.resenias}
          titulo="Reseñas"
        />
        <MetricaCard
          icono={AlertTriangle}
          valor={stats.reportes}
          titulo="Reportes"
        />
        <MetricaCard icono={Users} valor={stats.conductores} titulo="Conductores" />
      </div>

      {historial.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-autospot-border bg-white/70 p-12 text-center">
          <p className="text-sm font-bold text-autospot-muted">
            Este vehículo aún no tiene registros de uso.
          </p>
        </div>
      ) : (
        <>
          {/* TABLA (desktop) */}
          <div className="hidden w-full overflow-hidden rounded-2xl border border-autospot-border bg-white shadow-sm lg:block">
            <table className="w-full text-left text-sm text-autospot-black">
              <thead className="border-b border-autospot-border bg-autospot-cream/50 text-xs font-bold uppercase tracking-[0.06em] text-autospot-muted">
                <tr>
                  <th className="px-5 py-3.5">Conductor</th>
                  <th className="px-5 py-3.5">Retiro</th>
                  <th className="px-5 py-3.5">Devolución pactada</th>
                  <th className="px-5 py-3.5">Devolución real</th>
                  <th className="px-5 py-3.5">Reseña</th>
                  <th className="px-5 py-3.5 text-center">Fotos</th>
                  <th className="px-5 py-3.5 text-center">Reportes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-autospot-border/60">
                {historial.map((registro, idx) => (
                  <tr key={idx} className="align-top transition hover:bg-autospot-cream/30">
                    <td className="px-5 py-4 font-bold text-autospot-black">
                      {registro.conductor_nombre}
                    </td>
                    <td className="px-5 py-4 text-autospot-muted">
                      {formatFecha(registro.fecha_inicio)}
                    </td>
                    <td className="px-5 py-4 text-autospot-muted">
                      {formatFecha(registro.fecha_fin)}
                    </td>
                    <td className="px-5 py-4 font-semibold text-autospot-black">
                      {formatFecha(registro.fecha_devolucion_real)}
                    </td>
                    <td className="max-w-xs px-5 py-4">
                      <Resenia registro={registro} />
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex justify-center">
                        <Fotos urls={registro.fotos_entrega} onAbrir={abrirLightbox} />
                      </div>
                    </td>
                    <td className="px-5 py-4 text-center">
                      <LinksReporte registro={registro} vehiculoId={vehiculoId} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* CARDS (mobile/tablet) */}
          <div className="flex flex-col gap-3 lg:hidden">
            {historial.map((registro, idx) => (
              <article
                key={idx}
                className="rounded-2xl border border-autospot-border bg-white p-4 shadow-sm"
              >
                <div className="flex items-start justify-between gap-3">
                  <p className="font-display text-base font-bold text-autospot-black">
                    {registro.conductor_nombre}
                  </p>
                  {registro.puntaje ? <Estrellas puntaje={registro.puntaje} /> : null}
                </div>

                <div className="mt-3 grid grid-cols-2 gap-2 border-t border-autospot-border/60 pt-3 text-xs">
                  <div>
                    <p className="font-bold uppercase tracking-[0.06em] text-autospot-muted">Retiro</p>
                    <p className="text-autospot-black">{formatFecha(registro.fecha_inicio)}</p>
                  </div>
                  <div>
                    <p className="font-bold uppercase tracking-[0.06em] text-autospot-muted">Devolución real</p>
                    <p className="text-autospot-black">{formatFecha(registro.fecha_devolucion_real)}</p>
                  </div>
                </div>

                {registro.resenia && (
                  <p className="mt-3 text-sm italic text-autospot-muted">
                    "{registro.resenia}"
                  </p>
                )}

                {registro.fotos_entrega?.length > 0 && (
                  <div className="mt-3">
                    <p className="mb-1.5 text-[11px] font-bold uppercase tracking-[0.06em] text-autospot-muted">
                      Fotos
                    </p>
                    <Fotos urls={registro.fotos_entrega} onAbrir={abrirLightbox} />
                  </div>
                )}

                {registro.tiene_reporte && (
                  <div className="mt-3 border-t border-autospot-border/60 pt-3">
                    <p className="mb-1.5 text-[11px] font-bold uppercase tracking-[0.06em] text-autospot-muted">
                      Reportes
                    </p>
                    <LinksReporte registro={registro} vehiculoId={vehiculoId} />
                  </div>
                )}
              </article>
            ))}
          </div>
        </>
      )}

      <LightboxGaleria
        isOpen={lightboxAbierto}
        onClose={() => setLightboxAbierto(false)}
        fotos={fotosLightbox}
        indiceActivo={indiceLightbox}
        setIndiceActivo={setIndiceLightbox}
      />
    </section>
  );
};
