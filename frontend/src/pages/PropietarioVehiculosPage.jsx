import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  AlertCircle,
  ArrowRight,
  Car,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  Plus,
} from "lucide-react";
import { useAuth } from "../features/auth/hooks/useAuth";
import { listarVehiculosDelPropietario } from "../features/vehiculos/api/vehiculoService";

const AUTOS_PAGE_SIZE = 5;

const formatearMonto = (valor) => {
  if (valor === null || valor === undefined || valor === "") return "Sin definir";
  const numero = Number(valor);
  if (Number.isNaN(numero)) return `$${valor}`;
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0,
  }).format(numero);
};

const obtenerEstadoVehiculo = (vehiculo) => {
  const estado = (vehiculo?.estado_registro || "").toUpperCase();

  if (estado === "HABILITADO" || estado === "APROBADO") {
    if (vehiculo?.disponible) {
      return {
        label: "Disponible en estación",
        detalle: "Esperando alquiler",
        className: "bg-[#dcfce7] text-[#166534] border-[#bbf7d0]",
      };
    }
    if (vehiculo?.alquilado) {
      return {
        label: "Alquilado",
        detalle: "Con alquiler activo",
        className: "bg-[#dbeafe] text-[#1d4ed8] border-[#bfdbfe]",
      };
    }
    return {
      label: "No disponible",
      detalle: "Pausado por el propietario",
      className: "bg-[#f3f4f6] text-[#374151] border-[#e5e7eb]",
    };
  }

  if (estado === "EN_REVISION") {
    return {
      label: "En revisión",
      detalle: "Documentación pendiente",
      className: "bg-[#fef3c7] text-[#92400e] border-[#fde68a]",
    };
  }

  if (estado === "RECHAZADO") {
    return {
      label: "Rechazado",
      detalle: "Requiere corrección",
      className: "bg-[#fef2f2] text-[#b42318] border-[#fecaca]",
    };
  }

  return {
    label: "Pendiente",
    detalle: "Carga incompleta",
    className: "bg-[#f3f4f6] text-[#374151] border-[#e5e7eb]",
  };
};

const PropietarioVehiculosPage = () => {
  const location = useLocation();
  const { usuario } = useAuth();

  const [vehiculos, setVehiculos] = useState([]);
  const [cargandoVehiculos, setCargandoVehiculos] = useState(true);
  const [errorVehiculos, setErrorVehiculos] = useState("");
  const [paginaAutos, setPaginaAutos] = useState(1);
  const [paginaAlquileres, setPaginaAlquileres] = useState(1);

  const mensaje = location.state?.message;

  useEffect(() => {
    if (!usuario?.id) return;

    let cancelado = false;

    const cargarVehiculos = async () => {
      setCargandoVehiculos(true);
      setErrorVehiculos("");

      try {
        const data = await listarVehiculosDelPropietario(usuario.id);
        if (!cancelado) setVehiculos(Array.isArray(data) ? data : []);
      } catch {
        if (!cancelado) {
          setErrorVehiculos("No se pudieron cargar tus vehículos publicados.");
        }
      } finally {
        if (!cancelado) setCargandoVehiculos(false);
      }
    };

    cargarVehiculos();

    return () => {
      cancelado = true;
    };
  }, [usuario?.id]);

  const resumen = useMemo(() => {
    const activos = vehiculos.filter(
      (vehiculo) =>
        ["HABILITADO", "APROBADO"].includes(
          (vehiculo.estado_registro || "").toUpperCase(),
        ) && vehiculo.disponible,
    ).length;
    const enRevision = vehiculos.filter(
      (vehiculo) => (vehiculo.estado_registro || "").toUpperCase() === "EN_REVISION",
    ).length;

    return {
      total: vehiculos.length,
      activos,
      enRevision,
      noDisponibles: Math.max(vehiculos.length - activos, 0),
    };
  }, [vehiculos]);

  const totalPaginasAutos = Math.max(
    Math.ceil(vehiculos.length / AUTOS_PAGE_SIZE),
    1,
  );
  const autosPagina = vehiculos.slice(
    (paginaAutos - 1) * AUTOS_PAGE_SIZE,
    paginaAutos * AUTOS_PAGE_SIZE,
  );

  return (
    <section className="w-full min-w-0">
      {mensaje && (
        <div className="mb-5 rounded-lg border border-[#bbf7d0] bg-[#f0fdf4] px-4 py-3 text-sm font-semibold text-[#166534]">
          {mensaje}
        </div>
      )}

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-3xl font-black leading-tight text-autospot-black sm:text-4xl">
            Vehículos
          </h1>
        </div>

        <Link
          to="/dashboard"
          className="inline-flex items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
        >
          <LayoutDashboard className="h-4 w-4" aria-hidden="true" />
          Ver dashboard
        </Link>
      </div>

      <section className="mb-6 grid gap-4 md:grid-cols-3">
        <StatCard
          icono={Car}
          titulo="Autos activos"
          valor={resumen.activos}
          detalle={`${resumen.total} auto${resumen.total === 1 ? "" : "s"} publicado${resumen.total === 1 ? "" : "s"}`}
        />
        <StatCard
          icono={ClipboardList}
          titulo="En revisión"
          valor={resumen.enRevision}
          detalle="Documentación pendiente"
        />
        <StatCard
          icono={AlertCircle}
          titulo="No disponibles"
          valor={resumen.noDisponibles}
          detalle="Autos pausados, alquilados o sin aprobar"
        />
      </section>

      <div className="grid gap-5 xl:grid-cols-[1fr_320px]">
        <div className="min-w-0 space-y-5">
          <section className="overflow-hidden rounded-lg border border-autospot-border bg-autospot-white">
            <div className="flex flex-col gap-3 border-b border-autospot-border px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-base font-black text-autospot-black">
                  Mi flota ({resumen.total})
                </h2>
              </div>
              <Link
                to="/vehiculos/listado"
                className="inline-flex items-center gap-2 text-sm font-bold text-autospot-accent"
              >
                Ver mis autos
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </div>

            {cargandoVehiculos && (
              <div className="divide-y divide-autospot-border">
                {[0, 1, 2, 3, 4].map((item) => (
                  <div key={item} className="h-20 animate-pulse bg-white/55" />
                ))}
              </div>
            )}

            {!cargandoVehiculos && errorVehiculos && (
              <div className="px-5 py-6 text-sm font-semibold text-[#b42318]">
                {errorVehiculos}
              </div>
            )}

            {!cargandoVehiculos && !errorVehiculos && vehiculos.length === 0 && (
              <div className="px-5 py-8 text-center">
                <p className="font-bold text-autospot-black">
                  Todavía no publicaste autos.
                </p>
                <Link
                  to="/propietario/publicar"
                  className="mt-4 inline-flex rounded-full bg-autospot-accent px-5 py-2.5 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
                >
                  Publicar auto
                </Link>
              </div>
            )}

            {!cargandoVehiculos && !errorVehiculos && vehiculos.length > 0 && (
              <>
                <div className="divide-y divide-autospot-border">
                  {autosPagina.map((vehiculo) => (
                    <VehiculoRow key={vehiculo.id} vehiculo={vehiculo} />
                  ))}
                </div>
                <Paginacion
                  page={paginaAutos}
                  pages={totalPaginasAutos}
                  total={vehiculos.length}
                  labelSingular="auto"
                  labelPlural="autos"
                  onChange={setPaginaAutos}
                />
              </>
            )}
          </section>

          <section className="overflow-hidden rounded-lg border border-autospot-border bg-autospot-white">
            <div className="flex flex-col gap-3 border-b border-autospot-border px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-base font-black text-autospot-black">
                  Últimos alquileres
                </h2>
              </div>
            </div>

            <div className="px-5 py-8">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#efe9df] text-autospot-accent">
                  <ClipboardList className="h-5 w-5" aria-hidden="true" />
                </span>
                <div>
                  <p className="font-bold text-autospot-black">
                    Próximo a implementar.
                  </p>
                  <p className="mt-1 text-sm text-autospot-muted">
                    El historial de alquileres del propietario todavía no tiene
                    endpoint dedicado.
                  </p>
                </div>
              </div>
            </div>

            <Paginacion
              page={paginaAlquileres}
              pages={1}
              total={0}
              labelSingular="alquiler"
              labelPlural="alquileres"
              onChange={setPaginaAlquileres}
            />
          </section>
        </div>

        <aside className="space-y-5">
          <section className="rounded-lg border border-autospot-border bg-autospot-white p-5">
            <h2 className="text-base font-black text-autospot-black">
              Acciones de vehículos
            </h2>
            <div className="mt-4 grid gap-3">
              <Link
                to="/propietario/publicar"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
              >
                <Plus className="h-4 w-4" aria-hidden="true" />
                Publicar auto
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
              >
                <LayoutDashboard className="h-4 w-4" aria-hidden="true" />
                Ver dashboard
              </Link>
            </div>
          </section>

          <section className="rounded-lg border border-autospot-border bg-autospot-white p-5">
            <h2 className="text-base font-black text-autospot-black">
              Publicaciones
            </h2>
            <div className="mt-4 flex items-center gap-3">
              <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#efe9df] text-autospot-accent">
                <Car className="h-5 w-5" aria-hidden="true" />
              </span>
              <div>
                <p className="font-black text-autospot-black">
                  {resumen.noDisponibles} auto
                  {resumen.noDisponibles === 1 ? "" : "s"} no disponible
                  {resumen.noDisponibles === 1 ? "" : "s"}
                </p>
                <p className="mt-1 text-sm text-autospot-muted">
                  También convivís con autos activos en el panel.
                </p>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </section>
  );
};

const StatCard = ({ destacado = false, icono: Icono, titulo, valor, detalle }) => (
  <article
    className={`rounded-lg border p-5 ${
      destacado
        ? "border-autospot-black bg-autospot-black text-white"
        : "border-autospot-border bg-autospot-white text-autospot-black"
    }`}
  >
    <div className="flex items-start justify-between gap-4">
      <div className="min-w-0">
        <p className={`text-xs font-bold uppercase ${destacado ? "text-white/60" : "text-autospot-muted"}`}>
          {titulo}
        </p>
        <p className={`mt-2 break-words text-2xl font-black ${destacado ? "text-white" : "text-autospot-black"}`}>
          {valor}
        </p>
        <p className={`mt-1 text-xs ${destacado ? "text-white/60" : "text-autospot-muted"}`}>
          {detalle}
        </p>
      </div>
      <span
        className={`inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
          destacado ? "bg-white/10 text-white" : "bg-white text-autospot-accent"
        }`}
      >
        <Icono className="h-5 w-5" aria-hidden="true" />
      </span>
    </div>
  </article>
);

const VehiculoRow = ({ vehiculo }) => {
  const estado = obtenerEstadoVehiculo(vehiculo);

  return (
    <Link
      to={`/vehiculos/${vehiculo.id}/detalle`}
      className="grid gap-4 px-5 py-4 transition hover:bg-[#fafaf9] md:grid-cols-[minmax(0,1fr)_minmax(140px,0.55fr)_auto] md:items-center"
    >
      <div className="flex min-w-0 items-center gap-3">
        <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#efe9df] text-autospot-accent">
          <Car className="h-5 w-5" aria-hidden="true" />
        </span>
        <div className="min-w-0">
          <h3 className="truncate text-sm font-black text-autospot-black">
            {vehiculo.marca} {vehiculo.modelo} {vehiculo.anio || ""}
            {vehiculo.patente ? ` - ${vehiculo.patente}` : ""}
          </h3>
          <p className="mt-1 truncate text-xs text-autospot-muted">
            {vehiculo.estacion || "Sin estación"} -{" "}
            {vehiculo.categoria || "Sin categoría"}
          </p>
        </div>
      </div>

      <div className="text-sm">
        <p className="font-black text-autospot-black">
          {formatearMonto(vehiculo.precio_por_dia)}
        </p>
        <p className="mt-1 text-xs text-autospot-muted">Precio diario</p>
      </div>

      <div className="flex items-center justify-between gap-3 md:justify-end">
        <div className="text-right">
          <span
            className={`inline-flex rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${estado.className}`}
          >
            {estado.label}
          </span>
          <p className="mt-1 text-xs text-autospot-muted">{estado.detalle}</p>
        </div>
        <ChevronRight className="h-4 w-4 shrink-0 text-autospot-accent" aria-hidden="true" />
      </div>
    </Link>
  );
};

const Paginacion = ({
  page,
  pages,
  total,
  labelSingular,
  labelPlural,
  onChange,
}) => (
  <div className="flex flex-col gap-3 border-t border-autospot-border px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
    <p className="text-sm font-semibold text-autospot-muted">
      {total} {total === 1 ? labelSingular : labelPlural}
    </p>
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="inline-flex h-10 items-center gap-2 rounded-full border border-autospot-border bg-white px-4 text-sm font-bold text-autospot-black transition hover:border-autospot-accent disabled:cursor-not-allowed disabled:opacity-45"
      >
        <ChevronLeft className="h-4 w-4" aria-hidden="true" />
        Anterior
      </button>
      <span className="px-2 text-sm font-bold text-autospot-muted">
        {page} / {pages}
      </span>
      <button
        type="button"
        onClick={() => onChange(page + 1)}
        disabled={page >= pages}
        className="inline-flex h-10 items-center gap-2 rounded-full border border-autospot-border bg-white px-4 text-sm font-bold text-autospot-black transition hover:border-autospot-accent disabled:cursor-not-allowed disabled:opacity-45"
      >
        Siguiente
        <ChevronRight className="h-4 w-4" aria-hidden="true" />
      </button>
    </div>
  </div>
);

export default PropietarioVehiculosPage;
