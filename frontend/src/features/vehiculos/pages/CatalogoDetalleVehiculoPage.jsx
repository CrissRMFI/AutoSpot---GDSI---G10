import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getDetalleVehiculoCatalogo, verificarDisponibilidad } from "../api/vehiculoService";

const LADO_LABEL = {
  FRENTE: "Frente",
  TRASERA: "Trasera",
  LATERAL_IZQUIERDO: "Lateral izquierdo",
  LATERAL_DERECHO: "Lateral derecho",
  INTERIOR: "Interior",
  EXTRA: "Extra",
};

const CatalogoDetalleVehiculoPage = () => {
  const { vehiculoId } = useParams();
  const [vehiculo, setVehiculo] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [indiceActivo, setIndiceActivo] = useState(0);

  const [fechaInicio, setFechaInicio] = useState("");
  const [horaInicio, setHoraInicio] = useState("10:00");
  const [fechaFin, setFechaFin] = useState("");
  const [horaFin, setHoraFin] = useState("10:00");
  const [errorAlquiler, setErrorAlquiler] = useState("");
  const [verificando, setVerificando] = useState(false);
  const [resultadoVerificacion, setResultadoVerificacion] = useState(null);

  useEffect(() => {
    if (!vehiculoId) return;

    const cargarVehiculo = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await getDetalleVehiculoCatalogo(vehiculoId);
        setVehiculo(data);
        setIndiceActivo(0);
      } catch (err) {
        if (err.response?.status === 403) {
          setError("No tenés permiso para ver el catálogo.");
        } else if (err.response?.status === 404) {
          setError("El vehículo no existe o no está disponible.");
        } else {
          setError("No se pudo cargar el vehículo.");
        }
      } finally {
        setCargando(false);
      }
    };

    cargarVehiculo();
  }, [vehiculoId]);

  const fotos = vehiculo?.fotos ?? [];
  const totalFotos = fotos.length;

  const irAnterior = () => {
    setIndiceActivo((prev) => (prev - 1 + totalFotos) % totalFotos);
  };

  const irSiguiente = () => {
    setIndiceActivo((prev) => (prev + 1) % totalFotos);
  };

  const handleChange = (setter) => (e) => {
    setter(e.target.value);
    setResultadoVerificacion(null);
    setErrorAlquiler("");
  };

  const getFullDate = (fecha, hora) => {
    if (!fecha || !hora) return null;
    return new Date(`${fecha}T${hora}`);
  };

  const calcularHoras = () => {
    const inicio = getFullDate(fechaInicio, horaInicio);
    const fin = getFullDate(fechaFin, horaFin);
    if (!inicio || !fin) return 0;
    return (fin - inicio) / (1000 * 60 * 60);
  };

  const isValidLocal = () => calcularHoras() >= 24;

  const handleVerificar = async () => {
    if (!isValidLocal()) {
      setErrorAlquiler("El tiempo mínimo de alquiler es de 1 día");
      return;
    }
    
    setVerificando(true);
    setErrorAlquiler("");
    try {
      const inicioIso = getFullDate(fechaInicio, horaInicio).toISOString();
      const finIso = getFullDate(fechaFin, horaFin).toISOString();
      const data = await verificarDisponibilidad(vehiculoId, inicioIso, finIso);
      setResultadoVerificacion(data);
    } catch (err) {
      setErrorAlquiler(err.response?.data?.detail || "Error al verificar disponibilidad.");
    } finally {
      setVerificando(false);
    }
  };

  if (cargando) {
    return (
      <main className="min-h-screen bg-autospot-cream text-autospot-black">
        <div className="mx-auto max-w-6xl px-5 py-12 sm:px-8 lg:px-10">
          <div className="animate-pulse rounded-[28px] bg-white p-8 shadow-[0_18px_50px_rgba(15,23,42,0.07)]">
            <div className="h-8 w-1/2 rounded bg-gray-200" />
            <div className="mt-4 h-4 w-1/3 rounded bg-gray-200" />
            <div className="mt-8 h-72 w-full rounded-2xl bg-gray-200" />
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-autospot-cream text-autospot-black">
        <div className="mx-auto max-w-3xl px-5 py-16 text-center sm:px-8">
          <h1 className="font-display text-2xl font-bold text-autospot-black sm:text-3xl">
            {error}
          </h1>
          <Link
            to="/catalogo"
            className="mt-6 inline-flex rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
          >
            Volver al catálogo
          </Link>
        </div>
      </main>
    );
  }

  if (!vehiculo) return null;

  const fotoActiva = fotos[indiceActivo];

  return (
    <main className="min-h-screen bg-autospot-cream text-autospot-black">
      <header className="sticky top-0 z-40 border-b border-autospot-border bg-autospot-cream/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
          <Link
            to="/"
            className="font-display text-xl font-black tracking-[-0.04em] !text-autospot-black"
          >
            Auto<span className="!text-autospot-accent">Spot</span>
          </Link>

          <Link
            to="/catalogo"
            className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Volver al catálogo
          </Link>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-8 sm:px-8 sm:py-10 lg:grid-cols-[1.2fr_0.8fr] lg:px-10 lg:py-12">
        <article className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
            Galería
          </p>

          <h1 className="font-display text-2xl font-black tracking-[-0.05em] text-autospot-black sm:text-3xl">
            {vehiculo.marca} {vehiculo.modelo}
          </h1>

          <p className="mt-1 text-sm text-autospot-muted">
            {vehiculo.anio} · {vehiculo.categoria} · {vehiculo.estacion || "Sin estación"}
          </p>

          <div className="relative mt-6 overflow-hidden rounded-2xl bg-[#0f0f0f]">
            {fotoActiva ? (
              <img
                src={fotoActiva.url}
                alt={`Vehículo ${LADO_LABEL[fotoActiva.lado] || fotoActiva.lado}`}
                className="aspect-video w-full object-cover sm:aspect-[16/10]"
              />
            ) : (
              <div className="flex aspect-video w-full items-center justify-center text-sm text-white/70">
                Sin fotos cargadas
              </div>
            )}

            {totalFotos > 1 && (
              <>
                <button
                  type="button"
                  onClick={irAnterior}
                  aria-label="Foto anterior"
                  className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 px-3 py-2 text-base font-bold text-autospot-black shadow transition hover:bg-white sm:left-5"
                >
                  ‹
                </button>
                <button
                  type="button"
                  onClick={irSiguiente}
                  aria-label="Foto siguiente"
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 px-3 py-2 text-base font-bold text-autospot-black shadow transition hover:bg-white sm:right-5"
                >
                  ›
                </button>
              </>
            )}

            {fotoActiva && (
              <span className="absolute bottom-3 left-3 rounded-full bg-black/70 px-3 py-1 text-xs font-bold text-white sm:bottom-5 sm:left-5">
                {LADO_LABEL[fotoActiva.lado] || fotoActiva.lado} ·{" "}
                {indiceActivo + 1}/{totalFotos}
              </span>
            )}
          </div>

          {totalFotos > 0 && (
            <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
              {fotos.map((foto, indice) => (
                <button
                  type="button"
                  key={foto.id}
                  onClick={() => setIndiceActivo(indice)}
                  aria-label={`Ver foto ${indice + 1}`}
                  className={`relative h-16 w-24 flex-shrink-0 overflow-hidden rounded-lg border-2 transition sm:h-20 sm:w-28 ${
                    indice === indiceActivo
                      ? "border-autospot-accent"
                      : "border-transparent opacity-70 hover:opacity-100"
                  }`}
                >
                  <img
                    src={foto.url}
                    alt={`Miniatura ${indice + 1}`}
                    className="h-full w-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </article>

        <aside className="rounded-[28px] bg-autospot-black p-6 text-autospot-white shadow-autospot-large sm:p-8">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.1em] !text-autospot-accent-2">
            Ficha técnica
          </p>

          <h2 className="font-display text-xl font-black leading-[1.1] tracking-[-0.04em] !text-autospot-white sm:text-2xl">
            Datos del vehículo
          </h2>

          <dl className="mt-6 space-y-4 text-sm">
            <DatoFicha label="Marca" valor={vehiculo.marca} />
            <DatoFicha label="Modelo" valor={vehiculo.modelo} />
            <DatoFicha label="Año" valor={vehiculo.anio} />
            <DatoFicha label="Categoría" valor={vehiculo.categoria} />
            <DatoFicha label="Transmisión" valor={vehiculo.tipo_transmision} />
            <DatoFicha label="Capacidad" valor={`${vehiculo.capacidad} pasajeros`} />
            <DatoFicha label="Combustible" valor={vehiculo.tipo_combustible} />
            <DatoFicha
              label="Acepta mascotas"
              valor={vehiculo.pets_friendly ? "Sí" : "No"}
            />
          </dl>

          <div className="mt-6 space-y-4">
            <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-4">
              <p className="text-[11px] font-bold uppercase tracking-[0.1em] !text-white/60">
                Precio por día
              </p>
              <div className="mt-1 flex items-center justify-between gap-2">
                <p className="font-display text-xl font-bold !text-white">
                  ${vehiculo.precio_por_dia}
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-[11px] font-bold uppercase tracking-[0.1em] !text-white/60">
                Fechas de alquiler
              </p>
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold !text-white/80">Inicio</label>
                <input
                  type="date"
                  value={fechaInicio}
                  onChange={handleChange(setFechaInicio)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white focus:border-autospot-accent focus:outline-none [color-scheme:dark]"
                />
                <input
                  type="time"
                  value={horaInicio}
                  onChange={handleChange(setHoraInicio)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white focus:border-autospot-accent focus:outline-none [color-scheme:dark]"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold !text-white/80">Fin</label>
                <input
                  type="date"
                  value={fechaFin}
                  onChange={handleChange(setFechaFin)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white focus:border-autospot-accent focus:outline-none [color-scheme:dark]"
                />
                <input
                  type="time"
                  value={horaFin}
                  onChange={handleChange(setHoraFin)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white focus:border-autospot-accent focus:outline-none [color-scheme:dark]"
                />
              </div>

              {fechaInicio && fechaFin && !isValidLocal() && (
                <div className="mt-1 rounded-xl bg-red-500/10 p-2 text-xs font-bold text-red-400 border border-red-500/20">
                  El tiempo mínimo de alquiler es de 1 día (24h).
                </div>
              )}

              {errorAlquiler && isValidLocal() && (
                <div className="mt-1 rounded-xl bg-red-500/10 p-2 text-xs font-bold text-red-400 border border-red-500/20">
                  {errorAlquiler}
                </div>
              )}

              {resultadoVerificacion && (
                <div className="mt-1 rounded-xl bg-green-500/10 p-3 text-sm font-bold text-green-400 border border-green-500/20">
                  ✓ Disponible por {resultadoVerificacion.dias} día(s) y {resultadoVerificacion.horas} hora(s).
                </div>
              )}
            </div>

            {!resultadoVerificacion ? (
              <button
                type="button"
                onClick={handleVerificar}
                disabled={verificando || !isValidLocal()}
                className={`mt-4 inline-flex w-full justify-center rounded-full px-4 py-3 text-sm font-bold transition ${
                  verificando || !isValidLocal()
                    ? "bg-autospot-accent/50 !text-white/50 cursor-not-allowed"
                    : "bg-autospot-accent !text-white hover:bg-[#5a1420]"
                }`}
              >
                {verificando ? (
                  <span className="flex items-center gap-2">
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Verificando...
                  </span>
                ) : (
                  "Verificar disponibilidad"
                )}
              </button>
            ) : (
              <button
                type="button"
                className="mt-4 inline-flex w-full justify-center rounded-full bg-autospot-accent px-4 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
              >
                Continuar con la reserva
              </button>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
};

const DatoFicha = ({ label, valor }) => (
  <div className="flex items-center justify-between gap-3">
    <dt className="!text-white/65">{label}</dt>
    <dd className="text-right font-bold !text-autospot-white">
      {valor || "—"}
    </dd>
  </div>
);

export default CatalogoDetalleVehiculoPage;
