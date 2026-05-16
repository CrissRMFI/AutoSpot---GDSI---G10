import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import {
  definirPrecioVehiculo,
  publicarVehiculo,
  subirFotoVehiculo,
} from "../api/vehiculoService";

const CATALOGO = {
  Toyota: ["Corolla", "Hilux"],
  Ford: ["Fiesta", "Focus"],
  Volkswagen: ["Gol", "Vento"],
  Chevrolet: ["Onix", "Cruze"],
  Renault: ["Sandero", "Logan"],
  Fiat: ["Cronos", "Palio"],
  Peugeot: ["208", "308"],
};

const LADOS_REQUERIDOS = [
  { codigo: "FRENTE", label: "Frente" },
  { codigo: "TRASERA", label: "Trasera" },
  { codigo: "LATERAL_IZQUIERDO", label: "Lateral izquierdo" },
  { codigo: "LATERAL_DERECHO", label: "Lateral derecho" },
];

const inputClassName =
  "w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)] disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500";

const labelClassName = "mb-2 block text-sm font-bold text-autospot-black";

const PublicarVehiculoPage = () => {
  const navigate = useNavigate();
  const { usuario } = useAuth();

  const fileInputRefs = useRef({});

  const [form, setForm] = useState({
    marca: "",
    modelo: "",
    anio: "",
    tipo_transmision: "",
    capacidad: "",
    categoria: "",
    tipo_combustible: "",
    pets_friendly: "true",
    precio_por_dia: "",
    fotos: [],
  });

  const [fotosSubiendo, setFotosSubiendo] = useState(new Set());
  const [feedback, setFeedback] = useState({ message: "", type: "" });
  const [cargando, setCargando] = useState(false);

  const actualizarCampo = (evento) => {
    const { name, value } = evento.target;

    setForm((estadoActual) => {
      const actualizado = { ...estadoActual, [name]: value };

      if (name === "marca") {
        actualizado.modelo = "";
      }

      return actualizado;
    });
  };

  const handleSeleccionarArchivo = (lado) => {
    fileInputRefs.current[lado]?.click();
  };

  const handleArchivoSeleccionado = async (lado, evento) => {
    const archivo = evento.target.files?.[0];
    if (!archivo) return;

    setFotosSubiendo((prev) => new Set(prev).add(lado));
    setFeedback({ message: "", type: "" });

    try {
      const resultado = await subirFotoVehiculo(archivo, lado);

      setForm((estadoActual) => {
        const fotosSinLadoActual = estadoActual.fotos.filter(
          (foto) => foto.lado !== lado,
        );

        return {
          ...estadoActual,
          fotos: [
            ...fotosSinLadoActual,
            { lado, url: resultado.url, formato: resultado.formato, tamanio_bytes: resultado.tamanio_bytes },
          ],
        };
      });
    } catch (error) {
      const detalle = error.response?.data?.detail;
      mostrarFeedback(
        `Error al subir foto (${lado}): ${detalle || error.message}`,
        "error",
      );
    } finally {
      setFotosSubiendo((prev) => {
        const siguiente = new Set(prev);
        siguiente.delete(lado);
        return siguiente;
      });
      evento.target.value = "";
    }
  };

  const mostrarFeedback = (message, type) => {
    setFeedback({ message, type });
  };

  const validarFormulario = ({
    datosVehiculo,
    anioParsed,
    capacidadParsed,
    precioParsed,
  }) => {
    if (!usuario?.id) {
      mostrarFeedback("No se encontró el usuario autenticado.", "error");
      return false;
    }

    if (
      !datosVehiculo.marca ||
      !datosVehiculo.modelo ||
      !anioParsed ||
      !datosVehiculo.tipo_transmision ||
      !capacidadParsed ||
      !datosVehiculo.categoria ||
      !datosVehiculo.tipo_combustible
    ) {
      mostrarFeedback(
        "Por favor completá todos los campos obligatorios básicos.",
        "error",
      );
      return false;
    }

    if (precioParsed <= 0 || Number.isNaN(precioParsed)) {
      mostrarFeedback("El precio por día debe ser mayor a cero.", "error");
      return false;
    }

    if (datosVehiculo.fotos.length < 4) {
      mostrarFeedback(
        "Debés subir las 4 fotos del vehículo: frente, trasera, lateral izquierdo y lateral derecho.",
        "error",
      );
      return false;
    }

    const ladosCargados = new Set(datosVehiculo.fotos.map((foto) => foto.lado));
    const faltanLados = LADOS_REQUERIDOS.some(
      ({ codigo }) => !ladosCargados.has(codigo),
    );

    if (faltanLados) {
      mostrarFeedback(
        "Cada foto debe corresponder a un lado requerido del vehículo.",
        "error",
      );
      return false;
    }

    return true;
  };

  const enviarFormulario = async (evento) => {
    evento.preventDefault();

    const { precio_por_dia, ...datosVehiculo } = form;

    const anioParsed = parseInt(datosVehiculo.anio, 10);
    const capacidadParsed = parseInt(datosVehiculo.capacidad, 10);
    const petsParsed = datosVehiculo.pets_friendly === "true";
    const precioParsed = Number(precio_por_dia);

    const formularioValido = validarFormulario({
      datosVehiculo,
      anioParsed,
      capacidadParsed,
      precioParsed,
    });

    if (!formularioValido) {
      return;
    }

    const payload = {
      ...datosVehiculo,
      anio: anioParsed,
      capacidad: capacidadParsed,
      pets_friendly: petsParsed,
    };

    setCargando(true);
    setFeedback({ message: "", type: "" });

    try {
      const data = await publicarVehiculo(usuario.id, payload);

      await definirPrecioVehiculo(data.id, precioParsed);

      mostrarFeedback(
        `Vehículo registrado exitosamente con precio diario definido. ID: ${data.id}`,
        "success",
      );

      setTimeout(() => {
        navigate("/propietario/dashboard", {
          state: {
            message: "Vehículo publicado correctamente.",
          },
        });
      }, 2000);
    } catch (error) {
      const detalle = error.response?.data?.detail;

      let mensajeError = detalle;

      if (Array.isArray(detalle)) {
        mensajeError = detalle
          .map((item) => `${item.loc?.join(".")}: ${item.msg}`)
          .join(", ");
      }

      mostrarFeedback(
        `Error al registrar: ${mensajeError || error.message}`,
        "error",
      );
      setCargando(false);
    }
  };

  const isPhotoUploaded = (lado) => {
    return form.fotos.some((foto) => foto.lado === lado);
  };

  const obtenerNombreArchivo = (lado) => {
    const foto = form.fotos.find((item) => item.lado === lado);
    if (!foto) return "";
    const partes = foto.url.split("/");
    return partes[partes.length - 1] || "";
  };

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
            to="/propietario/dashboard"
            className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Volver al panel
          </Link>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-8 sm:px-8 sm:py-10 lg:grid-cols-[0.85fr_1.15fr] lg:px-10 lg:py-12">
        <aside className="rounded-[28px] bg-autospot-black p-6 text-autospot-white shadow-autospot-large sm:p-8 lg:sticky lg:top-28 lg:h-fit">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.1em] !text-autospot-accent-2">
            Publicación
          </p>

          <h1 className="font-display text-3xl font-black leading-[1.05] tracking-[-0.06em] !text-autospot-white sm:text-4xl">
            Publicar vehículo
          </h1>

          <p className="mt-4 text-sm leading-7 !text-[#b8b8b8] sm:text-base">
            Cargá las características principales, las fotos obligatorias y el
            precio diario para publicar tu vehículo en AutoSpot.
          </p>

          <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm font-bold !text-autospot-white">
              Estado inicial
            </p>

            <p className="mt-2 text-sm leading-6 !text-white/65">
              Luego del alta, el vehículo quedará pendiente de documentación
              para completar la validación.
            </p>
          </div>

          <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm font-bold !text-autospot-white">
              Fotos requeridas
            </p>

            <p className="mt-2 text-sm leading-6 !text-white/65">
              Frente, trasera, lateral izquierdo y lateral derecho.
            </p>
          </div>
        </aside>

        <section className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
          <form onSubmit={enviarFormulario} className="space-y-8">
            <section>
              <div className="mb-6">
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
                  Datos generales
                </p>

                <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black sm:text-3xl">
                  Características del auto
                </h2>

                <p className="mt-2 text-sm leading-6 text-autospot-muted">
                  Completá la información básica con valores válidos para el
                  catálogo.
                </p>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="marca" className={labelClassName}>
                    Marca *
                  </label>

                  <select
                    id="marca"
                    name="marca"
                    className={inputClassName}
                    value={form.marca}
                    onChange={actualizarCampo}
                  >
                    <option value="">Seleccioná una marca</option>
                    {Object.keys(CATALOGO).map((marca) => (
                      <option key={marca} value={marca}>
                        {marca}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="modelo" className={labelClassName}>
                    Modelo *
                  </label>

                  <select
                    id="modelo"
                    name="modelo"
                    className={inputClassName}
                    value={form.modelo}
                    onChange={actualizarCampo}
                    disabled={!form.marca}
                  >
                    <option value="">Seleccioná un modelo</option>
                    {form.marca
                      ? CATALOGO[form.marca].map((modelo) => (
                        <option key={modelo} value={modelo}>
                          {modelo}
                        </option>
                      ))
                      : null}
                  </select>
                </div>

                <div>
                  <label htmlFor="anio" className={labelClassName}>
                    Año *
                  </label>

                  <input
                    id="anio"
                    name="anio"
                    className={inputClassName}
                    type="number"
                    min="1990"
                    placeholder="Ej. 2023"
                    value={form.anio}
                    onChange={actualizarCampo}
                  />
                </div>

                <div>
                  <label htmlFor="tipo_transmision" className={labelClassName}>
                    Transmisión *
                  </label>

                  <select
                    id="tipo_transmision"
                    name="tipo_transmision"
                    className={inputClassName}
                    value={form.tipo_transmision}
                    onChange={actualizarCampo}
                  >
                    <option value="">Seleccioná</option>
                    <option value="MANUAL">Manual</option>
                    <option value="AUTOMATICA">Automática</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="capacidad" className={labelClassName}>
                    Capacidad *
                  </label>

                  <input
                    id="capacidad"
                    name="capacidad"
                    className={inputClassName}
                    type="number"
                    min="1"
                    placeholder="Ej. 5"
                    value={form.capacidad}
                    onChange={actualizarCampo}
                  />
                </div>

                <div>
                  <label htmlFor="categoria" className={labelClassName}>
                    Categoría *
                  </label>

                  <select
                    id="categoria"
                    name="categoria"
                    className={inputClassName}
                    value={form.categoria}
                    onChange={actualizarCampo}
                  >
                    <option value="">Seleccioná</option>
                    <option value="SEDAN">Sedán</option>
                    <option value="SUV">SUV</option>
                    <option value="HATCHBACK">Hatchback</option>
                    <option value="PICKUP">Pickup</option>
                    <option value="COUPE">Coupé</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="tipo_combustible" className={labelClassName}>
                    Combustible *
                  </label>

                  <select
                    id="tipo_combustible"
                    name="tipo_combustible"
                    className={inputClassName}
                    value={form.tipo_combustible}
                    onChange={actualizarCampo}
                  >
                    <option value="">Seleccioná</option>
                    <option value="NAFTA">Nafta</option>
                    <option value="DIESEL">Diesel</option>
                    <option value="ELECTRICO">Eléctrico</option>
                    <option value="HIBRIDO">Híbrido</option>
                    <option value="GNC">GNC</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="pets_friendly" className={labelClassName}>
                    Acepta mascotas *
                  </label>

                  <select
                    id="pets_friendly"
                    name="pets_friendly"
                    className={inputClassName}
                    value={form.pets_friendly}
                    onChange={actualizarCampo}
                  >
                    <option value="true">Sí</option>
                    <option value="false">No</option>
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label htmlFor="precio_por_dia" className={labelClassName}>
                    Precio por día *
                  </label>

                  <input
                    id="precio_por_dia"
                    name="precio_por_dia"
                    className={inputClassName}
                    type="number"
                    min="1"
                    step="0.01"
                    placeholder="Ej. 35000"
                    value={form.precio_por_dia}
                    onChange={actualizarCampo}
                  />
                </div>
              </div>
            </section>

            <section>
              <div className="mb-6">
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
                  Fotos
                </p>

                <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black">
                  Fotos del vehículo
                </h2>

                <p className="mt-2 text-sm leading-6 text-autospot-muted">
                  Subí una foto real por cada lado requerido (jpg, jpeg, png o webp, máx. 5 MB).
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                {LADOS_REQUERIDOS.map(({ codigo, label }) => {
                  const cargada = isPhotoUploaded(codigo);
                  const subiendo = fotosSubiendo.has(codigo);

                  return (
                    <article
                      key={codigo}
                      className={`rounded-2xl border p-4 transition ${cargada
                          ? "border-[#bbf7d0] bg-[#f0fdf4]"
                          : "border-autospot-border bg-white"
                        }`}
                    >
                      <input
                        ref={(el) => { fileInputRefs.current[codigo] = el; }}
                        type="file"
                        accept=".jpg,.jpeg,.png,.webp"
                        className="hidden"
                        onChange={(e) => handleArchivoSeleccionado(codigo, e)}
                      />

                      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <p className="text-sm font-bold text-autospot-black">
                            {label}
                          </p>

                          <p
                            className={`mt-1 text-xs leading-5 ${subiendo
                                ? "text-autospot-muted"
                                : cargada
                                  ? "text-[#166534]"
                                  : "text-autospot-muted"
                              }`}
                          >
                            {subiendo
                              ? "Subiendo..."
                              : cargada
                                ? obtenerNombreArchivo(codigo)
                                : "Foto pendiente"}
                          </p>
                        </div>

                        <button
                          type="button"
                          disabled={subiendo}
                          className={`inline-flex justify-center rounded-full px-4 py-2 text-sm font-bold transition disabled:cursor-not-allowed disabled:opacity-60 ${cargada
                              ? "border border-[#bbf7d0] bg-white !text-[#166534] hover:border-[#16a34a]"
                              : "bg-autospot-accent !text-white hover:bg-[#5a1420]"
                            }`}
                          onClick={() => handleSeleccionarArchivo(codigo)}
                        >
                          {subiendo ? "Subiendo..." : cargada ? "Cambiar" : "Subir"}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            {feedback.message && (
              <div
                className={`rounded-xl px-4 py-3 text-sm font-bold ${feedback.type === "success"
                    ? "bg-[#e7f8ed] text-[#166534]"
                    : "bg-red-50 text-[#b42318]"
                  }`}
              >
                {feedback.message}
              </div>
            )}

            <div className="flex flex-col gap-3 border-t border-autospot-border pt-6 sm:flex-row sm:items-center sm:justify-between">
              <Link
                to="/propietario/dashboard"
                className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
              >
                Cancelar
              </Link>

              <button
                type="submit"
                disabled={cargando}
                className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] disabled:cursor-not-allowed disabled:opacity-65"
              >
                {cargando ? "Publicando..." : "Publicar vehículo"}
              </button>
            </div>
          </form>
        </section>
      </section>

    </main>
  );
};

export default PublicarVehiculoPage;
