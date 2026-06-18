import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { AlertTriangle, ArrowLeft, Plus, RotateCcw, Trash2 } from "lucide-react";
import { Button, CircularProgress, Dialog, DialogActions, DialogContent, DialogTitle } from "@mui/material";
import {
  crearReporteIncidencia,
  obtenerMiAlquiler,
  obtenerReporteDeReserva,
} from "../api/reservasService";
import { subirFotoReporte } from "../../../api/uploadService";
import { formatearFechaHora } from "../utils/reservaFormatters";

const MAX_FOTOS = 10;
const MAX_DESCRIPCION = 1000;
const TELEFONO_AUTOSPOT = "0800-4444-28867768";

let contadorFotos = 0;
const nuevaFotoId = () => {
  contadorFotos += 1;
  return `foto-${contadorFotos}-${Date.now()}`;
};

const ReporteIncidenciaPage = () => {
  const { reservaId } = useParams();
  const navigate = useNavigate();
  const inputFileRef = useRef(null);

  const [alquiler, setAlquiler] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [fotos, setFotos] = useState([]);
  const [enviando, setEnviando] = useState(false);
  const [errorEnvio, setErrorEnvio] = useState("");
  const [duplicadoAbierto, setDuplicadoAbierto] = useState(false);
  const [reporteEnviado, setReporteEnviado] = useState(false);

  const cargarDetalle = useCallback(async () => {
    setCargando(true);
    setError("");
    try {
      const data = await obtenerMiAlquiler(reservaId);
      setAlquiler(data);

      // Si ya hay un reporte para la reserva, avisamos en lugar de permitir otro.
      try {
        await obtenerReporteDeReserva(reservaId);
        setDuplicadoAbierto(true);
      } catch (reporteErr) {
        if (reporteErr.response?.status !== 404) {
          throw reporteErr;
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo cargar el alquiler.");
    } finally {
      setCargando(false);
    }
  }, [reservaId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarDetalle();
  }, [cargarDetalle]);

  const actualizarFoto = (id, cambios) =>
    setFotos((prev) => prev.map((foto) => (foto.id === id ? { ...foto, ...cambios } : foto)));

  const subir = useCallback(async (id, file) => {
    actualizarFoto(id, { estado: "subiendo", error: "" });
    try {
      const data = await subirFotoReporte(file);
      actualizarFoto(id, {
        estado: "ok",
        url: data.url,
        formato: data.formato,
        tamanioBytes: data.tamanio_bytes,
      });
    } catch (err) {
      actualizarFoto(id, {
        estado: "error",
        error: err.response?.data?.detail || "No se pudo subir la foto. Reintentá.",
      });
    }
  }, []);

  const handleAgregarFoto = (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (fotos.length >= MAX_FOTOS) return;

    const id = nuevaFotoId();
    const previewUrl = URL.createObjectURL(file);
    setFotos((prev) => [
      ...prev,
      { id, file, previewUrl, descripcion: "", estado: "subiendo", url: null, error: "" },
    ]);
    subir(id, file);
  };

  const handleEliminarFoto = (id) => {
    setFotos((prev) => {
      const foto = prev.find((item) => item.id === id);
      if (foto?.previewUrl) URL.revokeObjectURL(foto.previewUrl);
      return prev.filter((item) => item.id !== id);
    });
  };

  const handleReintentar = (id) => {
    const foto = fotos.find((item) => item.id === id);
    if (foto?.file) subir(id, foto.file);
  };

  const hayAlgunaSubiendo = fotos.some((foto) => foto.estado === "subiendo");
  const hayAlgunError = fotos.some((foto) => foto.estado === "error");
  const fotosOk = fotos.filter((foto) => foto.estado === "ok");
  const todasConDescripcion = fotos.every((foto) => foto.descripcion.trim().length > 0);

  const puedeEnviar =
    descripcion.trim().length > 0 &&
    fotosOk.length >= 1 &&
    fotos.length <= MAX_FOTOS &&
    !hayAlgunaSubiendo &&
    !hayAlgunError &&
    todasConDescripcion &&
    !enviando;

  const handleEnviar = async () => {
    if (!puedeEnviar) return;
    setEnviando(true);
    setErrorEnvio("");
    try {
      const payload = {
        descripcion: descripcion.trim(),
        fotos: fotosOk.map((foto, indice) => ({
          url: foto.url,
          descripcion: foto.descripcion.trim(),
          formato: foto.formato,
          tamanio_bytes: foto.tamanioBytes,
          orden: indice + 1,
        })),
      };
      await crearReporteIncidencia(reservaId, payload);
      setReporteEnviado(true);
    } catch (err) {
      if (err.response?.status === 409) {
        setDuplicadoAbierto(true);
      } else {
        setErrorEnvio(err.response?.data?.detail || "No se pudo enviar el reporte. Intentá de nuevo.");
      }
    } finally {
      setEnviando(false);
    }
  };

  if (cargando) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <p className="rounded-xl border border-[#fecaca] bg-[#fee2e2] px-4 py-3 text-sm text-[#b42318]">
          {error}
        </p>
        <Link to="/usuario/alquileres" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-autospot-primary">
          <ArrowLeft size={16} /> Volver a Mis alquileres
        </Link>
      </div>
    );
  }

  if (reporteEnviado) {
    return <ReporteEnviadoPanel reservaId={reservaId} navigate={navigate} />;
  }

  const vehiculo = alquiler?.vehiculo || {};
  const fotoPrincipal = (vehiculo.fotos || [])[0];

  return (
    <div className="w-full px-4 py-6 sm:px-6 sm:py-8">
      <Link
        to={`/usuario/alquileres/${reservaId}`}
        className="inline-flex items-center gap-2 text-sm font-semibold text-autospot-primary hover:underline"
      >
        <ArrowLeft size={16} /> Volver al alquiler
      </Link>

      <div className="mt-4 flex items-start gap-3">
        <AlertTriangle className="mt-1 shrink-0 text-[#b42318]" size={26} />
        <div>
          <h1 className="text-2xl font-black text-autospot-text sm:text-3xl">
            Reportar incidencia critica
          </h1>
          <p className="mt-2 text-sm text-autospot-muted">
            Este formulario es para fallas criticas ocurridas durante el alquiler. Los detalles
            menores de devolución se registran en el checkout.
          </p>
        </div>
      </div>

      {/* Resumen del alquiler */}
      <section className="mt-6 overflow-hidden rounded-2xl border border-autospot-border bg-white">
        <div className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center">
          {fotoPrincipal ? (
            <img
              src={fotoPrincipal.url}
              alt={`${vehiculo.marca || "Auto"} ${vehiculo.modelo || ""}`}
              className="h-40 w-full rounded-xl object-cover sm:h-24 sm:w-36"
            />
          ) : (
            <div className="flex h-40 w-full items-center justify-center rounded-xl bg-autospot-cream text-xs text-autospot-muted sm:h-24 sm:w-36">
              Sin fotos cargadas
            </div>
          )}
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold uppercase tracking-wide text-autospot-muted">
              {alquiler?.codigo_reserva}
            </p>
            <p className="truncate text-lg font-bold text-autospot-text">
              {vehiculo.marca} {vehiculo.modelo}
            </p>
            <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-sm text-autospot-muted">
              {vehiculo.anio && <span>Año {vehiculo.anio}</span>}
              {vehiculo.categoria && <span>{vehiculo.categoria}</span>}
            </div>
            <div className="mt-2 grid grid-cols-1 gap-1 text-xs text-autospot-muted sm:grid-cols-2">
              <span>Inicio: {formatearFechaHora(alquiler?.fecha_inicio)}</span>
              <span>Devolución estimada: {formatearFechaHora(alquiler?.fecha_fin)}</span>
            </div>
          </div>
        </div>
      </section>

      {/* Descripción general */}
      <section className="mt-6">
        <label htmlFor="descripcion-reporte" className="block text-sm font-bold text-autospot-text">
          Descripción de la falla
        </label>
        <textarea
          id="descripcion-reporte"
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value.slice(0, MAX_DESCRIPCION))}
          rows={4}
          placeholder="Contanos qué pasó con el vehículo."
          className="mt-2 w-full resize-y rounded-xl border border-autospot-border bg-white px-3 py-2 text-sm text-autospot-text outline-none focus:border-autospot-primary"
        />
        <p className="mt-1 text-right text-xs text-autospot-muted">
          {descripcion.length}/{MAX_DESCRIPCION}
        </p>
      </section>

      {/* Fotos */}
      <section className="mt-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-autospot-text">
            Fotos ({fotos.length}/{MAX_FOTOS})
          </h2>
          <button
            type="button"
            onClick={() => inputFileRef.current?.click()}
            disabled={fotos.length >= MAX_FOTOS}
            className="inline-flex items-center gap-1 rounded-lg border border-autospot-primary px-3 py-1.5 text-sm font-semibold text-autospot-primary transition hover:bg-autospot-primary/5 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Plus size={16} /> Agregar foto
          </button>
          <input
            ref={inputFileRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={handleAgregarFoto}
          />
        </div>
        <p className="mt-1 text-xs text-autospot-muted">
          Adjuntá entre 1 y 10 fotos. Cada foto requiere una descripción.
        </p>

        <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {fotos.map((foto) => (
            <ReporteFotoItem
              key={foto.id}
              foto={foto}
              onChangeDescripcion={(valor) => actualizarFoto(foto.id, { descripcion: valor })}
              onReintentar={() => handleReintentar(foto.id)}
              onEliminar={() => handleEliminarFoto(foto.id)}
            />
          ))}
        </div>
      </section>

      {errorEnvio && (
        <p className="mt-4 rounded-xl border border-[#fecaca] bg-[#fee2e2] px-4 py-3 text-sm text-[#b42318]">
          {errorEnvio}
        </p>
      )}

      <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <Button variant="outlined" onClick={() => navigate(`/usuario/alquileres/${reservaId}`)}>
          Cancelar
        </Button>
        <Button variant="contained" color="error" disabled={!puedeEnviar} onClick={handleEnviar}>
          {enviando ? <CircularProgress size={20} color="inherit" /> : "Enviar reporte"}
        </Button>
      </div>

      <ReporteDuplicadoModal
        abierto={duplicadoAbierto}
        onVolver={() => navigate(`/usuario/alquileres/${reservaId}`)}
      />
    </div>
  );
};

const ReporteFotoItem = ({ foto, onChangeDescripcion, onReintentar, onEliminar }) => (
  <div className="rounded-xl border border-autospot-border bg-white p-3">
    <div className="flex gap-3">
      <img src={foto.previewUrl} alt="Adjunto" className="h-20 w-20 shrink-0 rounded-lg object-cover" />
      <div className="min-w-0 flex-1">
        {foto.estado === "subiendo" && (
          <p className="flex items-center gap-2 text-xs text-autospot-muted">
            <CircularProgress size={14} /> Subiendo…
          </p>
        )}
        {foto.estado === "ok" && (
          <p className="text-xs font-semibold text-[#166534]">Foto cargada</p>
        )}
        {foto.estado === "error" && (
          <p className="text-xs font-semibold text-[#b42318]">{foto.error}</p>
        )}
        <div className="mt-2 flex gap-2">
          {foto.estado === "error" && (
            <button
              type="button"
              onClick={onReintentar}
              className="inline-flex items-center gap-1 text-xs font-semibold text-autospot-primary"
            >
              <RotateCcw size={14} /> Reintentar
            </button>
          )}
          <button
            type="button"
            onClick={onEliminar}
            className="inline-flex items-center gap-1 text-xs font-semibold text-[#b42318]"
          >
            <Trash2 size={14} /> Eliminar
          </button>
        </div>
      </div>
    </div>
    <input
      type="text"
      value={foto.descripcion}
      onChange={(e) => onChangeDescripcion(e.target.value.slice(0, 500))}
      placeholder="Descripción de la foto (obligatoria)"
      className="mt-3 w-full rounded-lg border border-autospot-border bg-white px-3 py-2 text-sm text-autospot-text outline-none focus:border-autospot-primary"
    />
  </div>
);

const ReporteDuplicadoModal = ({ abierto, onVolver }) => (
  <Dialog open={abierto} onClose={onVolver} maxWidth="xs" fullWidth>
    <DialogTitle sx={{ fontWeight: 900 }}>Reporte ya registrado</DialogTitle>
    <DialogContent>
      <p className="text-sm text-autospot-muted">
        Ya existe un reporte de incidencia para esta reserva. Nuestro equipo fue notificado y está
        revisando el caso.
      </p>
    </DialogContent>
    <DialogActions>
      <Button variant="contained" onClick={onVolver}>
        Volver al alquiler
      </Button>
    </DialogActions>
  </Dialog>
);

const ReporteEnviadoPanel = ({ reservaId, navigate }) => (
  <div className="mx-auto w-full max-w-2xl px-4 py-10">
    <div className="rounded-2xl border border-autospot-border bg-white p-6 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[#fef3c7]">
        <AlertTriangle className="text-[#b42318]" size={28} />
      </div>
      <h1 className="mt-4 text-2xl font-black text-autospot-text">Reporte recibido</h1>
      <p className="mt-3 text-sm text-autospot-muted">
        Registramos la incidencia critica del vehículo. Nuestro equipo revisará el caso y se
        comunicará con usted a la brevedad.
      </p>
      <p className="mt-3 text-sm font-semibold text-autospot-text">
        Por seguridad, no continúe utilizando el vehículo si no está en condiciones de circular.
      </p>
      <p className="mt-3 text-sm text-autospot-muted">
        Comuníquese con AutoSpot al{" "}
        <span className="font-bold text-autospot-text">{TELEFONO_AUTOSPOT}</span>.
      </p>
      <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-center">
        <Button variant="outlined" onClick={() => navigate("/usuario/alquileres")}>
          Volver a Mis alquileres
        </Button>
        <Button variant="contained" onClick={() => navigate(`/usuario/alquileres/${reservaId}`)}>
          Ver detalle del alquiler
        </Button>
      </div>
    </div>
  </div>
);

export default ReporteIncidenciaPage;
