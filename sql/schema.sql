CREATE DATABASE IF NOT EXISTS metroflow DEFAULT CHARACTER SET utf8mb4;
USE metroflow;

CREATE TABLE IF NOT EXISTS dim_station (
  station_id INT PRIMARY KEY,
  station_name VARCHAR(64) NOT NULL,
  line_names VARCHAR(255) NOT NULL,
  line_count INT NOT NULL,
  line_variants TEXT NOT NULL,
  line_variant_count INT NOT NULL,
  topology_record_count INT NOT NULL,
  is_transfer TINYINT(1) NOT NULL DEFAULT 0,
  longitude DECIMAL(10, 6) NULL,
  latitude DECIMAL(10, 6) NULL,
  plot_x DOUBLE NOT NULL,
  plot_y DOUBLE NOT NULL,
  INDEX idx_station_name (station_name)
);

CREATE TABLE IF NOT EXISTS fact_hourly_flow (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  station_id INT NOT NULL,
  station_name VARCHAR(64) NOT NULL,
  line_names VARCHAR(255) NOT NULL,
  line_count INT NOT NULL,
  line_variants TEXT NOT NULL,
  line_variant_count INT NOT NULL,
  topology_record_count INT NOT NULL,
  is_transfer TINYINT(1) NOT NULL DEFAULT 0,
  hour_of_day TINYINT NOT NULL,
  hour_label VARCHAR(8) NOT NULL,
  avg_flow INT NOT NULL,
  crowd_index INT NOT NULL,
  plot_x DOUBLE NOT NULL,
  plot_y DOUBLE NOT NULL,
  INDEX idx_hour_station (hour_of_day, station_id),
  CONSTRAINT fk_hourly_station FOREIGN KEY (station_id) REFERENCES dim_station (station_id)
);

CREATE TABLE IF NOT EXISTS macro_city_flow (
  city_id INT PRIMARY KEY AUTO_INCREMENT,
  city_slug VARCHAR(64) NOT NULL,
  city_name VARCHAR(32) NOT NULL,
  stat_date DATE NOT NULL,
  avg_daily_flow DECIMAL(10, 2) NOT NULL,
  latest_update DATE NOT NULL,
  is_latest TINYINT(1) NOT NULL DEFAULT 0,
  days_from_latest INT NOT NULL DEFAULT 0,
  longitude DECIMAL(10, 6) NULL,
  latitude DECIMAL(10, 6) NULL,
  source VARCHAR(255) NULL,
  scraped_at_epoch BIGINT NULL,
  INDEX idx_city_name (city_name),
  INDEX idx_city_date (city_name, stat_date)
);
