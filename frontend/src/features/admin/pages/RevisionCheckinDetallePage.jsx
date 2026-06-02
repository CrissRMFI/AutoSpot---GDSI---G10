import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import {
  Box, Button, CircularProgress, Alert, Stack, Typography,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import {
  obtenerCheckin,
  aprobarCheckin,
  rechazarCheckin,
} from "../../reservas/api/checkinService";
import CheckinDetalle from "../../reservas/components/CheckinDetalle";
import ConfirmacionModal from "../../reservas/components/ConfirmacionModal";
import RechazoModal from "../../reservas/components/RechazoModal";
import MensajeModal from "../../reservas/components/MensajeModal";

/**
 * Detalle de un check-in para revisión del admin.
 *
 * Cubre:
 *  CA 6 — al rechazar se abre el modal que obliga a especificar el motivo.
 *  CA 1/CA 5 — al aprobar, la reserva queda disponible en Entrega de autos.
 */
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
  const irAEntrega = () => navigate("/admin/entrega");

  const handleAprobar = async () => {
    setProcesando(true);
    try {
      const actualizado = await aprobarCheckin(checkinId);
      setCheckin(actualizado);
      setConfirmAprobar(false);
      setMensaje({
        tipo: "exito",
        titulo: "Check-in aprobado",
        mensaje:
          "El check-in fue aprobado correctamente. La reserva ya aparece en " +
          "'Entrega de autos' para que puedas registrar la salida del conductor.",
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

  /**
   * CA 6 — el modal RechazoModal obliga a ingresar el motivo antes de confirmar.
   * Si se intenta confirmar sin motivo, el propio modal muestra un error local.
   */
  const handleRechazar = async (motivo) => {
    setProcesando(true);
    try {
      const actualizado = await rechazarCheckin(checkinId, motivo);
      setCheckin(actualizado);
      setRechazoAbierto(false);
      setMensaje({
        tipo: "advertencia",
        titulo: "Check-in rechazado",
        mensaje:
          "Se notificó al conductor para que corrija y reenvíe el check-in.",
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

  if (isLoading)
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );

  const estado = (checkin?.estado || "").toUpperCase();
  const pendiente = estado === "PENDIENTE";
  const aprobado = estado === "APROBADO";

  return (
    <section className="w-full min-w-0">
      <Button startIcon={<ArrowBackIcon />} onClick={volverAlListado} sx={{ mb: 3 }}>
        Volver al listado
      </Button>

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {checkin && (
        <>
          {/* Banner de estado para checkins ya resueltos */}
          {!pendiente && (
            <Alert
              severity={aprobado ? "success" : "warning"}
              sx={{ mb: 3 }}
              action={
                aprobado ? (
                  <Button
                    size="small"
                    startIcon={<LocalShippingIcon />}
                    onClick={irAEntrega}
                    color="inherit"
                    sx={{ fontWeight: 700 }}
                  >
                    Ir a Entrega
                  </Button>
                ) : null
              }
            >
              {aprobado
                ? "Este check-in fue aprobado. La reserva está lista para entregar."
                : `Este check-in fue rechazado.${checkin.motivo_rechazo ? ` Motivo: ${checkin.motivo_rechazo}` : ""}`}
            </Alert>
          )}

          <CheckinDetalle checkin={checkin} />

          {/* Botones solo mientras el check-in está PENDIENTE */}
          {pendiente && (
            <>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 3, mb: 1 }}>
                Revisá el formulario y las fotos del conductor antes de tomar una decisión.
              </Typography>
              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={2}
                sx={{ mt: 1 }}
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
                {/* CA 6 — abre el modal que exige especificar el motivo */}
                <Button
                  variant="outlined"
                  color="error"
                  disabled={procesando}
                  onClick={() => setRechazoAbierto(true)}
                  sx={{ borderRadius: 8, fontWeight: 700, flex: 1 }}
                >
                  Rechazar check-in
                </Button>
              </Stack>
            </>
          )}
        </>
      )}

      {/* Modal de confirmación de aprobación */}
      <ConfirmacionModal
        abierto={confirmAprobar}
        titulo="Aprobar check-in"
        mensaje="¿Confirmás la aprobación del check-in del conductor? La reserva pasará a estar disponible para Entrega de autos."
        onConfirmar={handleAprobar}
        onCancelar={() => setConfirmAprobar(false)}
        cargando={procesando}
        textoConfirmar="Aprobar"
        colorConfirmar="success"
      />

      {/*
        CA 6 — Modal de rechazo: el componente RechazoModal ya valida
        internamente que el campo de motivo no esté vacío antes de llamar
        al onConfirmar, por lo que el recepcionista SIEMPRE debe especificar
        el motivo del rechazo.
      */}
      <RechazoModal
        abierto={rechazoAbierto}
        titulo="Rechazar check-in"
        etiqueta="Especificá los motivos del rechazo"
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
    </section>
  );
};

export default RevisionCheckinDetallePage;
