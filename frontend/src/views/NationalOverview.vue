<template>
  <section class="screen-grid">
    <div class="metrics-grid">
      <MetricCard label="开通地铁城市" :value="overview.metrics.city_count" unit="座" />
      <MetricCard label="日均客流总量" :value="overview.metrics.total_daily_flow" unit="万人次" />
      <MetricCard label="上海站点总数" :value="overview.metrics.station_count" unit="站" />
      <MetricCard label="换乘站数量" :value="overview.metrics.transfer_station_count" unit="站" />
    </div>
    <div class="panel panel-large">
      <div class="panel-title">全国地铁城市气泡图</div>
      <BaseChart :option="cityOption" />
    </div>
    <div class="panel">
      <div class="panel-title">客流 Top10</div>
      <BaseChart :option="topOption" />
    </div>
    <div class="panel">
      <div class="panel-title">月度趋势</div>
      <BaseChart :option="trendOption" />
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import "echarts/map/js/china";

import MetricCard from "../components/cards/MetricCard.vue";
import BaseChart from "../components/charts/BaseChart.vue";

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

const cityOption = computed(() => ({
  backgroundColor: "transparent",
  tooltip: { trigger: "item" },
  geo: {
    map: "china",
    roam: true,
    itemStyle: {
      areaColor: "#152033",
      borderColor: "#314764",
    },
    emphasis: {
      itemStyle: {
        areaColor: "#1d2c45",
      },
    },
  },
  series: [
    {
      type: "scatter",
      coordinateSystem: "geo",
      data: props.cities.map((item) => ({
        name: item.city_name,
        value: [item.longitude, item.latitude, item.avg_daily_flow],
      })),
      symbolSize: (value) => Math.max(12, value[2] / 40),
      itemStyle: {
        color: "#00d2ff",
        shadowBlur: 16,
        shadowColor: "rgba(0, 210, 255, 0.35)",
      },
    },
  ],
}));

const topOption = computed(() => ({
  xAxis: {
    type: "value",
    axisLabel: { color: "#9db0c8" },
    splitLine: { lineStyle: { color: "#22334b" } },
  },
  yAxis: {
    type: "category",
    data: props.overview.top10.map((item) => item.city_name).reverse(),
    axisLabel: { color: "#dce7f5" },
  },
  series: [
    {
      type: "bar",
      data: props.overview.top10.map((item) => item.value).reverse(),
      itemStyle: { color: "#0081ff" },
    },
  ],
}));

const trendOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { textStyle: { color: "#dce7f5" } },
  xAxis: {
    type: "category",
    data: props.overview.trend.map((item) => item.label),
    axisLabel: { color: "#9db0c8" },
  },
  yAxis: {
    type: "value",
    axisLabel: { color: "#9db0c8" },
    splitLine: { lineStyle: { color: "#22334b" } },
  },
  series: [
    {
      name: "全国",
      type: "line",
      smooth: true,
      data: props.overview.trend.map((item) => item.national_flow),
      itemStyle: { color: "#00d2ff" },
    },
    {
      name: "上海",
      type: "line",
      smooth: true,
      data: props.overview.trend.map((item) => item.shanghai_flow),
      itemStyle: { color: "#faad14" },
    },
  ],
}));
</script>
