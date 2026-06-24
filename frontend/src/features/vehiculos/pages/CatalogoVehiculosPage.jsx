import { useEffect, useState, useMemo } from "react";
import { createPortal } from "react-dom";
import { Link } from "react-router-dom";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import InputAdornment from "@mui/material/InputAdornment";
import StarRoundedIcon from "@mui/icons-material/StarRounded";
import { obtenerCatalogoVehiculos } from "./../api/vehiculoService";
import PuntuacionVehiculo from "../components/PuntuacionVehiculo";

const obtenerFotoFrente = (vehiculo) => {
  const fotos = vehiculo?.fotos ?? [];
  return fotos.find((foto) => foto.lado === "FRENTE")?.url || fotos[0]?.url || "";
};

// US 8C — Opciones del filtro por puntuación (calificación promedio mínima).
const OPCIONES_PUNTUACION = [
  { value: "4.5", label: "4,5 o más" },
  { value: "4", label: "4 o más" },
  { value: "3", label: "3 o más" },
  { value: "2", label: "2 o más" },
  { value: "1", label: "1 o más" },
];

// Estilo compartido para los selects MUI de la barra de filtros (bordes
// redondeados acordes al diseño del catálogo).
const sxFiltroSelect = {
  minWidth: { xs: "100%", sm: 210 },
  "& .MuiOutlinedInput-root": {
    borderRadius: "9999px",
    backgroundColor: "#fff",
    fontWeight: 700,
    fontSize: "0.875rem",
  },
};

const FILTROS_INICIALES = {
  estacion: "",
  marca: "",
  categoria: "",
  transmision: "",
  tipo_combustible: "",
  anioMin: "",
  anioMax: "",
  capacidad: "",
  pets_friendly: "",
  puntuacion: "",
};

const CatalogoVehiculosPage = () => {
  const [vehiculosOriginales, setVehiculosOriginales] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [noAutorizado, setNoAutorizado] = useState(false);

  const [filtros, setFiltros] = useState(FILTROS_INICIALES);
  const [modalAbierto, setModalAbierto] = useState(false);

  // Estados temporales para el modal
  const [filtrosTemp, setFiltrosTemp] = useState(FILTROS_INICIALES);

  // US 8C: el filtro por puntuación se resuelve en el backend, por lo que se
  // recarga el catálogo cada vez que cambia. El resto de filtros se aplican
  // sobre el resultado en el cliente (CA 2 — intersección de condiciones).
  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      setError("");
      setNoAutorizado(false);
      try {
        const data = await obtenerCatalogoVehiculos(filtros.puntuacion);
        setVehiculosOriginales(data);
      } catch (err) {
        if (err.response?.status === 403) {
          setNoAutorizado(true);
        } else {
          setError("No se pudo cargar el catálogo de vehículos.");
        }
      } finally {
        setCargando(false);
      }
    };

    cargar();
  }, [filtros.puntuacion]);

  const opciones = useMemo(() => {
    const opts = {
      estaciones: new Set(),
      marcas: new Set(),
      categorias: new Set(),
      transmisiones: new Set(),
      combustibles: new Set(),
      capacidades: new Set(),
    };
    vehiculosOriginales.forEach((v) => {
      if (v.estacion) opts.estaciones.add(v.estacion);
      if (v.marca) opts.marcas.add(v.marca);
      if (v.categoria) opts.categorias.add(v.categoria);
      if (v.tipo_transmision) opts.transmisiones.add(v.tipo_transmision);
      if (v.tipo_combustible) opts.combustibles.add(v.tipo_combustible);
      if (v.capacidad) opts.capacidades.add(v.capacidad.toString());
    });
    return {
      estaciones: Array.from(opts.estaciones).sort(),
      marcas: Array.from(opts.marcas).sort(),
      categorias: Array.from(opts.categorias).sort(),
      transmisiones: Array.from(opts.transmisiones).sort(),
      combustibles: Array.from(opts.combustibles).sort(),
      capacidades: Array.from(opts.capacidades).sort((a, b) => Number(a) - Number(b)),
    };
  }, [vehiculosOriginales]);

  const vehiculosFiltrados = useMemo(() => {
    return vehiculosOriginales.filter((v) => {
      if (filtros.estacion && v.estacion !== filtros.estacion) return false;
      if (filtros.marca && v.marca !== filtros.marca) return false;
      if (filtros.categoria && v.categoria !== filtros.categoria) return false;
      if (filtros.transmision && v.tipo_transmision !== filtros.transmision) return false;
      if (filtros.tipo_combustible && v.tipo_combustible !== filtros.tipo_combustible) return false;
      if (filtros.capacidad && v.capacidad.toString() !== filtros.capacidad) return false;
      
      if (filtros.anioMin && v.anio < Number(filtros.anioMin)) return false;
      if (filtros.anioMax && v.anio > Number(filtros.anioMax)) return false;

      if (filtros.pets_friendly) {
        const wantsPets = filtros.pets_friendly === "si";
        if (v.pets_friendly !== wantsPets) return false;
      }
      return true;
    });
  }, [vehiculosOriginales, filtros]);

  const hayFiltrosActivos = Object.values(filtros).some((val) => val !== "");

  const handleLimpiarFiltros = () => {
    setFiltros(FILTROS_INICIALES);
    setFiltrosTemp(FILTROS_INICIALES);
  };

  const abrirModal = () => {
    setFiltrosTemp(filtros);
    setModalAbierto(true);
  };

  const aplicarFiltrosModal = () => {
    setFiltros(filtrosTemp);
    setModalAbierto(false);
  };

  if (noAutorizado) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center px-5 text-center">
        <div className="mb-6 rounded-full bg-red-50 p-4">
          <svg className="h-12 w-12 text-[#b42318]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black">
          Acceso denegado
        </h2>
        <p className="mt-3 max-w-md text-sm leading-6 text-autospot-muted">
          Tu documentación aún no está aprobada. Tenés que cargar o actualizar tu
          licencia de conducir y esperar a que sea validada para poder explorar
          los vehículos disponibles.
        </p>
        <Link
          to="/dashboard"
          className="mt-6 inline-flex justify-center rounded-full bg-autospot-accent px-6 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
        >
          Volver al panel
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Catálogo
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black break-words sm:text-4xl">
            Vehículos disponibles
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-autospot-muted">
            Explorá nuestra red y encontrá el vehículo ideal para tu próximo viaje.
          </p>
        </div>
      </div>

      {!cargando && !error && vehiculosOriginales.length > 0 && (
        <div className="mb-6 flex flex-wrap items-center gap-4 rounded-2xl border border-autospot-border bg-white p-4 shadow-[0_4px_20px_rgba(15,23,42,0.04)]">
          <TextField
            select
            size="small"
            label="Estación"
            value={filtros.estacion}
            onChange={(e) => setFiltros({ ...filtros, estacion: e.target.value })}
            sx={sxFiltroSelect}
          >
            <MenuItem value="">Todas las estaciones</MenuItem>
            {opciones.estaciones.map((est) => (
              <MenuItem key={est} value={est}>{est}</MenuItem>
            ))}
          </TextField>

          <TextField
            select
            size="small"
            label="Puntuación"
            value={filtros.puntuacion}
            onChange={(e) => setFiltros({ ...filtros, puntuacion: e.target.value })}
            sx={sxFiltroSelect}
            InputProps={{
              startAdornment: filtros.puntuacion ? (
                <InputAdornment position="start">
                  <StarRoundedIcon sx={{ color: "#f59e0b" }} fontSize="small" />
                </InputAdornment>
              ) : null,
            }}
          >
            <MenuItem value="">Todas las puntuaciones</MenuItem>
            {OPCIONES_PUNTUACION.map((op) => (
              <MenuItem key={op.value} value={op.value}>
                <span className="inline-flex items-center gap-1.5">
                  <StarRoundedIcon sx={{ color: "#f59e0b" }} fontSize="small" />
                  {op.label}
                </span>
              </MenuItem>
            ))}
          </TextField>

          <button
            onClick={abrirModal}
            className="inline-flex flex-1 sm:flex-none items-center justify-center gap-2 rounded-full border border-autospot-border bg-autospot-cream px-4 py-2.5 text-sm font-bold text-autospot-black transition hover:bg-gray-100"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            Búsqueda avanzada
          </button>

          {hayFiltrosActivos && (
            <button
              onClick={handleLimpiarFiltros}
              className="inline-flex flex-1 sm:flex-none items-center justify-center gap-2 rounded-full border border-red-200 bg-red-50 px-4 py-2.5 text-sm font-bold text-[#b42318] transition hover:bg-red-100"
            >
              ✕ Limpiar filtros
            </button>
          )}
        </div>
      )}

      {cargando && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((s) => (
            <div key={s} className="animate-pulse rounded-2xl border border-autospot-border bg-white p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
              <div className="mb-4 h-40 w-full rounded-xl bg-gray-200" />
              <div className="mb-2 h-5 w-2/3 rounded bg-gray-200" />
              <div className="mb-4 h-4 w-1/2 rounded bg-gray-200" />
              <div className="h-8 w-full rounded-full bg-gray-200" />
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
          {error}
        </div>
      )}

      {!cargando && !error && vehiculosOriginales.length === 0 && !hayFiltrosActivos && (
        <div className="rounded-2xl border border-dashed border-autospot-border bg-white/70 px-5 py-10 text-center">
          <h3 className="font-display text-lg font-bold tracking-[-0.04em] text-autospot-black">
            No hay vehículos disponibles
          </h3>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-autospot-muted">
            Por el momento no tenemos vehículos habilitados para alquilar.
            ¡Volvé a consultar más tarde!
          </p>
        </div>
      )}

      {!cargando && !error && hayFiltrosActivos && vehiculosFiltrados.length === 0 && (
        <div className="rounded-2xl border border-dashed border-autospot-border bg-white/70 px-5 py-10 text-center">
          <h3 className="font-display text-lg font-bold tracking-[-0.04em] text-autospot-black">
            Tu búsqueda no arrojó resultados
          </h3>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-autospot-muted">
            No encontramos ningún vehículo que cumpla con todos los filtros que seleccionaste. Intentá relajar las opciones.
          </p>
          <button
            onClick={handleLimpiarFiltros}
            className="mt-6 inline-flex justify-center rounded-full bg-autospot-accent px-6 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
          >
            Limpiar filtros
          </button>
        </div>
      )}

      {!cargando && !error && vehiculosFiltrados.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {vehiculosFiltrados.map((vehiculo) => {
            const fotoUrl = obtenerFotoFrente(vehiculo);

            return (
              <Link
                to={`/catalogo/${vehiculo.id}`}
                key={vehiculo.id}
                className="group block overflow-hidden rounded-2xl border border-autospot-border bg-white shadow-[0_12px_30px_rgba(15,23,42,0.06)] transition hover:-translate-y-0.5 hover:border-autospot-accent hover:shadow-[0_18px_40px_rgba(15,23,42,0.1)]"
              >
                <div className="relative aspect-video w-full overflow-hidden bg-[#0f0f0f]">
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
                  <span className="absolute left-3 top-3 rounded-full bg-[#f0fdf4] px-2.5 py-1 text-[11px] font-bold text-[#166534] border border-[#bbf7d0]">
                    Disponible
                  </span>
                </div>

                <div className="p-5">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-display text-lg font-bold tracking-[-0.04em] !text-autospot-black break-words">
                      {vehiculo.marca} {vehiculo.modelo}
                    </h3>
                    <PuntuacionVehiculo valor={vehiculo.calificacion_promedio} />
                  </div>
                  <p className="mt-1 text-sm text-autospot-muted">
                    {vehiculo.anio} · {vehiculo.categoria} · {vehiculo.estacion || "Sin estación"}
                  </p>

                  <div className="mt-4 flex items-baseline justify-between gap-2">
                    <div>
                      <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                        Precio diario
                      </p>
                      <p className="font-display text-xl font-bold text-autospot-black">
                        ${vehiculo.precio_por_dia}
                      </p>
                    </div>
                  </div>

                  <div className="mt-5 inline-flex w-full justify-center rounded-full bg-autospot-accent px-4 py-2.5 text-sm font-bold !text-white transition group-hover:bg-[#5a1420]">
                    Ver detalle
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {/* Modal Búsqueda Avanzada */}
      {modalAbierto && createPortal(
        <div className="fixed inset-0 z-[2000] flex items-center justify-center overflow-y-auto bg-black/60 p-4 backdrop-blur-sm">
          <div className="max-h-[calc(100vh-2rem)] w-full max-w-lg overflow-y-auto rounded-[28px] bg-white p-6 shadow-2xl sm:p-8">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="font-display text-2xl font-black tracking-[-0.04em] text-autospot-black">
                Búsqueda avanzada
              </h2>
              <button
                onClick={() => setModalAbierto(false)}
                className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-autospot-muted transition hover:bg-gray-200 hover:text-autospot-black"
              >
                ✕
              </button>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                  Marca
                </label>
                <select
                  value={filtrosTemp.marca}
                  onChange={(e) => setFiltrosTemp({ ...filtrosTemp, marca: e.target.value })}
                  className="w-full rounded-lg border border-autospot-border bg-white px-3 py-2.5 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent"
                >
                  <option value="">Cualquiera</option>
                  {opciones.marcas.map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                  Categoría
                </label>
                <select
                  value={filtrosTemp.categoria}
                  onChange={(e) => setFiltrosTemp({ ...filtrosTemp, categoria: e.target.value })}
                  className="w-full rounded-lg border border-autospot-border bg-white px-3 py-2.5 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent"
                >
                  <option value="">Cualquiera</option>
                  {opciones.categorias.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                  Transmisión
                </label>
                <select
                  value={filtrosTemp.transmision}
                  onChange={(e) => setFiltrosTemp({ ...filtrosTemp, transmision: e.target.value })}
                  className="w-full rounded-lg border border-autospot-border bg-white px-3 py-2.5 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent"
                >
                  <option value="">Cualquiera</option>
                  {opciones.transmisiones.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                  Combustible
                </label>
                <select
                  value={filtrosTemp.tipo_combustible}
                  onChange={(e) => setFiltrosTemp({ ...filtrosTemp, tipo_combustible: e.target.value })}
                  className="w-full rounded-lg border border-autospot-border bg-white px-3 py-2.5 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent"
                >
                  <option value="">Cualquiera</option>
                  {opciones.combustibles.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                  Capacidad
                </label>
                <select
                  value={filtrosTemp.capacidad}
                  onChange={(e) => setFiltrosTemp({ ...filtrosTemp, capacidad: e.target.value })}
                  className="w-full rounded-lg border border-autospot-border bg-white px-3 py-2.5 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent"
                >
                  <option value="">Cualquiera</option>
                  {opciones.capacidades.map((c) => <option key={c} value={c}>{c} pasajeros</option>)}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                  Mascotas
                </label>
                <select
                  value={filtrosTemp.pets_friendly}
                  onChange={(e) => setFiltrosTemp({ ...filtrosTemp, pets_friendly: e.target.value })}
                  className="w-full rounded-lg border border-autospot-border bg-white px-3 py-2.5 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent"
                >
                  <option value="">Cualquiera</option>
                  <option value="si">Pet friendly</option>
                  <option value="no">No se aceptan</option>
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="mb-1 block text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                  Año de fabricación
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    placeholder="Desde"
                    value={filtrosTemp.anioMin}
                    onChange={(e) => setFiltrosTemp({ ...filtrosTemp, anioMin: e.target.value })}
                    className="w-full rounded-lg border border-autospot-border bg-white px-3 py-2.5 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent"
                  />
                  <input
                    type="number"
                    placeholder="Hasta"
                    value={filtrosTemp.anioMax}
                    onChange={(e) => setFiltrosTemp({ ...filtrosTemp, anioMax: e.target.value })}
                    className="w-full rounded-lg border border-autospot-border bg-white px-3 py-2.5 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent"
                  />
                </div>
              </div>
            </div>

            <div className="mt-8 flex gap-3">
              <button
                onClick={() => setModalAbierto(false)}
                className="flex-1 rounded-full border border-autospot-border bg-white px-4 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
              >
                Cancelar
              </button>
              <button
                onClick={aplicarFiltrosModal}
                className="flex-1 rounded-full bg-autospot-accent px-4 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
              >
                Aplicar filtros
              </button>
            </div>
          </div>
        </div>,
        document.body,
      )}
    </>
  );
};

export default CatalogoVehiculosPage;
