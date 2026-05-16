<template>
  <section class="screen-grid sh-grid">
    <PlaybackBar v-model:hour="innerHour" :playing="playing" @toggle="$emit('toggle-play')" />
    <div class="panel panel-large">
      <div class="panel-title">上海站点散点图</div>
      <BaseChart :option="scatterOption" />
    </div>
    <div class="panel">
      <div class="panel-title">线路热力条</div>
      <BaseChart :option="lineOption" />
    </div>
    <div class="panel">
      <div class="panel-title">站点详情</div>
      <BaseChart :option="stationOption" />
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";

import BaseChart from "../components/charts/BaseChart.vue";
import PlaybackBar from "../components/controls/PlaybackBar.vue";

const props = defineProps({
  hour: Number,
  playing: Boolean,
  flow: Array,
  lines: Array,
  stationDetail: Object,
});

const emit = defineEmits(["update:hour", "toggle-play"]);

const innerHour = computed({
  get: () => props.hour,
  set: (value) => emit("update:hour", value),
});

const scatterOption = computed(() => ({
  tooltip: { trigger: "item" },
  xAxis: { show: false, min: "dataMin", max: "dataMax" },
  yAxis: { show: false, min: "dataMin", max: "dataMax" },
  series: [
    {
      type: "scatter",
      data: props.flow.map((item) => ({
        name: item.station_name,
        value: [item.plot_x, item.plot_y, item.crowd_index, item.avg_flow],
      })),
      symbolSize: (value) => Math.max(8, value[2] / 6),
      itemStyle: {
        color: (params) => {
          const v = params.value[2];
          if (v >= 75) return "#e60026";
          if (v >= 45) return "#faad14";
          return "#00b365";
        },
      },
    },
  ],
}));

const lineOption = computed(() => ({
  xAxis: {
    type: "value",
    axisLabel: { color: "#9db0c8" },
    splitLine: { lineStyle: { color: "#22334b" } },
  },
  yAxis: {
    type: "category",
    data: props.lines.map((item) => item.line_name).reverse(),
    axisLabel: { color: "#dce7f5" },
  },
  series: [
    {
      type: "bar",
      data: props.lines.map((item) => item.crowd_index).reverse(),
      itemStyle: { color: "#00d2ff" },
    },
  ],
}));

const stationOption = computed(() => ({
  tooltip: { trigger: "axis" },
  xAxis: {
    type: "category",
    data: props.stationDetail?.series?.map((item) => item.hour_label) ?? [],
    axisLabel: { color: "#9db0c8", rotate: 45 },
  },
  yAxis: {
    type: "value",
    axisLabel: { color: "#9db0c8" },
    splitLine: { lineStyle: { color: "#22334b" } },
  },
  series: [
    {
      type: "line",
      smooth: true,
      data: props.stationDetail?.series?.map((item) => item.avg_flow) ?? [],
      itemStyle: { color: "#faad14" },
    },
  ],
}));
</script>
