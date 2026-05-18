<template>
  <section class="national-screen">
    <div class="metrics-grid">
      <MetricCard label="开通地铁城市" :value="overview.metrics.city_count" unit="座" />
      <MetricCard label="最新统计日期" :value="overview.metrics.latest_stat_date" />
      <MetricCard label="全国最新总客流" :value="overview.metrics.total_daily_flow" unit="万人次" />
      <MetricCard label="监测时间跨度" :value="overview.metrics.tracked_days" unit="天" />
    </div>

    <div class="national-layout">
      <!-- Top10 柱状图 -->
      <div class="panel top10-panel">
        <div class="panel-title">客流 Top10 城市</div>
        <BaseChart :option="topOption" />
      </div>

      <!-- 全国动态地图 -->
      <div class="panel map-panel">
        <div class="panel-title map-title">全国线网客流强度分布图</div>
        <div ref="mapRef" class="national-map"></div>
      </div>

      <div class="side-column">
        <!-- 趋势折线图 -->
        <div class="panel trend-panel">
          <div class="panel-header">
            <div class="panel-title" style="margin-bottom: 0;">近 15 天客流趋势对比</div>
            <select v-model="selectedCity" class="city-select">
              <option v-for="city in cityList" :key="city" :value="city">{{ city }}</option>
            </select>
          </div>
          <BaseChart :option="trendOption" />
        </div>

        <!-- 客流结构分析图 -->
        <div class="panel structure-panel insight-panel">
          <div class="panel-title">全国客流结构分析</div>
          <div class="structure-charts">
            <BaseChart :option="tierOption" />
            <BaseChart :option="contributionOption" />
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

import { fetchCityTrend } from "../api/index";

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

// ==========================================
// 数据计算区
// ==========================================

const mapData = computed(() =>
  props.cities
    .filter((item) => Number.isFinite(Number(item.longitude)) && Number.isFinite(Number(item.latitude)))
    .map((item) => ({
      name: item.city_name,
      value: [Number(item.longitude), Number(item.latitude), Number(item.avg_daily_flow)],
      statDate: item.stat_date,
    }))
);

const top5MapData = computed(() => {
  return [...mapData.value].sort((a, b) => b.value[2] - a.value[2]).slice(0, 5);
});

const tierData = computed(() => {
  let high = 0, mid = 0, low = 0;
  props.cities.forEach(c => {
    const flow = Number(c.avg_daily_flow);
    if (flow >= 500) high++;
    else if (flow >= 100) mid++;
    else low++;
  });
  return [
    { name: '>500万', value: high, itemStyle: { color: '#e60026' } },
    { name: '100-500万', value: mid, itemStyle: { color: '#faad14' } },
    { name: '<100万', value: low, itemStyle: { color: '#0081ff' } }
  ];
});

const contributionData = computed(() => {
  let top4Flow = 0;
  let totalFlow = 0;
  const top4Names = ['北京', '上海', '广州', '深圳'];
  
  props.cities.forEach(c => {
    const flow = Number(c.avg_daily_flow) || 0;
    totalFlow += flow;
    if (top4Names.includes(c.city_name)) {
      top4Flow += flow;
    }
  });
  const othersFlow = totalFlow - top4Flow;
  
  return [
    { name: '北上广深', value: top4Flow, itemStyle: { color: '#0081ff' } }, // 扁平蓝
    { name: '其他城市', value: othersFlow, itemStyle: { color: '#22344d' } } // 暗灰
  ];
});

// 响应式变量和城市列表计算
const selectedCity = ref("上海");
const currentTrend = ref(props.overview.trend); // 初始化为 props 里的默认趋势

const cityList = computed(() => {
  // 从返回的全国城市气泡列表中提取唯一城市名字并排序
  return [...new Set(props.cities.map(c => c.city_name))].sort();
});

// 监听城市切换，拉取新数据
watch(selectedCity, async (newCity) => {
  try {
    const res = await fetchCityTrend(newCity);
    // 根据拦截器不同，适配返回结构
    if (res.data && res.data.data) {
      currentTrend.value = res.data.data;
    } else {
      currentTrend.value = res.data;
    }
  } catch (error) {
    console.error("Failed to fetch city trend:", error);
  }
}, { immediate: true });

// ==========================================
// ECharts 配置区 (极简扁平、放大比例)
// ==========================================

// --- Top10 柱状图：加宽柱子，统一纯文字颜色，扩大内容占比 ---
const topOption = computed(() => {
  const sorted = [...props.overview.top10].reverse();
  return {
    // 调小网格间距，让图表撑满面板
    grid: { top: 5, bottom: 5, left: 60, right: 35 }, // <--- top 和 bottom 收紧到 5
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(10, 15, 24, 0.95)",
      borderColor: "#22344d",
      textStyle: { color: "#e5eef9", fontSize: 14 },
      formatter: ({ name, value }) => `<b style="font-size:16px">${name}</b><br/>最新客流：${value} 万人次`,
    },
    xAxis: { type: "value", show: false },
    yAxis: {
      type: "category",
      data: sorted.map((item) => item.city_name),
      axisLine: { show: false },
      axisTick: { show: false },
      // 统一文字颜色，去除不同排名的色彩差异，放大字号
      axisLabel: { color: "#e5eef9", fontSize: 14, fontWeight: 500 },
    },
    series: [
      {
        type: "bar",
        data: sorted.map((item) => item.value),
        barWidth: 22, // 柱子大幅加宽 (原为14)
        showBackground: true,
        backgroundStyle: { color: "rgba(255, 255, 255, 0.05)", borderRadius: 2 },
        itemStyle: {
          borderRadius: [0, 2, 2, 0],
          // 采用简单的平滑单色或扁平渐变
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: "#006ee6" },
            { offset: 1, color: "#009dff" },
          ]),
        },
        label: {
          show: true,
          position: "right",
          color: "#e5eef9", // 统一扁平标签色
          fontSize: 14,
          fontWeight: "bold",
          fontFamily: "Courier New",
        },
      },
    ],
  };
});

// --- 趋势折线图：支持动态显示被选中的城市，并使用双 Y 轴解决数量级差距 ---
const trendOption = computed(() => {
  const trendData = currentTrend.value && currentTrend.value.length > 0 
    ? currentTrend.value 
    : props.overview.trend; 

  const cityKey = trendData[0] && trendData[0].city_flow !== undefined ? 'city_flow' : 'shanghai_flow';

  return {
    grid: { top: 40, bottom: 20, left: 45, right: 45 }, 
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(10, 15, 24, 0.95)",
      borderColor: "#22344d",
      textStyle: { color: "#e5eef9", fontSize: 14 }
    },
    legend: {
      data: ["全国总量", selectedCity.value],
      top: 0, right: 60,
      textStyle: { color: "#8ea5bf", fontSize: 14 },
      icon: "circle", itemWidth: 10,
    },
    xAxis: {
      type: "category",
      data: trendData.map((item) => item.label),
      axisLine: { lineStyle: { color: "#22344d" } },
      axisLabel: { color: "#8ea5bf", fontSize: 13 }, 
    },
    yAxis: [
      {
        type: "value",
        name: "城市",
        nameTextStyle: { color: "#0081ff", fontSize: 12, padding: [0, 20, 0, 0] },
        splitLine: { lineStyle: { color: "#22344d", type: "dashed" } },
        axisLabel: { color: "#0081ff", fontSize: 12 },
      },
      {
        type: "value",
        name: "全国",
        nameTextStyle: { color: "#8ea5bf", fontSize: 12, padding: [0, 0, 0, 20] },
        splitLine: { show: false }, // 隐藏右侧网格线避免画面杂乱
        axisLabel: { color: "#8ea5bf", fontSize: 12 },
      }
    ],
    series: [
      {
        name: "全国总量",
        type: "line",
        yAxisIndex: 1,
        smooth: true,
        symbol: "none",
        data: trendData.map((item) => item.national_flow),
        itemStyle: { color: "#8ea5bf" },
        lineStyle: { width: 2, type: "dashed" },
      },
      {
        name: selectedCity.value,
        type: "line",
        yAxisIndex: 0,
        smooth: true,
        symbol: "circle",
        symbolSize: 8,
        data: trendData.map((item) => item[cityKey]),
        itemStyle: { color: "#0081ff" }, 
        lineStyle: { width: 3 }, 
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(0, 129, 255, 0.2)" },
            { offset: 1, color: "rgba(0, 129, 255, 0)" },
          ]),
        },
      },
    ],
  };
});

// --- 图表 A：城市梯队分布玫瑰图（扩大饼图半径和字号） ---
const tierOption = computed(() => ({
  tooltip: { trigger: 'item', textStyle: { fontSize: 14 }, formatter: '{b} : {c}座 ({d}%)' },
  title: {
    text: '客流梯队分布',
    left: 'center', top: 'bottom',
    textStyle: { color: '#8ea5bf', fontSize: 14, fontWeight: 'normal' }
  },
  series: [{
    type: 'pie',
    radius: ['25%', '70%'], // 扩大半径，占比更大
    center: ['50%', '42%'],
    roseType: 'radius',
    itemStyle: { borderRadius: 2, borderColor: '#0a0f18', borderWidth: 2 },
    label: { show: true, color: '#e5eef9', fontSize: 12, formatter: '{b}\n{c}座' },
    labelLine: { length: 5, length2: 5 },
    data: tierData.value
  }]
}));

// --- 图表 B：北上广深承载比环形图（扩大饼图半径和字号） ---
const contributionOption = computed(() => {
  const percent = total => {
    const val = contributionData.value[0].value;
    const tot = contributionData.value[0].value + contributionData.value[1].value;
    return tot === 0 ? 0 : ((val / tot) * 100).toFixed(1);
  };
  return {
    tooltip: { trigger: 'item', textStyle: { fontSize: 14 }, formatter: '{b} : {c}万 ({d}%)' },
    title: [{
      text: '一线客流承载比',
      left: 'center', top: 'bottom',
      textStyle: { color: '#8ea5bf', fontSize: 14, fontWeight: 'normal' }
    }, {
      text: `${percent()}%`,
      left: 'center', top: '35%',
      textStyle: { color: '#e5eef9', fontSize: 20, fontWeight: 'bold' } // 去除发光阴影，放大纯文本
    }],
    series: [{
      type: 'pie',
      radius: ['55%', '75%'], // 扩大内环和外环半径，使画面更饱满
      center: ['50%', '42%'],
      itemStyle: { borderColor: '#0a0f18', borderWidth: 2 },
      label: { show: false },
      data: contributionData.value
    }]
  };
});

// ==========================================
// 地图渲染逻辑升级 (扩大地图字体)
// ==========================================

const resizeMap = () => { if (mapChart) mapChart.resize(); };

const loadChinaGeoJson = async () => {
  if (!chinaGeoPromise) {
    chinaGeoPromise = fetch(CHINA_GEOJSON_URL).then((res) => {
      if (!res.ok) throw new Error(`Failed to load china geojson: ${res.status}`);
      return res.json();
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
      backgroundColor: "rgba(10, 15, 24, 0.95)",
      borderColor: "#22344d",
      textStyle: { color: "#e5eef9", fontSize: 14 },
      formatter: ({ data }) => {
        if (!data) return "";
        return `<div style="border-bottom: 1px solid #22344d; padding-bottom:4px; margin-bottom:4px; font-weight:bold; font-size:16px;">${data.name}</div>
                最新客流：<span style="color:#0081ff; font-weight:bold; font-size:16px;">${data.value[2]}</span> 万人次<br/>
                <span style="color:#8ea5bf; font-size:13px">统计日期：${data.statDate}</span>`;
      },
    },
    visualMap: {
      type: "continuous",
      show: true,
      min, max,
      calculable: true,
      inRange: { color: ["#00b365", "#0081ff", "#faad14", "#e60026"] },
      textStyle: { color: "#8ea5bf", fontSize: 13 },
      bottom: 15, left: 15,
      itemHeight: 110, itemWidth: 12,
    },
series: [
      {
        name: "普通城市",
        type: "scatter",
        coordinateSystem: hasGeoJson ? "geo" : "cartesian2d",
        data: mapData.value,
        // 基础点大小：最小 5，最大 16
        symbolSize: (val) => Math.max((val[2] / max) * 16, 5), 
        itemStyle: { opacity: 0.85 },
        label: {
          show: true, 
          formatter: "{b}", 
          position: "right",
          color: "#e5eef9", 
          fontSize: 11, // 略微缩小普通文字
        },
      },
      {
        name: "Top5 头部枢纽",
        type: "effectScatter",
        coordinateSystem: hasGeoJson ? "geo" : "cartesian2d",
        data: top5MapData.value,
        // 【变动】Top5 点大小：仅略大于普通点，最大 19，最小 7
        symbolSize: (val) => Math.max((val[2] / max) * 19, 7), 
        showEffectOn: "render",
        // 【变动】减小波纹扩散倍数，使其内敛 (scale 3 -> 2.2)
        rippleEffect: { brushType: "stroke", scale: 2.2 }, 
        itemStyle: { color: "#faad14" },
        label: {
          show: true, 
          formatter: "{b}", 
          position: "right",
          color: "#ffffff", 
          fontSize: 13, // 略微缩小
          fontWeight: "bold", 
        },
        zlevel: 1,
      }
    ],
  };

  if (hasGeoJson) {
    option.geo = {
      map: "china",
      roam: true,
      zoom: 1.18,
      center: [105, 36],
      itemStyle: {
        // 强化地图轮廓与省份区分
        areaColor: "#0a1018",      // 加深省份底色，增强对比度
        borderColor: "#4a6c98",    // 提亮省份边界线的颜色，使其明显突出 (明显区别于深色背景的灰蓝色)
        borderWidth: 1.5,          // 加粗边界线
      },
      emphasis: {
        // 鼠标悬浮时的明显交互反馈
        itemStyle: { 
            areaColor: "#1a2a40", 
            borderColor: "#00d2ff", 
            borderWidth: 2 
        },
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
  if (!mapChart) mapChart = echarts.init(mapRef.value);

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

watch(() => props.cities, () => { updateMap(); }, { deep: true });

onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeMap);
  if (mapChart) { mapChart.dispose(); mapChart = null; }
});
</script>

<style scoped>
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.city-select {
  background-color: rgba(10, 15, 24, 0.8);
  color: #e5eef9;
  border: 1px solid #22344d;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 13px;
  outline: none;
  cursor: pointer;
}
.city-select option {
  background-color: #0a0f18; /* 下拉选项背景适配暗黑风 */
}
</style>