const formatearMontoCompacto = (valor) => {
  const numero = Number(valor ?? 0);
  if (Number.isNaN(numero)) return "$0";
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(numero);
};

const formatearPorcentaje = (valor) => {
  const numero = Number(valor ?? 0);
  return `${new Intl.NumberFormat("es-AR", {
    maximumFractionDigits: 1,
  }).format(Number.isNaN(numero) ? 0 : numero)}%`;
};

const limitar = (valor, minimo, maximo) => Math.min(Math.max(valor, minimo), maximo);

const crearCurvaSuave = (puntos, { limiteSuperior, limiteInferior }) => {
  if (puntos.length === 0) return "";
  if (puntos.length === 1) return `M ${puntos[0].x} ${puntos[0].y}`;

  return puntos.reduce((path, punto, index) => {
    if (index === 0) return `M ${punto.x} ${punto.y}`;

    const anterior = puntos[index - 1];
    const previo = puntos[index - 2] || anterior;
    const siguiente = puntos[index + 1] || punto;
    const cp1x = anterior.x + (punto.x - previo.x) / 6;
    const cp1y = limitar(
      anterior.y + (punto.y - previo.y) / 6,
      limiteSuperior,
      limiteInferior,
    );
    const cp2x = punto.x - (siguiente.x - anterior.x) / 6;
    const cp2y = limitar(
      punto.y - (siguiente.y - anterior.y) / 6,
      limiteSuperior,
      limiteInferior,
    );

    return `${path} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${punto.x} ${punto.y}`;
  }, "");
};

const EvolucionMensualChart = ({
  datos = [],
  datosComparacion = [],
  etiquetaActual = "Actual",
  etiquetaComparacion = "Período anterior",
  cargando = false,
  mostrarOcupacion = false,
  emptyMessage = "Sin ingresos registrados en este período.",
}) => {
  const puntosBase =
    datos.length > 0
      ? datos
      : Array.from({ length: 6 }, (_, index) => ({
          etiqueta: `Mes ${index + 1}`,
          ingreso_bruto: 0,
          tasa_ocupacion: 0,
          reservas_finalizadas: 0,
        }));
  // La serie de comparación (período anterior) se dibuja como 2da línea.
  const hayComparacion = Array.isArray(datosComparacion) && datosComparacion.length > 0;
  const comparacionBase = hayComparacion
    ? datosComparacion.slice(0, puntosBase.length)
    : [];

  const valores = puntosBase.map((item) => Number(item.ingreso_bruto ?? 0));
  const valoresComparacion = comparacionBase.map((item) =>
    Number(item.ingreso_bruto ?? 0),
  );
  // Escala compartida: el máximo del eje Y considera AMBAS series para que las
  // dos líneas sean visualmente comparables.
  const maximo = Math.max(...valores, ...valoresComparacion, 1);
  const hayIngresos = [...valores, ...valoresComparacion].some((valor) => valor > 0);

  const ancho = 1000;
  const alto = 390;
  const izquierda = 84;
  const derecha = 44;
  const arriba = 42;
  const base = 278;
  const altoGrafico = base - arriba;
  const paso = (ancho - izquierda - derecha) / Math.max(puntosBase.length - 1, 1);

  const calcularPunto = (item, index) => {
    const valor = Number(item.ingreso_bruto ?? 0);
    return {
      x: izquierda + index * paso,
      y: base - (valor / maximo) * altoGrafico,
      valor,
      item,
    };
  };

  const puntos = puntosBase.map(calcularPunto);
  const puntosComparacion = comparacionBase.map(calcularPunto);

  const linea = crearCurvaSuave(puntos, {
    limiteSuperior: arriba,
    limiteInferior: base,
  });
  const lineaComparacion = crearCurvaSuave(puntosComparacion, {
    limiteSuperior: arriba,
    limiteInferior: base,
  });
  const area =
    puntos.length > 0
      ? `${linea} L ${puntos[puntos.length - 1].x} ${base} L ${puntos[0].x} ${base} Z`
      : "";

  return (
    <div className="mt-5 overflow-hidden rounded-lg border border-autospot-border bg-white">
      {hayComparacion && (
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-b border-autospot-border bg-[#fbfaf8] px-4 py-2.5">
          <span className="inline-flex items-center gap-2 text-xs font-bold text-autospot-black">
            <svg width="22" height="8" aria-hidden="true">
              <line x1="1" y1="4" x2="21" y2="4" stroke="#8f1d34" strokeWidth="3.25" strokeLinecap="round" />
            </svg>
            {etiquetaActual}
          </span>
          <span className="inline-flex items-center gap-2 text-xs font-bold text-autospot-black">
            <svg width="22" height="8" aria-hidden="true">
              <line x1="1" y1="4" x2="21" y2="4" stroke="#0a0a0a" strokeWidth="3" strokeLinecap="round" />
            </svg>
            {etiquetaComparacion}
          </span>
        </div>
      )}
      <svg
        viewBox={`0 0 ${ancho} ${alto}`}
        role="img"
        aria-label="Evolución de ingresos del período"
        className={`block aspect-[1000/390] min-h-72 w-full ${cargando ? "animate-pulse opacity-70" : ""}`}
      >
        <defs>
          <linearGradient id="ingresos-area" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#8f1d34" stopOpacity="0.18" />
            <stop offset="72%" stopColor="#8f1d34" stopOpacity="0.04" />
            <stop offset="100%" stopColor="#8f1d34" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="ingresos-linea" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="#6f1427" />
            <stop offset="100%" stopColor="#b92c47" />
          </linearGradient>
        </defs>

        <rect x="0" y="0" width={ancho} height={alto} fill="#fff" />

        {[0, 0.5, 1].map((fraccion) => {
          const y = base - fraccion * altoGrafico;
          return (
            <g key={fraccion}>
              <line
                x1={izquierda}
                x2={ancho - derecha}
                y1={y}
                y2={y}
                stroke="#e8e0d5"
                strokeDasharray="8 10"
                strokeLinecap="round"
                strokeWidth="1.5"
              />
              <text
                x={izquierda - 18}
                y={y + 5}
                textAnchor="end"
                className="fill-autospot-muted text-[12px] font-bold"
              >
                {formatearMontoCompacto(maximo * fraccion)}
              </text>
            </g>
          );
        })}

        {area && <path d={area} fill="url(#ingresos-area)" aria-hidden="true" />}

        {/* Línea del período de comparación (2da serie) — negra continua */}
        {hayComparacion && lineaComparacion && (
          <path
            d={lineaComparacion}
            fill="none"
            stroke="#0a0a0a"
            strokeWidth="2.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}
        {hayComparacion &&
          puntosComparacion.map((punto) => (
            <circle
              key={`comp-${punto.item.etiqueta}`}
              cx={punto.x}
              cy={punto.y}
              r="3.5"
              fill="#fff"
              stroke="#0a0a0a"
              strokeWidth="2.5"
            />
          ))}

        <path
          d={linea}
          fill="none"
          stroke="url(#ingresos-linea)"
          strokeWidth="3.25"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {puntos.map((punto, index) => {
          const esUltimo = index === puntos.length - 1;
          return (
            <g key={punto.item.etiqueta}>
              <circle
                cx={punto.x}
                cy={punto.y}
                r={esUltimo ? 7 : 4.5}
                fill="#fff"
                stroke="#8f1d34"
                strokeWidth={esUltimo ? 4 : 3}
              />
              {esUltimo && (
                <text
                  x={punto.x}
                  y={Math.max(punto.y - 18, 18)}
                  textAnchor="middle"
                  className="fill-autospot-black text-[13px] font-black"
                >
                  {cargando ? "..." : formatearMontoCompacto(punto.valor)}
                </text>
              )}
              <text
                x={punto.x}
                y={base + 42}
                textAnchor="middle"
                className="fill-autospot-muted text-[13px] font-bold"
              >
                {punto.item.etiqueta}
              </text>
              <text
                x={punto.x}
                y={base + 64}
                textAnchor="middle"
                className="fill-autospot-black text-[12px] font-black"
              >
                {cargando ? "" : `${punto.item.reservas_finalizadas ?? 0} alq.`}
              </text>
            </g>
          );
        })}
      </svg>

      {mostrarOcupacion && (
        <div className="border-t border-autospot-border bg-[#fbfaf8] px-4 py-3">
          <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
            {puntosBase.map((item) => {
              const tasa = Math.max(
                0,
                Math.min(Number(item.tasa_ocupacion ?? 0), 100),
              );
              return (
                <div key={`${item.etiqueta}-ocupacion`} className="min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-[11px] font-bold text-autospot-muted">
                      {item.etiqueta}
                    </span>
                    <span className="text-[11px] font-black text-autospot-black">
                      {cargando ? "..." : formatearPorcentaje(tasa)}
                    </span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-[#ece4d8]">
                    <div
                      className="h-full rounded-full bg-autospot-black"
                      style={{ width: `${cargando ? 35 : tasa}%` }}
                      aria-hidden="true"
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!cargando && !hayIngresos && (
        <p className="border-t border-autospot-border bg-[#fbfaf8] px-4 py-3 text-center text-sm font-semibold text-autospot-muted">
          {emptyMessage}
        </p>
      )}
    </div>
  );
};

export default EvolucionMensualChart;
