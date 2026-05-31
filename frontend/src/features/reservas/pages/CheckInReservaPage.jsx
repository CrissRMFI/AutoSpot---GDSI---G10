import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import CheckinForm from "../components/CheckinForm";
import { crearCheckin, reenviarCheckin } from "../api/checkinService";

const CheckInReservaPage = () => {
  const { reservaId } = useParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  
  // Si la reserva estuviese rechazada, cargaríamos initialData
  // Para este sprint el flujo básico carga el formulario vacío.
  const [initialData] = useState(null);

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    try {
      if (initialData && initialData.id) {
        await reenviarCheckin(initialData.id, formData);
      } else {
        await crearCheckin({ ...formData, reserva_id: reservaId });
      }
      alert("Check-in enviado con éxito. Esperando validación del Administrador.");
      navigate("/usuario/reservas");
    } catch (error) {
      alert("Error al enviar el check-in: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="w-full min-w-0 px-5 py-8 sm:px-8 lg:px-10">
      <Link
        to="/usuario/reservas"
        className="mb-5 inline-flex rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
      >
        Volver a mis reservas
      </Link>

      <div className="w-full rounded-[28px] bg-transparent p-0 mb-6">
        <h1 className="mt-2 font-display text-3xl font-black text-autospot-black sm:text-4xl">
          Check-in del Vehículo
        </h1>
        <p className="mt-3 max-w-2xl text-sm font-semibold leading-6 text-autospot-muted">
          Complete el registro del estado inicial del vehículo para poder iniciar su alquiler.
        </p>
      </div>

      <CheckinForm 
        onSubmit={handleSubmit} 
        isLoading={isLoading} 
        initialData={initialData}
        motivoRechazo={initialData?.motivo_rechazo}
      />
    </section>
  );
};

export default CheckInReservaPage;
