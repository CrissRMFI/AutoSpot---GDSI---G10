import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Stepper from "@mui/material/Stepper";
import useMediaQuery from "@mui/material/useMediaQuery";
import {
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import { obtenerDocumentacionHabilitante } from "../../usuarios/api/documentacionHabilitanteService";
import { obtenerDatosPersonales } from "../../usuarios/api/usuarioService";
import {
  getDetalleVehiculoCatalogo,
  verificarDisponibilidad,
} from "../../vehiculos/api/vehiculoService";
import { crearReservaConCodigo } from "../api/reservasService";
import { formatearFechaHora, formatearMonto } from "../utils/reservaFormatters";

const PASOS_ALQUILER = [
  { label: "Devolución" },
  { label: "Pago" },
  { label: "Código" },
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
  const [revisandoRequisitos, setRevisandoRequisitos] = useState(false);
  const [bloqueoRequisito, setBloqueoRequisito] = useState(null);
  const [pasoActivo, setPasoActivo] = useState(0);
  const [fechaFin, setFechaFin] = useState("");
  const [horaFin, setHoraFin] = useState("10:00");
  const [inicioEstimado, setInicioEstimado] = useState(null);
  const [resultadoVerificacion, setResultadoVerificacion] = useState(null);
  const [reservaConfirmada, setReservaConfirmada] = useState(null);
  const [errorAlquiler, setErrorAlquiler] = useState("");
  const [verificando, setVerificando] = useState(false);
  const [reservando, setReservando] = useState(false);
  const [advertenciaPagoAbierta, setAdvertenciaPagoAbierta] = useState(false);
  const [modalErrorAbierto, setModalErrorAbierto] = useState(false);

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

    let cancelado = false;

    const revisarRequisitos = async () => {
      setRevisandoRequisitos(true);
      setBloqueoRequisito(null);

      try {
        await obtenerDatosPersonales(usuario.id);
      } catch {
        if (!cancelado) {
          setBloqueoRequisito({
            titulo: "Completá tus datos personales",
            mensaje:
              "Para iniciar un alquiler necesitamos tener registrados tus datos personales.",
            accion: "Cargar datos personales",
            to: "/datos-personales",
          });
          setEstaHabilitado(false);
          setRevisandoRequisitos(false);
        }
        return;
      }

      try {
        const data = await obtenerDocumentacionHabilitante(usuario.id);
        const aprobada = data?.estado_validacion === "APROBADO";
        if (!cancelado) {
          setEstaHabilitado(aprobada);
          if (!aprobada) {
            setBloqueoRequisito({
              titulo: "Documentación pendiente",
              mensaje:
                "Para alquilar un vehículo, tu documentación habilitante debe estar aprobada.",
              accion: "Ver documentación",
              to: "/documentacion-habilitante",
            });
          }
        }
      } catch {
        if (!cancelado) {
          setEstaHabilitado(false);
          setBloqueoRequisito({
            titulo: "Cargá tu documentación habilitante",
            mensaje:
              "Antes de alquilar necesitamos validar tu documentación habilitante.",
            accion: "Cargar documentación",
            to: "/documentacion-habilitante",
          });
        }
      } finally {
        if (!cancelado) setRevisandoRequisitos(false);
      }
    };

    revisarRequisitos();

    return () => {
      cancelado = true;
    };
  }, [usuario?.id]);

  const fin = obtenerFechaCompleta(fechaFin, horaFin);
  const horasAlquiler = fin ? (fin - new Date()) / (1000 * 60 * 60) : 0;
  const fechasValidas = Boolean(fin) && horasAlquiler >= 24;
  const montoEstimado = calcularMontoEstimado(
    vehiculo?.precio_por_dia,
    resultadoVerificacion?.dias,
    resultadoVerificacion?.horas,
  );

  const limpiarVerificacion = () => {
    setResultadoVerificacion(null);
    setReservaConfirmada(null);
    setInicioEstimado(null);
    setErrorAlquiler("");
    setPasoActivo(0);
  };

  const handleVerificar = async () => {
    if (!estaHabilitado) {
      setErrorAlquiler(
        "Para alquilar necesitás tener tu documentación aprobada.",
      );
      return;
    }

    if (!fechasValidas) {
      setErrorAlquiler("El tiempo mínimo de alquiler es de 1 día.");
      return;
    }

    setVerificando(true);
    setErrorAlquiler("");

    try {
      const inicioActual = new Date();
      const data = await verificarDisponibilidad(
        vehiculo.id,
        inicioActual.toISOString(),
        fin.toISOString(),
      );
      setInicioEstimado(inicioActual);
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
        fechaFin: fin.toISOString(),
      });

      setAdvertenciaPagoAbierta(false);
      setInicioEstimado(new Date(data.fecha_inicio));
      setReservaConfirmada(data);
      setPasoActivo(2);
    } catch (err) {
      setAdvertenciaPagoAbierta(false);
      setErrorAlquiler(
        err.response?.data?.detail || "No se pudo confirmar la reserva.",
      );
      setModalErrorAbierto(true);
    } finally {
      setReservando(false);
    }
  };

  if (cargando || revisandoRequisitos) {
    return (
      <div className="w-full min-w-0 px-5 py-12 sm:px-8 lg:px-10">
        <div className="h-96 animate-pulse rounded-[28px] border border-autospot-border bg-white/70" />
      </div>
    );
  }

  if (bloqueoRequisito) {
    return (
      <section className="mx-auto w-full max-w-2xl px-5 py-16 text-center sm:px-8">
        <h1 className="font-display text-2xl font-black text-autospot-black">
          {bloqueoRequisito.titulo}
        </h1>
        <p className="mx-auto mt-3 max-w-lg text-sm font-semibold leading-6 text-autospot-muted">
          {bloqueoRequisito.mensaje}
        </p>
        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link
            to={`/catalogo/${vehiculoId}`}
            className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Volver al auto
          </Link>
          <Link
            to={bloqueoRequisito.to}
            className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
          >
            {bloqueoRequisito.accion}
          </Link>
        </div>
      </section>
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
        <div className="rounded-2xl  bg-transparent px-4 py-3 text-sm">
          <p className="font-bold text-autospot-muted">Precio por día</p>
          <p className="font-display text-2xl font-black text-autospot-black">
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
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        <div className="mt-8">
          {pasoActivo === 0 && (
            <PasoFechas
              fechaFin={fechaFin}
              horaFin={horaFin}
              fechasValidas={fechasValidas}
              verificando={verificando}
              error={errorAlquiler}
              requiereDocumentacion={!estaHabilitado}
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
              inicio={inicioEstimado}
              fin={fin}
              montoEstimado={montoEstimado}
              onBack={() => setPasoActivo(0)}
              onPagar={() => setAdvertenciaPagoAbierta(true)}
              pagando={reservando}
              error={errorAlquiler}
            />
          )}

          {pasoActivo === 2 && <PasoCodigo reserva={reservaConfirmada} />}
        </div>
      </div>

      <AdvertenciaPagoModal
        abierto={advertenciaPagoAbierta}
        cargando={reservando}
        precioPorDia={vehiculo.precio_por_dia}
        onCancelar={() => setAdvertenciaPagoAbierta(false)}
        onConfirmar={handleConfirmarReserva}
      />

      <ErrorReservaModal
        abierto={modalErrorAbierto}
        mensaje={errorAlquiler}
        onCerrar={() => setModalErrorAbierto(false)}
      />
    </section>
  );
};

const PasoFechas = ({
  fechaFin,
  horaFin,
  fechasValidas,
  verificando,
  error,
  requiereDocumentacion,
  onFechaFinChange,
  onHoraFinChange,
  onVerificar,
}) => (
  <div>
    <h2 className="font-display text-xl font-black text-autospot-black">
      Seleccionar devolución
    </h2>
    <div className="mt-4 grid gap-4 md:grid-cols-2">
      <FechaHoraField
        label="Devolución estimada"
        fecha={fechaFin}
        hora={horaFin}
        onFechaChange={onFechaFinChange}
        onHoraChange={onHoraFinChange}
      />
    </div>

    {requiereDocumentacion && (
      <EstadoMensaje tipo="info">
        Necesitás documentación aprobada para avanzar.{" "}
        <Link
          className="font-black text-autospot-accent"
          to="/documentacion-habilitante"
        >
          Cargar documentación
        </Link>
      </EstadoMensaje>
    )}
    {fechaFin && !fechasValidas && (
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
      <EstadoMensaje tipo="error">
        La reserva todavía no fue confirmada.
      </EstadoMensaje>
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

const FechaHoraField = ({
  label,
  fecha,
  hora,
  onFechaChange,
  onHoraChange,
}) => (
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

const AdvertenciaPagoModal = ({
  abierto,
  cargando,
  precioPorDia,
  onCancelar,
  onConfirmar,
}) => {
  const precio = Number(precioPorDia) || 0;
  const recargoPorDia = precio * 1.1;

  return (
    <Dialog
      open={abierto}
      onClose={cargando ? undefined : onCancelar}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          bgcolor: "#f5f2ed",
          border: "1px solid #d4cec6",
        },
      }}
    >
      <DialogTitle
        sx={{
          color: "#0a0a0a",
          fontFamily: "Unbounded, sans-serif",
          fontWeight: 900,
          letterSpacing: "-0.04em",
          pb: 1,
        }}
      >
        Confirmar pago
      </DialogTitle>
      <DialogContent>
        <div className="rounded-lg border border-autospot-border bg-white p-4">
          <p className="text-sm font-bold leading-6 text-autospot-black">
            Al confirmar el pago aceptás que una devolución posterior a la fecha
            estimada podrá generar un recargo diario.
          </p>
          <div className="mt-4 rounded-lg bg-autospot-black px-4 py-3 text-sm font-bold !text-white">
            {formatearMonto(recargoPorDia)} por día de retraso.
          </div>
        </div>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={onCancelar}
          disabled={cargando}
          sx={{
            color: "#0a0a0a",
            fontWeight: 800,
            borderRadius: 999,
          }}
        >
          Cancelar
        </Button>
        <Button
          onClick={onConfirmar}
          disabled={cargando}
          variant="contained"
          sx={{
            bgcolor: "#7b1c2e",
            borderRadius: 999,
            fontWeight: 900,
            px: 3,
            "&:hover": { bgcolor: "#5a1420" },
          }}
        >
          {cargando ? (
            <CircularProgress size={20} color="inherit" />
          ) : (
            "Pagar y aceptar"
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const ErrorReservaModal = ({ abierto, mensaje, onCerrar }) => {
  return (
    <Dialog
      open={abierto}
      onClose={onCerrar}
      maxWidth="xs"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          bgcolor: "#fcfaf8",
          border: "1px solid #fecdd3", // red-200 aprox
        },
      }}
    >
      <DialogTitle
        sx={{
          color: "#b91c1c", // red-700
          fontFamily: "Unbounded, sans-serif",
          fontWeight: 900,
          letterSpacing: "-0.04em",
          pb: 1,
        }}
      >
        No se pudo confirmar
      </DialogTitle>
      <DialogContent>
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-bold leading-6 text-red-700">
            {mensaje}
          </p>
        </div>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={onCerrar}
          variant="contained"
          sx={{
            bgcolor: "#b91c1c",
            color: "white",
            borderRadius: 999,
            fontWeight: 800,
            px: 3,
            "&:hover": { bgcolor: "#991b1b" },
          }}
        >
          Entendido
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AlquilerStepperPage;
