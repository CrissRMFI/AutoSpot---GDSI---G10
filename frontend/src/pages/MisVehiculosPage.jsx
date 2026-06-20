import { useEffect, useState } from "react";
import { LayoutDashboard, Plus } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";
import { formatearEstado } from "../utils/formatStatus";
import {
  getStatusSolicitud,
  listarVehiculosDelPropietario,
} from "../features/vehiculos/api/vehiculoService";

const formatEstado = (estado) => {
  switch (estado) {
    case "PENDIENTE_DOCUMENTACION":
      return {
        label: "Pendiente Doc.",
        className: "bg-[#f1f5f9] text-[#475569] border border-[#e2e8f0]",
      };
    case "EN_REVISION":
      return {
        label: "En Revisión",
        className: "bg-[#fef9c3] text-[#854d0e] border border-[#fef08a]",
      };
    case "HABILITADO":
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
        label: formatearEstado(estado),
        className: "bg-[#f3f4f6] text-[#374151]",
      };
  }
};

const obtenerFotoFrente = (vehiculo) => {
  const fotos = vehiculo?.fotos ?? [];
  return fotos.find((foto) => foto.lado === "FRENTE")?.url || fotos[0]?.url || "";
};

const MisVehiculosPage = () => {
  const { usuario } = useAuth();
  const [vehiculos, setVehiculos] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!usuario?.id) return;

    const cargar = async () => {
      setCargando(true);
      setError("");
      try {
        const data = await listarVehiculosDelPropietario(usuario.id);
        const conEstado = await Promise.all(
          data.map(async (v) => {
            try {
              const status = await getStatusSolicitud(v.id);
              return {
                ...v,
                estado_registro: status.estado_registro,
                motivo_rechazo: status.motivo_rechazo,
              };
            } catch {
              return v;
            }
          }),
        );
        setVehiculos(conEstado);
      } catch {
        setError("No se pudieron cargar tus vehículos publicados.");
      } finally {
        setCargando(false);
      }
    };

    cargar();
  }, [usuario?.id]);

  return (
    <>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Propietario
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black break-words sm:text-4xl">
            Mis vehículos
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-autospot-muted">
            Tocá cualquier vehículo para ver toda su información, cargar
            documentación o actualizar su precio.
          </p>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row">
          <Link
            to="/vehiculos"
            className="inline-flex items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            <LayoutDashboard className="h-4 w-4" aria-hidden="true" />
            Resumen vehículos
          </Link>
          <Link
            to="/propietario/publicar"
            className="inline-flex items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
          >
            <Plus className="h-4 w-4" aria-hidden="true" />
            Publicar vehículo
          </Link>
        </div>
      </div>

      {cargando && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className="animate-pulse rounded-2xl border border-autospot-border bg-white p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)]"
            >
              <div className="mb-4 h-40 w-full rounded-xl bg-gray-200" />
              <div className="mb-2 h-5 w-2/3 rounded bg-gray-200" />
              <div className="mb-4 h-4 w-1/2 rounded bg-gray-200" />
              <div className="h-8 w-full rounded-full bg-gray-200" />
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
          {error}
        </div>
      )}

      {!cargando && !error && vehiculos.length === 0 && (
        <div className="rounded-2xl border border-dashed border-autospot-border bg-white/70 px-5 py-10 text-center">
          <h3 className="font-display text-lg font-bold tracking-[-0.04em] text-autospot-black">
            Todavía no publicaste vehículos
          </h3>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-autospot-muted">
            Cuando registres tu primer vehículo, vas a poder verlo acá y
            continuar con la carga de documentación.
          </p>
          <Link
            to="/propietario/publicar"
            className="mt-5 inline-flex rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
          >
            Publicar mi primer vehículo
          </Link>
        </div>
      )}

      {!cargando && !error && vehiculos.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {vehiculos.map((vehiculo) => {
            const estado = formatEstado(vehiculo.estado_registro);
            const fotoUrl = obtenerFotoFrente(vehiculo);

            return (
              <Link
                key={vehiculo.id}
                to={`/vehiculos/${vehiculo.id}/detalle`}
                className="group block overflow-hidden rounded-2xl border border-autospot-border bg-white shadow-[0_12px_30px_rgba(15,23,42,0.06)] transition hover:-translate-y-0.5 hover:border-autospot-accent hover:shadow-[0_18px_40px_rgba(15,23,42,0.1)]"
              >
                <div className="relative aspect-video w-full overflow-hidden bg-[#0f0f0f]">
                  {fotoUrl ? (
                    <img
                      src={fotoUrl}
                      alt={`${vehiculo.marca} ${vehiculo.modelo}`}
                      className="h-full w-full object-cover transition group-hover:scale-105"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-xs text-white/60">
                      Sin foto
                    </div>
                  )}
                  <span
                    className={`absolute left-3 top-3 rounded-full px-2.5 py-1 text-[11px] font-bold ${estado.className}`}
                  >
                    {estado.label}
                  </span>
                </div>

                <div className="p-5">
                  <h3 className="font-display text-lg font-bold tracking-[-0.04em] !text-autospot-black break-words">
                    {vehiculo.marca} {vehiculo.modelo}
                  </h3>
                  <p className="mt-1 text-sm text-autospot-muted">
                    {vehiculo.anio} · {vehiculo.categoria}
                  </p>

                  <div className="mt-4 flex items-baseline justify-between gap-2">
                    <div>
                      <p className="text-[11px] font-bold uppercase tracking-[0.08em] text-autospot-muted">
                        Precio diario
                      </p>
                      <p className="font-display text-xl font-bold text-autospot-black">
                        {vehiculo.precio_por_dia
                          ? `$${vehiculo.precio_por_dia}`
                          : "Sin definir"}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-[11px] font-bold ${
                        vehiculo.disponible
                          ? "bg-[#f0fdf4] text-[#166534] border border-[#bbf7d0]"
                          : "bg-[#fef2f2] text-[#b42318] border border-[#fecaca]"
                      }`}
                    >
                      {vehiculo.disponible ? "Disponible" : "No disponible"}
                    </span>
                  </div>

                  <p className="mt-5 inline-flex text-xs font-bold text-autospot-accent transition group-hover:translate-x-0.5">
                    Ver detalle →
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </>
  );
};

export default MisVehiculosPage;
