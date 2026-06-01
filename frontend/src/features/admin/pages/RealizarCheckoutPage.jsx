import { useState, useEffect } from "react";
import {
  Container, Typography, Box, Card, CardContent, Button,
  CircularProgress, Alert,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { listarReservasDevueltas } from "../../reservas/api/reservasService";
import { crearCheckout } from "../../reservas/api/checkoutService";
import CheckoutForm from "../../reservas/components/CheckoutForm";
import MensajeModal from "../../reservas/components/MensajeModal";

const RealizarCheckoutPage = () => {
  const [reservas, setReservas] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [seleccionada, setSeleccionada] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  const fetchReservas = async () => {
    try {
      const data = await listarReservasDevueltas();
      setReservas(data);
    } catch {
      setError("Error al cargar los autos devueltos.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchReservas();
  }, []);

  const handleSubmit = async (formData) => {
    setIsSubmitting(true);
    try {
      await crearCheckout({ ...formData, reserva_id: seleccionada.id });
      setSeleccionada(null);
      setMensaje({
        tipo: "exito",
        titulo: "Checkout registrado",
        mensaje: "La inspección de devolución se guardó y el alquiler fue finalizado.",
      });
      setIsLoading(true);
      fetchReservas();
    } catch (err) {
      setMensaje({
        tipo: "error",
        titulo: "No se pudo registrar el checkout",
        mensaje: err.response?.data?.detail || "Ocurrió un error inesperado.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) return <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}><CircularProgress /></Box>;

  if (seleccionada) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => setSeleccionada(null)}
          sx={{ mb: 3 }}
        >
          Volver al listado
        </Button>
        <CheckoutForm
          onSubmit={handleSubmit}
          isLoading={isSubmitting}
          reservaResumen={seleccionada}
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
  }

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: "var(--text)" }}>
        Checkout de Devolución (Admin)
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {reservas.length === 0 && !error ? (
        <Alert severity="info">No hay autos devueltos pendientes de checkout.</Alert>
      ) : (
        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 3 }}>
          {reservas.map((reserva) => (
            <Card key={reserva.id} sx={{ borderRadius: 4, boxShadow: "var(--shadow-autospot-soft)" }}>
              <CardContent>
                <Typography variant="h6" fontWeight="bold">
                  {reserva.vehiculo?.marca} {reserva.vehiculo?.modelo}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Reserva {reserva.codigo_reserva}
                  {reserva.vehiculo?.patente ? ` — ${reserva.vehiculo.patente}` : ""}
                </Typography>

                {reserva.monto_penalizacion && (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    Devolución tardía. Penalización: ${reserva.monto_penalizacion}
                  </Alert>
                )}

                <Button
                  variant="contained"
                  onClick={() => setSeleccionada(reserva)}
                  sx={{
                    bgcolor: "var(--accent)",
                    fontWeight: 700,
                    borderRadius: 8,
                    "&:hover": { bgcolor: "var(--accent-dark)" },
                  }}
                >
                  Realizar checkout
                </Button>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

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

export default RealizarCheckoutPage;
