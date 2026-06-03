import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  getDetalleEstacion,
  getEstacionesActivas,
} from "../api/estacionesApi";
import { obtenerCatalogoVehiculos } from "../../vehiculos/api/vehiculoService";
import { useAuth } from "../../auth/hooks/useAuth";
import { obtenerDocumentacionHabilitante } from "../../usuarios/api/documentacionHabilitanteService";
import MapaEstacionesCABA from "../components/MapaEstacionesCABA";

const EstacionesPage = () => {
  const location = useLocation();
  const { usuario } = useAuth();

  const [estaciones, setEstaciones] = useState([]);
  const [vehiculos, setVehiculos] = useState([]);
  const [estacionSeleccionada, setEstacionSeleccionada] = useState(null);
  const [barrioSeleccionado, setBarrioSeleccionado] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [error, setError] = useState("");

  // Determinar si el modo es solo visualización
  const [soloVisualizacion, setSoloVisualizacion] = useState(
    location.state?.soloVisualizacion ?? false
  );
  const [estadoDocumentacion, setEstadoDocumentacion] = useState(
    location.state?.estadoDocumentacion ?? null
  );

  // Verificar habilitación independientemente (por si acceden directo por URL)
  useEffect(() => {
    const verificarHabilitacion = async () => {
      if (!usuario?.id || usuario?.rol === "ADMIN" || usuario?.rol === "PROPIETARIO") return;
      try {
        const data = await obtenerDocumentacionHabilitante(usuario.id);
        setEstadoDocumentacion(data.estado_validacion);
        if (data.estado_validacion !== "APROBADO") {
          setSoloVisualizacion(true);
        } else {
          setSoloVisualizacion(false);
        }
      } catch {
        // Sin documentación → solo visualización
        setEstadoDocumentacion("SIN_DOCUMENTACION");
        setSoloVisualizacion(true);
      }
    };
    verificarHabilitacion();
  }, [usuario?.id, usuario?.rol]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [estacionesData, vehiculosData] = await Promise.all([
          getEstacionesActivas(),
          obtenerCatalogoVehiculos()
        ]);

        const estacionesOrdenadas = estacionesData.sort((a, b) => 
          a.nombre.localeCompare(b.nombre)
        );

        setEstaciones(estacionesOrdenadas);
        setVehiculos(vehiculosData);
      } catch (err) {
        console.error(err);
        setError("Error al cargar las estaciones o los vehículos. Intenta nuevamente más tarde.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSeleccionarEstacion = async (id) => {
    if (estacionSeleccionada?.id === id) {
      setEstacionSeleccionada(null);
      return;
    }

    setLoadingDetalle(true);
    try {
      const data = await getDetalleEstacion(id);
      setEstacionSeleccionada(data);
      setTimeout(() => {
        const el = document.getElementById(`estacion-${id}`);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 100);
    } catch (err) {
      console.error(err);
      setError("Error al cargar los detalles de la estación.");
    } finally {
      setLoadingDetalle(false);
    }
  };

  const handleBarrioSelect = (barrio) => {
    setBarrioSeleccionado(barrio === barrioSeleccionado ? null : barrio);
    setEstacionSeleccionada(null);
  };

  const estacionesFiltradas = estacionSeleccionada
    ? estaciones.filter((e) => e.id === estacionSeleccionada.id)
    : (barrioSeleccionado
        ? estaciones.filter((e) => e.zona?.toLowerCase() === barrioSeleccionado.toLowerCase())
        : estaciones)
        .sort((a, b) => a.nombre.localeCompare(b.nombre));

  return (
    <>
      <div className="mb-8">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Red Logística
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
            Estaciones Habilitadas
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-autospot-muted sm:text-base">
            Explorá el mapa interactivo de la Ciudad de Buenos Aires para encontrar vehículos disponibles en tu barrio. Seleccioná una estación para ver sus instrucciones de retiro.
          </p>
        </div>

        {soloVisualizacion && (
          <div className={`mb-6 flex items-center gap-2 rounded-2xl border px-4 py-3 text-sm font-semibold ${
            estadoDocumentacion === "RECHAZADO" 
              ? "border-[#fecaca] bg-[#fef2f2] text-[#b42318]" 
              : "border-[#fef08a] bg-[#fef9c3] text-[#854d0e]"
          }`}>
            <span>{estadoDocumentacion === "RECHAZADO" ? "❌" : "⏳"}</span>
            {estadoDocumentacion === "RECHAZADO"
              ? "Tu documentación fue rechazada. Mientras tanto, podés ver las estaciones disponibles."
              : estadoDocumentacion === "SIN_DOCUMENTACION"
              ? "Aún no subiste tu documentación. Mientras tanto, podés ver las estaciones disponibles."
              : "Tu documentación está en revisión. Mientras tanto, podés ver las estaciones disponibles."}
          </div>
        )}

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
          <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_1fr] gap-8 items-start">
            {/* Mapa Interactivo */}
            <div className="rounded-[28px] bg-white p-6 shadow-sm border border-autospot-border sticky top-24">
              <h2 className="font-display text-xl font-bold mb-4">Mapa de CABA</h2>
              <MapaEstacionesCABA 
                onEstacionSelect={handleSeleccionarEstacion}
                datosEstaciones={estaciones}
              />
            </div>

            {/* Listado de estaciones y autos */}
            <div className="flex flex-col gap-4">
              {(barrioSeleccionado || estacionSeleccionada) && (
                <div className="flex items-center justify-between rounded-xl bg-gray-100 px-4 py-3">
                  <span className="text-sm font-bold text-autospot-black">
                    {estacionSeleccionada 
                      ? `Estación: ${estacionSeleccionada.nombre}`
                      : `Barrio: ${barrioSeleccionado}`
                    }
                  </span>
                  <button 
                    onClick={() => {
                      setBarrioSeleccionado(null);
                      setEstacionSeleccionada(null);
                    }}
                    className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-3 py-1.5 text-xs font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
                  >
                    Ver todas
                  </button>
                </div>
              )}

              {estacionesFiltradas.length === 0 ? (
                <div className="rounded-[22px] border border-dashed border-autospot-border bg-white/70 px-5 py-8 text-center">
                  <p className="text-sm font-bold text-autospot-muted">
                    No hay estaciones ni vehículos en {barrioSeleccionado || "este momento"}.
                  </p>
                </div>
              ) : (
                estacionesFiltradas.map((estacion) => {
                  const estaSeleccionada = estacionSeleccionada?.id === estacion.id;
                  const cargandoDetalle = loadingDetalle && !estaSeleccionada;
                  
                  // Autos de esta estación
                  const autosEstacion = vehiculos.filter(v => v.estacion === estacion.nombre);

                  return (
                    <article
                      id={`estacion-${estacion.id}`}
                      key={estacion.id}
                      onClick={() => handleSeleccionarEstacion(estacion.id)}
                      className={`cursor-pointer overflow-hidden rounded-[22px] border border-autospot-border bg-autospot-white shadow-[0_12px_30px_rgba(15,23,42,0.04)] transition hover:-translate-y-1 hover:shadow-[0_18px_40px_rgba(15,23,42,0.08)] ${soloVisualizacion ? 'opacity-90' : ''}`}
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
                            <Link 
                              to={`/estaciones/${estacion.id}`}
                              onClick={(e) => e.stopPropagation()}
                              className="font-display text-lg font-bold tracking-[-0.04em] text-autospot-black hover:text-autospot-accent hover:underline"
                            >
                              {estacion.nombre}
                            </Link>
                            <p className="mt-1 text-sm text-autospot-muted">
                              Zona: {estacion.zona}
                            </p>
                          </div>
                          <span className="inline-flex items-center rounded-full bg-[#f0fdf4] px-2.5 py-1 text-xs font-bold text-[#166534] border border-[#bbf7d0]">
                            Operativa
                          </span>
                        </div>

                        {/* Listado de Autos disponibles en la estación */}
                        <div className="mt-4 pt-4 border-t border-gray-100">
                          <p className="text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted mb-3">
                            Vehículos Disponibles ({autosEstacion.length})
                          </p>
                          
                          {autosEstacion.length === 0 ? (
                            <p className="text-sm text-autospot-muted italic">No hay autos disponibles para alquiler.</p>
                          ) : (
                            <div className="flex flex-col gap-2">
                              {autosEstacion.map(auto => (
                                <Link 
                                  key={auto.id}
                                  to={`/catalogo/${auto.id}`}
                                  onClick={(e) => e.stopPropagation()} // Para no disparar el click de la estación
                                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 transition border border-transparent hover:border-gray-200"
                                >
                                  <div className="w-12 h-12 rounded-md overflow-hidden bg-gray-100 shrink-0">
                                    {auto.fotos?.[0]?.url ? (
                                      <img src={auto.fotos[0].url} alt={auto.modelo} className="w-full h-full object-cover" />
                                    ) : (
                                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                                      </div>
                                    )}
                                  </div>
                                  <div>
                                    <p className="text-sm font-bold text-autospot-black leading-tight">
                                      {auto.marca} {auto.modelo} ({auto.anio})
                                    </p>
                                    <p className="text-xs text-autospot-accent font-semibold mt-1">
                                      ${auto.precio_por_dia} / día
                                    </p>
                                  </div>
                                </Link>
                              ))}
                            </div>
                          )}
                        </div>

                        {soloVisualizacion && (
                          <p className="mt-4 text-xs text-autospot-muted italic">
                            Tu documentación está pendiente — solo visualización
                          </p>
                        )}

                        {!soloVisualizacion && estaSeleccionada && (
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

                        {!soloVisualizacion && cargandoDetalle && (
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
          </div>
        )}
    </>
  );
};

export default EstacionesPage;