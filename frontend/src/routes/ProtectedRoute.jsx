import { Navigate } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";

const rutaPorRol = (rol) => {
  switch ((rol || "").toUpperCase()) {
    case "ADMIN":
      return "/dashboard";
    case "PROPIETARIO":
      return "/dashboard";
    case "CLIENTE":
    default:
      return "/dashboard";
  }
};

const ProtectedRoute = ({ children, rolesPermitidos }) => {
  const { estaAutenticado, usuario } = useAuth();

  if (!estaAutenticado) {
    return <Navigate to="/login" replace />;
  }

  if (rolesPermitidos && rolesPermitidos.length > 0) {
    const rolUsuario = (usuario?.rol || "").toUpperCase();
    if (!rolesPermitidos.map((r) => r.toUpperCase()).includes(rolUsuario)) {
      return <Navigate to={rutaPorRol(rolUsuario)} replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
