import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  AlertTriangle,
  ArrowRight,
  CalendarDays,
  Car,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  FileCheck,
  MapPin,
} from "lucide-react";
import ProximamenteModal from "../components/ProximamenteModal";
import { useAuth } from "../features/auth/hooks/useAuth";
import { obtenerDocumentacionHabilitante } from "../features/usuarios/api/documentacionHabilitanteService";
import { listarMisAlquileres } from "../features/reservas/api/reservasService";
import {
  formatearFechaHora,
  formatearMonto,
} from "../features/reservas/utils/reservaFormatters";

const PAGE_SIZE = 10;
const ESTADOS_ACTIVOS = new Set([
  "EN_CURSO",
  "ENTREGA_SOLICITADA",
  "DEVUELTO",
  "CHECKOUT_PENDIENTE",
]);

const ESTADO_ALQUILER_UI = {
  EN_CURSO: {
    label: "En curso",
    className: "bg-[#dcfce7] text-[#166534] border-[#bbf7d0]",
  },
  ENTREGA_SOLICITADA: {
    label: "Esperando recepción",
    className: "bg-[#fef3c7] text-[#92400e] border-[#fde68a]",
  },
  DEVUELTO: {
    label: "Recibido",
    className: "bg-[#e0f2fe] text-[#0369a1] border-[#bae6fd]",
  },
  CHECKOUT_PENDIENTE: {
    label: "Checkout realizado",
    className: "bg-[#dbeafe] text-[#1d4ed8] border-[#bfdbfe]",
  },
  FINALIZADA: {
    label: "Completado",
    className: "bg-[#f3f4f6] text-[#374151] border-[#e5e7eb]",
  },
};

const formatEstadoHabilitacion = (estado) => {
  switch (estado) {
    case "PENDIENTE_REVISION":
      return {
        label: "En revisión",
        className: "bg-[#fef9c3] text-[#854d0e] border-[#fef08a]",
      };
    case "APROBADO":
      return {
        label: "Aprobada",
        className: "bg-[#f0fdf4] text-[#166534] border-[#bbf7d0]",
      };
    case "RECHAZADO":
      return {
        label: "Rechazada",
        className: "bg-[#fef2f2] text-[#b42318] border-[#fecaca]",
      };
    default:
      return {
        label: "Sin documentación",
        className: "bg-[#f3f4f6] text-[#374151] border-[#e5e7eb]",
      };
  }
};

const nombrePresentable = (usuario) => {
  if (usuario?.nombre) return usuario.nombre;
  if (usuario?.first_name) return usuario.first_name;
  const local = (usuario?.email || "").split("@")[0];
  return local || "Usuario";
};

const obtenerEstadoAlquiler = (estado) =>
  ESTADO_ALQUILER_UI[(estado || "").toUpperCase()] || {
    label: estado || "Sin estado",
    className: "bg-autospot-cream text-autospot-muted border-autospot-border",
  };

const esAlquilerActivo = (alquiler) =>
  ESTADOS_ACTIVOS.has((alquiler?.estado || "").toUpperCase());

const ClienteDashboardPage = () => {
  const location = useLocation();
  const { usuario } = useAuth();

  const [habilitacion, setHabilitacion] = useState(null);
  const [cargandoHabilitacion, setCargandoHabilitacion] = useState(false);
  const [paginaActual, setPaginaActual] = useState(1);
  const [paginaAlquileres, setPaginaAlquileres] = useState({
    items: [],
    total: 0,
    pages: 0,
  });
  const [resumenAlquileres, setResumenAlquileres] = useState({
    activos: 0,
    total: 0,
    alquilerActivo: null,
  });
  const [cargandoAlquileres, setCargandoAlquileres] = useState(true);
  const [errorAlquileres, setErrorAlquileres] = useState("");
  const [modalProximamente, setModalProximamente] = useState(null);

  const mensaje = location.state?.message;
  const nombreUsuario = nombrePresentable(usuario);

  useEffect(() => {
    const cargarHabilitacion = async () => {
      if (!usuario?.id) return;

      setCargandoHabilitacion(true);

      try {
        const data = await obtenerDocumentacionHabilitante(usuario.id);
        setHabilitacion(data);
      } catch {
        setHabilitacion(null);
      } finally {
        setCargandoHabilitacion(false);
      }
    };

    cargarHabilitacion();
  }, [usuario?.id]);

  useEffect(() => {
    let cancelado = false;

    const cargarResumen = async () => {
      try {
        const data = await listarMisAlquileres({ page: 1, size: 50 });
        if (cancelado) return;

        const items = Array.isArray(data.items) ? data.items : [];
        const activos = items.filter(esAlquilerActivo);
        setResumenAlquileres({
          activos: activos.length,
          total: data.total || 0,
          alquilerActivo: activos[0] || null,
        });
      } catch {
        if (!cancelado) {
          setResumenAlquileres({ activos: 0, total: 0, alquilerActivo: null });
        }
      }
    };

    cargarResumen();

    return () => {
      cancelado = true;
    };
  }, []);

  useEffect(() => {
    let cancelado = false;

    const cargarAlquileres = async () => {
      setCargandoAlquileres(true);
      setErrorAlquileres("");

      try {
        const data = await listarMisAlquileres({
          page: paginaActual,
          size: PAGE_SIZE,
        });
        if (cancelado) return;

        setPaginaAlquileres({
          items: Array.isArray(data.items) ? data.items : [],
          total: data.total || 0,
          pages: data.pages || 0,
        });
      } catch (err) {
        if (!cancelado) {
          setErrorAlquileres(
            err.response?.data?.detail ||
              "No se pudieron cargar tus alquileres.",
          );
        }
      } finally {
        if (!cancelado) setCargandoAlquileres(false);
      }
    };

    cargarAlquileres();

    return () => {
      cancelado = true;
    };
  }, [paginaActual]);

  const estadoHabilitacion = useMemo(
    () => formatEstadoHabilitacion(habilitacion?.estado_validacion),
    [habilitacion?.estado_validacion],
  );
  const alquilerActivo = resumenAlquileres.alquilerActivo;
  const vehiculoActivo = alquilerActivo?.vehiculo;
  const totalPaginas = Math.max(paginaAlquileres.pages, 1);

  return (
    <section className="w-full min-w-0">
      {mensaje && (
        <div className="mb-5 rounded-lg border border-[#bbf7d0] bg-[#f0fdf4] px-4 py-3 text-sm font-semibold text-[#166534]">
          {mensaje}
        </div>
      )}

      <div className="mb-6 flex min-w-0 flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <h1 className="text-3xl font-black leading-tight text-autospot-black sm:text-4xl">
            Buen día, {nombreUsuario}
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-autospot-muted">
            Tenés {resumenAlquileres.activos} alquiler
            {resumenAlquileres.activos === 1 ? "" : "es"} activo
            {resumenAlquileres.activos === 1 ? "" : "s"} y acceso al catálogo.
          </p>
        </div>

        <Link
          to="/catalogo"
          className="inline-flex shrink-0 items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
        >
          Explorar catálogo
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </Link>
      </div>

      <section className="mb-5 grid gap-3 md:grid-cols-3">
        <StatCard
          destacado
          icono={Car}
          titulo="Alquiler activo"
          valor={resumenAlquileres.activos}
          detalle={
            alquilerActivo
              ? `${vehiculoActivo?.marca || "Auto"} ${vehiculoActivo?.modelo || ""}`.trim()
              : "Sin alquiler activo"
          }
        />
        <StatCard
          icono={ClipboardList}
          titulo="Total de alquileres"
          valor={resumenAlquileres.total}
          detalle="Historial completo"
        />
        <StatCard
          icono={FileCheck}
          titulo="Documentación"
          valor={cargandoHabilitacion ? "..." : estadoHabilitacion.label}
          detalle="Estado de habilitación"
        />
      </section>

      <div className="grid gap-4 xl:grid-cols-[1fr_300px]">
        <div className="min-w-0 space-y-4">
          <section className="rounded-lg bg-autospot-black p-4 text-white">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="min-w-0">
                <h2 className="text-base font-black text-white">
                  Alquiler activo
                </h2>
                {alquilerActivo ? (
                  <>
                    <span
                      className={`mt-4 inline-flex rounded-full border px-3 py-1 text-xs font-bold ${
                        obtenerEstadoAlquiler(alquilerActivo.estado).className
                      }`}
                    >
                      {obtenerEstadoAlquiler(alquilerActivo.estado).label}
                    </span>
                    <h3 className="mt-3 text-xl font-black text-white">
                      {vehiculoActivo?.marca} {vehiculoActivo?.modelo}{" "}
                      {vehiculoActivo?.anio || ""}
                    </h3>
                    <p className="mt-1 text-sm text-white/65">
                      {alquilerActivo.estacion_retiro}
                      {vehiculoActivo?.patente
                        ? ` - Patente ${vehiculoActivo.patente}`
                        : ""}
                    </p>

                    <dl className="mt-5 grid gap-4 sm:grid-cols-2">
                      <DatoOscuro
                        label="Inicio registrado"
                        valor={formatearFechaHora(alquilerActivo.fecha_inicio)}
                      />
                      <DatoOscuro
                        label="Devolución estimada"
                        valor={formatearFechaHora(alquilerActivo.fecha_fin)}
                      />
                    </dl>
                  </>
                ) : (
                  <p className="mt-4 max-w-xl text-sm leading-6 text-white/65">
                    Cuando tengas un alquiler en curso, vas a verlo acá con sus
                    datos principales.
                  </p>
                )}
              </div>

              {alquilerActivo && (
                <Link
                  to={`/usuario/alquileres/${alquilerActivo.id}`}
                  className="inline-flex items-center justify-center gap-2 text-sm font-bold text-white transition hover:text-white/75"
                >
                  Ver detalles
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              )}
            </div>

            <button
              type="button"
              onClick={() => setModalProximamente("Reportar problema")}
              className="mt-5 inline-flex items-center justify-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:bg-autospot-cream"
            >
              <AlertTriangle className="h-4 w-4" aria-hidden="true" />
              Reportar problema
            </button>
          </section>

          <section className="overflow-hidden rounded-lg border border-autospot-border bg-autospot-white">
            <div className="flex flex-col gap-3 border-b border-autospot-border px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-base font-black text-autospot-black">
                  Historial reciente
                </h2>
              </div>
              <Link
                to="/usuario/alquileres"
                className="inline-flex items-center gap-2 text-sm font-bold text-autospot-accent"
              >
                Ver todo
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </div>

            {cargandoAlquileres && (
              <div className="divide-y divide-autospot-border">
                {[0, 1, 2].map((item) => (
                  <div key={item} className="h-20 animate-pulse bg-white/55" />
                ))}
              </div>
            )}

            {!cargandoAlquileres && errorAlquileres && (
              <div className="px-5 py-6 text-sm font-semibold text-[#b42318]">
                {errorAlquileres}
              </div>
            )}

            {!cargandoAlquileres &&
              !errorAlquileres &&
              paginaAlquileres.items.length === 0 && (
                <div className="px-5 py-8 text-center">
                  <p className="font-bold text-autospot-black">
                    Todavía no tenés alquileres.
                  </p>
                  <Link
                    to="/catalogo"
                    className="mt-4 inline-flex rounded-full bg-autospot-accent px-5 py-2.5 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
                  >
                    Ver catálogo
                  </Link>
                </div>
              )}

            {!cargandoAlquileres &&
              !errorAlquileres &&
              paginaAlquileres.items.length > 0 && (
                <>
                  <div className="divide-y divide-autospot-border">
                    {paginaAlquileres.items.map((alquiler) => (
                      <AlquilerRow key={alquiler.id} alquiler={alquiler} />
                    ))}
                  </div>
                  <Paginacion
                    page={paginaActual}
                    pages={totalPaginas}
                    total={paginaAlquileres.total}
                    onChange={setPaginaActual}
                  />
                </>
              )}
          </section>
        </div>

        <aside className="space-y-4">
          <section className="rounded-lg border border-autospot-border bg-autospot-white p-4">
            <h2 className="text-base font-black text-autospot-black">
              Acceso rápido
            </h2>
            <div className="mt-4 grid gap-3">
              <Link
                to="/catalogo"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
              >
                <Car className="h-4 w-4" aria-hidden="true" />
                Ir al catálogo
              </Link>
              <Link
                to="/usuario/alquileres"
                className="inline-flex items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
              >
                <CalendarDays className="h-4 w-4" aria-hidden="true" />
                Mis alquileres
              </Link>
            </div>
          </section>

          <section className="rounded-lg border border-autospot-border bg-autospot-white p-4">
            <h2 className="text-base font-black text-autospot-black">
              Habilitación
            </h2>
            <span
              className={`mt-4 inline-flex rounded-full border px-3 py-1 text-xs font-bold ${estadoHabilitacion.className}`}
            >
              {estadoHabilitacion.label}
            </span>
            <Link
              to="/documentacion-habilitante"
              className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
            >
              <FileCheck className="h-4 w-4" aria-hidden="true" />
              Ver documentación
            </Link>
          </section>
        </aside>
      </div>

      <ProximamenteModal
        abierto={Boolean(modalProximamente)}
        titulo={modalProximamente || undefined}
        onClose={() => setModalProximamente(null)}
      />
    </section>
  );
};

const StatCard = ({
  destacado = false,
  icono: Icono,
  titulo,
  valor,
  detalle,
}) => (
  <article
    className={`rounded-lg border p-4 ${
      destacado
        ? "border-autospot-black bg-autospot-black text-white"
        : "border-autospot-border bg-autospot-white text-autospot-black"
    }`}
  >
    <div className="flex items-start justify-between gap-4">
      <div className="min-w-0">
        <p
          className={`text-xs font-bold uppercase ${
            destacado ? "text-white/60" : "text-autospot-muted"
          }`}
        >
          {titulo}
        </p>
        <p
          className={`mt-2 truncate text-2xl font-black ${
            destacado ? "text-white" : "text-autospot-black"
          }`}
        >
          {valor}
        </p>
        <p
          className={`mt-1 truncate text-xs ${destacado ? "text-white/60" : "text-autospot-muted"}`}
        >
          {detalle}
        </p>
      </div>
      <span
        className={`inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
          destacado ? "bg-white/10 text-white" : "bg-white text-autospot-accent"
        }`}
      >
        <Icono className="h-4 w-4" aria-hidden="true" />
      </span>
    </div>
  </article>
);

const DatoOscuro = ({ label, valor }) => (
  <div className="min-w-0">
    <dt className="text-xs font-bold uppercase text-white/50">{label}</dt>
    <dd className="mt-1 truncate text-base font-bold text-white">{valor}</dd>
  </div>
);

const AlquilerRow = ({ alquiler }) => {
  const vehiculo = alquiler.vehiculo;
  const estado = obtenerEstadoAlquiler(alquiler.estado);

  return (
    <Link
      to={`/usuario/alquileres/${alquiler.id}`}
      className="grid gap-4 px-5 py-4 transition hover:bg-[#fafaf9] md:grid-cols-[minmax(0,1fr)_minmax(180px,0.8fr)_auto] md:items-center"
    >
      <div className="flex min-w-0 items-center gap-3">
        <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#efe9df] text-autospot-accent">
          <Car className="h-5 w-5" aria-hidden="true" />
        </span>
        <div className="min-w-0">
          <h3 className="truncate text-sm font-black text-autospot-black">
            {vehiculo?.marca} {vehiculo?.modelo} {vehiculo?.anio || ""}
          </h3>
          <p className="mt-1 truncate text-xs text-autospot-muted">
            {formatearFechaHora(alquiler.fecha_inicio)} ·{" "}
            {alquiler.estacion_retiro}
          </p>
        </div>
      </div>

      <div className="flex min-w-0 items-center gap-2 text-sm text-autospot-muted">
        <MapPin className="h-4 w-4 shrink-0" aria-hidden="true" />
        <span className="truncate">{vehiculo?.patente || "Sin patente"}</span>
      </div>

      <div className="flex items-center justify-between gap-3 md:justify-end">
        <div className="text-right">
          <p className="font-black text-autospot-black">
            {formatearMonto(alquiler.monto_total)}
          </p>
          <span
            className={`mt-1 inline-flex rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${estado.className}`}
          >
            {estado.label}
          </span>
        </div>
        <ChevronRight
          className="h-4 w-4 shrink-0 text-autospot-accent"
          aria-hidden="true"
        />
      </div>
    </Link>
  );
};

const Paginacion = ({ page, pages, total, onChange }) => (
  <div className="flex flex-col gap-3 border-t border-autospot-border px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
    <p className="text-sm font-semibold text-autospot-muted">
      {total} alquiler{total === 1 ? "" : "es"}
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

export default ClienteDashboardPage;
