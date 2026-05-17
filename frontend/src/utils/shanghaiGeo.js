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

export const DEFAULT_GEO_VIEW = {
  center: [121.48, 31.23],
  zoom: 1.08,
  layoutCenter: ["50%", "52%"],
  layoutSize: "112%",
};

function walkCoordinates(geometry, visitor) {
  const { type, coordinates } = geometry ?? {};
  if (!coordinates) return;

  if (type === "Polygon") {
    for (const ring of coordinates) {
      for (const point of ring) visitor(point);
    }
    return;
  }

  if (type === "MultiPolygon") {
    for (const polygon of coordinates) {
      for (const ring of polygon) {
        for (const point of ring) visitor(point);
      }
    }
  }
}

function pointInRing(lng, lat, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    const intersect =
      yi > lat !== yj > lat && lng < ((xj - xi) * (lat - yi)) / (yj - yi + Number.EPSILON) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

export function getDistrictFeature(districtName) {
  return (shanghaiGeoJson.features ?? []).find((feature) => feature.properties?.name === districtName);
}

export function pointInDistrict(lng, lat, districtName) {
  const feature = getDistrictFeature(districtName);
  if (!feature?.geometry) return false;

  const { type, coordinates } = feature.geometry;
  if (type === "Polygon") {
    return pointInRing(lng, lat, coordinates[0]);
  }
  if (type === "MultiPolygon") {
    return coordinates.some((polygon) => pointInRing(lng, lat, polygon[0]));
  }
  return false;
}

export function getDistrictBounds(districtName) {
  const feature = getDistrictFeature(districtName);
  if (!feature) return null;

  let minLng = Infinity;
  let maxLng = -Infinity;
  let minLat = Infinity;
  let maxLat = -Infinity;

  walkCoordinates(feature.geometry, ([lng, lat]) => {
    minLng = Math.min(minLng, lng);
    maxLng = Math.max(maxLng, lng);
    minLat = Math.min(minLat, lat);
    maxLat = Math.max(maxLat, lat);
  });

  if (!Number.isFinite(minLng)) return null;
  return { minLng, maxLng, minLat, maxLat };
}

/** 根据区划范围计算合适的 geo 缩放与中心 */
export function geoViewForBounds(bounds, padding = 1.22) {
  const lngSpan = Math.max((bounds.maxLng - bounds.minLng) * padding, 0.055);
  const latSpan = Math.max((bounds.maxLat - bounds.minLat) * padding, 0.045);
  const span = Math.max(lngSpan, latSpan);

  return {
    center: [(bounds.minLng + bounds.maxLng) / 2, (bounds.minLat + bounds.maxLat) / 2],
    zoom: Math.min(14, Math.max(2.4, 0.46 / span)),
    layoutCenter: ["50%", "50%"],
    layoutSize: "88%",
  };
}

export function getDistrictLabelPoints() {
  return (shanghaiGeoJson.features ?? []).map((feature) => {
    const name = feature.properties?.name ?? "";
    const center = feature.properties?.centroid ?? feature.properties?.center ?? [0, 0];
    return { name, value: center };
  });
}
