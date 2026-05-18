# MetroFlow 地铁客流可视化系统

MetroFlow 是一个面向课程项目与本地演示场景的地铁客流可视化系统，采用前后端分离架构，实现全国城市宏观客流展示与上海地铁微观时空客流分析。

## 项目概述

系统包含两个业务页面：

- 全国概览
  - 城市客流分布图
  - 客流 Top10 排名
  - 关键指标卡片
  - 全国与上海趋势对比
- 上海微观
  - 地铁线路拓扑与站点客流叠加图
  - 小时级时间轴与动态回放
  - 线路热力条
  - 全天负荷趋势
  - 热点站点 Top5

## 技术栈

- 前端：Vue 3、Vite、ECharts 5、Axios
- 后端：Flask
- 数据处理：Python、Pandas
- 数据存储：CSV 直读为默认模式，MySQL 为可选模式

## 核心数据源

项目当前仅使用以下原始数据文件：

- `data/count_df.csv`
- `data/metro_global.json`
- `data/station_info.json`

允许通过脚本生成中间产物，所有处理后文件统一输出到 `data/processed/`。

## 目录结构

```text
final-project/
├── backend/
├── data/
├── docs/
├── frontend/
├── scripts/
├── sql/
├── demo.html
└── README.md
```

详细目录说明见 [docs/项目结构设计.md](/home/cxy/projects/final-project/docs/项目结构设计.md:1)。

## 快速开始

推荐采用默认的 CSV 直读模式。

1. 生成处理后数据

```bash
python scripts/clean_data.py
```

2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

如需使用单文件页面联调，可在后端启动后直接打开 `demo.html`，或通过静态服务器访问：

```bash
python -m http.server 8080
```

详细启动说明见：

- [docs/快速启动.md](/home/cxy/projects/final-project/docs/快速启动.md:1)
- [docs/使用指南.md](/home/cxy/projects/final-project/docs/使用指南.md:1)

## 处理后数据

执行 `scripts/clean_data.py` 后，默认生成以下文件：

- `data/processed/dim_station.csv`
- `data/processed/fact_hourly_flow.csv`
- `data/processed/macro_city_flow_clean.csv`
- `data/processed/shanghai_line_topology.json`

## 主要接口

- `GET /api/overview`
- `GET /api/overview/cities`
- `GET /api/shanghai/topology`
- `GET /api/shanghai/flow?hour=8`
- `GET /api/shanghai/lines?hour=8`
- `GET /api/shanghai/load-trend?line=all`
- `GET /api/shanghai/station/<station>`

## 文档索引

- [快速启动](/home/cxy/projects/final-project/docs/快速启动.md:1)
- [使用指南](/home/cxy/projects/final-project/docs/使用指南.md:1)
- [项目结构设计](/home/cxy/projects/final-project/docs/项目结构设计.md:1)
- [系统设计指南](/home/cxy/projects/final-project/docs/系统设计指南.md:1)
