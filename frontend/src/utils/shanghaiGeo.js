import * as echarts from "echarts";

import shanghaiGeoJson from "../assets/shanghai.json";

const MERCATOR_RADIUS = 20037508.342789244;
export const SHANGHAI_GEOJSON_URL =
  "https://geo.datav.aliyun.com/areas_v3/bound/310000_full.json";

let mapRegistered = false;

/** 标准 Web Mercator (EPSG:3857) → [lng, lat] */
export function mercatorToLngLat(x, y) {
  const lng = (x / MERCATOR_RADIUS) * 180;
  const latRad = Math.atan(Math.sinh((y / MERCATOR_RADIUS) * Math.PI));
  const lat = (latRad * 180) / Math.PI;
  return [lng, lat];
}

/**
 * station_info.json 的 plot_y 比 GCJ 下的 Web Mercator 纵坐标少约 21778m。
 * 用龙漕路参考点（121.4397, 31.1716）标定，叠到 DataV GCJ 市界底图时需补回。
 */
export const STATION_MERCATOR_Y_OFFSET = 21778.16;

/** 将站点拓扑 plot_x/plot_y 转为可与上海 GCJ 底图对齐的 [lng, lat] */
export function stationPlotToGcjLngLat(plotX, plotY) {
  return mercatorToLngLat(plotX, plotY + STATION_MERCATOR_Y_OFFSET);
}

function registerShanghaiMap() {
  if (!mapRegistered) {
    echarts.registerMap("shanghai", shanghaiGeoJson);
    mapRegistered = true;
  }
}

/** 注册 ECharts 上海地图（内置静态 GeoJSON，不依赖外网） */
export function loadShanghaiGeoMap() {
  registerShanghaiMap();
  return Promise.resolve(shanghaiGeoJson);
}
