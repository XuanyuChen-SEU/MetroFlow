<template>
  <section class="national-screen">
    <div class="metrics-grid">
      <MetricCard label="开通地铁城市" :value="overview.metrics.city_count" unit="座" />
      <MetricCard label="最新统计日期" :value="overview.metrics.latest_stat_date" />
      <MetricCard label="全国最新总客流" :value="overview.metrics.total_daily_flow" unit="万人次" />
      <MetricCard label="监测时间跨度" :value="overview.metrics.tracked_days" unit="天" />
    </div>

    <div class="national-layout">
      <div class="panel top10-panel">
        <div class="panel-title">客流 Top10 城市</div>
        <BaseChart :option="topOption" />
      </div>

      <div class="panel map-panel">
        <div class="panel-title map-title">全国线网客流强度分布图</div>
        <div ref="mapRef" class="national-map"></div>
      </div>

      <div class="side-column">
        <div class="panel trend-panel">
          <div class="panel-title">近 15 天客流趋势对比</div>
          <BaseChart :option="trendOption" />
        </div>

        <div class="panel insight-panel">
          <div class="panel-title">最新监测摘要</div>
          <div class="insight-list">
            <div v-for="item in insightItems" :key="item.label" class="insight-item">
              <div class="insight-label">{{ item.label }}</div>
              <div class="insight-value">{{ item.value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import * as echarts from "echarts";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

import MetricCard from "../components/cards/MetricCard.vue";
import BaseChart from "../components/charts/BaseChart.vue";

const CHINA_GEOJSON_URL = "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json";

const props = defineProps({
  overview: {
    type: Object,
    required: true,
  },
  cities: {
    type: Array,
    required: true,
  },
});

const mapRef = ref(null);
let mapChart;
let chinaGeoPromise;

const insightItems = computed(() => {
  const peakCity = props.overview.meta?.peak_city;
  return [
    {
      label: "监测峰值城市",
      value: peakCity ? `${peakCity.city_name} · ${peakCity.value} 万人次` : "-",
    },
    {
      label: "上海站点总数",
      value: `${props.overview.metrics.station_count ?? 0} 站`,
    },
    {
      label: "换乘站数量",
      value: `${props.overview.metrics.transfer_station_count ?? 0} 站`,
    },
    {
      label: "数据来源",
      value: props.overview.meta?.source ?? "-",
    },
  ];
});

const mapData = computed(() =>
  props.cities
    .filter((item) => Number.isFinite(Number(item.longitude)) && Number.isFinite(Number(item.latitude)))
    .map((item) => ({
      name: item.city_name,
      value: [Number(item.longitude), Number(item.latitude), Number(item.avg_daily_flow)],
      statDate: item.stat_date,
    }))
);

const topOption = computed(() => {
  const sorted = [...props.overview.top10].reverse();
  return {
    grid: { top: 10, bottom: 20, left: 45, right: 40 },
    tooltip: {
      trigger: "item",
      formatter: ({ name, value }) => `${name}<br/>最新客流：${value} 万人次`,
    },
    xAxis: { type: "value", show: false },
    yAxis: {
      type: "category",
      data: sorted.map((item) => item.city_name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: "#8b9bb4" },
    },
    series: [
      {
        type: "bar",
        data: sorted.map((item) => item.value),
        barWidth: 22,
        itemStyle: {
          color: "#0081ff",
          borderRadius: [0, 4, 4, 0],
        },
        label: {
          show: true,
          position: "right",
          color: "#00d2ff",
          fontSize: 12,
          fontWeight: 600,
          formatter: ({ value }) => `${value}`,
        },
      },
    ],
  };
});

const trendOption = computed(() => ({
  grid: { top: 30, bottom: 20, left: 40, right: 12 },
  tooltip: { trigger: "axis" },
  legend: {
    data: ["全国总量", "上海"],
    top: 0,
    right: 0,
    textStyle: { color: "#8b9bb4" },
    icon: "circle",
    itemWidth: 8,
  },
  xAxis: {
    type: "category",
    data: props.overview.trend.map((item) => item.label),
    axisLine: { lineStyle: { color: "#212d40" } },
    axisLabel: { color: "#8b9bb4" },
  },
  yAxis: {
    type: "value",
    splitLine: { lineStyle: { color: "#212d40", type: "dashed" } },
    axisLabel: { color: "#8b9bb4" },
  },
  series: [
    {
      name: "全国总量",
      type: "line",
      smooth: true,
      symbol: "none",
      data: props.overview.trend.map((item) => item.national_flow),
      itemStyle: { color: "#64748b" },
      lineStyle: { width: 2, type: "dashed" },
    },
    {
      name: "上海",
      type: "line",
      smooth: true,
      data: props.overview.trend.map((item) => item.shanghai_flow),
      itemStyle: { color: "#00d2ff" },
      lineStyle: { width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(0, 210, 255, 0.20)" },
          { offset: 1, color: "rgba(0, 210, 255, 0)" },
        ]),
      },
    },
  ],
}));

const resizeMap = () => {
  if (mapChart) {
    mapChart.resize();
  }
};

const loadChinaGeoJson = async () => {
  if (!chinaGeoPromise) {
    chinaGeoPromise = fetch(CHINA_GEOJSON_URL).then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to load china geojson: ${response.status}`);
      }
      return response.json();
    });
  }
  return chinaGeoPromise;
};

const renderMap = (hasGeoJson) => {
  if (!mapChart) return;

  const values = mapData.value.map((item) => item.value[2]);
  const min = values.length ? Math.min(...values) : 0;
  const max = values.length ? Math.max(...values) : 1;

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item",
      formatter: ({ data }) => {
        if (!data) return "";
        return `${data.name}<br/>最新客流：${data.value[2]} 万人次<br/>统计日期：${data.statDate}`;
      },
    },
    visualMap: {
      type: "continuous",
      show: true,
      min,
      max,
      calculable: true,
      inRange: {
        color: ["#00b365", "#0081ff", "#faad14", "#e60026"],
        symbolSize: [8, 26],
      },
      textStyle: { color: "#8b9bb4" },
      bottom: 12,
      left: 12,
      itemHeight: 92,
      itemWidth: 10,
    },
    series: [
      {
        type: "scatter",
        coordinateSystem: hasGeoJson ? "geo" : "cartesian2d",
        data: mapData.value,
        itemStyle: { opacity: 0.9 },
        label: {
          show: true,
          formatter: "{b}",
          position: "right",
          color: "#8b9bb4",
          fontSize: 10,
        },
      },
    ],
  };

  if (hasGeoJson) {
    option.geo = {
      map: "china",
      roam: true,
      zoom: 1.15,
      center: [105, 36],
      itemStyle: {
        areaColor: "#0c1421",
        borderColor: "#1b263b",
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: { areaColor: "#122036" },
        label: { show: false },
      },
    };
  } else {
    option.xAxis = { type: "value", show: false, min: 70, max: 140 };
    option.yAxis = { type: "value", show: false, min: 15, max: 55 };
  }

  mapChart.setOption(option, true);
};

const updateMap = async () => {
  if (!mapRef.value) return;
  if (!mapChart) {
    mapChart = echarts.init(mapRef.value);
  }

  try {
    const geoJson = await loadChinaGeoJson();
    echarts.registerMap("china", geoJson);
    renderMap(true);
  } catch (error) {
    console.warn("China geojson unavailable, falling back to scatter view.", error);
    renderMap(false);
  }
};

onMounted(() => {
  updateMap();
  window.addEventListener("resize", resizeMap);
});

watch(
  () => props.cities,
  () => {
    updateMap();
  },
  { deep: true }
);

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeMap);
  if (mapChart) {
    mapChart.dispose();
    mapChart = null;
  }
});
</script>
