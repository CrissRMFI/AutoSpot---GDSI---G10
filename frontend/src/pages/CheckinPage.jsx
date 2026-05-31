import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Container } from "@mui/material";
import CheckinForm from "../features/reservas/components/CheckinForm";
import { crearCheckin, reenviarCheckin } from "../features/reservas/api/checkinService";

const CheckinPage = () => {
  const { id } = useParams(); // reservaId o checkinId (para el caso de rechazo)
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [initialData] = useState(null);
  
  // En un caso real consultaríamos si la reserva ya tiene un checkin rechazado.
  // Para simplificar, asumimos que se recibe initialData si es un PUT, 
  // o null si es un POST nuevo. Si recibimos un estado en el history lo usamos.
  // Pero aquí simplemente inicializaremos sin state para el POST nuevo.

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    try {
      if (initialData && initialData.id) {
        await reenviarCheckin(initialData.id, formData);
      } else {
        await crearCheckin({ ...formData, reserva_id: id });
      }
      // Redirigir a pantalla de espera o éxito
      alert("Check-in enviado con éxito. Esperando validación del Administrador.");
      navigate("/dashboard");
    } catch (error) {
      alert("Error al enviar el check-in: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <CheckinForm 
        onSubmit={handleSubmit} 
        isLoading={isLoading} 
        initialData={initialData}
        motivoRechazo={initialData?.motivo_rechazo}
      />
    </Container>
  );
};

export default CheckinPage;
