import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";
import { obtenerDocumentacionHabilitante } from "../features/usuarios/api/documentacionHabilitanteService";

const formatEstadoHabilitacion = (estado) => {
  switch (estado) {
    case "PENDIENTE_REVISION":
      return {
        label: "En Revisión",
        className: "bg-[#fef9c3] text-[#854d0e] border border-[#fef08a]",
      };
    case "APROBADO":
      return {
        label: "Aprobado",
        className: "bg-[#f0fdf4] text-[#166534] border border-[#bbf7d0]",
      };
    case "RECHAZADO":
      return {
        label: "Rechazado",
        className: "bg-[#fef2f2] text-[#b42318] border border-[#fecaca]",
      };
    default:
      return {
        label: "Sin estado",
        className: "bg-[#f3f4f6] text-[#374151]",
      };
  }
};

const ClienteDashboardPage = () => {
  const location = useLocation();
  const { usuario } = useAuth();

  const [habilitacion, setHabilitacion] = useState(null);
  const [cargandoHabilitacion, setCargandoHabilitacion] = useState(false);

  const mensaje = location.state?.message;
  const nombreUsuario =
    usuario?.nombre || usuario?.first_name || usuario?.email || "Usuario";

  useEffect(() => {
    const cargarHabilitacion = async () => {
      if (!usuario?.id) {
        return;
      }

      setCargandoHabilitacion(true);

      try {
        const data = await obtenerDocumentacionHabilitante(usuario.id);
        setHabilitacion(data);
      } catch {
        // Si no hay documentación registrada (404), habilitacion queda null
        setHabilitacion(null);
      } finally {
        setCargandoHabilitacion(false);
      }
    };

    cargarHabilitacion();
  }, [usuario?.id]);

  const estadoHabilitacion = habilitacion?.estado_validacion;
  const estaHabilitado = estadoHabilitacion === "APROBADO";
  const estaRechazado = estadoHabilitacion === "RECHAZADO";
  const estadoInfo = estadoHabilitacion
    ? formatEstadoHabilitacion(estadoHabilitacion)
    : null;

  return (
    <>
      {mensaje && (
        <div className="mb-6 rounded-2xl border border-[#bbf7d0] bg-[#f0fdf4] px-4 py-3 text-sm font-semibold text-[#166534]">
          {mensaje}
        </div>
      )}

      <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Panel del cliente
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
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
          <div className="mb-2 flex items-center justify-between">
            <p className="text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
              Conductor
            </p>
            {!cargandoHabilitacion && estadoInfo && (
              <span
                className={`rounded-full px-3 py-1 text-xs font-bold ${estadoInfo.className}`}
              >
                {estadoInfo.label}
              </span>
            )}
            {cargandoHabilitacion && (
              <span className="h-6 w-20 animate-pulse rounded-full bg-gray-200" />
            )}
          </div>
          <h2 className="mb-2 font-display text-xl font-bold tracking-[-0.04em] text-autospot-black">
            Documentación habilitante
          </h2>
          <p className="mb-5 text-sm leading-6 text-autospot-muted">
            {estaRechazado
              ? "Tu documentación fue rechazada. Revisá el motivo y volvé a cargarla."
              : "Cargá o actualizá tu licencia de conducir para poder contratar vehículos."}
          </p>

          {estaRechazado && habilitacion?.motivo_rechazo && (
            <div className="mb-5 rounded-xl border border-[#fecaca] bg-[#fef2f2] p-4 text-sm text-[#b42318]">
              <p className="font-bold">Motivo de rechazo:</p>
              <p className="mt-1">{habilitacion.motivo_rechazo}</p>
            </div>
          )}

          <Link
            to="/documentacion-habilitante"
            className={
              estaRechazado
                ? "inline-flex w-full justify-center rounded-full bg-red-600 px-5 py-3 text-sm font-bold !text-white transition hover:bg-red-700 sm:w-auto"
                : "inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
            }
          >
            {estaRechazado ? "Re-subir documentación" : "Cargar documentación"}
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
            {estaHabilitado
              ? "Explorá las estaciones disponibles y conocé los autos publicados en cada una."
              : "Necesitás tener tu documentación aprobada para explorar estaciones."}
          </p>

          {estaHabilitado ? (
            <Link
              to="/estaciones"
              className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
            >
              Ver estaciones
            </Link>
          ) : (
            <button
              disabled
              title="Tu documentación debe estar Aprobada para acceder a las estaciones"
              className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white opacity-50 cursor-not-allowed sm:w-auto"
            >
              Ver estaciones
            </button>
          )}
        </article>
      </section>
    </>
  );
};

export default ClienteDashboardPage;
