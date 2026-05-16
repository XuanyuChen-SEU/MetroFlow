import axios from "axios";

const request = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

export const fetchOverview = () => request.get("/overview");
export const fetchCities = () => request.get("/overview/cities");
export const fetchShanghaiTopology = () => request.get("/shanghai/topology");
export const fetchHourFlow = (hour) => request.get("/shanghai/flow", { params: { hour } });
export const fetchLineHeat = (hour) => request.get("/shanghai/lines", { params: { hour } });
export const fetchShanghaiLoadTrend = (line = "all") => request.get("/shanghai/load-trend", { params: { line } });
export const fetchStationDetail = (station) => request.get(`/shanghai/station/${encodeURIComponent(station)}`);
