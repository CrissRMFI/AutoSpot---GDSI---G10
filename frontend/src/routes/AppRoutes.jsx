import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "../features/auth/pages/LoginPage";
import RegisterPage from "../features/auth/pages/RegisterPage";
import LandingPage from "../features/landing/pages/LandingPage";
import AdminDashboardPage from "../pages/AdminDashboardPage";
import ClienteDashboardPage from "../pages/ClienteDashboardPage";
import PropietarioDashboardPage from "../pages/PropietarioDashboardPage";
import { useAuth } from "../features/auth/hooks/useAuth";
import ProtectedRoute from "./ProtectedRoute";
import DatosPersonalesPage from "../features/usuarios/pages/DatosPersonalesPage";
import DocumentacionHabilitantePage from "../features/usuarios/pages/DocumentacionHabilitantePage";
import PublicarVehiculoPage from "../features/vehiculos/pages/PublicarVehiculoPage";
import DocumentacionVehiculoPage from "../features/vehiculos/pages/DocumentacionVehiculoPage";
import ModificarVehiculoPage from "../features/vehiculos/pages/ModificarVehiculoPage";
import DetalleVehiculoPage from "../features/vehiculos/pages/DetalleVehiculoPage";
import EstacionesPage from "../features/estaciones/pages/EstacionesPage";

const rutaPorRol = (rol) => {
  switch ((rol || "").toUpperCase()) {
    case "ADMIN":
      return "/admin/dashboard";
    case "PROPIETARIO":
      return "/propietario/dashboard";
    case "CLIENTE":
    default:
      return "/usuario/dashboard";
  }
};

const DashboardRedirect = () => {
  const { estaAutenticado, usuario } = useAuth();
  if (!estaAutenticado) {
    return <Navigate to="/login" replace />;
  }
  return <Navigate to={rutaPorRol(usuario?.rol)} replace />;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />

      <Route path="/login" element={<LoginPage />} />
      <Route path="/registro" element={<RegisterPage />} />
      <Route path="/estaciones" element={<EstacionesPage />} />

      <Route
        path="/datos-personales"
        element={
          <ProtectedRoute>
            <DatosPersonalesPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/documentacion-habilitante"
        element={
          <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
            <DocumentacionHabilitantePage />
          </ProtectedRoute>
        }
      />

      <Route path="/dashboard" element={<DashboardRedirect />} />

      <Route
        path="/usuario/dashboard"
        element={
          <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
            <ClienteDashboardPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/propietario/dashboard"
        element={
          <ProtectedRoute rolesPermitidos={["PROPIETARIO"]}>
            <PropietarioDashboardPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/propietario/publicar"
        element={
          <ProtectedRoute rolesPermitidos={["PROPIETARIO"]}>
            <PublicarVehiculoPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/modificar-datos/:vehiculoId"
        element={
          <ProtectedRoute rolesPermitidos={["PROPIETARIO"]}>
            <ModificarVehiculoPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/vehiculos/:vehiculoId/documentacion"
        element={
          <ProtectedRoute rolesPermitidos={["PROPIETARIO"]}>
            <DocumentacionVehiculoPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/vehiculos/:vehiculoId/detalle"
        element={
          <ProtectedRoute rolesPermitidos={["PROPIETARIO"]}>
            <DetalleVehiculoPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute rolesPermitidos={["ADMIN"]}>
            <AdminDashboardPage />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
