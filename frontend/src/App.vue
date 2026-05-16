<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <div class="brand">MetroFlow</div>
        <div class="subtitle">地铁客流可视化演示</div>
      </div>
      <nav class="tabs">
        <button :class="['tab-btn', activeTab === 'national' && 'active']" @click="activeTab = 'national'">全国概览</button>
        <button :class="['tab-btn', activeTab === 'shanghai' && 'active']" @click="activeTab = 'shanghai'">上海微观</button>
      </nav>
    </header>

    <NationalOverview v-if="activeTab === 'national'" :overview="overview" :cities="cities" />
    <ShanghaiDetail
      v-else
      v-model:hour="hour"
      :flow="flow"
      :lines="lines"
      :playing="playing"
      :station-detail="stationDetail"
      @toggle-play="togglePlay"
    />
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

import { fetchCities, fetchHourFlow, fetchLineHeat, fetchOverview, fetchStationDetail } from "./api";
import NationalOverview from "./views/NationalOverview.vue";
import ShanghaiDetail from "./views/ShanghaiDetail.vue";

const activeTab = ref("national");
const overview = ref({ metrics: { city_count: 0, total_daily_flow: 0, station_count: 0, transfer_station_count: 0 }, top10: [], trend: [] });
const cities = ref([]);
const hour = ref(8);
const flow = ref([]);
const lines = ref([]);
const stationDetail = ref({ station: null, series: [] });
const playing = ref(false);

let timer = null;

const loadOverview = async () => {
  const [overviewRes, cityRes] = await Promise.all([fetchOverview(), fetchCities()]);
  overview.value = overviewRes.data.data;
  cities.value = cityRes.data.data;
};

const loadShanghai = async () => {
  const [flowRes, lineRes] = await Promise.all([fetchHourFlow(hour.value), fetchLineHeat(hour.value)]);
  flow.value = flowRes.data.data;
  lines.value = lineRes.data.data;
  const defaultStation = flow.value[0]?.station_name ?? "人民广场";
  const stationRes = await fetchStationDetail(defaultStation);
  stationDetail.value = stationRes.data.data;
};

const togglePlay = () => {
  playing.value = !playing.value;
  if (playing.value) {
    timer = window.setInterval(() => {
      hour.value = (hour.value + 1) % 24;
    }, 1000);
  } else if (timer) {
    window.clearInterval(timer);
    timer = null;
  }
};

watch(hour, loadShanghai);

onMounted(async () => {
  await loadOverview();
  await loadShanghai();
});

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer);
  }
});
</script>
