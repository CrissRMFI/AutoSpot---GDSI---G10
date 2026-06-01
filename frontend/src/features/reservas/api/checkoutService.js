import httpClient from "../../../api/httpClient";

export const crearCheckout = async (payload) => {
  const response = await httpClient.post("/checkouts", payload);
  return response.data;
};

export const obtenerCheckoutVigenteAdmin = async (reservaId) => {
  const response = await httpClient.get(`/checkouts/reservas/${reservaId}/vigente`);
  return response.data;
};

export const subirFotoCheckout = async (file) => {
  const formData = new FormData();
  formData.append("archivo", file);

  const response = await httpClient.post("/upload/foto-checkout", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};
