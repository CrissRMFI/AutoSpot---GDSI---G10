import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  CalendarDays,
  CircleDollarSign,
  History,
  Minus,
  Percent,
  TrendingDown,
  TrendingUp,
  Wallet,
} from "lucide-react";
import { useAuth } from "../features/auth/hooks/useAuth";
import EvolucionMensualChart from "../features/propietarios/components/EvolucionMensualChart";
import { obtenerGananciasGenerales } from "../features/propietarios/api/gananciasService";

const PERIODOS_GANANCIAS = [
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
  este_mes: "Semanas del mes actual",
  mes_anterior: "Semanas del mes anterior",
  anio_actual: "Meses del año",
};

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

const PropietarioDashboardPage = () => {
  const location = useLocation();
  const { usuario } = useAuth();

  const [periodoGanancias, setPeriodoGanancias] = useState("este_mes");
  const [ganancias, setGanancias] = useState(null);
  const [cargandoGanancias, setCargandoGanancias] = useState(true);
  const [errorGanancias, setErrorGanancias] = useState("");

  const mensaje = location.state?.message;

  useEffect(() => {
    if (!usuario?.id) return;

    let cancelado = false;

    const cargarGanancias = async () => {
      setCargandoGanancias(true);
      setErrorGanancias("");

      try {
        const data = await obtenerGananciasGenerales(usuario.id, periodoGanancias);
        if (!cancelado) setGanancias(data);
      } catch {
        if (!cancelado) {
          setErrorGanancias("No se pudieron cargar las ganancias generales.");
        }
      } finally {
        if (!cancelado) setCargandoGanancias(false);
      }
    };

    cargarGanancias();

    return () => {
      cancelado = true;
    };
  }, [usuario?.id, periodoGanancias]);

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
            Dashboard general
          </h1>
        </div>
        <Link
          to="/vehiculos"
          className="inline-flex items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
        >
          Ver vehículos
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </Link>
      </div>

      <GananciasGeneralesSection
        periodo={periodoGanancias}
        reporte={ganancias}
        cargando={cargandoGanancias}
        error={errorGanancias}
        onPeriodoChange={setPeriodoGanancias}
      />
    </section>
  );
};

const GananciasGeneralesSection = ({
  periodo,
  reporte,
  cargando,
  error,
  onPeriodoChange,
}) => {
  const periodoActivo =
    PERIODOS_GANANCIAS.find((item) => item.valor === periodo) ||
    PERIODOS_GANANCIAS[0];

  return (
    <section id="ganancias-generales" className="mb-6 scroll-mt-6">
      <div className="flex flex-col gap-4">
        <div>
          <h2 className="text-base font-black text-autospot-black">
            Ganancias generales
          </h2>
        </div>
        <div className="grid gap-2 rounded-lg border border-autospot-border bg-white p-2 sm:grid-cols-3">
          {PERIODOS_GANANCIAS.map((item) => {
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
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-[#fecaca] bg-[#fef2f2] px-4 py-3 text-sm font-semibold text-[#b42318]">
          {error}
        </div>
      )}

      <div className="mt-4 grid gap-4 md:grid-cols-3">
        <GananciaCard
          destacado
          icono={CircleDollarSign}
          titulo="Ingreso bruto"
          valor={cargando ? "Cargando..." : formatearMonto(reporte?.ingreso_bruto)}
          detalle={`${reporte?.reservas_finalizadas ?? 0} reserva${reporte?.reservas_finalizadas === 1 ? "" : "s"} finalizada${reporte?.reservas_finalizadas === 1 ? "" : "s"}`}
        />
        <GananciaCard
          icono={Percent}
          titulo="Comisión plataforma"
          valor={cargando ? "Cargando..." : formatearMonto(reporte?.comision_plataforma)}
          detalle="20% del ingreso bruto"
        />
        <GananciaCard
          icono={Wallet}
          titulo="Ganancia neta final"
          valor={cargando ? "Cargando..." : formatearMonto(reporte?.ganancia_neta)}
          detalle="80% para el propietario"
        />
      </div>

      <GraficoGanancias
        reporte={reporte}
        cargando={cargando}
        periodo={periodo}
        periodoActivo={periodoActivo}
      />
    </section>
  );
};

const GananciaCard = ({ destacado = false, icono: Icono, titulo, valor, detalle }) => (
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

const GraficoGanancias = ({ reporte, cargando, periodo, periodoActivo }) => {
  const descripcionGrafico =
    DESCRIPCION_GRAFICO_PERIODO[periodo] || "Evolución del período";

  return (
    <article className="mt-4 rounded-lg border border-autospot-border bg-autospot-white p-4 sm:p-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-base font-black text-autospot-black">
            Evolución de ingresos
          </h3>
          <p className="mt-1 text-sm font-semibold text-autospot-muted">
            {descripcionGrafico} · {periodoActivo.comparacion}
          </p>
        </div>
        <IndicadorVariacion reporte={reporte} cargando={cargando} />
      </div>

      <EvolucionMensualChart
        datos={reporte?.evolucion_periodo}
        cargando={cargando}
        emptyMessage="Sin ingresos registrados en este período."
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
  const actual = Number(reporte.ingreso_bruto ?? 0);
  const comparacion = Number(reporte.ingreso_bruto_comparacion ?? 0);
  const sube = direccion === "SUBE";
  const baja = direccion === "BAJA";
  const Icono = sube ? TrendingUp : baja ? TrendingDown : Minus;
  const className = sube
    ? "border-[#bbf7d0] bg-[#f0fdf4] text-[#166534]"
    : baja
      ? "border-[#fecaca] bg-[#fef2f2] text-[#b42318]"
      : "border-autospot-border bg-white text-autospot-muted";

  let texto = "Sin cambios respecto del período anterior.";
  if (actual === 0 && comparacion === 0) {
    texto = "Sin ingresos registrados para comparar.";
  } else if (direccion === "SIN_COMPARACION") {
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

export default PropietarioDashboardPage;
