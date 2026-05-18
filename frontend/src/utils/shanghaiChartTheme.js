import shanghaiGeoJson from "../assets/shanghai.json";
import { getDistrictLabelPoints } from "./shanghaiGeo.js";

/** Nature / Science 风格低饱和区划色（深色底图友好） */
export const DISTRICT_FILL_PALETTE = [
  "rgba(72, 114, 158, 0.34)",
  "rgba(88, 132, 118, 0.32)",
  "rgba(128, 108, 158, 0.30)",
  "rgba(158, 118, 92, 0.28)",
  "rgba(92, 138, 168, 0.33)",
  "rgba(108, 148, 128, 0.31)",
  "rgba(138, 118, 148, 0.29)",
  "rgba(118, 142, 108, 0.30)",
  "rgba(148, 128, 98, 0.28)",
  "rgba(98, 128, 148, 0.32)",
  "rgba(128, 138, 158, 0.30)",
  "rgba(108, 128, 138, 0.31)",
  "rgba(138, 128, 118, 0.29)",
  "rgba(118, 138, 128, 0.30)",
  "rgba(128, 118, 138, 0.28)",
  "rgba(108, 118, 148, 0.32)",
];

export const buildDistrictGeoRegions = (focusedDistrict = null) =>
  (shanghaiGeoJson.features ?? []).map((feature, index) => {
    const name = feature.properties?.name ?? "";
    const baseColor = DISTRICT_FILL_PALETTE[index % DISTRICT_FILL_PALETTE.length];
    const isFocused = Boolean(focusedDistrict);
    const isSelected = focusedDistrict === name;
    const isDimmed = isFocused && !isSelected;

    return {
      name,
      itemStyle: {
        areaColor: isDimmed ? "rgba(18, 28, 42, 0.72)" : baseColor,
        borderColor: isSelected ? "rgba(160, 210, 255, 0.95)" : "rgba(120, 160, 200, 0.55)",
        borderWidth: isSelected ? 1.6 : 0.9,
      },
      label: { show: false },
      emphasis: {
        label: { show: false },
        itemStyle: {
          areaColor: isDimmed ? "rgba(28, 42, 62, 0.82)" : baseColor.replace("0.3", "0.45").replace("0.34", "0.48"),
          borderColor: "rgba(180, 220, 255, 0.9)",
          borderWidth: 1.4,
        },
      },
    };
  });

const DISTRICT_LABEL_STYLE = {
  show: true,
  formatter: "{b}",
  color: "#e8f0fa",
  fontSize: 12,
  fontWeight: "normal",
  textBorderColor: "rgba(12, 24, 40, 0.75)",
  textBorderWidth: 2,
};

/** 区名独立图层，置于线路与站点之上，始终显示 */
export function buildDistrictLabelSeries() {
  const alwaysLabel = {
    ...DISTRICT_LABEL_STYLE,
    show: true,
    opacity: 1,
  };

  return {
    name: "区名",
    type: "scatter",
    coordinateSystem: "geo",
    geoIndex: 0,
    zlevel: 3,
    z: 100,
    silent: false,
    symbol: "circle",
    symbolSize: 1,
    itemStyle: {
      color: "rgba(0, 0, 0, 0)",
      borderWidth: 0,
      opacity: 1,
    },
    emphasis: {
      scale: false,
      itemStyle: { color: "rgba(0, 0, 0, 0)", opacity: 1 },
      label: alwaysLabel,
    },
    labelLayout: {
      hideOverlap: false,
    },
    label: alwaysLabel,
    data: getDistrictLabelPoints(),
  };
}

/** 科技感横向条形图（底轨 + 渐变发光条） */
export function buildTechBarChartOption({
  categories,
  values,
  maxValue,
  tooltipFormatter,
  valueLabelFormatter = (v) => String(v),
  grid = { top: 10, bottom: 16, left: 54, right: 36 },
  barWidth = 13,
  getBarColor,
  showXAxis = false,
  xMax,
}) {
  const max = xMax ?? Math.max(maxValue ?? 0, ...values, 1);
  const trackData = categories.map(() => max);

  return {
    backgroundColor: "transparent",
    grid,
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(12, 20, 34, 0.94)",
      borderColor: "rgba(0, 210, 255, 0.35)",
      textStyle: { color: "#dce7f5", fontSize: 12 },
      formatter: tooltipFormatter,
    },
    xAxis: {
      type: "value",
      max,
      show: showXAxis,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        show: showXAxis,
        color: "rgba(157, 176, 200, 0.75)",
        fontSize: 10,
      },
      splitLine: {
        show: showXAxis,
        lineStyle: {
          color: "rgba(0, 129, 255, 0.08)",
          type: "dashed",
        },
      },
    },
    yAxis: {
      type: "category",
      data: categories,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: "#c8daf0",
        fontSize: 11,
        fontWeight: 500,
        margin: 10,
      },
    },
    series: [
      {
        name: "底轨",
        type: "bar",
        barGap: "-100%",
        barWidth,
        silent: true,
        z: 1,
        data: trackData,
        itemStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: "rgba(0, 80, 140, 0.06)" },
              { offset: 1, color: "rgba(0, 129, 255, 0.10)" },
            ],
          },
          borderRadius: [0, 6, 6, 0],
          borderColor: "rgba(0, 129, 255, 0.14)",
          borderWidth: 1,
        },
      },
      {
        name: "数值",
        type: "bar",
        barWidth,
        z: 2,
        data: values.map((value, index) => ({
          value,
          itemStyle: {
            color: getBarColor(value, index),
            borderRadius: [0, 6, 6, 0],
            shadowColor: "rgba(0, 210, 255, 0.4)",
            shadowBlur: 14,
            shadowOffsetX: 2,
          },
        })),
        label: {
          show: true,
          position: "right",
          distance: 8,
          color: "#00d2ff",
          fontSize: 11,
          fontWeight: 600,
          textShadowColor: "rgba(0, 129, 255, 0.5)",
          textShadowBlur: 8,
          formatter: ({ value }) => valueLabelFormatter(value),
        },
        animationDuration: 650,
        animationEasing: "cubicOut",
      },
    ],
  };
}

export function techFlowBarGradient(flow, minFlow, maxFlow) {
  const t = maxFlow > minFlow ? (flow - minFlow) / (maxFlow - minFlow) : 0.5;
  return horizontalBarGradient([
    { offset: 0, color: `rgba(18, 52, 88, ${0.85 + t * 0.1})` },
    { offset: 0.45, color: `rgba(0, 129, 255, ${0.55 + t * 0.25})` },
    { offset: 1, color: `rgba(0, 210, 255, ${0.88 + t * 0.1})` },
  ]);
}

export function techCrowdBarGradient(crowdIndex) {
  if (crowdIndex <= 0) {
    return horizontalBarGradient([
      { offset: 0, color: "rgba(45, 58, 78, 0.7)" },
      { offset: 1, color: "rgba(110, 128, 155, 0.9)" },
    ]);
  }
  if (crowdIndex >= 18) {
    return horizontalBarGradient([
      { offset: 0, color: "rgba(100, 28, 40, 0.85)" },
      { offset: 0.5, color: "rgba(200, 60, 75, 0.9)" },
      { offset: 1, color: "rgba(255, 120, 130, 0.98)" },
    ]);
  }
  if (crowdIndex >= 8) {
    return horizontalBarGradient([
      { offset: 0, color: "rgba(110, 75, 25, 0.8)" },
      { offset: 0.5, color: "rgba(220, 150, 40, 0.92)" },
      { offset: 1, color: "rgba(255, 200, 80, 0.98)" },
    ]);
  }
  return horizontalBarGradient([
    { offset: 0, color: "rgba(20, 75, 55, 0.8)" },
    { offset: 0.5, color: "rgba(0, 150, 95, 0.9)" },
    { offset: 1, color: "rgba(80, 230, 170, 0.98)" },
  ]);
}

/** 客流 → 散点半径（6~22px，平方根压缩避免极端值过大） */
export function flowToSymbolSize(flow, minFlow, maxFlow) {
  const minSize = 6;
  const maxSize = 22;
  if (maxFlow <= minFlow) return 12;
  const t = Math.sqrt((flow - minFlow) / (maxFlow - minFlow));
  return minSize + t * (maxSize - minSize);
}

/** 拥挤指数 → 站点填充色 */
export function crowdColor(crowdIndex) {
  if (crowdIndex <= 0) return "#5f6f86";
  if (crowdIndex >= 18) return "#c44e52";
  if (crowdIndex >= 8) return "#d4a24c";
  return "#3d9a6e";
}

/** 横向条形图渐变（顶刊常用蓝青—琥珀点缀） */
export function horizontalBarGradient(stops) {
  return {
    type: "linear",
    x: 0,
    y: 0,
    x2: 1,
    y2: 0,
    colorStops: stops,
  };
}

export function crowdBarGradient(crowdIndex) {
  if (crowdIndex <= 0) {
    return horizontalBarGradient([
      { offset: 0, color: "rgba(70, 85, 105, 0.5)" },
      { offset: 1, color: "rgba(95, 111, 134, 0.85)" },
    ]);
  }
  if (crowdIndex >= 18) {
    return horizontalBarGradient([
      { offset: 0, color: "rgba(140, 45, 55, 0.65)" },
      { offset: 1, color: "rgba(230, 90, 100, 0.95)" },
    ]);
  }
  if (crowdIndex >= 8) {
    return horizontalBarGradient([
      { offset: 0, color: "rgba(150, 110, 40, 0.6)" },
      { offset: 1, color: "rgba(250, 173, 20, 0.95)" },
    ]);
  }
  return horizontalBarGradient([
    { offset: 0, color: "rgba(35, 100, 75, 0.55)" },
    { offset: 1, color: "rgba(0, 179, 101, 0.92)" },
  ]);
}

export function flowBarGradient(flow, minFlow, maxFlow) {
  const t = maxFlow > minFlow ? (flow - minFlow) / (maxFlow - minFlow) : 0.5;
  const deep = `rgba(${Math.round(40 + t * 30)}, ${Math.round(90 + t * 50)}, ${Math.round(130 + t * 40)}, 0.55)`;
  const bright = `rgba(${Math.round(80 + t * 40)}, ${Math.round(160 + t * 50)}, ${Math.round(220 + t * 20)}, 0.95)`;
  return horizontalBarGradient([
    { offset: 0, color: deep },
    { offset: 1, color: bright },
  ]);
}
