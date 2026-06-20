import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEstacionesActivas } from "../api/estacionesApi";
import {
  obtenerCatalogoVehiculos,
  listarVehiculosDelPropietario,
} from "../../vehiculos/api/vehiculoService";
import { useAuth } from "../../auth/hooks/useAuth";
import MapaEstacionModal from "../components/MapaEstacionModal";

const PLACEHOLDER_ESTACION =
  "data:image/svg+xml;charset=UTF-8," +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="220" viewBox="0 0 400 220"><rect width="400" height="220" fill="#f0ebe2"/><g fill="none" stroke="#c4bdb2" stroke-width="3"><path d="M120 150v-44l80-40 80 40v44"/><path d="M104 150h192"/><path d="M150 150v-34h40v34M210 150v-34h40v34"/></g><text x="200" y="194" fill="#a79f93" font-family="sans-serif" font-size="14" text-anchor="middle">Estación AutoSpot</text></svg>`,
  );

const PLACEHOLDER_AUTO =
  "data:image/svg+xml;charset=UTF-8," +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="90" viewBox="0 0 120 90"><rect width="120" height="90" fill="#f0ebe2"/><g fill="none" stroke="#b9b2a8" stroke-width="2"><path d="M24 58l8-20a5 5 0 014.6-3h36.8a5 5 0 014.6 3l8 20"/><path d="M18 58h84v10a3 3 0 01-3 3h-9a3 3 0 01-3-3v-3H33v3a3 3 0 01-3 3h-9a3 3 0 01-3-3z"/><circle cx="36" cy="63" r="5"/><circle cx="84" cy="63" r="5"/></g></svg>`,
  );

// Etiqueta y destino del clic en un auto según el rol.
const ACCION_POR_ROL = {
  ADMIN: { label: "Ver alquileres", ruta: (id) => `/admin/autos/${id}/alquileres` },
  PROPIETARIO: { label: "Ver ganancias", ruta: (id) => `/vehiculos/${id}/ganancias` },
  CLIENTE: { label: "Ver ficha", ruta: (id) => `/catalogo/${id}` },
};

const fotoDeAuto = (auto) => {
  const fotos = auto?.fotos ?? [];
  return (
    fotos.find((f) => f.lado === "FRENTE")?.url || fotos[0]?.url || PLACEHOLDER_AUTO
  );
};

const EstacionesPage = () => {
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const rol = (usuario?.rol || "CLIENTE").toUpperCase();
  const esPropietario = rol === "PROPIETARIO";

  const [estaciones, setEstaciones] = useState([]);
  const [vehiculos, setVehiculos] = useState([]);
  const [estacionSeleccionada, setEstacionSeleccionada] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [mostrarMapa, setMostrarMapa] = useState(false);
  const [ubicacionUsuario, setUbicacionUsuario] = useState(null);

  // Ubicación del usuario (para el mapa "Cómo llegar").
  useEffect(() => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        setUbicacionUsuario({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        }),
      (err) => console.warn("Ubicación no disponible:", err?.message),
    );
  }, []);

  // Carga de estaciones y vehículos (la fuente de autos depende del rol).
  useEffect(() => {
    if (!usuario) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const fuenteVehiculos =
          esPropietario && usuario?.id
            ? listarVehiculosDelPropietario(usuario.id)
            : obtenerCatalogoVehiculos();

        const [estacionesData, vehiculosData] = await Promise.all([
          getEstacionesActivas(),
          fuenteVehiculos,
        ]);

        setEstaciones(
          [...estacionesData].sort((a, b) => a.nombre.localeCompare(b.nombre)),
        );
        setVehiculos(Array.isArray(vehiculosData) ? vehiculosData : []);
      } catch (err) {
        console.error(err);
        setError("No se pudieron cargar las estaciones. Intentá nuevamente.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario?.id, esPropietario]);

  const autosDeEstacion = (estacion) =>
    vehiculos.filter((v) => v.estacion === estacion.nombre);

  const estacionesFiltradas = useMemo(() => {
    const q = busqueda.trim().toLowerCase();
    if (!q) return estaciones;
    return estaciones.filter(
      (e) =>
        e.nombre.toLowerCase().includes(q) ||
        (e.zona || "").toLowerCase().includes(q),
    );
  }, [estaciones, busqueda]);

  const handleVerDetalle = (estacion) => {
    setEstacionSeleccionada(estacion);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleClickAuto = (auto) => {
    const accion = ACCION_POR_ROL[rol] || ACCION_POR_ROL.CLIENTE;
    navigate(accion.ruta(auto.id));
  };

  const accionRol = ACCION_POR_ROL[rol] || ACCION_POR_ROL.CLIENTE;

  // ───────────────────────── Loading / error ─────────────────────────
  if (loading) {
    return (
      <div className="flex w-full justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent" />
      </div>
    );
  }

  // ───────────────────────── Vista detalle ─────────────────────────
  if (estacionSeleccionada) {
    const autos = autosDeEstacion(estacionSeleccionada);
    return (
      <div className="w-full">
        <button
          onClick={() => setEstacionSeleccionada(null)}
          className="mb-5 inline-flex items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Volver a estaciones
        </button>

        {/* Encabezado de la estación */}
        <div className="overflow-hidden rounded-3xl border border-autospot-border bg-white shadow-sm">
          <div className="relative h-48 w-full sm:h-60">
            <img
              src={estacionSeleccionada.imagen_url || PLACEHOLDER_ESTACION}
              onError={(e) => {
                e.currentTarget.src = PLACEHOLDER_ESTACION;
              }}
              alt={estacionSeleccionada.nombre}
              className="h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/10 to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 flex flex-col gap-3 p-5 sm:flex-row sm:items-end sm:justify-between sm:p-6">
              <div className="min-w-0">
                <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-white/80">
                  {estacionSeleccionada.zona}
                </p>
                <h1 className="font-display text-3xl font-black tracking-[-0.04em] text-white sm:text-4xl">
                  {estacionSeleccionada.nombre}
                </h1>
                <p className="mt-1 text-sm font-semibold text-white/85">
                  {autos.length} {autos.length === 1 ? "vehículo" : "vehículos"}
                  {esPropietario ? " tuyos" : " disponibles"}
                </p>
              </div>
              <button
                onClick={() => setMostrarMapa(true)}
                className="inline-flex shrink-0 items-center justify-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-bold text-autospot-black shadow-lg transition hover:bg-autospot-cream"
              >
                <svg className="h-4 w-4 text-autospot-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                Ver Mapa
              </button>
            </div>
          </div>

          {/* Lista de autos */}
          <div className="p-5 sm:p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-lg font-bold text-autospot-black">
                {esPropietario ? "Tus vehículos en esta estación" : "Vehículos disponibles"}
              </h2>
              <span className="rounded-full bg-autospot-cream px-2.5 py-1 text-xs font-bold text-autospot-accent border border-autospot-border">
                {autos.length}
              </span>
            </div>

            {autos.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-autospot-border bg-autospot-cream/30 px-5 py-12 text-center">
                <p className="text-sm font-bold text-autospot-muted">
                  {esPropietario
                    ? "No tenés vehículos en esta estación."
                    : "No hay vehículos disponibles en esta estación por ahora."}
                </p>
              </div>
            ) : (
              <ul className="flex flex-col gap-3">
                {autos.map((auto) => (
                  <li key={auto.id}>
                    <button
                      onClick={() => handleClickAuto(auto)}
                      className="group flex w-full items-center gap-4 rounded-2xl border border-autospot-border bg-white p-3 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-autospot-accent hover:shadow-md sm:p-4"
                    >
                      <img
                        src={fotoDeAuto(auto)}
                        onError={(e) => {
                          e.currentTarget.src = PLACEHOLDER_AUTO;
                        }}
                        alt={`${auto.marca} ${auto.modelo}`}
                        className="h-20 w-28 shrink-0 rounded-xl object-cover sm:h-24 sm:w-36"
                      />
                      <div className="min-w-0 flex-1">
                        <h3 className="truncate font-display text-base font-bold text-autospot-black sm:text-lg">
                          {auto.marca} {auto.modelo}
                        </h3>
                        <p className="mt-0.5 text-sm text-autospot-muted">
                          {auto.anio}
                          {auto.categoria ? ` · ${auto.categoria}` : ""}
                        </p>
                        <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1">
                          {auto.precio_por_dia != null && (
                            <span className="text-sm font-bold text-autospot-accent">
                              ${auto.precio_por_dia} / día
                            </span>
                          )}
                          {auto.patente && (
                            <span className="rounded-md bg-autospot-cream px-1.5 py-0.5 text-xs font-bold text-autospot-muted">
                              {auto.patente}
                            </span>
                          )}
                        </div>
                      </div>
                      <span className="hidden shrink-0 items-center gap-1.5 rounded-full border border-autospot-border px-3.5 py-2 text-xs font-bold text-autospot-black transition group-hover:border-autospot-accent group-hover:text-autospot-accent sm:inline-flex">
                        {accionRol.label}
                        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </span>
                      <svg className="h-5 w-5 shrink-0 text-autospot-muted transition group-hover:text-autospot-accent sm:hidden" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {mostrarMapa && (
          <MapaEstacionModal
            estacion={estacionSeleccionada}
            ubicacionUsuario={ubicacionUsuario}
            onClose={() => setMostrarMapa(false)}
          />
        )}
      </div>
    );
  }

  // ───────────────────────── Vista principal (grilla de cards) ─────────────────────────
  return (
    <div className="w-full">
      <div className="mb-7">
        <p className="mb-2 text-xs font-bold uppercase tracking-[0.12em] text-autospot-accent">
          Red Logística
        </p>
        <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
          Estaciones Habilitadas
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-autospot-muted sm:text-base">
          {esPropietario
            ? "Encontrá tus vehículos por estación y accedé a sus ganancias."
            : rol === "ADMIN"
            ? "Explorá las estaciones y consultá los alquileres de cada vehículo."
            : "Explorá las estaciones de la Ciudad de Buenos Aires y mirá los vehículos disponibles en cada una."}
        </p>
      </div>

      {/* Buscador */}
      <div className="relative mb-6 max-w-md">
        <svg className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-autospot-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z" />
        </svg>
        <input
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          placeholder="Buscar estación o zona…"
          className="w-full rounded-xl border border-autospot-border bg-white py-2.5 pl-10 pr-3 text-sm font-medium text-autospot-black placeholder:text-autospot-muted focus:border-autospot-accent focus:outline-none"
        />
      </div>

      {error && (
        <div className="mb-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
          {error}
        </div>
      )}

      {estacionesFiltradas.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-autospot-border bg-white/70 px-5 py-16 text-center">
          <p className="text-sm font-bold text-autospot-muted">
            No se encontraron estaciones{busqueda ? ` para "${busqueda}"` : ""}.
          </p>
        </div>
      ) : (
        <div className="grid w-full grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {estacionesFiltradas.map((estacion) => {
            const cantidad = autosDeEstacion(estacion).length;
            return (
              <article
                key={estacion.id}
                className="flex flex-col overflow-hidden rounded-3xl border border-autospot-border bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-[0_18px_40px_rgba(15,23,42,0.08)]"
              >
                <div className="relative h-40 w-full">
                  <img
                    src={estacion.imagen_url || PLACEHOLDER_ESTACION}
                    onError={(e) => {
                      e.currentTarget.src = PLACEHOLDER_ESTACION;
                    }}
                    alt={estacion.nombre}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                  <span className="absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full bg-white/95 px-2.5 py-1 text-[11px] font-bold text-[#166534] shadow-sm">
                    <span className="h-1.5 w-1.5 rounded-full bg-[#16a34a]" /> Operativa
                  </span>
                </div>

                <div className="flex flex-1 flex-col p-5">
                  <h2 className="font-display text-lg font-bold tracking-[-0.03em] text-autospot-black">
                    {estacion.nombre}
                  </h2>
                  <p className="mt-0.5 text-sm text-autospot-muted">Zona · {estacion.zona}</p>

                  <div className="mt-4 flex items-center gap-2 text-sm">
                    <span className="inline-flex h-7 min-w-7 items-center justify-center rounded-full bg-autospot-cream px-2 text-xs font-black text-autospot-accent border border-autospot-border">
                      {cantidad}
                    </span>
                    <span className="font-semibold text-autospot-black">
                      {cantidad === 1 ? "vehículo" : "vehículos"}
                      {esPropietario ? " tuyos" : " disponibles"}
                    </span>
                  </div>

                  <button
                    onClick={() => handleVerDetalle(estacion)}
                    className="mt-5 inline-flex items-center gap-1.5 self-start text-sm font-bold text-autospot-accent transition hover:gap-2.5 hover:text-autospot-accent-dark"
                  >
                    Ver detalles
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default EstacionesPage;
