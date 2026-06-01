import { useState, useEffect } from "react";
import {
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import {
  listarReservasParaEntregar,
  registrarSalida,
} from "../../reservas/api/reservasService";
import ConfirmacionModal from "../../reservas/components/ConfirmacionModal";
import MensajeModal from "../../reservas/components/MensajeModal";

const EntregaAutosPage = () => {
  const [reservas, setReservas] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [confirmacion, setConfirmacion] = useState(null);
  const [procesando, setProcesando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  const fetchReservas = async () => {
    try {
      const data = await listarReservasParaEntregar();
      setReservas(data);
    } catch {
      setError("Error al cargar las reservas para entregar.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchReservas();
  }, []);

  const handleConfirmarSalida = async () => {
    const reservaId = confirmacion?.id;
    if (!reservaId) return;
    setProcesando(true);
    try {
      await registrarSalida(reservaId);
      setConfirmacion(null);
      setMensaje({
        tipo: "exito",
        titulo: "Salida registrada",
        mensaje:
          "El auto fue entregado al conductor y el alquiler quedó EN CURSO.",
      });
      setIsLoading(true);
      fetchReservas();
    } catch (err) {
      setConfirmacion(null);
      setMensaje({
        tipo: "error",
        titulo: "No se pudo registrar la salida",
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

  return (
    <div className="w-full p-5">
      <Typography
        variant="h4"
        sx={{ mb: 1, fontWeight: 700, color: "var(--text)" }}
      >
        Entrega de Autos
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
        Reservas con check-in aprobado, listas para entregar al conductor.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {reservas.length === 0 && !error ? (
        <Alert severity="info">No hay autos listos para entregar.</Alert>
      ) : (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
            gap: 3,
          }}
        >
          {reservas.map((reserva) => (
            <Card
              key={reserva.id}
              sx={{ borderRadius: 4, boxShadow: "var(--shadow-autospot-soft)" }}
            >
              <CardContent>
                <Typography variant="h6" fontWeight="bold">
                  {reserva.vehiculo?.marca} {reserva.vehiculo?.modelo}
                </Typography>
                <Typography
                  variant="body2"
                  color="textSecondary"
                  sx={{ mb: 2 }}
                >
                  Reserva {reserva.codigo_reserva}
                  {reserva.vehiculo?.patente
                    ? ` — ${reserva.vehiculo.patente}`
                    : ""}
                </Typography>

                <Box
                  sx={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 2,
                    mb: 2,
                  }}
                >
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      Estación
                    </Typography>
                    <Typography variant="body1">
                      {reserva.estacion_retiro}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      Inicio pactado
                    </Typography>
                    <Typography variant="body1">
                      {new Date(reserva.fecha_inicio).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>

                <Button
                  variant="contained"
                  onClick={() => setConfirmacion(reserva)}
                  sx={{
                    bgcolor: "var(--accent)",
                    fontWeight: 700,
                    borderRadius: 8,
                    "&:hover": { bgcolor: "var(--accent-dark)" },
                  }}
                >
                  Registrar salida (entregar)
                </Button>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      <ConfirmacionModal
        abierto={Boolean(confirmacion)}
        titulo="Entregar auto"
        mensaje={
          confirmacion
            ? `¿Confirmás la entrega del ${confirmacion.vehiculo?.marca} ${confirmacion.vehiculo?.modelo} (reserva ${confirmacion.codigo_reserva})? El alquiler pasará a EN CURSO.`
            : ""
        }
        onConfirmar={handleConfirmarSalida}
        onCancelar={() => setConfirmacion(null)}
        cargando={procesando}
        textoConfirmar="Registrar salida"
      />

      <MensajeModal
        abierto={Boolean(mensaje)}
        tipo={mensaje?.tipo}
        titulo={mensaje?.titulo}
        mensaje={mensaje?.mensaje}
        onClose={() => setMensaje(null)}
      />
    </div>
  );
};

export default EntregaAutosPage;
