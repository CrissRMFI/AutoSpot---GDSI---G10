import httpClient from "../../../api/httpClient";

export const registrarUsuario = async ({ email, password, rol }) => {
  const response = await httpClient.post("/usuarios/registro", {
    email,
    password,
    rol,
  });

  return response.data;
};

export const loginUsuario = async ({ email, password }) => {
  const response = await httpClient.post("/usuarios/login", {
    email,
    password,
  });

  return response.data;
};

export const logoutUsuario = async () => {
  const response = await httpClient.post("/usuarios/logout");

  return response.data;
};
