<template>
  <div ref="container" class="chart-host"></div>
</template>

<script setup>
import * as echarts from "echarts";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  option: {
    type: Object,
    required: true,
  },
});

const container = ref(null);
let chart;

const render = () => {
  if (!container.value) return;
  if (!chart) {
    chart = echarts.init(container.value);
  }
  chart.setOption(props.option, true);
};

onMounted(() => {
  render();
  window.addEventListener("resize", render);
});

watch(
  () => props.option,
  () => render(),
  { deep: true }
);

onBeforeUnmount(() => {
  window.removeEventListener("resize", render);
  if (chart) {
    chart.dispose();
  }
});
</script>
