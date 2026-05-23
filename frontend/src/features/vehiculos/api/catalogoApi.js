import httpClient from "../../../api/httpClient";

export const getCatalogoMarcas = async () => {
  const response = await httpClient.get("/marcas");
  return response.data;
};
