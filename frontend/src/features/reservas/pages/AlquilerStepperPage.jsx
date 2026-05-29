import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Stepper from "@mui/material/Stepper";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import { obtenerDocumentacionHabilitante } from "../../usuarios/api/documentacionHabilitanteService";
import {
  getDetalleVehiculoCatalogo,
  verificarDisponibilidad,
} from "../../vehiculos/api/vehiculoService";
import { crearReservaConCodigo } from "../api/reservasService";
import { formatearFechaHora, formatearMonto } from "../utils/reservaFormatters";

const PASOS_ALQUILER = [
  { label: "Fechas", historia: "US 3C" },
  { label: "Pago", historia: "US 13C" },
  { label: "Código", historia: "US 14C" },
];

const inputClass =
  "w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm font-semibold text-autospot-black focus:border-autospot-accent focus:outline-none";

const AlquilerStepperPage = () => {
  const { vehiculoId } = useParams();
  const { usuario } = useAuth();
  const esDesktop = useMediaQuery("(min-width: 768px)");

  const [vehiculo, setVehiculo] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [errorCarga, setErrorCarga] = useState("");
  const [estaHabilitado, setEstaHabilitado] = useState(false);
  const [pasoActivo, setPasoActivo] = useState(0);
  const [fechaInicio, setFechaInicio] = useState("");
  const [horaInicio, setHoraInicio] = useState("10:00");
  const [fechaFin, setFechaFin] = useState("");
  const [horaFin, setHoraFin] = useState("10:00");
  const [resultadoVerificacion, setResultadoVerificacion] = useState(null);
  const [reservaConfirmada, setReservaConfirmada] = useState(null);
  const [errorAlquiler, setErrorAlquiler] = useState("");
  const [verificando, setVerificando] = useState(false);
  const [reservando, setReservando] = useState(false);

  useEffect(() => {
    if (!vehiculoId) return;

    const cargarVehiculo = async () => {
      setCargando(true);
      setErrorCarga("");

      try {
        const data = await getDetalleVehiculoCatalogo(vehiculoId);
        setVehiculo(data);
      } catch (err) {
        if (err.response?.status === 404) {
          setErrorCarga("El vehículo no existe o no está disponible.");
        } else {
          setErrorCarga("No se pudo cargar el vehículo.");
        }
      } finally {
        setCargando(false);
      }
    };

    cargarVehiculo();
  }, [vehiculoId]);

  useEffect(() => {
    if (!usuario?.id) return;

    obtenerDocumentacionHabilitante(usuario.id)
      .then((data) => {
        setEstaHabilitado(data?.estado_validacion === "APROBADO");
      })
      .catch(() => setEstaHabilitado(false));
  }, [usuario?.id]);

  const inicio = obtenerFechaCompleta(fechaInicio, horaInicio);
  const fin = obtenerFechaCompleta(fechaFin, horaFin);
  const horasAlquiler = inicio && fin ? (fin - inicio) / (1000 * 60 * 60) : 0;
  const fechasValidas = horasAlquiler >= 24;
  const montoEstimado = calcularMontoEstimado(
    vehiculo?.precio_por_dia,
    resultadoVerificacion?.dias,
    resultadoVerificacion?.horas,
  );

  const limpiarVerificacion = () => {
    setResultadoVerificacion(null);
    setReservaConfirmada(null);
    setErrorAlquiler("");
    setPasoActivo(0);
  };

  const handleVerificar = async () => {
    if (!estaHabilitado) {
      setErrorAlquiler("Para alquilar necesitás tener tu documentación aprobada.");
      return;
    }

    if (!fechasValidas) {
      setErrorAlquiler("El tiempo mínimo de alquiler es de 1 día.");
      return;
    }

    setVerificando(true);
    setErrorAlquiler("");

    try {
      const data = await verificarDisponibilidad(
        vehiculo.id,
        inicio.toISOString(),
        fin.toISOString(),
      );
      setResultadoVerificacion(data);
      setPasoActivo(1);
    } catch (err) {
      setErrorAlquiler(
        err.response?.data?.detail || "No se pudo verificar la disponibilidad.",
      );
    } finally {
      setVerificando(false);
    }
  };

  const handleConfirmarReserva = async () => {
    if (!resultadoVerificacion) {
      setPasoActivo(0);
      setErrorAlquiler("Primero verificá las fechas de alquiler.");
      return;
    }

    setReservando(true);
    setErrorAlquiler("");

    try {
      const data = await crearReservaConCodigo({
        vehiculoId: vehiculo.id,
        fechaInicio: inicio.toISOString(),
        fechaFin: fin.toISOString(),
      });

      setReservaConfirmada(data);
      setPasoActivo(2);
    } catch (err) {
      setErrorAlquiler(
        err.response?.data?.detail || "No se pudo confirmar la reserva.",
      );
    } finally {
      setReservando(false);
    }
  };

  if (cargando) {
    return (
      <div className="w-full min-w-0 px-5 py-12 sm:px-8 lg:px-10">
        <div className="h-96 animate-pulse rounded-[28px] border border-autospot-border bg-white/70" />
      </div>
    );
  }

  if (errorCarga || !vehiculo) {
    return (
      <div className="mx-auto w-full max-w-3xl px-5 py-16 text-center sm:px-8">
        <h1 className="font-display text-2xl font-black text-autospot-black">
          {errorCarga || "No se pudo cargar el alquiler."}
        </h1>
        <Link
          to="/catalogo"
          className="mt-6 inline-flex rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
        >
          Volver al catálogo
        </Link>
      </div>
    );
  }

  const tituloVehiculo = `${vehiculo.marca} ${vehiculo.modelo}`;

  return (
    <section className="w-full min-w-0 px-5 py-6 sm:px-8 lg:px-10">
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <Link
            to={`/catalogo/${vehiculo.id}`}
            className="mb-3 inline-flex items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Volver al auto
          </Link>
          <p className="text-xs font-bold uppercase text-autospot-accent">
            Alquiler
          </p>
          <h1 className="mt-1 font-display text-3xl font-black text-autospot-black sm:text-4xl">
            {tituloVehiculo}
          </h1>
        </div>
        <div className="rounded-2xl border border-autospot-border bg-transparent px-4 py-3 text-sm">
          <p className="font-bold text-autospot-muted">Precio por día</p>
          <p className="font-display text-xl font-black text-autospot-black">
            {formatearMonto(vehiculo.precio_por_dia)}
          </p>
        </div>
      </div>

      <div className="w-full rounded-[28px] border border-transparent bg-transparent p-0">
        <Stepper
          activeStep={pasoActivo}
          orientation={esDesktop ? "horizontal" : "vertical"}
          sx={{
            "& .MuiStepLabel-label": {
              fontFamily: "inherit",
              fontSize: "0.82rem",
              fontWeight: 800,
            },
            "& .MuiStepIcon-root.Mui-active": { color: "#6f1d2b" },
            "& .MuiStepIcon-root.Mui-completed": { color: "#1f7a4d" },
          }}
        >
          {PASOS_ALQUILER.map((paso) => (
            <Step key={paso.label}>
              <StepLabel>
                <span className="block">{paso.label}</span>
                <span className="block text-[11px] font-bold text-autospot-muted">
                  {paso.historia}
                </span>
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        <div className="mt-8">
          {pasoActivo === 0 && (
            <PasoFechas
              fechaInicio={fechaInicio}
              fechaFin={fechaFin}
              horaInicio={horaInicio}
              horaFin={horaFin}
              fechasValidas={fechasValidas}
              verificando={verificando}
              error={errorAlquiler}
              requiereDocumentacion={!estaHabilitado}
              onFechaInicioChange={(valor) => {
                setFechaInicio(valor);
                limpiarVerificacion();
              }}
              onHoraInicioChange={(valor) => {
                setHoraInicio(valor);
                limpiarVerificacion();
              }}
              onFechaFinChange={(valor) => {
                setFechaFin(valor);
                limpiarVerificacion();
              }}
              onHoraFinChange={(valor) => {
                setHoraFin(valor);
                limpiarVerificacion();
              }}
              onVerificar={handleVerificar}
            />
          )}

          {pasoActivo === 1 && (
            <PasoPago
              resultadoVerificacion={resultadoVerificacion}
              inicio={inicio}
              fin={fin}
              montoEstimado={montoEstimado}
              onBack={() => setPasoActivo(0)}
              onPagar={handleConfirmarReserva}
              pagando={reservando}
              error={errorAlquiler}
            />
          )}

          {pasoActivo === 2 && (
            <PasoCodigo
              reserva={reservaConfirmada}
            />
          )}
        </div>
      </div>
    </section>
  );
};

const PasoFechas = ({
  fechaInicio,
  fechaFin,
  horaInicio,
  horaFin,
  fechasValidas,
  verificando,
  error,
  requiereDocumentacion,
  onFechaInicioChange,
  onFechaFinChange,
  onHoraInicioChange,
  onHoraFinChange,
  onVerificar,
}) => (
  <div>
    <h2 className="font-display text-xl font-black text-autospot-black">
      Seleccionar fechas de alquiler
    </h2>
    <div className="mt-4 grid gap-4 md:grid-cols-2">
      <FechaHoraField
        label="Inicio"
        fecha={fechaInicio}
        hora={horaInicio}
        onFechaChange={onFechaInicioChange}
        onHoraChange={onHoraInicioChange}
      />
      <FechaHoraField
        label="Fin"
        fecha={fechaFin}
        hora={horaFin}
        onFechaChange={onFechaFinChange}
        onHoraChange={onHoraFinChange}
      />
    </div>

    {requiereDocumentacion && (
      <EstadoMensaje tipo="info">
        Necesitás documentación aprobada para avanzar.{" "}
        <Link className="font-black text-autospot-accent" to="/documentacion-habilitante">
          Cargar documentación
        </Link>
      </EstadoMensaje>
    )}
    {fechaInicio && fechaFin && !fechasValidas && (
      <EstadoMensaje tipo="error">
        El tiempo mínimo de alquiler es de 1 día.
      </EstadoMensaje>
    )}
    {error && <EstadoMensaje tipo="error">{error}</EstadoMensaje>}

    <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
      <button
        type="button"
        onClick={onVerificar}
        disabled={verificando || !fechasValidas}
        className={`inline-flex justify-center rounded-full px-5 py-3 text-sm font-bold transition ${
          verificando || !fechasValidas
            ? "cursor-not-allowed bg-autospot-accent/45 text-white/60"
            : "bg-autospot-accent text-white hover:bg-[#5a1420]"
        }`}
      >
        {verificando ? "Verificando..." : "Verificar disponibilidad"}
      </button>
    </div>
  </div>
);

const PasoPago = ({
  resultadoVerificacion,
  inicio,
  fin,
  montoEstimado,
  onBack,
  onPagar,
  pagando,
  error,
}) => (
  <div>
    <h2 className="font-display text-xl font-black text-autospot-black">
      Pago
    </h2>
    <p className="mt-2 text-sm font-semibold text-autospot-muted">
      Próximo a implementar: US 13C Alquiler de auto.
    </p>
    <ResumenReserva
      inicio={inicio}
      fin={fin}
      resultadoVerificacion={resultadoVerificacion}
      montoEstimado={montoEstimado}
    />

    {error && <EstadoMensaje tipo="error">{error}</EstadoMensaje>}

    <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
      <button
        type="button"
        onClick={onBack}
        className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
      >
        Volver
      </button>
      <button
        type="button"
        onClick={onPagar}
        disabled={pagando}
        className={`inline-flex justify-center rounded-full px-5 py-3 text-sm font-bold transition ${
          pagando
            ? "cursor-not-allowed bg-autospot-accent/45 text-white/60"
            : "bg-autospot-accent text-white hover:bg-[#5a1420]"
        }`}
      >
        {pagando ? "Procesando..." : "Pagar"}
      </button>
    </div>
  </div>
);

const PasoCodigo = ({ reserva }) => (
  <div>
    <h2 className="font-display text-xl font-black text-autospot-black">
      Código de reserva
    </h2>
    {reserva ? (
      <div className="mt-4 rounded-2xl border border-green-200 bg-green-50 p-5 text-center">
        <p className="text-xs font-bold uppercase text-green-700">
          Reserva confirmada
        </p>
        <p className="mt-2 break-all font-display text-4xl font-black text-autospot-black sm:text-5xl">
          {reserva.codigo_reserva}
        </p>
      </div>
    ) : (
      <EstadoMensaje tipo="error">La reserva todavía no fue confirmada.</EstadoMensaje>
    )}

    <div className="mt-4 rounded-2xl border border-autospot-border bg-white p-4">
      <p className="text-[11px] font-bold uppercase text-autospot-accent">
        Mis reservas
      </p>
      <p className="mt-2 text-sm font-semibold text-autospot-muted">
        Este código también queda disponible en la pantalla Mis reservas.
      </p>
      <Link
        to="/usuario/reservas"
        className="mt-4 inline-flex rounded-full border border-autospot-border bg-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
      >
        Ver mis reservas
      </Link>
    </div>

    <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
      <Link
        to="/catalogo"
        className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
      >
        Volver al catálogo
      </Link>
      <Link
        to="/usuario/reservas"
        className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
      >
        Ir a mis reservas
      </Link>
    </div>
  </div>
);

const FechaHoraField = ({ label, fecha, hora, onFechaChange, onHoraChange }) => (
  <div className="rounded-2xl border border-autospot-border bg-white p-4">
    <label className="text-xs font-bold uppercase text-autospot-muted">
      {label}
    </label>
    <div className="mt-3 grid gap-3 sm:grid-cols-2">
      <input
        type="date"
        value={fecha}
        onChange={(event) => onFechaChange(event.target.value)}
        className={inputClass}
      />
      <input
        type="time"
        value={hora}
        onChange={(event) => onHoraChange(event.target.value)}
        className={inputClass}
      />
    </div>
  </div>
);

const ResumenReserva = ({
  inicio,
  fin,
  resultadoVerificacion,
  montoEstimado,
}) => (
  <div className="mt-4 rounded-2xl border border-autospot-border bg-autospot-cream/40 p-4">
    <DatoResumen label="Inicio" valor={formatearFechaHora(inicio)} />
    <DatoResumen label="Fin" valor={formatearFechaHora(fin)} />
    <DatoResumen
      label="Duración"
      valor={
        resultadoVerificacion
          ? `${resultadoVerificacion.dias} día(s) y ${resultadoVerificacion.horas} hora(s)`
          : "—"
      }
    />
    <DatoResumen label="Total estimado" valor={formatearMonto(montoEstimado)} />
  </div>
);

const DatoResumen = ({ label, valor }) => (
  <div className="flex items-center justify-between gap-3 border-b border-autospot-border/70 py-2 text-sm first:pt-0 last:border-b-0 last:pb-0">
    <dt className="text-autospot-muted">{label}</dt>
    <dd className="text-right font-bold text-autospot-black">{valor || "—"}</dd>
  </div>
);

const EstadoMensaje = ({ tipo, children }) => {
  const styles =
    tipo === "error"
      ? "border-red-200 bg-red-50 text-red-700"
      : "border-autospot-border bg-autospot-cream/50 text-autospot-muted";

  return (
    <div className={`mt-4 rounded-2xl border p-3 text-sm font-bold ${styles}`}>
      {children}
    </div>
  );
};

const obtenerFechaCompleta = (fecha, hora) => {
  if (!fecha || !hora) return null;
  return new Date(`${fecha}T${hora}`);
};

const calcularMontoEstimado = (precioPorDia, dias = 0, horas = 0) => {
  const precio = Number(precioPorDia);
  if (!Number.isFinite(precio)) return 0;

  return precio * (Number(dias) + Number(horas) / 24);
};

export default AlquilerStepperPage;
