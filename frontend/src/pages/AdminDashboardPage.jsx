import { useAuth } from "../features/auth/hooks/useAuth";

const nombrePresentable = (usuario) => {
  if (usuario?.nombre) return usuario.nombre;
  if (usuario?.first_name) return usuario.first_name;
  const local = (usuario?.email || "").split("@")[0];
  return local || "Admin";
};

const AdminDashboardPage = () => {
  const { usuario } = useAuth();
  const nombreUsuario = nombrePresentable(usuario);

  return (
    <>
      <div className="mb-6 flex min-w-0 flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Panel administrativo
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black break-words sm:text-4xl">
            Buen día, {nombreUsuario} 👋
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-autospot-muted">
            Vista operativa para sprints 1 y 2: usuarios, vehículos publicados y
            estaciones registradas.
          </p>
        </div>
      </div>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Recepción
          </p>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
            Solicitudes de documentación
          </h2>
          <p className="mb-5 text-sm leading-6 text-autospot-muted">
            Atendé los trámites pendientes en orden cronológico (los más
            antiguos primero).
          </p>
          <a
            href="/admin/solicitudes-documentacion"
            className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
          >
            Ver solicitudes
          </a>
        </article>

        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Red AutoSpot
          </p>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
            Estaciones
          </h2>
          <p className="mb-5 text-sm leading-6 text-autospot-muted">
            Consultá las estaciones registradas y su estado actual.
          </p>
          <a
            href="/estaciones"
            className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
          >
            Ver estaciones
          </a>
        </article>

      </section>
    </>
  );
};

export default AdminDashboardPage;
