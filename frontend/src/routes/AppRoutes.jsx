import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "../features/auth/pages/LoginPage";
import RegisterPage from "../features/auth/pages/RegisterPage";
import LandingPage from "../features/landing/pages/LandingPage";
import DashboardPage from "../pages/DashboardPage";
import ProtectedRoute from "./ProtectedRoute";
import DatosPersonalesPage from "../features/usuarios/pages/DatosPersonalesPage";
import DocumentacionHabilitantePage from "../features/usuarios/pages/DocumentacionHabilitantePage";
import PublicarVehiculoPage from "../features/vehiculos/pages/PublicarVehiculoPage";
import DocumentacionVehiculoPage from "../features/vehiculos/pages/DocumentacionVehiculoPage";
import ModificarVehiculoPage from "../features/vehiculos/pages/ModificarVehiculoPage";
import DetalleVehiculoPage from "../features/vehiculos/pages/DetalleVehiculoPage";
import EstacionesPage from "../features/estaciones/pages/EstacionesPage";

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
          <ProtectedRoute>
            <DocumentacionHabilitantePage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/usuario/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/propietario/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/propietario/publicar"
        element={
          <ProtectedRoute>
            <PublicarVehiculoPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/modificar-datos/:vehiculoId"
        element={
          <ProtectedRoute>
            <ModificarVehiculoPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/vehiculos/:vehiculoId/documentacion"
        element={
          <ProtectedRoute>
            <DocumentacionVehiculoPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/vehiculos/:vehiculoId/detalle"
        element={
          <ProtectedRoute>
            <DetalleVehiculoPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
