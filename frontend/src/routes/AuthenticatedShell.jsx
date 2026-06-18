import { Outlet } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";
import DashboardLayout from "../layouts/DashboardLayout";

const SECCIONES_POR_ROL = {
  CLIENTE: [
    {
      titulo: "Principal",
      items: [
        { to: "/dashboard", label: "Dashboard", end: true },
        { to: "/catalogo", label: "Catálogo" },
        { to: "/usuario/reservas", label: "Mis reservas" },
        { to: "/usuario/alquileres", label: "Mis alquileres" },
        { to: "/estaciones", label: "Estaciones" },
      ],
    },
    {
      titulo: "Cuenta",
      items: [
        { to: "/datos-personales", label: "Datos personales" },
        { to: "/documentacion-habilitante", label: "Documentación habilitante" },
      ],
    },
  ],
  PROPIETARIO: [
    {
      titulo: "Principal",
      items: [
        { to: "/dashboard", label: "Dashboard", end: true },
        { to: "/vehiculos", label: "Vehículos" },
        { to: "/propietario/publicar", label: "Publicar vehículo" },
        { to: "/estaciones", label: "Estaciones" },
      ],
    },
    {
      titulo: "Cuenta",
      items: [{ to: "/datos-personales", label: "Datos personales" }],
    },
  ],
  ADMIN: [
    {
      titulo: "Principal",
      items: [
        { to: "/dashboard", label: "Dashboard", end: true },
        {
          to: "/admin/solicitudes-documentacion",
          label: "Solicitudes de documentación",
        },
        {
          to: "/admin/reservas/verificar",
          label: "Verificar reservas",
        },
        {
          to: "/admin/checkins/revision",
          label: "Revisión de check-ins",
        },
        {
          to: "/admin/entrega",
          label: "Entrega de autos",
        },
        {
          to: "/admin/recepcion",
          label: "Recepción de autos",
        },
        {
          to: "/admin/historial-conductores",
          label: "Historial conductores",
        },
        {
          to: "/admin/historial-autos",
          label: "Historial de Autos",
        },
        { to: "/estaciones", label: "Estaciones" },
      ],
    },
  ],
};

const AuthenticatedShell = () => {
  const { estaAutenticado, usuario } = useAuth();

  if (!estaAutenticado) {
    return <Outlet />;
  }

  const rol = (usuario?.rol || "CLIENTE").toUpperCase();
  const secciones = SECCIONES_POR_ROL[rol] || SECCIONES_POR_ROL.CLIENTE;

  return (
    <DashboardLayout secciones={secciones}>
      <Outlet />
    </DashboardLayout>
  );
};

export default AuthenticatedShell;
