<template>
  <div ref="container" class="chart-host"></div>
</template>

<script setup>
import * as echarts from "echarts";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const emit = defineEmits(["chart-click"]);

const props = defineProps({
  option: {
    type: Object,
    required: true,
  },
  preserveState: {
    type: Boolean,
    default: false,
  },
  replaceMerge: {
    type: Array,
    default: () => [],
  },
});

const container = ref(null);
let chart;
let clickBound = false;

const render = () => {
  if (!container.value) return;
  if (!chart) {
    chart = echarts.init(container.value);
  }
  if (!clickBound) {
    chart.on("click", (params) => emit("chart-click", params));
    clickBound = true;
  }
  chart.setOption(props.option, {
    notMerge: !props.preserveState,
    replaceMerge: props.replaceMerge,
  });
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
  clickBound = false;
});
</script>
