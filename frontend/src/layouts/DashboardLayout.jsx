import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";
import NotificacionesBell from "../features/notificaciones/components/NotificacionesBell";

const obtenerIniciales = (email) => {
  if (!email) return "U";
  const local = email.split("@")[0];
  const partes = local.split(/[._-]/).filter(Boolean);
  if (partes.length >= 2) {
    return (partes[0][0] + partes[1][0]).toUpperCase();
  }
  return local.slice(0, 2).toUpperCase();
};

const etiquetaRol = (rol) => {
  switch ((rol || "").toUpperCase()) {
    case "ADMIN":
      return "Administrador";
    case "PROPIETARIO":
      return "Propietario";
    case "CLIENTE":
    default:
      return "Cliente";
  }
};

const DashboardLayout = ({ secciones = [], children }) => {
  const navigate = useNavigate();
  const { usuario, logout } = useAuth();
  const [abierto, setAbierto] = useState(false);

  const cerrarSesion = async () => {
    try {
      await logout();
    } catch {
      // logout ya limpió estado en su finally
    }
    navigate("/login");
  };

  const iniciales = obtenerIniciales(usuario?.email);
  const rolLabel = etiquetaRol(usuario?.rol);

  return (
    <div className="min-h-screen w-full max-w-full overflow-x-hidden lg:overflow-visible bg-autospot-cream text-autospot-black lg:grid lg:grid-cols-[260px_1fr]">
      {/* Topbar mobile */}
      <header className="sticky top-0 z-40 flex items-center justify-between gap-3 border-b border-autospot-border bg-autospot-cream/95 px-5 py-4 backdrop-blur-xl lg:hidden">
        <Link
          to="/"
          className="font-display text-xl font-black tracking-[-0.04em] !text-autospot-black"
        >
          Auto<span className="!text-autospot-accent">Spot</span>
        </Link>

        <div className="flex items-center gap-2">
          <NotificacionesBell />

          <button
            type="button"
            onClick={() => setAbierto((valor) => !valor)}
            aria-expanded={abierto}
            aria-controls="dashboard-sidebar"
            aria-label={abierto ? "Cerrar menú" : "Abrir menú"}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-autospot-border bg-white text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
          >
          {abierto ? (
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          ) : (
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path d="M3 6h18M3 12h18M3 18h18" />
            </svg>
          )}
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        id="dashboard-sidebar"
        className={`${abierto ? "block" : "hidden"} flex flex-col gap-6 border-b border-white/10 bg-autospot-black px-5 py-6 text-autospot-white lg:sticky lg:top-0 lg:flex lg:h-screen lg:border-b-0 lg:border-r lg:px-6 lg:py-8`}
      >
        <div>
          <Link
            to="/"
            className="mb-5 inline-flex text-xs font-bold !text-white/70 transition hover:!text-white"
          >
            ← Volver al inicio
          </Link>

          <Link
            to="/dashboard"
            className="block font-display text-2xl font-black tracking-[-0.04em] !text-white"
          >
            Auto<span className="!text-autospot-accent-2">Spot</span>
          </Link>
        </div>

        <nav className="flex flex-col gap-5">
          <div>
            <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.14em] !text-white/50">
              Perfiles
            </p>
            <div className="flex items-center gap-2 rounded-lg bg-white/[0.06] px-3 py-2 text-sm">
              <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-autospot-accent text-[11px] font-bold !text-white">
                {iniciales}
              </span>
              <span className="text-sm font-bold !text-white">
                Perfil {rolLabel.toLowerCase()}
              </span>
            </div>
          </div>

          {secciones.map(({ titulo, items }) => (
            <div key={titulo}>
              <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.14em] !text-white/50">
                {titulo}
              </p>

              <div className="flex flex-col gap-1">
                {items.map(({ to, label, end = false }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={end}
                    onClick={() => setAbierto(false)}
                    className={({ isActive }) =>
                      `block rounded-lg px-3 py-2 text-sm font-bold transition ${
                        isActive
                          ? "bg-autospot-accent !text-white"
                          : "!text-white/70 hover:bg-white/[0.06] hover:!text-white"
                      }`
                    }
                  >
                    {label}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="mt-auto rounded-2xl border border-white/10 bg-white/[0.06] p-4">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-autospot-accent text-xs font-bold !text-white">
              {iniciales}
            </span>
            <div className="min-w-0">
              <p className="truncate text-xs font-bold !text-white">
                {usuario?.email || "—"}
              </p>
              <p className="text-[11px] !text-white/60">{rolLabel}</p>
            </div>
          </div>

          <button
            type="button"
            onClick={cerrarSesion}
            className="mt-3 inline-flex w-full justify-center rounded-full border border-white/20 bg-white/[0.04] px-3 py-1.5 text-xs font-bold !text-white transition hover:bg-white/[0.1]"
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-col">
        {/* Topbar desktop con campanita */}
        <div className="sticky top-0 z-30 hidden items-center justify-between gap-4 border-b border-autospot-border bg-autospot-cream/95 px-10 py-4 backdrop-blur-xl lg:flex">
          <div className="flex items-center gap-3 text-sm text-autospot-muted">
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-autospot-accent text-xs font-bold !text-white">
              {iniciales}
            </span>
            <div className="leading-tight">
              <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-autospot-muted">
                {rolLabel}
              </p>
              <p className="font-bold text-autospot-black">
                {usuario?.email || "—"}
              </p>
            </div>
          </div>
          <NotificacionesBell />
        </div>

        <main className="px-5 py-6 sm:px-8 sm:py-8 lg:px-10 lg:py-10">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
