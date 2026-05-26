import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { getDetalleEstacion } from "../api/estacionesApi";
import { obtenerCatalogoVehiculos } from "../../vehiculos/api/vehiculoService";

const DetalleEstacionPublicoPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [estacion, setEstacion] = useState(null);
  const [vehiculosEstacion, setVehiculosEstacion] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [estacionData, catalogoData] = await Promise.all([
          getDetalleEstacion(id),
          obtenerCatalogoVehiculos()
        ]);
        setEstacion(estacionData);
        // Filtrar vehículos que pertenezcan a esta estación
        const autos = catalogoData.filter(v => v.estacion === estacionData.nombre);
        setVehiculosEstacion(autos);
      } catch (err) {
        console.error(err);
        setError("No se pudo cargar la información de la estación.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  return (
    <>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <button
            onClick={() => navigate(-1)}
            className="mb-4 inline-flex items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver
          </button>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Red Logística
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black break-words sm:text-4xl">
            Detalle de la estación
          </h1>
        </div>
      </div>
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent"></div>
          </div>
        ) : error ? (
          <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
            {error}
          </div>
        ) : estacion ? (
          <article className="overflow-hidden rounded-[32px] border border-autospot-border bg-autospot-white shadow-[0_12px_40px_rgba(15,23,42,0.06)]">

            <div className="p-6 sm:p-10">
              <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h1 className="font-display text-3xl font-black tracking-[-0.04em] text-autospot-black sm:text-4xl">
                    {estacion.nombre}
                  </h1>
                  <p className="mt-2 flex items-center gap-2 text-sm font-bold text-autospot-muted">
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Zona {estacion.zona}
                  </p>
                </div>
                <span className="inline-flex items-center rounded-full bg-[#f0fdf4] px-3 py-1.5 text-sm font-bold text-[#166534] border border-[#bbf7d0]">
                  Estación Operativa
                </span>
              </div>

              <div className="space-y-6">
                <div className="rounded-2xl bg-gray-50 p-6 border border-gray-100">
                  <h3 className="mb-3 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
                    Dirección Exacta
                  </h3>
                  <p className="font-display text-xl font-bold text-autospot-black">
                    {estacion.direccion || "Av. Siempre Viva 742, Springfield"} {/* Fallback lúdico por si acaso */}
                  </p>
                </div>

                <div className="rounded-2xl bg-autospot-cream/30 p-6 border border-autospot-border">
                  <h3 className="mb-3 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                    Instrucciones de Acceso y Retiro
                  </h3>
                  <p className="text-base leading-relaxed text-autospot-black">
                    {estacion.instrucciones_acceso || "Dirígete a la recepción con tu documento de identidad para retirar las llaves de tu vehículo."}
                  </p>
                </div>

                <div className="pt-4 border-t border-autospot-border mt-8">
                  <h3 className="mb-4 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
                    Vehículos disponibles en esta estación ({vehiculosEstacion.length})
                  </h3>
                  
                  {vehiculosEstacion.length === 0 ? (
                    <div className="rounded-2xl border border-dashed border-autospot-border bg-gray-50 px-5 py-8 text-center">
                      <p className="text-sm font-bold text-autospot-muted">No hay vehículos disponibles en esta estación por el momento.</p>
                    </div>
                  ) : (
                    <div className="grid gap-4 sm:grid-cols-2">
                      {vehiculosEstacion.map((vehiculo) => {
                        const fotoUrl = vehiculo.fotos?.[0]?.url;
                        return (
                          <Link
                            key={vehiculo.id}
                            to={`/catalogo/${vehiculo.id}`}
                            className="group block overflow-hidden rounded-2xl border border-autospot-border bg-white shadow-sm transition hover:-translate-y-0.5 hover:border-autospot-accent"
                          >
                            <div className="flex h-32 w-full bg-[#0f0f0f]">
                              {fotoUrl ? (
                                <img
                                  src={fotoUrl}
                                  alt={`${vehiculo.marca} ${vehiculo.modelo}`}
                                  className="h-full w-full object-cover transition group-hover:scale-105"
                                />
                              ) : (
                                <div className="flex h-full w-full items-center justify-center text-xs text-white/60">
                                  Sin foto
                                </div>
                              )}
                            </div>
                            <div className="p-4">
                              <h4 className="font-display text-base font-bold text-autospot-black break-words">
                                {vehiculo.marca} {vehiculo.modelo}
                              </h4>
                              <p className="text-sm text-autospot-muted">
                                {vehiculo.anio} · {vehiculo.categoria}
                              </p>
                              <div className="mt-3 text-autospot-accent font-bold text-sm">
                                ${vehiculo.precio_por_dia} / día
                              </div>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </article>
        ) : null}
    </>
  );
};

export default DetalleEstacionPublicoPage;
