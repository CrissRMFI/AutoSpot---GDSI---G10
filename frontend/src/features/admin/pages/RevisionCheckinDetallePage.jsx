import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import {
  Container, Box, Button, CircularProgress, Alert, Stack,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import {
  obtenerCheckin,
  aprobarCheckin,
  rechazarCheckin,
} from "../../reservas/api/checkinService";
import CheckinDetalle from "../../reservas/components/CheckinDetalle";
import ConfirmacionModal from "../../reservas/components/ConfirmacionModal";
import RechazoModal from "../../reservas/components/RechazoModal";
import MensajeModal from "../../reservas/components/MensajeModal";

const RevisionCheckinDetallePage = () => {
  const { checkinId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [checkin, setCheckin] = useState(location.state?.checkin || null);
  const [isLoading, setIsLoading] = useState(!location.state?.checkin);
  const [error, setError] = useState(null);
  const [confirmAprobar, setConfirmAprobar] = useState(false);
  const [rechazoAbierto, setRechazoAbierto] = useState(false);
  const [procesando, setProcesando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  // Siempre re-confirmar el estado real contra el backend (sobrevive recargas).
  useEffect(() => {
    let cancelado = false;
    (async () => {
      try {
        const data = await obtenerCheckin(checkinId);
        if (!cancelado) setCheckin(data);
      } catch (err) {
        if (!cancelado) {
          setError(
            err.response?.status === 404
              ? "El check-in no existe."
              : "Error al cargar el check-in.",
          );
        }
      } finally {
        if (!cancelado) setIsLoading(false);
      }
    })();
    return () => { cancelado = true; };
  }, [checkinId]);

  const volverAlListado = () => navigate("/admin/checkins/revision");

  const handleAprobar = async () => {
    setProcesando(true);
    try {
      const actualizado = await aprobarCheckin(checkinId);
      setCheckin(actualizado);
      setConfirmAprobar(false);
      setMensaje({
        tipo: "exito",
        titulo: "Check-in aprobado",
        mensaje: "El check-in fue aprobado. La reserva ya aparece en Entrega de autos para registrar la salida.",
      });
    } catch (err) {
      setConfirmAprobar(false);
      setMensaje({
        tipo: "error",
        titulo: "No se pudo aprobar",
        mensaje: err.response?.data?.detail || "Ocurrió un error inesperado.",
      });
    } finally {
      setProcesando(false);
    }
  };

  const handleRechazar = async (motivo) => {
    setProcesando(true);
    try {
      const actualizado = await rechazarCheckin(checkinId, motivo);
      setCheckin(actualizado);
      setRechazoAbierto(false);
      setMensaje({
        tipo: "advertencia",
        titulo: "Check-in rechazado",
        mensaje: "Se notificó al conductor para que corrija y reenvíe el check-in.",
      });
    } catch (err) {
      setRechazoAbierto(false);
      setMensaje({
        tipo: "error",
        titulo: "No se pudo rechazar",
        mensaje: err.response?.data?.detail || "Ocurrió un error inesperado.",
      });
    } finally {
      setProcesando(false);
    }
  };

  if (isLoading) return <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}><CircularProgress /></Box>;

  const estado = (checkin?.estado || "").toUpperCase();
  const pendiente = estado === "PENDIENTE";

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Button startIcon={<ArrowBackIcon />} onClick={volverAlListado} sx={{ mb: 3 }}>
        Volver al listado
      </Button>

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {checkin && (
        <>
          {!pendiente && (
            <Alert
              severity={estado === "APROBADO" ? "success" : "warning"}
              sx={{ mb: 3 }}
            >
              Este check-in ya fue {estado === "APROBADO" ? "aprobado" : "rechazado"}.
              {estado === "RECHAZADO" && checkin.motivo_rechazo
                ? ` Motivo: ${checkin.motivo_rechazo}`
                : ""}
            </Alert>
          )}

          <CheckinDetalle checkin={checkin} />

          {pendiente && (
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={2}
              sx={{ mt: 3 }}
            >
              <Button
                variant="contained"
                color="success"
                disabled={procesando}
                onClick={() => setConfirmAprobar(true)}
                sx={{ borderRadius: 8, fontWeight: 700, flex: 1 }}
              >
                Aprobar check-in
              </Button>
              <Button
                variant="outlined"
                color="error"
                disabled={procesando}
                onClick={() => setRechazoAbierto(true)}
                sx={{ borderRadius: 8, fontWeight: 700, flex: 1 }}
              >
                Rechazar
              </Button>
            </Stack>
          )}
        </>
      )}

      <ConfirmacionModal
        abierto={confirmAprobar}
        titulo="Aprobar check-in"
        mensaje="¿Confirmás la aprobación del check-in del conductor?"
        onConfirmar={handleAprobar}
        onCancelar={() => setConfirmAprobar(false)}
        cargando={procesando}
        textoConfirmar="Aprobar"
        colorConfirmar="success"
      />

      <RechazoModal
        abierto={rechazoAbierto}
        titulo="Rechazar check-in"
        etiqueta="Motivo del rechazo"
        onConfirmar={handleRechazar}
        onCancelar={() => setRechazoAbierto(false)}
        cargando={procesando}
      />

      <MensajeModal
        abierto={Boolean(mensaje)}
        tipo={mensaje?.tipo}
        titulo={mensaje?.titulo}
        mensaje={mensaje?.mensaje}
        onClose={() => setMensaje(null)}
      />
    </Container>
  );
};

export default RevisionCheckinDetallePage;
