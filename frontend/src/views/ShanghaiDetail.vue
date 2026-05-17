<template>
  <section class="shanghai-screen">
    <PlaybackBar v-model:hour="innerHour" :playing="playing" @toggle="$emit('toggle-play')" />

    <div class="shanghai-main">
      <div class="panel panel-large shanghai-map-panel">
        <div class="panel-title">上海站点散点图</div>
        <div v-if="focusedDistrict" class="district-focus-bar">
          <span class="district-focus-label">当前：{{ focusedDistrict }}</span>
          <button type="button" class="district-reset-btn" @click="resetDistrictView">返回全市</button>
        </div>
        <div class="map-legend-stack">
          <div class="map-legend">
            <div class="legend-title">城市线网监控</div>
            <div class="legend-items">
              <div class="legend-item"><span class="legend-dot green"></span>畅通</div>
              <div class="legend-item"><span class="legend-dot yellow"></span>繁忙</div>
              <div class="legend-item"><span class="legend-dot red"></span>拥挤</div>
            </div>
            <div class="legend-size-hint">圆点大小表示小时客流（越大客流越高）</div>
          </div>
          <div class="map-interact-hint" role="note">
            <span class="map-interact-pulse" aria-hidden="true"></span>
            <div class="map-interact-body">
              <div class="map-interact-title">点击行政区域 · 放大查看</div>
              <div class="map-interact-desc">选中区划后将居中展示该区地铁线路与站点客流</div>
            </div>
          </div>
        </div>
        <BaseChart
          :key="mapRenderKey"
          :option="scatterOption"
          preserve-state
          :replace-merge="['geo', 'series', 'xAxis', 'yAxis', 'dataZoom']"
          @chart-click="handleChartClick"
        />
      </div>

      <div class="shanghai-side">
        <div class="panel compact-panel">
          <div class="panel-title">线路快速筛选</div>
          <select v-model="selectedLine" class="line-select">
            <option value="all">-- 全线网监控 --</option>
            <option v-for="line in lineOptions" :key="line" :value="line">{{ line }}</option>
          </select>
        </div>

        <div class="panel heat-panel">
          <div class="panel-title">线路热力条</div>
          <BaseChart :option="lineOption" />
        </div>

        <div class="panel trend-side-panel">
          <div class="panel-title">全天客流负荷趋势</div>
          <BaseChart :option="loadTrendOption" />
        </div>
        <div class="panel hot-panel">
          <div class="panel-title">热点客流站点 Top 5</div>
          <BaseChart :option="hotOption" @chart-click="handleChartClick" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";

import { fetchShanghaiLoadTrend } from "../api";
import BaseChart from "../components/charts/BaseChart.vue";
import PlaybackBar from "../components/controls/PlaybackBar.vue";
import {
  DEFAULT_GEO_VIEW,
  geoViewForBounds,
  getDistrictBounds,
  loadShanghaiGeoMap,
  pointInDistrict,
  stationPlotToGcjLngLat,
} from "../utils/shanghaiGeo.js";
import {
  buildDistrictGeoRegions,
  buildDistrictLabelSeries,
  buildTechBarChartOption,
  crowdColor,
  flowToSymbolSize,
  techCrowdBarGradient,
  techFlowBarGradient,
} from "../utils/shanghaiChartTheme.js";

const props = defineProps({
  hour: Number,
  playing: Boolean,
  flow: Array,
  lines: Array,
  topology: Object,
  stationDetail: Object,
});

const emit = defineEmits(["update:hour", "toggle-play", "select-station"]);

const selectedLine = ref("all");
const loadTrend = ref([]);
const focusedDistrict = ref(null);
const geoView = ref({ ...DEFAULT_GEO_VIEW });
const mapRenderKey = ref(0);
loadShanghaiGeoMap();

const innerHour = computed({
  get: () => props.hour,
  set: (value) => emit("update:hour", value),
});

const lineOptions = computed(() => (props.topology?.lines ?? []).map((line) => line.line_name));

const filteredFlow = computed(() => {
  let list = props.flow;
  if (selectedLine.value !== "all") {
    list = list.filter((item) => item.line_names.split("|").includes(selectedLine.value));
  }
  if (!focusedDistrict.value) return list;
  return list.filter((item) => {
    const [lng, lat] = stationPlotToGcjLngLat(item.plot_x, item.plot_y);
    return pointInDistrict(lng, lat, focusedDistrict.value);
  });
});

const filteredLines = computed(() => {
  if (selectedLine.value === "all") return props.lines;
  return props.lines.filter((item) => item.line_name === selectedLine.value);
});

const topStations = computed(() =>
  [...filteredFlow.value]
    .sort((a, b) => b.avg_flow - a.avg_flow)
    .slice(0, 5)
);

const flowExtent = computed(() => {
  const flows = filteredFlow.value.map((item) => item.avg_flow ?? 0);
  if (!flows.length) return { min: 0, max: 1 };
  return { min: Math.min(...flows), max: Math.max(...flows) };
});

const focusDistrict = (districtName) => {
  if (!districtName) return;
  const bounds = getDistrictBounds(districtName);
  if (!bounds) return;
  focusedDistrict.value = districtName;
  geoView.value = geoViewForBounds(bounds);
  mapRenderKey.value += 1;
};

const resetDistrictView = () => {
  focusedDistrict.value = null;
  geoView.value = { ...DEFAULT_GEO_VIEW };
  mapRenderKey.value += 1;
};

const handleChartClick = (params) => {
  if (params.componentType === "geo" && params.name) {
    focusDistrict(params.name);
    return;
  }
  if (params.seriesName === "区名" && params.name) {
    focusDistrict(params.name);
    return;
  }
  if (params.seriesName === "站点客流") {
    const stationName = params?.data?.name ?? params?.name;
    if (stationName) emit("select-station", stationName);
  }
};

const loadTrendData = async () => {
  const response = await fetchShanghaiLoadTrend(selectedLine.value);
  loadTrend.value = response.data.data;
};

watch(selectedLine, loadTrendData);
onMounted(loadTrendData);

const scatterOption = computed(() => {
  const visibleLineNames = new Set(selectedLine.value === "all" ? lineOptions.value : [selectedLine.value]);
  const { min: minFlow, max: maxFlow } = flowExtent.value;
  const district = focusedDistrict.value;

  const metroLineSeries = (props.topology?.lines ?? [])
    .filter((line) => visibleLineNames.has(line.line_name))
    .map((line) => {
      const coords = line.points.map(([x, y]) => stationPlotToGcjLngLat(x, y));
      if (district) {
        const intersects = coords.some(([lng, lat]) => pointInDistrict(lng, lat, district));
        if (!intersects) return null;
      }
      return {
        name: line.line_name,
        type: "lines",
        coordinateSystem: "geo",
        geoIndex: 0,
        polyline: true,
        data: [{ coords }],
        silent: true,
        z: 3,
        lineStyle: {
          width: district ? 4.5 : 3.5,
          color: line.color,
          opacity: 0.95,
          shadowColor: "rgba(0, 0, 0, 0.45)",
          shadowBlur: 4,
        },
      };
    })
    .filter(Boolean);

  const stationSeries = {
    name: "站点客流",
    type: "scatter",
    coordinateSystem: "geo",
    geoIndex: 0,
    z: 4,
    data: filteredFlow.value.map((item) => {
      const [lng, lat] = stationPlotToGcjLngLat(item.plot_x, item.plot_y);
      return {
        name: item.station_name,
        value: [lng, lat, item.crowd_index, item.avg_flow],
        lineNames: item.line_names,
      };
    }),
    symbolSize: (value) => flowToSymbolSize(value[3], minFlow, maxFlow),
    itemStyle: {
      color: (params) => crowdColor(params.value[2]),
      borderColor: "rgba(255, 255, 255, 0.35)",
      borderWidth: 1,
      shadowColor: "rgba(0, 0, 0, 0.35)",
      shadowBlur: 6,
    },
    emphasis: {
      scale: 1.15,
      itemStyle: {
        borderColor: "#fff",
        borderWidth: 1.5,
      },
    },
  };

  return {
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(12, 20, 34, 0.94)",
      borderColor: "rgba(0, 210, 255, 0.35)",
      textStyle: { color: "#dce7f5", fontSize: 12 },
      formatter: ({ componentSubType, data, seriesName }) => {
        if (componentSubType === "lines") {
          return `${seriesName}`;
        }
        if (!data?.value) return "";
        return [
          data.name,
          `小时客流：${data.value[3]} 人次`,
          `拥挤指数：${data.value[2]}`,
          `线路：${data.lineNames}`,
        ].join("<br/>");
      },
    },
    geo: {
      map: "shanghai",
      roam: true,
      center: geoView.value.center,
      zoom: geoView.value.zoom,
      layoutCenter: geoView.value.layoutCenter,
      layoutSize: geoView.value.layoutSize,
      z: 0,
      silent: false,
      selectedMode: false,
      itemStyle: {
        borderColor: "rgba(100, 140, 180, 0.45)",
        borderWidth: 0.8,
      },
      label: { show: false },
      emphasis: {
        label: { show: false },
      },
      regions: buildDistrictGeoRegions(district),
    },
    series: [...metroLineSeries, stationSeries, buildDistrictLabelSeries()],
  };
});

const hotOption = computed(() => {
  const items = topStations.value.map((item) => ({
    name: item.station_name,
    value: item.avg_flow,
  }));
  const reversed = [...items].reverse();
  const flows = reversed.map((item) => item.value);
  const minFlow = flows.length ? Math.min(...flows) : 0;
  const maxFlow = flows.length ? Math.max(...flows) : 1;

  return buildTechBarChartOption({
    categories: reversed.map((item) => item.name),
    values: flows,
    maxValue: maxFlow,
    xMax: maxFlow * 1.12,
    grid: { top: 10, bottom: 18, left: 56, right: 40 },
    barWidth: 13,
    tooltipFormatter: ({ name, value }) => `${name}<br/>小时客流：${value} 人次`,
    valueLabelFormatter: (v) => `${v}`,
    getBarColor: (value) => techFlowBarGradient(value, minFlow, maxFlow),
  });
});

const loadTrendOption = computed(() => ({
  grid: { top: 30, bottom: 20, left: 35, right: 10 },
  tooltip: { trigger: "axis" },
  xAxis: {
    type: "category",
    data: loadTrend.value.map((item) => item.hour_label.slice(0, 2)),
    axisLine: { lineStyle: { color: "#212d40" } },
    axisLabel: { color: "#8b9bb4" },
  },
  yAxis: {
    type: "value",
    max: 100,
    splitLine: { lineStyle: { color: "#212d40", type: "dashed" } },
    axisLabel: { color: "#8b9bb4" },
  },
  series: [
    {
      type: "line",
      smooth: true,
      symbol: "none",
      itemStyle: { color: "#0081ff" },
      areaStyle: {
        color: {
          type: "linear",
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: "rgba(0,129,255,0.40)" },
            { offset: 1, color: "rgba(0,129,255,0)" },
          ],
        },
      },
      data: loadTrend.value.map((item) => item.load_index),
      markLine: {
        symbol: ["none", "none"],
        label: { show: false },
        lineStyle: { color: "#00d2ff", type: "solid", width: 2 },
        data: [{ xAxis: String(props.hour).padStart(2, "0") }],
      },
    },
  ],
}));

const lineOption = computed(() => {
  const items = filteredLines.value.map((item) => ({
    name: item.line_name,
    value: item.crowd_index,
  }));
  const reversed = [...items].reverse();
  const values = reversed.map((item) => item.value);
  const maxCrowd = values.length ? Math.max(...values, 20) : 20;
  const visibleCount = Math.min(Math.max(items.length, 1), 8);

  const option = buildTechBarChartOption({
    categories: reversed.map((item) => item.name),
    values,
    maxValue: maxCrowd,
    xMax: Math.ceil(maxCrowd * 1.15),
    grid: { top: 12, bottom: items.length > visibleCount ? 40 : 18, left: 58, right: 36 },
    barWidth: 12,
    showXAxis: true,
    tooltipFormatter: ({ name, value }) => `${name}<br/>拥挤指数：${value}`,
    valueLabelFormatter: (v) => String(v),
    getBarColor: (value) => techCrowdBarGradient(value),
  });

  if (items.length > visibleCount) {
    option.dataZoom = [
      {
        type: "slider",
        yAxisIndex: 0,
        right: 2,
        width: 8,
        top: 12,
        bottom: 12,
        startValue: 0,
        endValue: visibleCount - 1,
        fillerColor: "rgba(0, 129, 255, 0.22)",
        borderColor: "rgba(0, 129, 255, 0.25)",
        backgroundColor: "rgba(8, 14, 24, 0.6)",
        moveHandleSize: 0,
        textStyle: { color: "#8b9bb4", fontSize: 10 },
      },
      {
        type: "inside",
        yAxisIndex: 0,
        startValue: 0,
        endValue: visibleCount - 1,
        zoomOnMouseWheel: true,
        moveOnMouseWheel: true,
        moveOnMouseMove: true,
      },
    ];
  }

  return option;
});
</script>
