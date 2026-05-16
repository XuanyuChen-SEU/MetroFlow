<template>
  <section class="shanghai-screen">
    <PlaybackBar v-model:hour="innerHour" :playing="playing" @toggle="$emit('toggle-play')" />

    <div class="shanghai-main">
      <div class="panel panel-large shanghai-map-panel">
        <div class="panel-title">上海站点散点图</div>
        <div class="map-legend">
          <div class="legend-title">城市线网监控</div>
          <div class="legend-items">
            <div class="legend-item"><span class="legend-dot green"></span>畅通</div>
            <div class="legend-item"><span class="legend-dot yellow"></span>繁忙</div>
            <div class="legend-item"><span class="legend-dot red"></span>拥挤</div>
          </div>
        </div>
        <BaseChart :option="scatterOption" preserve-state :replace-merge="['series']" @chart-click="handleChartClick" />
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

const innerHour = computed({
  get: () => props.hour,
  set: (value) => emit("update:hour", value),
});

const lineOptions = computed(() => (props.topology?.lines ?? []).map((line) => line.line_name));

const filteredFlow = computed(() => {
  if (selectedLine.value === "all") return props.flow;
  return props.flow.filter((item) => item.line_names.split("|").includes(selectedLine.value));
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

const getStationColor = (crowdIndex) => {
  if (crowdIndex <= 0) return "#5f6f86";
  if (crowdIndex >= 18) return "#e60026";
  if (crowdIndex >= 8) return "#faad14";
  return "#00b365";
};

const handleChartClick = (params) => {
  const stationName = params?.data?.name ?? params?.name;
  if (stationName && stationName !== "站点客流") {
    emit("select-station", stationName);
  }
};

const loadTrendData = async () => {
  const response = await fetchShanghaiLoadTrend(selectedLine.value);
  loadTrend.value = response.data.data;
};

watch(selectedLine, loadTrendData);
onMounted(loadTrendData);

const scatterOption = computed(() => {
  const extent = props.topology?.extent ?? {};
  const visibleLineNames = new Set(selectedLine.value === "all" ? lineOptions.value : [selectedLine.value]);
  const lineSeries = (props.topology?.lines ?? [])
    .filter((line) => visibleLineNames.has(line.line_name))
    .map((line) => ({
      name: line.line_name,
      type: "line",
      data: line.points,
      showSymbol: false,
      smooth: false,
      silent: true,
      lineStyle: {
        width: 4,
        color: line.color,
        opacity: 0.92,
      },
      z: 1,
    }));

  return {
    tooltip: {
      trigger: "item",
      formatter: ({ componentSubType, data, seriesName }) => {
        if (componentSubType === "line") {
          return `${seriesName}`;
        }
        if (!data) return "";
        return [
          data.name,
          `小时客流：${data.value[3]}`,
          `拥挤指数：${data.value[2]}`,
          `线路：${data.lineNames}`,
        ].join("<br/>");
      },
    },
    xAxis: {
      show: false,
      min: extent.min_x ? extent.min_x - 1200 : "dataMin",
      max: extent.max_x ? extent.max_x + 1200 : "dataMax",
      scale: true,
    },
    yAxis: {
      show: false,
      min: extent.min_y ? extent.min_y - 1200 : "dataMin",
      max: extent.max_y ? extent.max_y + 1200 : "dataMax",
      scale: true,
    },
    dataZoom: [
      {
        type: "inside",
        xAxisIndex: 0,
        filterMode: "none",
        zoomOnMouseWheel: true,
        moveOnMouseWheel: true,
      },
      {
        type: "inside",
        yAxisIndex: 0,
        filterMode: "none",
        zoomOnMouseWheel: true,
        moveOnMouseWheel: true,
      },
    ],
    series: [
      ...lineSeries,
      {
        name: "站点客流",
        type: "scatter",
        z: 3,
        data: filteredFlow.value.map((item) => ({
          name: item.station_name,
          value: [item.plot_x, item.plot_y, item.crowd_index, item.avg_flow],
          lineNames: item.line_names,
        })),
        symbolSize: (value) => Math.max(8, value[2] / 6),
        itemStyle: {
          color: (params) => getStationColor(params.value[2]),
        },
      },
    ],
  };
});

const hotOption = computed(() => ({
  grid: { top: 10, bottom: 20, left: 55, right: 20 },
  tooltip: {
    trigger: "item",
    formatter: ({ name, value }) => `${name}<br/>小时客流：${value}`,
  },
  xAxis: { type: "value", show: false },
  yAxis: {
    type: "category",
    data: topStations.value.map((item) => item.station_name).reverse(),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: "#8b9bb4" },
  },
  series: [
    {
      type: "bar",
      data: topStations.value.map((item) => ({
        name: item.station_name,
        value: item.avg_flow,
        itemStyle: { color: getStationColor(item.crowd_index) },
      })).reverse(),
      barWidth: 14,
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
      },
      label: {
        show: true,
        position: "right",
        color: "#fff",
        fontSize: 12,
      },
    },
  ],
}));

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
  })).reverse();
  const visibleCount = Math.min(Math.max(items.length, 1), 8);

  return {
    grid: { top: 12, bottom: items.length > visibleCount ? 40 : 20, left: 58, right: 18 },
    tooltip: {
      trigger: "item",
      formatter: ({ name, value }) => `${name}<br/>拥挤指数：${value}`,
    },
    xAxis: {
      type: "value",
      axisLabel: { color: "#9db0c8" },
      splitLine: { lineStyle: { color: "#22334b" } },
    },
    yAxis: {
      type: "category",
      data: items.map((item) => item.name),
      axisLabel: { color: "#dce7f5", fontSize: items.length > 10 ? 10 : 12 },
      axisTick: { show: false },
      axisLine: { show: false },
    },
    dataZoom: items.length > visibleCount ? [
      {
        type: "slider",
        yAxisIndex: 0,
        right: 0,
        width: 10,
        top: 12,
        bottom: 12,
        startValue: 0,
        endValue: visibleCount - 1,
        fillerColor: "rgba(0, 129, 255, 0.18)",
        borderColor: "#22334b",
        moveHandleSize: 0,
        textStyle: { color: "#8b9bb4" },
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
    ] : [],
    series: [
      {
        type: "bar",
        data: items.map((item) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: "#00d2ff" },
        })),
        barMaxWidth: 18,
        barMinHeight: 6,
        itemStyle: { borderRadius: [0, 4, 4, 0] },
        label: {
          show: items.length <= 8,
          position: "right",
          color: "#dce7f5",
          fontSize: 11,
        },
      },
    ],
  };
});

</script>
