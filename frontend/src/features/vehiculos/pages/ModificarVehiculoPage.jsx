import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import {
  definirPrecioVehiculo,
  actualizarVehiculo,
  subirFotoVehiculo,
  getDetalleVehiculo,
} from "../api/vehiculoService";

const CATALOGO = {
  Toyota: ["Corolla", "Hilux"],
  Ford: ["Fiesta", "Focus"],
  Volkswagen: ["Gol", "Vento", "Polo", "Amarok"],
  Chevrolet: ["Onix", "Cruze", "S10"],
  Renault: ["Sandero", "Logan", "Clio", "Kangoo"],
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

const ModificarVehiculoPage = () => {
  const navigate = useNavigate();
  const { vehiculoId } = useParams();
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
    patente: "",
    chasis: "",
    motor: "",
    titular: "",
    estacion: "",
    telefono: "",
  });

  const [originalData, setOriginalData] = useState({});
  const [estadoRegistro, setEstadoRegistro] = useState("");
  const [fotosSubiendo, setFotosSubiendo] = useState(new Set());
  const [feedback, setFeedback] = useState({ message: "", type: "" });
  const [cargando, setCargando] = useState(false);
  const [cargandoInicial, setCargandoInicial] = useState(true);

  const mostrarFeedback = (message, type) => {
    setFeedback({ message, type });
  };

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const datos = await getDetalleVehiculo(vehiculoId);
        setEstadoRegistro(datos.estado_registro || "");
        setOriginalData({
          patente: datos.patente || "",
          chasis: datos.chasis || "",
          motor: datos.motor || "",
        });
        setForm({
          marca: datos.marca || "",
          modelo: datos.modelo || "",
          anio: datos.anio?.toString() || "",
          tipo_transmision: datos.tipo_transmision || "",
          capacidad: datos.capacidad?.toString() || "",
          categoria: datos.categoria || "",
          tipo_combustible: datos.tipo_combustible || "",
          pets_friendly: datos.pets_friendly ? "true" : "false",
          precio_por_dia: datos.precio_por_dia?.toString() || "",
          fotos: datos.fotos || [],
          patente: datos.patente || "",
          chasis: datos.chasis || "",
          motor: datos.motor || "",
          titular: datos.titular || "",
          estacion: datos.estacion || "",
          telefono: datos.telefono || "",
        });
      } catch (error) {
        console.error("Error al cargar los datos del vehículo:", error);
        mostrarFeedback("Error al cargar los datos del vehículo.", "error");
      } finally {
        setCargandoInicial(false);
      }
    };
    if (vehiculoId) {
      cargarDatos();
    }
  }, [vehiculoId]);

  const actualizarCampo = (evento) => {
    const { name, value } = evento.target;

    setForm((estadoActual) => {
      const actualizado = { ...estadoActual, [name]: value };
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

    const camposFaltantes = [];
    if (!datosVehiculo.marca) camposFaltantes.push("Marca");
    if (!datosVehiculo.modelo) camposFaltantes.push("Modelo");
    if (!anioParsed) camposFaltantes.push("Año");
    if (!datosVehiculo.tipo_transmision) camposFaltantes.push("Transmisión");
    if (!capacidadParsed) camposFaltantes.push("Capacidad");
    if (!datosVehiculo.categoria) camposFaltantes.push("Categoría");
    if (!datosVehiculo.tipo_combustible) camposFaltantes.push("Combustible");

    if (camposFaltantes.length > 0) {
      mostrarFeedback(
        `Por favor completá los siguientes campos obligatorios: ${camposFaltantes.join(", ")}.`,
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
        "Debés tener las 4 fotos del vehículo: frente, trasera, lateral izquierdo y lateral derecho.",
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

    const docsChanged =
      datosVehiculo.patente !== originalData.patente ||
      datosVehiculo.chasis !== originalData.chasis ||
      datosVehiculo.motor !== originalData.motor;

    if (docsChanged && estadoRegistro !== "EN_REVISION") {
      mostrarFeedback(
        "Para modificar la patente, chasis o número de motor, debés contactar a un administrador.",
        "error"
      );
      return;
    }

    // Remapear id de fotos para la actualizacion, aunque backend solo necesita url, lado, etc.
    const fotosMapped = datosVehiculo.fotos.map(({ lado, url, formato, tamanio_bytes }) => ({
        lado,
        url,
        formato,
        tamanio_bytes
    }));

    const payload = {
      ...datosVehiculo,
      fotos: fotosMapped,
      anio: anioParsed,
      capacidad: capacidadParsed,
      pets_friendly: petsParsed,
    };

    setCargando(true);
    setFeedback({ message: "", type: "" });

    try {
      await actualizarVehiculo(vehiculoId, payload);
      await definirPrecioVehiculo(vehiculoId, precioParsed);

      mostrarFeedback(
        `Datos del vehículo actualizados exitosamente.`,
        "success",
      );

      setTimeout(() => {
        navigate("/propietario/dashboard", {
          state: {
            message: "Datos del vehículo actualizados correctamente.",
          },
        });
      }, 2000);
    } catch (error) {
      const detalle = error.response?.data?.detail;

      let mensajeError = detalle;

      if (Array.isArray(detalle)) {
        mensajeError = detalle
          .map((item) => {
            let msg = item.msg || "";
            // Quitar prefijo técnico de Pydantic
            if (msg.startsWith("Value error, ")) {
              msg = msg.replace("Value error, ", "");
            }
            // Correcciones ortográficas para la vista
            msg = msg.replace(/Anio/g, "Año").replace(/invalido/g, "inválido").replace(/tamanio/g, "tamaño");
            
            // Capitalizar la primera letra
            return msg.charAt(0).toUpperCase() + msg.slice(1);
          })
          .join(" | ");
      }

      mostrarFeedback(
        `Error al actualizar: ${mensajeError || error.message}`,
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

  if (cargandoInicial) {
    return (
      <main className="min-h-screen bg-autospot-cream text-autospot-black flex items-center justify-center">
        <p className="text-autospot-black font-bold">Cargando datos del vehículo...</p>
      </main>
    );
  }

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
            Edición
          </p>

          <h1 className="font-display text-3xl font-black leading-[1.05] tracking-[-0.06em] !text-autospot-white sm:text-4xl">
            Modificar vehículo
          </h1>

          <p className="mt-4 text-sm leading-7 !text-[#b8b8b8] sm:text-base">
            Actualizá las características de tu vehículo o cambiá sus fotos. La marca y el modelo no pueden modificarse.
          </p>
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
                  Editá la información de tu vehículo. Recordá que la marca y el modelo no se pueden cambiar.
                </p>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="marca" className={labelClassName}>
                    Marca <span className="text-red-500">*</span>
                  </label>

                  <select
                    id="marca"
                    name="marca"
                    className={inputClassName}
                    value={form.marca}
                    onChange={actualizarCampo}
                    disabled={true}
                  >
                    <option value="">Seleccioná una marca</option>
                    {Object.keys(CATALOGO).map((marca) => (
                      <option key={marca} value={marca}>
                        {marca}
                      </option>
                    ))}
                    {!CATALOGO[form.marca] && form.marca && (
                      <option value={form.marca}>{form.marca}</option>
                    )}
                  </select>
                </div>

                <div>
                  <label htmlFor="modelo" className={labelClassName}>
                    Modelo <span className="text-red-500">*</span>
                  </label>

                  <select
                    id="modelo"
                    name="modelo"
                    className={inputClassName}
                    value={form.modelo}
                    onChange={actualizarCampo}
                    disabled={true}
                  >
                    <option value="">Seleccioná un modelo</option>
                    {form.marca && CATALOGO[form.marca]
                      ? CATALOGO[form.marca].map((modelo) => (
                        <option key={modelo} value={modelo}>
                          {modelo}
                        </option>
                      ))
                      : null}
                    {(!CATALOGO[form.marca] || !CATALOGO[form.marca].includes(form.modelo)) && form.modelo && (
                      <option value={form.modelo}>{form.modelo}</option>
                    )}
                  </select>
                </div>

                <div>
                  <label htmlFor="anio" className={labelClassName}>
                    Año <span className="text-red-500">*</span>
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
                    Transmisión <span className="text-red-500">*</span>
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
                    Capacidad <span className="text-red-500">*</span>
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
                    Categoría <span className="text-red-500">*</span>
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
                    Combustible <span className="text-red-500">*</span>
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
                    Acepta mascotas <span className="text-red-500">*</span>
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
                    Precio por día <span className="text-red-500">*</span>
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
                  Documentación y Contacto
                </p>

                <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black sm:text-3xl">
                  Datos legales y operativos
                </h2>

                <p className="mt-2 text-sm leading-6 text-autospot-muted">
                  Actualizá los datos de tu vehículo. Si el auto no está en revisión, necesitarás contactar a un administrador para cambiar patente, chasis o motor.
                </p>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="patente" className={labelClassName}>
                    Patente
                  </label>
                  <input
                    id="patente"
                    name="patente"
                    className={inputClassName}
                    type="text"
                    placeholder="Ej. AB123CD"
                    value={form.patente}
                    onChange={actualizarCampo}
                  />
                </div>

                <div>
                  <label htmlFor="motor" className={labelClassName}>
                    Nro. de Motor
                  </label>
                  <input
                    id="motor"
                    name="motor"
                    className={inputClassName}
                    type="text"
                    placeholder="Ej. 123456789"
                    value={form.motor}
                    onChange={actualizarCampo}
                  />
                </div>

                <div>
                  <label htmlFor="chasis" className={labelClassName}>
                    Chasis
                  </label>
                  <input
                    id="chasis"
                    name="chasis"
                    className={inputClassName}
                    type="text"
                    placeholder="Ej. 987654321"
                    value={form.chasis}
                    onChange={actualizarCampo}
                  />
                </div>

                <div>
                  <label htmlFor="titular" className={labelClassName}>
                    Titular Registral
                  </label>
                  <input
                    id="titular"
                    name="titular"
                    className={inputClassName}
                    type="text"
                    placeholder="Ej. Juan Pérez"
                    value={form.titular}
                    onChange={actualizarCampo}
                  />
                </div>

                <div>
                  <label htmlFor="estacion" className={labelClassName}>
                    Estación
                  </label>
                  <input
                    id="estacion"
                    name="estacion"
                    className={inputClassName}
                    type="text"
                    placeholder="Ej. Sede Central"
                    value={form.estacion}
                    onChange={actualizarCampo}
                  />
                </div>

                <div>
                  <label htmlFor="telefono" className={labelClassName}>
                    Teléfono de Contacto
                  </label>
                  <input
                    id="telefono"
                    name="telefono"
                    className={inputClassName}
                    type="text"
                    placeholder="Ej. +54 9 11 1234-5678"
                    value={form.telefono}
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
                  Podés cambiar las fotos subiendo nuevos archivos (jpg, jpeg, png o webp, máx. 5 MB).
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
                {cargando ? "Guardando..." : "Aplicar cambios"}
              </button>
            </div>
          </form>
        </section>
      </section>

    </main>
  );
};

export default ModificarVehiculoPage;
