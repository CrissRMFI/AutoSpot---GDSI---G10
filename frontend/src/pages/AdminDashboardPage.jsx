import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertCircle,
  ArrowRight,
  Car,
  ClipboardCheck,
  FileText,
  Inbox,
  KeyRound,
} from "lucide-react";
import { getSolicitudesDocumentacion } from "../features/admin/api/solicitudesApi";
import { listarCheckins } from "../features/reservas/api/checkinService";
import {
  listarRecepcionAutos,
  listarReservasParaEntregar,
} from "../features/reservas/api/reservasService";
import { listarReportesAdmin } from "../features/reportes/api/reportesService";

const RECEPCION_PAGE_SIZE = 50;

const esRecepcionNoFinalizada = (reserva) =>
  (reserva?.estado || "").toUpperCase() !== "FINALIZADA";

const contarRecepcionNoFinalizada = async () => {
  const primeraPagina = await listarRecepcionAutos({
    page: 1,
    size: RECEPCION_PAGE_SIZE,
  });
  const paginas = Math.max(Number(primeraPagina?.pages || 1), 1);
  let items = Array.isArray(primeraPagina?.items) ? primeraPagina.items : [];

  if (paginas > 1) {
    const restantes = await Promise.all(
      Array.from({ length: paginas - 1 }, (_, index) =>
        listarRecepcionAutos({
          page: index + 2,
          size: RECEPCION_PAGE_SIZE,
        }),
      ),
    );
    items = items.concat(
      restantes.flatMap((pagina) =>
        Array.isArray(pagina?.items) ? pagina.items : [],
      ),
    );
  }

  return items.filter(esRecepcionNoFinalizada).length;
};

const AdminDashboardPage = () => {
  const [solicitudes, setSolicitudes] = useState([]);
  const [checkins, setCheckins] = useState([]);
  const [reservasParaEntregar, setReservasParaEntregar] = useState([]);
  const [totalRecepcion, setTotalRecepcion] = useState(0);
  const [totalIncidentes, setTotalIncidentes] = useState(0);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let cancelado = false;

    const cargarPanel = async () => {
      setCargando(true);

      const [
        solicitudesResult,
        checkinsResult,
        entregasResult,
        recepcionResult,
        incidentesResult,
      ] = await Promise.allSettled([
        getSolicitudesDocumentacion(),
        listarCheckins(),
        listarReservasParaEntregar(),
        contarRecepcionNoFinalizada(),
        listarReportesAdmin({ estado: "ACTIVO" }),
      ]);

      if (cancelado) return;

      if (solicitudesResult.status === "fulfilled") {
        setSolicitudes(
          Array.isArray(solicitudesResult.value) ? solicitudesResult.value : [],
        );
      }

      if (checkinsResult.status === "fulfilled") {
        setCheckins(
          Array.isArray(checkinsResult.value) ? checkinsResult.value : [],
        );
      }

      if (entregasResult.status === "fulfilled") {
        setReservasParaEntregar(
          Array.isArray(entregasResult.value) ? entregasResult.value : [],
        );
      }

      if (recepcionResult.status === "fulfilled") {
        setTotalRecepcion(Number(recepcionResult.value || 0));
      }

      if (incidentesResult.status === "fulfilled") {
        setTotalIncidentes(
          Array.isArray(incidentesResult.value) ? incidentesResult.value.length : 0,
        );
      }

      setCargando(false);
    };

    cargarPanel();

    return () => {
      cancelado = true;
    };
  }, []);

  const resumen = useMemo(() => {
    const checkinsPendientes = checkins.filter(
      (checkin) => (checkin.estado || "").toUpperCase() === "PENDIENTE",
    ).length;

    return {
      documentos: solicitudes.length,
      checkinsPendientes,
      entregas: reservasParaEntregar.length,
      recepcion: totalRecepcion,
      incidentes: totalIncidentes,
    };
  }, [
    checkins,
    reservasParaEntregar.length,
    solicitudes.length,
    totalRecepcion,
    totalIncidentes,
  ]);

  return (
    <section className="w-full min-w-0">
      <div className="mb-6 min-w-0">
        <h1 className="text-3xl font-black leading-tight text-autospot-black sm:text-4xl">
          Panel administrativo
        </h1>
      </div>

      <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          destacado
          icono={FileText}
          titulo="Documentos a revisar"
          valor={cargando ? "..." : resumen.documentos}
          detalle="Pendientes de validación"
          to="/admin/solicitudes-documentacion"
        />
        <StatCard
          icono={ClipboardCheck}
          titulo="Check-ins pendientes"
          valor={cargando ? "..." : resumen.checkinsPendientes}
          detalle="Con fotos obligatorias"
          to="/admin/checkins/revision"
        />
        <StatCard
          icono={AlertCircle}
          titulo="Incidentes abiertos"
          valor={cargando ? "..." : resumen.incidentes}
          detalle="Pendientes de resolución"
          to="/admin/incidentes"
        />
      </section>

      <section className="w-full overflow-hidden rounded-lg border border-autospot-border bg-autospot-white">
        <div className="border-b border-autospot-border px-5 py-4">
          <h2 className="text-base font-black text-autospot-black">
            Tareas prioritarias
          </h2>
        </div>

        <div className="divide-y divide-autospot-border">
          <TaskRow
            icono={FileText}
            titulo="Validar documentación"
            detalle={`${resumen.documentos} solicitud${resumen.documentos === 1 ? "" : "es"} pendiente${resumen.documentos === 1 ? "" : "s"}`}
            to="/admin/solicitudes-documentacion"
          />
          <TaskRow
            icono={KeyRound}
            titulo="Verificar reservas"
            detalle="Buscar por código y aprobar o rechazar"
            to="/admin/reservas/verificar"
          />
          <TaskRow
            icono={Car}
            titulo="Entrega de autos"
            detalle={`${resumen.entregas} reserva${resumen.entregas === 1 ? "" : "s"} lista${resumen.entregas === 1 ? "" : "s"} para entregar`}
            to="/admin/entrega"
          />
          <TaskRow
            icono={Inbox}
            titulo="Recepción de autos"
            detalle={`${resumen.recepcion} alquiler${resumen.recepcion === 1 ? "" : "es"} en recepción o checkout`}
            to="/admin/recepcion"
          />
        </div>
      </section>
    </section>
  );
};

const StatCard = ({
  destacado = false,
  icono: Icono,
  titulo,
  valor,
  detalle,
  to,
}) => {
  const className = `block rounded-lg border p-5 ${
    destacado
      ? "border-autospot-black bg-autospot-black text-white"
      : "border-autospot-border bg-autospot-white text-autospot-black"
  } ${to ? "transition hover:-translate-y-0.5 hover:shadow-[0_12px_30px_rgba(15,23,42,0.12)]" : ""}`;

  const contenido = (
    <div className="flex items-start justify-between gap-4">
      <div className="min-w-0">
        <p
          className={`text-xs font-bold uppercase ${destacado ? "text-white/60" : "text-autospot-muted"}`}
        >
          {titulo}
        </p>
        <p
          className={`mt-2 break-words text-2xl font-black ${destacado ? "text-white" : "text-autospot-black"}`}
        >
          {valor}
        </p>
        <p
          className={`mt-1 text-xs ${destacado ? "text-white/60" : "text-autospot-muted"}`}
        >
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
  );

  if (to) {
    return (
      <Link to={to} className={className}>
        {contenido}
      </Link>
    );
  }

  return <article className={className}>{contenido}</article>;
};

const TaskRow = ({ icono: Icono, titulo, detalle, to }) => (
  <Link
    to={to}
    className="grid gap-4 px-5 py-4 transition hover:bg-[#fafaf9] sm:grid-cols-[auto_minmax(0,1fr)_auto] sm:items-center"
  >
    <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-[#efe9df] text-autospot-accent">
      <Icono className="h-5 w-5" aria-hidden="true" />
    </span>
    <div className="min-w-0">
      <h3 className="text-sm font-black text-autospot-black">{titulo}</h3>
      <p className="mt-1 text-sm text-autospot-muted">{detalle}</p>
    </div>
    <span className="inline-flex items-center gap-2 text-sm font-bold text-autospot-accent">
      Abrir
      <ArrowRight className="h-4 w-4" aria-hidden="true" />
    </span>
  </Link>
);

export default AdminDashboardPage;
