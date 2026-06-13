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

const GraficoIngresos = ({ reporte, cargando, periodoActivo }) => {
  const actual = Number(reporte?.ingreso_bruto ?? 0);
  const comparacion = Number(reporte?.ingreso_bruto_comparacion ?? 0);
  const maximo = Math.max(actual, comparacion, 1);
  const barras = [
    {
      label: periodoActivo.label,
      valor: actual,
      className: "bg-autospot-accent",
    },
    {
      label: "Comparación",
      valor: comparacion,
      className: "bg-[#d8c7b0]",
    },
  ];

  return (
    <article className="rounded-lg border border-autospot-border bg-autospot-white p-4 sm:p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-base font-black text-autospot-black">
            Comparativa de ingresos
          </h2>
          <p className="mt-1 text-sm font-semibold text-autospot-muted">
            {periodoActivo.comparacion}
          </p>
        </div>
        <IndicadorVariacion reporte={reporte} cargando={cargando} />
      </div>

      <div className="mt-5 rounded-lg border border-autospot-border bg-[#fafaf9] p-4">
        <div className="relative h-56 overflow-hidden rounded-md bg-white px-4 pb-12 pt-4 sm:h-64 sm:px-8">
          <div className="absolute inset-x-4 top-4 h-px bg-autospot-border sm:inset-x-8" />
          <div className="absolute inset-x-4 top-1/3 h-px bg-autospot-border sm:inset-x-8" />
          <div className="absolute inset-x-4 top-2/3 h-px bg-autospot-border sm:inset-x-8" />
          <div className="absolute inset-x-4 bottom-12 h-px bg-autospot-black/20 sm:inset-x-8" />

          <div className="relative z-10 grid h-full grid-cols-2 items-end gap-5">
            {barras.map((barra) => {
              const alto = cargando
                ? 36
                : barra.valor > 0
                  ? Math.max((barra.valor / maximo) * 100, 8)
                  : 0;

              return (
                <div
                  key={barra.label}
                  className="flex h-full min-w-0 flex-col justify-end"
                >
                  <div className="mb-2 text-center text-xs font-black text-autospot-black sm:text-sm">
                    {cargando ? "..." : formatearMonto(barra.valor)}
                  </div>
                  <div className="flex h-[calc(100%-3rem)] items-end justify-center">
                    <div
                      className={`w-full max-w-28 rounded-t-md transition-all duration-300 ${barra.className} ${
                        cargando ? "animate-pulse opacity-60" : ""
                      }`}
                      style={{ height: `${alto}%` }}
                      aria-hidden="true"
                    />
                  </div>
                  <p className="mt-3 truncate text-center text-xs font-bold text-autospot-muted">
                    {barra.label}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {!cargando && actual === 0 && comparacion === 0 && (
          <p className="mt-3 text-center text-sm font-semibold text-autospot-muted">
            Sin ingresos registrados en los períodos comparados.
          </p>
        )}
      </div>
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
