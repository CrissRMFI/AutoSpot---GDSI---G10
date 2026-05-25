import { Outlet } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";
import DashboardLayout from "../layouts/DashboardLayout";

const SECCIONES_POR_ROL = {
  CLIENTE: [
    {
      titulo: "Principal",
      items: [
        { to: "/usuario/dashboard", label: "Dashboard", end: true },
        { to: "/catalogo", label: "Catálogo" },
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
        { to: "/propietario/dashboard", label: "Dashboard", end: true },
        { to: "/propietario/vehiculos", label: "Mis vehículos" },
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
        { to: "/admin/dashboard", label: "Dashboard", end: true },
        {
          to: "/admin/solicitudes-documentacion",
          label: "Solicitudes de documentación",
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
