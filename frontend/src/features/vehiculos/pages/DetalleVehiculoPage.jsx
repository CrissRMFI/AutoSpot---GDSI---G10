import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import {
  agregarFotoAVehiculo,
  reemplazarFotoVehiculo,
  subirFotoVehiculo,
} from "../../../api/uploadService";
import {
  definirPrecioVehiculo,
  getDetalleVehiculo,
  toggleEstadoVehiculo,
} from "../api/vehiculoService";

const LADO_LABEL = {
  FRENTE: "Frente",
  TRASERA: "Trasera",
  LATERAL_IZQUIERDO: "Lateral izquierdo",
  LATERAL_DERECHO: "Lateral derecho",
  INTERIOR: "Interior",
  EXTRA: "Extra",
};

const DetalleVehiculoPage = () => {
  const { vehiculoId } = useParams();
  const { usuario } = useAuth();
  const esPropietario = (usuario?.rol || "").toUpperCase() === "PROPIETARIO";

  const fileInputRef = useRef(null);
  const fileInputReemplazoRef = useRef(null);

  const [vehiculo, setVehiculo] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [indiceActivo, setIndiceActivo] = useState(0);
  const [subiendoFoto, setSubiendoFoto] = useState(false);
  const [reemplazandoFotoId, setReemplazandoFotoId] = useState(null);
  const [feedback, setFeedback] = useState({ message: "", type: "" });

  const [editandoPrecio, setEditandoPrecio] = useState(false);
  const [inputPrecio, setInputPrecio] = useState("");
  const [guardandoPrecio, setGuardandoPrecio] = useState(false);
  const [togglingDisponible, setTogglingDisponible] = useState(false);

  const isDisponibilidadInactiva =
    vehiculo?.estado_registro === "EN_REVISION" ||
    vehiculo?.estado_registro === "RECHAZADO" ||
    vehiculo?.estado_registro === "PENDIENTE_DOCUMENTACION";
  const puedeCargarDocumentacion =
    vehiculo?.estado_registro === "PENDIENTE_DOCUMENTACION" ||
    vehiculo?.estado_registro === "RECHAZADO";

  const handleToggleDisponible = async () => {
    if (!vehiculo) return;
    setTogglingDisponible(true);
    try {
      const nuevoEstado = !vehiculo.disponible;
      await toggleEstadoVehiculo(vehiculo.id, nuevoEstado);
      setVehiculo((prev) =>
        prev ? { ...prev, disponible: nuevoEstado } : prev,
      );
      mostrarFeedback(
        `Vehículo marcado como ${nuevoEstado ? "Disponible" : "No Disponible"}.`,
        "success",
      );
    } catch (err) {
      mostrarFeedback(
        err.response?.data?.detail ||
          "No se pudo cambiar la disponibilidad del vehículo.",
        "error",
      );
    } finally {
      setTogglingDisponible(false);
    }
  };

  const handleActualizarPrecio = async () => {
    const precio = Number(inputPrecio);
    if (!precio || precio <= 0 || Number.isNaN(precio)) {
      mostrarFeedback("El precio debe ser mayor a cero.", "error");
      return;
    }
    setGuardandoPrecio(true);
    try {
      await definirPrecioVehiculo(vehiculo.id, precio);
      setVehiculo((prev) =>
        prev ? { ...prev, precio_por_dia: precio } : prev,
      );
      setEditandoPrecio(false);
      mostrarFeedback("Precio actualizado correctamente.", "success");
    } catch (err) {
      mostrarFeedback(
        err.response?.data?.detail || "No se pudo actualizar el precio.",
        "error",
      );
    } finally {
      setGuardandoPrecio(false);
    }
  };

  useEffect(() => {
    if (!vehiculoId) return;

    const cargarVehiculo = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await getDetalleVehiculo(vehiculoId);
        setVehiculo(data);
        setIndiceActivo(0);
      } catch (err) {
        if (err.response?.status === 403) {
          setError("No tenés permiso para ver este vehículo.");
        } else if (err.response?.status === 404) {
          setError("El vehículo no existe.");
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

  const mostrarFeedback = (message, type) => {
    setFeedback({ message, type });
    setTimeout(() => setFeedback({ message: "", type: "" }), 3500);
  };

  const handleSeleccionarFoto = () => {
    fileInputRef.current?.click();
  };

  const handleArchivoSeleccionado = async (evento) => {
    const archivo = evento.target.files?.[0];
    if (!archivo) return;

    setSubiendoFoto(true);

    try {
      const subida = await subirFotoVehiculo(archivo, "EXTRA");
      const fotoPersistida = await agregarFotoAVehiculo(vehiculoId, {
        lado: "EXTRA",
        url: subida.url,
        formato: subida.formato,
        tamanio_bytes: subida.tamanio_bytes,
      });

      setVehiculo((estadoActual) =>
        estadoActual
          ? { ...estadoActual, fotos: [...estadoActual.fotos, fotoPersistida] }
          : estadoActual,
      );
      setIndiceActivo(totalFotos);
      mostrarFeedback("Foto agregada al vehículo.", "success");
    } catch (err) {
      const detalle = err.response?.data?.detail;
      mostrarFeedback(
        typeof detalle === "string"
          ? `No se pudo agregar la foto: ${detalle}`
          : "No se pudo agregar la foto.",
        "error",
      );
    } finally {
      setSubiendoFoto(false);
      evento.target.value = "";
    }
  };

  const handleSeleccionarReemplazo = () => {
    if (!fotoActiva) return;
    fileInputReemplazoRef.current?.click();
  };

  const handleArchivoReemplazoSeleccionado = async (evento) => {
    const archivo = evento.target.files?.[0];
    if (!archivo || !fotoActiva) return;

    setReemplazandoFotoId(fotoActiva.id);

    try {
      const subida = await subirFotoVehiculo(archivo, fotoActiva.lado);
      const fotoActualizada = await reemplazarFotoVehiculo(
        vehiculoId,
        fotoActiva.id,
        {
          url: subida.url,
          formato: subida.formato,
          tamanio_bytes: subida.tamanio_bytes,
        },
      );

      setVehiculo((estadoActual) =>
        estadoActual
          ? {
              ...estadoActual,
              fotos: estadoActual.fotos.map((foto) =>
                foto.id === fotoActualizada.id ? fotoActualizada : foto,
              ),
            }
          : estadoActual,
      );
      mostrarFeedback("Foto reemplazada correctamente.", "success");
    } catch (err) {
      const detalle = err.response?.data?.detail;
      mostrarFeedback(
        typeof detalle === "string"
          ? `No se pudo reemplazar la foto: ${detalle}`
          : "No se pudo reemplazar la foto.",
        "error",
      );
    } finally {
      setReemplazandoFotoId(null);
      evento.target.value = "";
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
            to="/dashboard"
            className="mt-6 inline-flex rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
          >
            Volver al panel
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
            to="/dashboard"
            className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Volver al panel
          </Link>
        </div>
      </header>

      <div
        className={`fixed left-1/2 top-6 z-50 -translate-x-1/2 rounded-full px-5 py-3 text-sm font-bold shadow-[0_12px_40px_rgba(15,23,42,0.12)] transition-all duration-500 ${
          feedback.message
            ? "translate-y-0 opacity-100"
            : "-translate-y-6 opacity-0 pointer-events-none"
        } ${
          feedback.type === "success"
            ? "border border-[#bbf7d0] bg-[#f0fdf4] text-[#166534]"
            : "border border-red-200 bg-red-50 text-[#b42318]"
        }`}
      >
        {feedback.message}
      </div>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-8 sm:px-8 sm:py-10 lg:grid-cols-[1.2fr_0.8fr] lg:px-10 lg:py-12">
        <article className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
            Galería
          </p>

          <h1 className="font-display text-2xl font-black tracking-[-0.05em] text-autospot-black sm:text-3xl">
            {vehiculo.marca} {vehiculo.modelo}
          </h1>

          <p className="mt-1 text-sm text-autospot-muted">
            {vehiculo.anio} · {vehiculo.categoria}
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

          {esPropietario && (
            <>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                ref={fileInputRef}
                onChange={handleArchivoSeleccionado}
                className="hidden"
              />

              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                ref={fileInputReemplazoRef}
                onChange={handleArchivoReemplazoSeleccionado}
                className="hidden"
              />

              <div className="mt-6 flex flex-col gap-2">
                <button
                  type="button"
                  onClick={handleSeleccionarFoto}
                  disabled={subiendoFoto || reemplazandoFotoId !== null}
                  className="inline-flex flex-1 items-center justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] disabled:cursor-not-allowed disabled:opacity-65 sm:flex-none"
                >
                  {subiendoFoto ? "Subiendo foto..." : "Agregar foto"}
                </button>

                <button
                  type="button"
                  onClick={handleSeleccionarReemplazo}
                  disabled={
                    !fotoActiva || subiendoFoto || reemplazandoFotoId !== null
                  }
                  className="inline-flex flex-1 items-center justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent disabled:cursor-not-allowed disabled:opacity-65 sm:flex-none"
                >
                  {reemplazandoFotoId
                    ? "Reemplazando foto..."
                    : fotoActiva
                      ? `Cambiar foto (${LADO_LABEL[fotoActiva.lado] || fotoActiva.lado})`
                      : "Cambiar foto"}
                </button>
              </div>
            </>
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
            {esPropietario && (
              <DatoFicha
                label="Estado registro"
                valor={vehiculo.estado_registro}
              />
            )}
            <DatoFicha
              label="Precio por día"
              valor={
                vehiculo.precio_por_dia
                  ? `$${vehiculo.precio_por_dia}`
                  : "Sin definir"
              }
            />
            <DatoFicha
              label="Disponible"
              valor={vehiculo.disponible ? "Sí" : "No"}
            />
          </dl>

          {esPropietario && vehiculo.estado_registro === "RECHAZADO" &&
            vehiculo.motivo_rechazo && (
              <div className="mt-5 rounded-xl border border-[#fecaca] bg-[#fef2f2] p-3 text-xs text-[#b42318]">
                <p className="font-bold">Motivo de rechazo</p>
                <p className="mt-1 leading-5">{vehiculo.motivo_rechazo}</p>
              </div>
            )}

          {esPropietario && (
            <div className="mt-6 space-y-4">
              <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-4">
                <p className="text-[11px] font-bold uppercase tracking-[0.1em] !text-white/60">
                  Disponibilidad
                </p>
                <p className="mt-1 text-sm !text-white">
                  {vehiculo.disponible ? "Disponible para alquilar" : "No disponible"}
                </p>
                <button
                  type="button"
                  onClick={handleToggleDisponible}
                  disabled={togglingDisponible || isDisponibilidadInactiva}
                  title={
                    isDisponibilidadInactiva
                      ? "El vehículo debe estar Aprobado para definir disponibilidad"
                      : ""
                  }
                  className={`mt-3 inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-sm font-bold transition disabled:cursor-not-allowed disabled:opacity-50 ${
                    vehiculo.disponible
                      ? "bg-[#fef2f2] text-[#b42318] hover:bg-[#fee2e2]"
                      : "bg-[#f0fdf4] text-[#166534] hover:bg-[#dcfce7]"
                  }`}
                >
                  {togglingDisponible
                    ? "Cambiando..."
                    : vehiculo.disponible
                      ? "Marcar como No disponible"
                      : "Marcar como Disponible"}
                </button>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-4">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <p className="text-[11px] font-bold uppercase tracking-[0.1em] !text-white/60">
                    Ubicación Actual
                  </p>
                  {vehiculo.estacion && (
                    <p className="text-sm font-bold !text-white text-right">
                      {vehiculo.estacion}
                    </p>
                  )}
                </div>
                {vehiculo.estacion ? (
                  <div className="overflow-hidden rounded-xl border border-white/10">
                    <iframe
                      width="100%"
                      height="150"
                      style={{ border: 0 }}
                      loading="lazy"
                      allowFullScreen
                      referrerPolicy="no-referrer-when-downgrade"
                      src={`https://maps.google.com/maps?q=${encodeURIComponent(vehiculo.estacion)}&t=&z=14&ie=UTF8&iwloc=&output=embed`}
                      title={`Ubicación de ${vehiculo.estacion}`}
                    ></iframe>
                  </div>
                ) : (
                  <div className="mt-2 flex h-24 items-center justify-center rounded-xl bg-[#2a2a2a] border border-white/5">
                    <p className="text-sm font-bold text-white/60">
                      El auto está en alquiler
                    </p>
                  </div>
                )}
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-4">
                <p className="text-[11px] font-bold uppercase tracking-[0.1em] !text-white/60">
                  Precio por día
                </p>
                {editandoPrecio ? (
                  <div className="mt-2 flex flex-col gap-2">
                    <input
                      type="number"
                      min="1"
                      step="100"
                      autoFocus
                      value={inputPrecio}
                      onChange={(e) => setInputPrecio(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleActualizarPrecio();
                        if (e.key === "Escape") setEditandoPrecio(false);
                      }}
                      className="w-full min-w-0 rounded-lg bg-white px-2 py-1.5 text-sm font-bold text-autospot-black focus:outline-none focus:ring-2 focus:ring-autospot-accent"
                    />
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={handleActualizarPrecio}
                        disabled={guardandoPrecio}
                        className="flex-1 rounded-lg bg-autospot-accent px-2 py-1.5 text-xs font-bold !text-white transition hover:bg-[#5a1420] disabled:opacity-50"
                      >
                        {guardandoPrecio ? "Guardando..." : "✓ Guardar"}
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditandoPrecio(false)}
                        className="flex-1 rounded-lg border border-white/20 bg-white/[0.04] px-2 py-1.5 text-xs font-bold !text-white transition hover:bg-white/[0.1]"
                      >
                        ✕ Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="mt-1 flex items-center justify-between gap-2">
                    <p className="font-display text-xl font-bold !text-white">
                      {vehiculo.precio_por_dia
                        ? `$${vehiculo.precio_por_dia}`
                        : "Sin definir"}
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        setEditandoPrecio(true);
                        setInputPrecio(vehiculo.precio_por_dia || "");
                      }}
                      className="rounded-full border border-white/20 bg-white/[0.06] px-3 py-1 text-[11px] font-bold !text-white transition hover:bg-white/[0.12]"
                    >
                      Actualizar
                    </button>
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-2">
                <Link
                  to={`/modificar-datos/${vehiculo.id}`}
                  className="inline-flex w-full justify-center rounded-full border border-white/30 bg-white/[0.06] px-4 py-2.5 text-sm font-bold !text-white transition hover:bg-white/[0.12]"
                >
                  Modificar datos
                </Link>
                {puedeCargarDocumentacion ? (
                  <Link
                    to={`/vehiculos/${vehiculo.id}/documentacion`}
                    className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-4 py-2.5 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
                  >
                    Documentación
                  </Link>
                ) : (
                  <span className="inline-flex w-full justify-center rounded-full border border-white/15 bg-white/[0.04] px-4 py-2.5 text-center text-sm font-bold !text-white/55">
                    Documentación no editable
                  </span>
                )}
              </div>
            </div>
          )}
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

export default DetalleVehiculoPage;
