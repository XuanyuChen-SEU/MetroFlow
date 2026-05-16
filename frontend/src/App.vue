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
      :topology="topology"
      :playing="playing"
      :station-detail="stationDetail"
      @select-station="loadStationDetail"
      @toggle-play="togglePlay"
    />
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

import { fetchCities, fetchHourFlow, fetchLineHeat, fetchOverview, fetchShanghaiTopology, fetchStationDetail } from "./api";
import NationalOverview from "./views/NationalOverview.vue";
import ShanghaiDetail from "./views/ShanghaiDetail.vue";

const activeTab = ref("national");
const overview = ref({
  metrics: { city_count: 0, latest_stat_date: "-", tracked_days: 0, total_daily_flow: 0, station_count: 0, transfer_station_count: 0 },
  top10: [],
  trend: [],
  meta: { source: null, scraped_at_epoch: null, peak_city: null },
});
const cities = ref([]);
const hour = ref(8);
const flow = ref([]);
const lines = ref([]);
const topology = ref({ lines: [], extent: null });
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
  const currentStation = stationDetail.value?.station?.station_name;
  const nextStation = flow.value.some((item) => item.station_name === currentStation)
    ? currentStation
    : (flow.value[0]?.station_name ?? "人民广场");
  await loadStationDetail(nextStation);
};

const loadStationDetail = async (station) => {
  if (!station) return;
  const stationRes = await fetchStationDetail(station);
  stationDetail.value = stationRes.data.data;
};

const loadTopology = async () => {
  const topologyRes = await fetchShanghaiTopology();
  topology.value = topologyRes.data.data;
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
  await loadTopology();
  await loadShanghai();
});

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer);
  }
});
</script>
