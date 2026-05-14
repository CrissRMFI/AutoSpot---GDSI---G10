import { useMemo, useState } from "react";
import { loginUsuario, logoutUsuario } from "../api/authService";
import { AuthContext } from "./authContext";

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
    };

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("usuario", JSON.stringify(usuarioAutenticado));

    setToken(data.access_token);
    setUsuario(usuarioAutenticado);

    return usuarioAutenticado;
  };

  const logout = async () => {
    try {
      await logoutUsuario();
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
