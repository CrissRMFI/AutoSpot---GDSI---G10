import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getDetalleEstacion,
  getEstacionesActivas,
} from "../api/estacionesApi";

const EstacionesPage = () => {
  const [estaciones, setEstaciones] = useState([]);
  const [estacionSeleccionada, setEstacionSeleccionada] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchEstaciones = async () => {
      try {
        const data = await getEstacionesActivas();
        setEstaciones(data);
      } catch (err) {
        console.error(err);
        setError("Error al cargar las estaciones. Intenta nuevamente más tarde.");
      } finally {
        setLoading(false);
      }
    };
    fetchEstaciones();
  }, []);

  const handleSeleccionarEstacion = async (id) => {
    setLoadingDetalle(true);
    setEstacionSeleccionada(null);
    try {
      const data = await getDetalleEstacion(id);
      setEstacionSeleccionada(data);
    } catch (err) {
      console.error(err);
      setError("Error al cargar los detalles de la estación.");
    } finally {
      setLoadingDetalle(false);
    }
  };

  return (
    <main className="min-h-screen bg-autospot-cream text-autospot-black">
      <header className="sticky top-0 z-40 border-b border-autospot-border bg-autospot-cream/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-5 py-4 sm:px-8">
          <Link
            to="/"
            className="font-display text-xl font-black tracking-[-0.04em] !text-autospot-black"
          >
            Auto<span className="!text-autospot-accent">Spot</span>
          </Link>
          <Link
            to="/dashboard"
            className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Volver al Panel
          </Link>
        </div>
      </header>

      <section className="mx-auto w-full max-w-4xl px-5 py-8 sm:px-8 sm:py-12">
        <div className="mb-8">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Red Logística
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
            Estaciones Habilitadas
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-autospot-muted sm:text-base">
            Seleccioná una estación de retiro para visualizar las instrucciones necesarias para la operatividad de tu Activo.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent"></div>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {estaciones.length === 0 ? (
              <div className="rounded-[22px] border border-dashed border-autospot-border bg-white/70 px-5 py-8 text-center">
                <p className="text-sm font-bold text-autospot-muted">No hay estaciones activas en este momento.</p>
              </div>
            ) : (
              estaciones.map((estacion) => {
                const estaSeleccionada = estacionSeleccionada?.id === estacion.id;
                const cargandoDetalle = loadingDetalle && !estaSeleccionada;

                return (
                  <article
                    key={estacion.id}
                    onClick={() => handleSeleccionarEstacion(estacion.id)}
                    className="cursor-pointer overflow-hidden rounded-[22px] border border-autospot-border bg-autospot-white shadow-[0_12px_30px_rgba(15,23,42,0.04)] transition hover:-translate-y-1 hover:shadow-[0_18px_40px_rgba(15,23,42,0.08)]"
                  >
                    {estacion.imagen_url && (
                      <img
                        src={estacion.imagen_url}
                        alt={estacion.nombre}
                        className="h-40 w-full object-cover"
                        loading="lazy"
                      />
                    )}

                    <div className="p-5">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-display text-lg font-bold tracking-[-0.04em] text-autospot-black">
                            {estacion.nombre}
                          </h3>
                          <p className="mt-1 text-sm text-autospot-muted">
                            Zona: {estacion.zona}
                          </p>
                        </div>
                        <span className="inline-flex items-center rounded-full bg-[#f0fdf4] px-2.5 py-1 text-xs font-bold text-[#166534] border border-[#bbf7d0]">
                          Operativa
                        </span>
                      </div>

                      {estaSeleccionada && (
                        <div className="mt-5 rounded-xl bg-[#f9fafb] p-4 border border-autospot-border">
                          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                            Dirección Exacta
                          </p>
                          <p className="mb-4 font-display text-base font-bold text-autospot-black">
                            {estacionSeleccionada.direccion}
                          </p>
                          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                            Instrucciones de Retiro
                          </p>
                          <p className="text-sm text-autospot-black">
                            {estacionSeleccionada.instrucciones_acceso}
                          </p>
                        </div>
                      )}

                      {cargandoDetalle && (
                        <div className="mt-4 flex justify-center">
                          <div className="h-5 w-5 animate-spin rounded-full border-2 border-autospot-border border-t-autospot-accent"></div>
                        </div>
                      )}
                    </div>
                  </article>
                );
              })
            )}
          </div>
        )}
      </section>
    </main>
  );
};

export default EstacionesPage;