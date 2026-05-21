import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";

const ClienteDashboardPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { usuario, logout } = useAuth();

  const mensaje = location.state?.message;
  const nombreUsuario =
    usuario?.nombre || usuario?.first_name || usuario?.email || "Usuario";

  const cerrarSesion = async () => {
    try {
      await logout();
    } catch {
      // logout's finally block ya limpió localStorage y estado
    }
    navigate("/login");
  };

  return (
    <main className="min-h-screen bg-autospot-cream text-autospot-black">
      <header className="sticky top-0 z-40 border-b border-autospot-border bg-autospot-cream/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
          <Link
            to="/"
            className="font-display text-xl font-black tracking-[-0.04em] !text-autospot-black"
          >
            Auto<span className="!text-autospot-accent">Spot</span>
          </Link>

          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <Link
              to="/"
              className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
            >
              Inicio
            </Link>

            <button
              type="button"
              onClick={cerrarSesion}
              className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
            >
              Cerrar sesión
            </button>
          </div>
        </div>
      </header>

      <section className="mx-auto w-full max-w-6xl px-5 py-8 sm:px-8 sm:py-10 lg:px-10 lg:py-12">
        {mensaje && (
          <div className="mb-6 rounded-2xl border border-[#bbf7d0] bg-[#f0fdf4] px-4 py-3 text-sm font-semibold text-[#166534]">
            {mensaje}
          </div>
        )}

        <section className="mb-8 rounded-[28px] border border-autospot-border bg-white/70 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.07)] sm:p-8">
          <p className="mb-2 text-sm font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Panel del cliente
          </p>

          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
            Bienvenido, {nombreUsuario}
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-autospot-muted sm:text-base">
            Mantené tus datos personales y tu licencia al día, y explorá las
            estaciones disponibles en AutoSpot.
          </p>
        </section>

        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <article className="rounded-[22px] border border-autospot-border bg-autospot-white p-6 shadow-[0_18px_40px_rgba(15,23,42,0.08)]">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
              Cuenta
            </p>

            <h2 className="mb-3 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
              Sesión activa
            </h2>

            <p className="break-words text-sm leading-6 text-autospot-muted">
              {usuario?.email || "Email no disponible"}
            </p>
          </article>

          <article className="rounded-[22px] border border-autospot-border bg-autospot-white p-6 shadow-[0_18px_40px_rgba(15,23,42,0.08)]">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
              Perfil
            </p>

            <h2 className="mb-3 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
              Datos personales
            </h2>

            <p className="mb-5 text-sm leading-6 text-autospot-muted">
              Completá o actualizá la información asociada a tu cuenta.
            </p>

            <Link
              to="/datos-personales"
              className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
            >
              Actualizar datos
            </Link>
          </article>

          <article className="rounded-[22px] border border-autospot-border bg-autospot-white p-6 shadow-[0_18px_40px_rgba(15,23,42,0.08)]">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
              Conductor
            </p>

            <h2 className="mb-3 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
              Documentación habilitante
            </h2>

            <p className="mb-5 text-sm leading-6 text-autospot-muted">
              Cargá o actualizá tu licencia de conducir para contratar
              vehículos.
            </p>

            <Link
              to="/documentacion-habilitante"
              className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
            >
              Cargar documentación
            </Link>
          </article>

          <article className="rounded-[22px] border border-autospot-border bg-autospot-white p-6 shadow-[0_18px_40px_rgba(15,23,42,0.08)] md:col-span-2 xl:col-span-1">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
              Estaciones
            </p>

            <h2 className="mb-3 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
              Red de estaciones
            </h2>

            <p className="mb-5 text-sm leading-6 text-autospot-muted">
              Explorá las estaciones disponibles y los autos publicados en cada
              una.
            </p>

            <Link
              to="/estaciones"
              className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
            >
              Ver estaciones
            </Link>
          </article>
        </section>
      </section>
    </main>
  );
};

export default ClienteDashboardPage;
