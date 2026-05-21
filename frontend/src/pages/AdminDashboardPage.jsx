import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";

const AdminDashboardPage = () => {
  const navigate = useNavigate();
  const { usuario, logout } = useAuth();

  const [sidebarAbierto, setSidebarAbierto] = useState(false);

  const cerrarSesion = async () => {
    try {
      await logout();
    } catch {
      // logout's finally block ya limpió localStorage y estado
    }
    navigate("/login");
  };

  return (
    <main className="min-h-screen bg-autospot-cream text-autospot-black lg:grid lg:grid-cols-[260px_1fr]">
      {/* Topbar mobile */}
      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-autospot-border bg-autospot-cream/95 px-5 py-4 backdrop-blur-xl lg:hidden">
        <Link
          to="/admin/dashboard"
          className="font-display text-xl font-black tracking-[-0.04em] !text-autospot-black"
        >
          Auto<span className="!text-autospot-accent">Spot</span>
        </Link>

        <button
          type="button"
          onClick={() => setSidebarAbierto((valor) => !valor)}
          aria-expanded={sidebarAbierto}
          aria-controls="admin-sidebar"
          className="inline-flex items-center justify-center rounded-full border border-autospot-border bg-white px-3 py-1.5 text-xs font-bold text-autospot-black"
        >
          {sidebarAbierto ? "Cerrar menú" : "Menú"}
        </button>
      </header>

      {/* Sidebar */}
      <aside
        id="admin-sidebar"
        className={`${sidebarAbierto ? "block" : "hidden"} border-b border-autospot-border bg-autospot-black px-5 py-6 text-autospot-white lg:sticky lg:top-0 lg:block lg:h-screen lg:border-b-0 lg:border-r lg:border-white/10 lg:px-6 lg:py-8`}
      >
        <Link
          to="/"
          className="mb-6 inline-flex text-xs font-bold !text-white/70 hover:!text-white"
        >
          ← Volver al inicio
        </Link>

        <Link
          to="/admin/dashboard"
          className="block font-display text-2xl font-black tracking-[-0.04em] !text-white"
        >
          Auto<span className="!text-autospot-accent-2">Spot</span>
        </Link>

        <nav className="mt-8 space-y-1">
          <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.14em] !text-white/50">
            Operación
          </p>
          <Link
            to="/admin/dashboard"
            className="block rounded-lg bg-white/[0.08] px-3 py-2 text-sm font-bold !text-white"
          >
            Dashboard
          </Link>
          <Link
            to="/estaciones"
            className="block rounded-lg px-3 py-2 text-sm font-bold !text-white/70 transition hover:bg-white/[0.06] hover:!text-white"
          >
            Estaciones
          </Link>
        </nav>

        <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.06] p-4">
          <div className="text-xs font-bold !text-white">
            {usuario?.email || "—"}
          </div>
          <div className="mt-0.5 text-[11px] !text-white/60">
            Rol: {usuario?.rol || "ADMIN"}
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
      <section className="px-5 py-6 sm:px-8 sm:py-8 lg:px-10 lg:py-10">
        <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
              Panel administrativo
            </p>
            <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
              Operación AutoSpot
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-autospot-muted">
              Vista operativa para sprints 1 y 2: usuarios, vehículos publicados
              y estaciones registradas.
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <article className="rounded-2xl bg-autospot-black p-5 text-autospot-white shadow-[0_18px_40px_rgba(15,23,42,0.18)]">
            <p className="text-xs font-bold uppercase tracking-[0.1em] !text-white/60">
              Sprint actual
            </p>
            <p className="mt-2 font-display text-3xl font-black !text-white">
              Sprint 2
            </p>
            <p className="mt-1 text-xs !text-white/60">
              Funcionalidades publicadas
            </p>
          </article>

          <article className="rounded-2xl border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_40px_rgba(15,23,42,0.06)]">
            <p className="text-xs font-bold uppercase tracking-[0.1em] text-autospot-muted">
              Vehículos
            </p>
            <p className="mt-2 font-display text-3xl font-black text-autospot-black">
              —
            </p>
            <p className="mt-1 text-xs text-autospot-muted">
              Listado a habilitar en próximos sprints
            </p>
          </article>

          <article className="rounded-2xl border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_40px_rgba(15,23,42,0.06)]">
            <p className="text-xs font-bold uppercase tracking-[0.1em] text-autospot-muted">
              Usuarios
            </p>
            <p className="mt-2 font-display text-3xl font-black text-autospot-black">
              —
            </p>
            <p className="mt-1 text-xs text-autospot-muted">
              Gestión disponible vía API
            </p>
          </article>

          <article className="rounded-2xl border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_40px_rgba(15,23,42,0.06)]">
            <p className="text-xs font-bold uppercase tracking-[0.1em] text-autospot-muted">
              Estaciones
            </p>
            <p className="mt-2 font-display text-3xl font-black text-autospot-black">
              —
            </p>
            <p className="mt-1 text-xs text-autospot-muted">
              Ver detalle en la sección estaciones
            </p>
          </article>
        </div>

        <div className="mt-8 grid gap-5 lg:grid-cols-2">
          <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
              Accesos rápidos
            </p>
            <h2 className="mb-4 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
              Operación diaria
            </h2>

            <div className="flex flex-col gap-2">
              <Link
                to="/estaciones"
                className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-4 py-2.5 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
              >
                Ver estaciones
              </Link>
            </div>
          </article>

          <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
              Próximamente
            </p>
            <h2 className="mb-4 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
              Validación de documentación
            </h2>
            <p className="text-sm leading-6 text-autospot-muted">
              La validación de documentación de vehículos llegará en próximos
              sprints. Por ahora, las acciones de aprobación/rechazo se
              ejecutan vía API.
            </p>
          </article>
        </div>
      </section>
    </main>
  );
};

export default AdminDashboardPage;
