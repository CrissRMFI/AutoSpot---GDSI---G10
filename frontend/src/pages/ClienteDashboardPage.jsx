import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";

const nombrePresentable = (usuario) => {
  if (usuario?.nombre) return usuario.nombre;
  if (usuario?.first_name) return usuario.first_name;
  const local = (usuario?.email || "").split("@")[0];
  return local || "Usuario";
};

const ClienteDashboardPage = () => {
  const location = useLocation();
  const { usuario } = useAuth();

  const mensaje = location.state?.message;
  const nombreUsuario = nombrePresentable(usuario);

  return (
    <>
      {mensaje && (
        <div className="mb-6 rounded-2xl border border-[#bbf7d0] bg-[#f0fdf4] px-4 py-3 text-sm font-semibold text-[#166534]">
          {mensaje}
        </div>
      )}

      <div className="mb-6 flex min-w-0 flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Panel del cliente
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black break-words sm:text-4xl">
            Buen día, {nombreUsuario} 👋
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-autospot-muted">
            Desde acá podés mantener tu perfil al día y explorar la red de
            estaciones de AutoSpot.
          </p>
        </div>
      </div>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Perfil
          </p>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
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

        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Conductor
          </p>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
            Documentación habilitante
          </h2>
          <p className="mb-5 text-sm leading-6 text-autospot-muted">
            Cargá o actualizá tu licencia de conducir para poder contratar
            vehículos.
          </p>
          <Link
            to="/documentacion-habilitante"
            className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
          >
            Cargar documentación
          </Link>
        </article>

        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)] md:col-span-2 xl:col-span-1">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Red AutoSpot
          </p>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
            Estaciones
          </h2>
          <p className="mb-5 text-sm leading-6 text-autospot-muted">
            Explorá las estaciones disponibles y conocé los autos publicados en
            cada una.
          </p>
          <Link
            to="/estaciones"
            className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
          >
            Ver estaciones
          </Link>
        </article>
      </section>
    </>
  );
};

export default ClienteDashboardPage;
