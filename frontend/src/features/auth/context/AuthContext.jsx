import { useMemo, useState } from "react";
import { loginUsuario, logoutUsuario } from "../api/authService";
import { AuthContext } from "./authContext";
import {
  desregistrarPushWeb,
  registrarPushWeb,
} from "../../notificaciones/services/pushNotifications";

export const AuthProvider = ({ children }) => {
  const [usuario, setUsuario] = useState(() => {
    const usuarioGuardado = localStorage.getItem("usuario");

    if (!usuarioGuardado) {
      return null;
    }

    return JSON.parse(usuarioGuardado);
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem("access_token");
  });

  const estaAutenticado = Boolean(token && usuario);

  const login = async ({ email, password }) => {
    const data = await loginUsuario({ email, password });

    const usuarioAutenticado = {
      id: data.id,
      email: data.email,
      isActive: data.is_active,
      rol: data.rol,
    };

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("usuario", JSON.stringify(usuarioAutenticado));

    setToken(data.access_token);
    setUsuario(usuarioAutenticado);

    registrarPushWeb().catch((error) => {
      console.warn("No se pudo registrar Web Push", error);
    });

    return usuarioAutenticado;
  };

  const logout = async () => {
    let pushEndpoint = null;

    try {
      pushEndpoint = await desregistrarPushWeb();
    } catch (error) {
      console.warn("No se pudo eliminar la suscripción Web Push", error);
    }

    try {
      await logoutUsuario(pushEndpoint ? { endpoint: pushEndpoint } : null);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("usuario");

      setToken(null);
      setUsuario(null);
    }
  };

  const value = useMemo(
    () => ({
      usuario,
      token,
      estaAutenticado,
      login,
      logout,
    }),
    [usuario, token, estaAutenticado],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
