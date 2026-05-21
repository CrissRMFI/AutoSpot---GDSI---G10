import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";
import { listarVehiculosDelPropietario } from "../features/vehiculos/api/vehiculoService";

const nombrePresentable = (usuario) => {
  if (usuario?.nombre) return usuario.nombre;
  if (usuario?.first_name) return usuario.first_name;
  const local = (usuario?.email || "").split("@")[0];
  return local || "Usuario";
};

const PropietarioDashboardPage = () => {
  const location = useLocation();
  const { usuario } = useAuth();

  const [totalVehiculos, setTotalVehiculos] = useState(null);

  const mensaje = location.state?.message;
  const nombreUsuario = nombrePresentable(usuario);

  useEffect(() => {
    if (!usuario?.id) return;
    listarVehiculosDelPropietario(usuario.id)
      .then((data) => setTotalVehiculos(data.length))
      .catch(() => setTotalVehiculos(null));
  }, [usuario?.id]);

  return (
    <>
      {mensaje && (
        <div className="mb-6 rounded-2xl border border-[#bbf7d0] bg-[#f0fdf4] px-4 py-3 text-sm font-semibold text-[#166534]">
          {mensaje}
        </div>
      )}

      <div className="mb-6 min-w-0">
        <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
          Panel del propietario
        </p>
        <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black break-words sm:text-4xl">
          Buen día, {nombreUsuario} 👋
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-autospot-muted">
          Publicá tus vehículos, definí su precio y consultá el estado de cada
          solicitud.
        </p>
      </div>

      <section className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <article className="rounded-2xl bg-autospot-black p-5 text-autospot-white shadow-[0_18px_40px_rgba(15,23,42,0.18)]">
          <p className="text-xs font-bold uppercase tracking-[0.1em] !text-white/60">
            Mis vehículos
          </p>
          <p className="mt-2 font-display text-3xl font-black !text-white">
            {totalVehiculos ?? "—"}
          </p>
          <p className="mt-1 text-xs !text-white/60">
            Vehículos publicados en tu cuenta
          </p>
        </article>

        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)] sm:col-span-1 xl:col-span-2">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Cuenta
          </p>
          <h2 className="font-display text-lg font-bold tracking-[-0.04em] text-autospot-black break-words">
            Sesión activa
          </h2>
          <p className="mt-1 truncate text-sm text-autospot-muted">
            {usuario?.email || "Email no disponible"}
          </p>
        </article>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Vehículos
          </p>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
            Mis vehículos
          </h2>
          <p className="mb-5 text-sm leading-6 text-autospot-muted">
            Revisá tu flota, su estado y entrá al detalle de cada auto.
          </p>
          <Link
            to="/propietario/vehiculos"
            className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
          >
            Ver mis vehículos
          </Link>
        </article>

        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)]">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Nuevo
          </p>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
            Publicar vehículo
          </h2>
          <p className="mb-5 text-sm leading-6 text-autospot-muted">
            Cargá las características, las fotos obligatorias y el precio diario.
          </p>
          <Link
            to="/propietario/publicar"
            className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
          >
            Publicar vehículo
          </Link>
        </article>

        <article className="rounded-2xl border border-autospot-border bg-autospot-white p-6 shadow-[0_12px_30px_rgba(15,23,42,0.06)] md:col-span-2 xl:col-span-1">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
            Perfil
          </p>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
            Datos personales
          </h2>
          <p className="mb-5 text-sm leading-6 text-autospot-muted">
            Mantené tu información personal al día.
          </p>
          <Link
            to="/datos-personales"
            className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
          >
            Actualizar datos
          </Link>
        </article>
      </section>
    </>
  );
};

export default PropietarioDashboardPage;
