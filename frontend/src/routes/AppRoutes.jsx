import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "../features/auth/pages/LoginPage";
import RegisterPage from "../features/auth/pages/RegisterPage";
import LandingPage from "../features/landing/pages/LandingPage";
import AdminDashboardPage from "../pages/AdminDashboardPage";
import ClienteDashboardPage from "../pages/ClienteDashboardPage";
import MisVehiculosPage from "../pages/MisVehiculosPage";
import PropietarioDashboardPage from "../pages/PropietarioDashboardPage";
import { useAuth } from "../features/auth/hooks/useAuth";
import AuthenticatedShell from "./AuthenticatedShell";
import ProtectedRoute from "./ProtectedRoute";
import DatosPersonalesPage from "../features/usuarios/pages/DatosPersonalesPage";
import DocumentacionHabilitantePage from "../features/usuarios/pages/DocumentacionHabilitantePage";
import PublicarVehiculoPage from "../features/vehiculos/pages/PublicarVehiculoPage";
import DocumentacionVehiculoPage from "../features/vehiculos/pages/DocumentacionVehiculoPage";
import ModificarVehiculoPage from "../features/vehiculos/pages/ModificarVehiculoPage";
import DetalleVehiculoPage from "../features/vehiculos/pages/DetalleVehiculoPage";
import CatalogoVehiculosPage from "../features/vehiculos/pages/CatalogoVehiculosPage";
import CatalogoDetalleVehiculoPage from "../features/vehiculos/pages/CatalogoDetalleVehiculoPage";
import { HistorialUsoVehiculoPage } from "../features/vehiculos/pages/HistorialUsoVehiculoPage";
import MisReservasPage from "../features/reservas/pages/MisReservasPage";
import MisAlquileresPage from "../features/reservas/pages/MisAlquileresPage";
import AlquilerDetallePage from "../features/reservas/pages/AlquilerDetallePage";
import AlquilerStepperPage from "../features/reservas/pages/AlquilerStepperPage";
import CheckInReservaPage from "../features/reservas/pages/CheckInReservaPage";
import EstacionesPage from "../features/estaciones/pages/EstacionesPage";
import DetalleEstacionPublicoPage from "../features/estaciones/pages/DetalleEstacionPublicoPage";
import DetalleSolicitudDocumentacionPage from "../features/admin/pages/DetalleSolicitudDocumentacionPage";
import SolicitudesDocumentacionPage from "../features/admin/pages/SolicitudesDocumentacionPage";
import VerificarReservaPage from "../features/admin/pages/VerificarReservaPage";
import RevisionCheckinPage from "../features/admin/pages/RevisionCheckinPage";
import RevisionCheckinDetallePage from "../features/admin/pages/RevisionCheckinDetallePage";
import EntregaAutosPage from "../features/admin/pages/EntregaAutosPage";
import RecepcionAutosPage from "../features/admin/pages/RecepcionAutosPage";
import RecepcionDetallePage from "../features/admin/pages/RecepcionDetallePage";

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

const PublicOnlyRoute = ({ children }) => {
  const { estaAutenticado, usuario } = useAuth();

  if (estaAutenticado) {
    return <Navigate to={rutaPorRol(usuario?.rol)} replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* El inicio es accesible siempre: un usuario logueado puede volver a la
          landing. Los botones de la landing lo llevan a su panel si tiene sesión. */}
      <Route path="/" element={<LandingPage />} />

      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <LoginPage />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/registro"
        element={
          <PublicOnlyRoute>
            <RegisterPage />
          </PublicOnlyRoute>
        }
      />

      <Route element={<AuthenticatedShell />}>
        <Route path="/estaciones" element={<EstacionesPage />} />
        <Route path="/estaciones/:id" element={<DetalleEstacionPublicoPage />} />

        <Route path="/dashboard" element={<DashboardRedirect />} />

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

        <Route
          path="/usuario/dashboard"
          element={
            <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
              <ClienteDashboardPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/catalogo"
          element={
            <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
              <CatalogoVehiculosPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/catalogo/:vehiculoId"
          element={
            <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
              <CatalogoDetalleVehiculoPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/catalogo/:vehiculoId/alquilar"
          element={
            <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
              <AlquilerStepperPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/usuario/reservas"
          element={
            <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
              <MisReservasPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/usuario/alquileres"
          element={
            <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
              <MisAlquileresPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/usuario/alquileres/:reservaId"
          element={
            <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
              <AlquilerDetallePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/usuario/reservas/:reservaId/checkin"
          element={
            <ProtectedRoute rolesPermitidos={["CLIENTE"]}>
              <CheckInReservaPage />
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
          path="/propietario/vehiculos"
          element={
            <ProtectedRoute rolesPermitidos={["PROPIETARIO"]}>
              <MisVehiculosPage />
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
          path="/vehiculos/:vehiculoId/documentacion/actualizar"
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
          path="/vehiculos/:vehiculoId/historial"
          element={
            <ProtectedRoute rolesPermitidos={["PROPIETARIO"]}>
              <HistorialUsoVehiculoPage />
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

        <Route
          path="/admin/solicitudes-documentacion"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <SolicitudesDocumentacionPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/reservas/verificar"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <VerificarReservaPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/checkins/revision"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <RevisionCheckinPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/checkins/:checkinId"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <RevisionCheckinDetallePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/entrega"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <EntregaAutosPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/recepcion"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <RecepcionAutosPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/recepcion/:reservaId"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <RecepcionDetallePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/checkout"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <Navigate to="/admin/recepcion" replace />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/solicitudes-documentacion/:tipo/:recursoId"
          element={
            <ProtectedRoute rolesPermitidos={["ADMIN"]}>
              <DetalleSolicitudDocumentacionPage />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
