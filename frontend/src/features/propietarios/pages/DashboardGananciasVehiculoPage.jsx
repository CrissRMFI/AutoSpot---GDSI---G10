import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  BarChart3,
  CalendarDays,
  Car,
  CircleDollarSign,
  Clock3,
  History,
  Minus,
  Percent,
  TrendingDown,
  TrendingUp,
  Wallet,
} from "lucide-react";
import EvolucionMensualChart from "../components/EvolucionMensualChart";
import { obtenerGananciasVehiculo } from "../api/gananciasService";

const PERIODOS_GANANCIAS_VEHICULO = [
  {
    valor: "esta_semana",
    label: "Esta semana",
    comparacion: "vs semana anterior",
    icono: CalendarDays,
  },
  {
    valor: "este_mes",
    label: "Este mes",
    comparacion: "vs mes anterior",
    icono: CalendarDays,
  },
  {
    valor: "mes_anterior",
    label: "Mes anterior",
    comparacion: "vs mes previo",
    icono: History,
  },
  {
    valor: "anio_actual",
    label: "Reporte por año",
    comparacion: "vs año anterior",
    icono: BarChart3,
  },
];

const DESCRIPCION_GRAFICO_PERIODO = {
  esta_semana: "Días de la semana",
  este_mes: "Semanas del mes actual",
  mes_anterior: "Semanas del mes anterior",
  anio_actual: "Meses del año",
};

const formatearMonto = (valor) => {
  if (valor === null || valor === undefined || valor === "") return "$0";
  const numero = Number(valor);
  if (Number.isNaN(numero)) return `$${valor}`;
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0,
  }).format(numero);
};

const formatearNumero = (valor) => {
  const numero = Number(valor ?? 0);
  return new Intl.NumberFormat("es-AR", {
    maximumFractionDigits: 2,
  }).format(Number.isNaN(numero) ? 0 : numero);
};

const formatearPorcentaje = (valor) => `${formatearNumero(valor)}%`;

const formatearFecha = (valor) => {
  if (!valor) return "";
  return new Intl.DateTimeFormat("es-AR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(valor));
};

const formatearFechaHasta = (valor) => {
  if (!valor) return "";
  const fecha = new Date(valor);
  fecha.setMilliseconds(fecha.getMilliseconds() - 1);
  return formatearFecha(fecha);
};

const DashboardGananciasVehiculoPage = () => {
  const { vehiculoId } = useParams();
  const [periodo, setPeriodo] = useState("esta_semana");
  const [reporte, setReporte] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!vehiculoId) return;

    let cancelado = false;

    const cargarReporte = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await obtenerGananciasVehiculo(vehiculoId, periodo);
        if (!cancelado) setReporte(data);
      } catch (err) {
        if (!cancelado) {
          if (err.response?.status === 404) {
            setError("No encontramos este auto asociado a tu cuenta.");
          } else {
            setError("No se pudo cargar el dashboard de ganancias del auto.");
          }
        }
      } finally {
        if (!cancelado) setCargando(false);
      }
    };

    cargarReporte();

    return () => {
      cancelado = true;
    };
  }, [vehiculoId, periodo]);

  const periodoActivo = useMemo(
    () =>
      PERIODOS_GANANCIAS_VEHICULO.find((item) => item.valor === periodo) ||
      PERIODOS_GANANCIAS_VEHICULO[0],
    [periodo],
  );

  const nombreVehiculo = reporte
    ? `${reporte.marca} ${reporte.modelo}`
    : "Dashboard de ganancias";

  return (
    <section className="w-full min-w-0">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <Link
            to={`/vehiculos/${vehiculoId}/detalle`}
            className="mb-3 inline-flex items-center gap-2 text-sm font-bold !text-autospot-accent transition hover:!text-[#5a1420]"
          >
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Volver al auto
          </Link>
          <h1 className="text-3xl font-black leading-tight text-autospot-black sm:text-4xl">
            Dashboard de ganancias
          </h1>
        </div>
      </div>

      {error && (
        <div className="mb-5 rounded-lg border border-[#fecaca] bg-[#fef2f2] px-4 py-3 text-sm font-semibold text-[#b42318]">
          {error}
        </div>
      )}

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="min-w-0 space-y-4">
          <SelectorPeriodo
            periodo={periodo}
            onPeriodoChange={setPeriodo}
          />

          <div className="grid gap-4 md:grid-cols-3">
            <MetricaCard
              destacado
              icono={CircleDollarSign}
              titulo="Ingreso bruto"
              valor={cargando ? "Cargando..." : formatearMonto(reporte?.ingreso_bruto)}
              detalle={`${reporte?.reservas_finalizadas ?? 0} alquiler${reporte?.reservas_finalizadas === 1 ? "" : "es"} finalizado${reporte?.reservas_finalizadas === 1 ? "" : "s"}`}
            />
            <MetricaCard
              icono={Percent}
              titulo="Comisión plataforma"
              valor={cargando ? "Cargando..." : formatearMonto(reporte?.comision_plataforma)}
              detalle="20% del ingreso bruto"
            />
            <MetricaCard
              icono={Wallet}
              titulo="Ganancia neta"
              valor={cargando ? "Cargando..." : formatearMonto(reporte?.ganancia_neta)}
              detalle="80% para el propietario"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <MetricaCard
              icono={Clock3}
              titulo="Días alquilados"
              valor={cargando ? "Cargando..." : formatearNumero(reporte?.dias_alquilados)}
              detalle={`${formatearNumero(reporte?.dias_disponibles)} días disponibles`}
            />
            <MetricaCard
              icono={Car}
              titulo="Tasa de ocupación"
              valor={cargando ? "Cargando..." : formatearPorcentaje(reporte?.tasa_ocupacion)}
              detalle="Uso sobre disponibilidad del período"
            />
            <MetricaCard
              icono={BarChart3}
              titulo="Comparación"
              valor={
                cargando
                  ? "Cargando..."
                  : formatearMonto(reporte?.ingreso_bruto_comparacion)
              }
              detalle={periodoActivo.comparacion}
            />
          </div>

          <GraficoIngresos
            reporte={reporte}
            cargando={cargando}
            periodo={periodo}
            periodoActivo={periodoActivo}
          />
        </div>

        <aside className="space-y-4">
          <FichaVehiculo
            cargando={cargando}
            reporte={reporte}
            nombreVehiculo={nombreVehiculo}
          />
          <OcupacionPanel reporte={reporte} cargando={cargando} />
        </aside>
      </section>
    </section>
  );
};

const SelectorPeriodo = ({ periodo, onPeriodoChange }) => (
  <div className="grid gap-2 rounded-lg border border-autospot-border bg-white p-2 sm:grid-cols-2 xl:grid-cols-4">
    {PERIODOS_GANANCIAS_VEHICULO.map((item) => {
      const activo = item.valor === periodo;
      const Icono = item.icono;
      return (
        <button
          key={item.valor}
          type="button"
          onClick={() => onPeriodoChange(item.valor)}
          className={`flex min-h-16 items-center gap-3 rounded-md border px-3 py-3 text-left transition ${
            activo
              ? "border-autospot-black bg-autospot-black text-white shadow-sm"
              : "border-transparent bg-[#fafaf9] text-autospot-black hover:border-autospot-border"
          }`}
        >
          <span
            className={`inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md ${
              activo ? "bg-white/10 text-white" : "bg-white text-autospot-accent"
            }`}
          >
            <Icono className="h-4 w-4" aria-hidden="true" />
          </span>
          <span className="min-w-0">
            <span className="block text-sm font-black leading-tight">
              {item.label}
            </span>
            <span
              className={`mt-1 block text-xs font-semibold ${
                activo ? "text-white/65" : "text-autospot-muted"
              }`}
            >
              {item.comparacion}
            </span>
          </span>
        </button>
      );
    })}
  </div>
);

const MetricaCard = ({ destacado = false, icono: Icono, titulo, valor, detalle }) => (
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

const FichaVehiculo = ({ cargando, reporte, nombreVehiculo }) => (
  <article className="rounded-lg border border-autospot-border bg-autospot-white p-5">
    <div className="flex items-start gap-3">
      <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-[#efe9df] text-autospot-accent">
        <Car className="h-5 w-5" aria-hidden="true" />
      </span>
      <div className="min-w-0">
        <p className="text-xs font-bold uppercase text-autospot-muted">
          Unidad
        </p>
        <h2 className="mt-1 break-words text-xl font-black text-autospot-black">
          {cargando ? "Cargando auto..." : nombreVehiculo}
        </h2>
      </div>
    </div>

    <dl className="mt-5 space-y-3 text-sm">
      <DatoFicha label="Patente" valor={reporte?.patente || "Sin patente"} />
      <DatoFicha label="Marca" valor={reporte?.marca || "-"} />
      <DatoFicha label="Modelo" valor={reporte?.modelo || "-"} />
      <DatoFicha label="Categoría" valor={reporte?.categoria || "-"} />
    </dl>

    <div className="mt-5 rounded-lg border border-autospot-border bg-[#fafaf9] px-4 py-3 text-sm">
      <p className="font-bold text-autospot-black">
        {formatearFecha(reporte?.fecha_desde)} - {formatearFechaHasta(reporte?.fecha_hasta)}
      </p>
    </div>
  </article>
);

const DatoFicha = ({ label, valor }) => (
  <div className="flex items-center justify-between gap-3">
    <dt className="text-autospot-muted">{label}</dt>
    <dd className="break-words text-right font-black text-autospot-black">
      {valor}
    </dd>
  </div>
);

const OcupacionPanel = ({ reporte, cargando }) => {
  const tasa = Math.max(0, Math.min(Number(reporte?.tasa_ocupacion ?? 0), 100));

  return (
    <article className="rounded-lg border border-autospot-border bg-autospot-white p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-black text-autospot-black">
          Ocupación
        </h2>
        <span className="rounded-full bg-[#efe9df] px-3 py-1 text-xs font-black text-autospot-accent">
          {cargando ? "..." : formatearPorcentaje(reporte?.tasa_ocupacion)}
        </span>
      </div>

      <div className="mt-5 h-3 overflow-hidden rounded-full bg-[#f1ece5]">
        <div
          className={`h-full rounded-full bg-autospot-accent transition-all duration-300 ${
            cargando ? "animate-pulse" : ""
          }`}
          style={{ width: `${cargando ? 42 : tasa}%` }}
          aria-hidden="true"
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-lg border border-autospot-border bg-[#fafaf9] p-3">
          <p className="text-xs font-bold uppercase text-autospot-muted">
            Alquilados
          </p>
          <p className="mt-1 text-lg font-black text-autospot-black">
            {cargando ? "..." : formatearNumero(reporte?.dias_alquilados)}
          </p>
        </div>
        <div className="rounded-lg border border-autospot-border bg-[#fafaf9] p-3">
          <p className="text-xs font-bold uppercase text-autospot-muted">
            Disponibles
          </p>
          <p className="mt-1 text-lg font-black text-autospot-black">
            {cargando ? "..." : formatearNumero(reporte?.dias_disponibles)}
          </p>
        </div>
      </div>
    </article>
  );
};

const etiquetaComparacionPeriodo = (periodoActivo) => {
  const base =
    (periodoActivo?.comparacion || "").replace(/^vs\s+/i, "") || "Período anterior";
  return base.charAt(0).toUpperCase() + base.slice(1);
};

const GraficoIngresos = ({ reporte, cargando, periodo, periodoActivo }) => {
  const descripcionGrafico =
    DESCRIPCION_GRAFICO_PERIODO[periodo] || "Evolución del período";

  return (
    <article className="rounded-lg border border-autospot-border bg-autospot-white p-4 sm:p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-base font-black text-autospot-black">
            Evolución de la unidad
          </h2>
          <p className="mt-1 text-sm font-semibold text-autospot-muted">
            {descripcionGrafico} · ingresos y ocupación · {periodoActivo.comparacion}
          </p>
        </div>
        <IndicadorVariacion reporte={reporte} cargando={cargando} />
      </div>

      <EvolucionMensualChart
        datos={reporte?.evolucion_periodo}
        datosComparacion={reporte?.evolucion_comparacion}
        etiquetaActual="Período actual"
        etiquetaComparacion={etiquetaComparacionPeriodo(periodoActivo)}
        cargando={cargando}
        mostrarOcupacion
        emptyMessage="Sin ingresos registrados para esta unidad en este período."
      />
    </article>
  );
};

const IndicadorVariacion = ({ reporte, cargando }) => {
  if (cargando) {
    return <p className="text-sm font-bold text-autospot-muted">Calculando comparación...</p>;
  }

  if (!reporte) {
    return <p className="text-sm font-bold text-autospot-muted">Sin datos de comparación.</p>;
  }

  const direccion = reporte.direccion_variacion;
  const porcentaje = reporte.porcentaje_variacion;
  const sube = direccion === "SUBE";
  const baja = direccion === "BAJA";
  const Icono = sube ? TrendingUp : baja ? TrendingDown : Minus;
  const className = sube
    ? "border-[#bbf7d0] bg-[#f0fdf4] text-[#166534]"
    : baja
      ? "border-[#fecaca] bg-[#fef2f2] text-[#b42318]"
      : "border-autospot-border bg-white text-autospot-muted";

  let texto = "Sin cambios respecto del período anterior.";
  if (direccion === "SIN_COMPARACION") {
    texto = "Sin base previa para comparar.";
  } else if (sube || baja) {
    texto = `${porcentaje}% ${sube ? "de crecimiento" : "de caída"} de ingresos.`;
  }

  return (
    <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-black ${className}`}>
      <Icono className="h-4 w-4" aria-hidden="true" />
      {texto}
    </div>
  );
};

export default DashboardGananciasVehiculoPage;
