# MetroFlow 地铁客流可视化系统

> 课程项目目标：构建一套基于 `Vue3 + Vite + ECharts + Axios + Flask + MySQL` 的双页面地铁客流可视化系统。
>
> 当前仓库阶段：`需求梳理 + 运行文档 + 项目结构设计`。

## 1. 这份 README 的作用

这份文档先解决两件事：

1. 明确当前仓库里已经有什么、还缺什么。
2. 给出后续完整项目生成后的标准运行方式，避免目录和启动命令混乱。

目前仓库中已经存在：

- [demo.html](/D:/Desktop/虚拟现实与数据可视化/final-project/demo.html)
- [data/count_df.csv](/D:/Desktop/虚拟现实与数据可视化/final-project/data/count_df.csv)
- [data/metro_city_flow.csv](/D:/Desktop/虚拟现实与数据可视化/final-project/data/metro_city_flow.csv)
- [data/station_info.json](/D:/Desktop/虚拟现实与数据可视化/final-project/data/station_info.json)
- [docs/系统设计指南.md](/D:/Desktop/虚拟现实与数据可视化/final-project/docs/系统设计指南.md)
- [docs/使用指南.md](/D:/Desktop/虚拟现实与数据可视化/final-project/docs/使用指南.md)

当前仓库现在已经补齐的可启动内容：

- `backend/` Flask 后端
- `frontend/` Vue3 + Vite 前端骨架
- `scripts/` 数据清洗与导入脚本
- `sql/` MySQL 建表脚本
- `data/processed/` 清洗后中间数据

如果你要最快速联调，优先看：

- [docs/使用指南.md](/D:/Desktop/虚拟现实与数据可视化/final-project/docs/使用指南.md)

早期版本中还没有真正可启动的：

- `frontend/` Vue3 前端工程
- `backend/` Flask 后端工程
- `sql/` MySQL 初始化脚本
- `scripts/` 数据清洗与入库脚本

现在这部分已经完成，可以按使用指南直接启动后端和演示页。

## 2. 项目目标

系统分为两个主页面：

- `Tab1` 全国地铁概览
  - 气泡地图
  - 客流 Top10 柱状图
  - 4 个指标卡片
  - 趋势图
- `Tab2` 上海地铁微观客流可视化
  - 站点散点图
  - 24 小时时间滑块
  - 动态回放
  - 线路热力条
  - 站点详情折线图

## 3. 指定数据源

本项目后续只使用以下 3 个文件作为业务数据源：

- `count_df.csv`
- `metro_city_flow.csv`
- `station_info.json`

约束说明：

- 不再引入额外原始 CSV 作为核心输入。
- 允许通过 Python 清洗脚本基于这 3 份文件生成中间产物。
- `demo.html` 只作为前端视觉和布局参考，不作为数据源。

## 4. 推荐目录结构

完整项目将采用下面这套目录结构：

```text
final-project/
├── frontend/                       # Vue3 + Vite 前端
│   ├── public/
│   │   └── china.json             # 全国地图 GeoJSON
│   ├── src/
│   │   ├── api/
│   │   │   └── index.js           # Axios 请求封装
│   │   ├── assets/
│   │   │   └── styles/
│   │   │       ├── theme.css
│   │   │       └── screen.css
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── cards/
│   │   │   ├── charts/
│   │   │   └── controls/
│   │   ├── composables/
│   │   ├── views/
│   │   │   ├── NationalOverview.vue
│   │   │   └── ShanghaiDetail.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── backend/                        # Flask 后端
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── extensions.py
│   ├── db/
│   │   └── mysql.py
│   ├── api/
│   │   ├── macro.py
│   │   └── shanghai.py
│   ├── services/
│   │   ├── macro_service.py
│   │   └── shanghai_service.py
│   └── utils/
│       └── response.py
├── sql/
│   ├── schema.sql                  # 3 张表建表语句
│   └── seed_example.sql            # 可选示例导入脚本
├── scripts/                        # 数据清洗、转换、入库
│   ├── clean_data.py
│   ├── export_seed_csv.py
│   └── load_mysql.py
├── data/
│   ├── count_df.csv
│   ├── metro_city_flow.csv
│   ├── station_info.json
│   ├── processed/
│   │   ├── dim_station.csv
│   │   ├── fact_hourly_flow.csv
│   │   └── macro_city_flow_clean.csv
│   └── samples/
├── docs/
│   ├── 系统设计指南.md
│   └── 项目结构设计.md
├── demo.html
└── README.md
```

详细说明见 [docs/项目结构设计.md](/D:/Desktop/虚拟现实与数据可视化/final-project/docs/项目结构设计.md)。

## 5. 数据库设计

系统使用 MySQL，包含 3 张业务表：

### 5.1 `dim_station`

上海地铁站点维表，保存站点基础信息：

- 站点 ID
- 站点名称
- 所属线路
- 经纬度
- 是否换乘站

### 5.2 `fact_hourly_flow`

上海地铁小时客流事实表，保存每个站点在 24 小时维度上的客流或拥挤度：

- 日期
- 小时
- 站点 ID
- 进站量
- 出站量
- 总客流
- 拥挤指数

### 5.3 `macro_city_flow`

全国地铁城市宏观统计表，保存城市级聚合指标：

- 城市名称
- 客流规模
- 线路数量
- 运营里程
- 经纬度

## 6. 规划中的 5 个 RESTful API

后端将提供以下 5 个接口：

1. `GET /api/macro/overview`
   - 全国概览卡片数据
2. `GET /api/macro/cities`
   - 全国城市气泡地图数据
3. `GET /api/macro/top10`
   - 全国客流 Top10
4. `GET /api/shanghai/flow?hour=08`
   - 上海指定小时站点散点数据
5. `GET /api/shanghai/station/<station_id>`
   - 单站点 24 小时详情曲线

说明：

- 线路热力条可以由 `/api/shanghai/flow` 聚合生成，也可以在实现阶段单独拆出接口。
- 如果后续你坚持必须独立成第 6 个接口，我会在真正开发后端时补为 `/api/shanghai/line-heat`。

## 7. 前端页面规划

### 7.1 Tab1 全国地铁概览

参考 [demo.html](/D:/Desktop/虚拟现实与数据可视化/final-project/demo.html) 的深色大屏风格，实现：

- 顶部导航
- 4 个指标卡
- 全国地铁客流气泡地图
- 客流 Top10 柱状图
- 趋势折线图

### 7.2 Tab2 上海微观客流

实现：

- 24 小时时间滑块
- 自动回放控制
- 上海站点散点图
- 线路热力条
- 站点详情折线图

## 8. 运行环境约定

后续完整代码生成后，运行环境统一按下面准备：

### 8.1 基础环境

- Node.js `18+`
- npm `9+`
- Python `3.10+`
- MySQL `8.0+`

### 8.2 建议的本地端口

- 前端：`5173`
- 后端：`5000`
- MySQL：`3306`

## 9. 完整系统的标准运行流程

下面这部分是后续完整代码生成完之后的标准启动顺序。

### 9.1 创建数据库

先在 MySQL 中创建数据库：

```sql
CREATE DATABASE metroflow DEFAULT CHARACTER SET utf8mb4;
```

### 9.2 执行建表脚本

```bash
mysql -u root -p metroflow < sql/schema.sql
```

### 9.3 清洗并生成中间数据

```bash
python scripts/clean_data.py
```

输出目录预期为：

- `data/processed/dim_station.csv`
- `data/processed/fact_hourly_flow.csv`
- `data/processed/macro_city_flow_clean.csv`

### 9.4 导入 MySQL

```bash
python scripts/load_mysql.py
```

### 9.5 启动后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

启动成功后预期访问：

- `http://127.0.0.1:5000`

### 9.6 启动前端

```bash
cd frontend
npm install
npm run dev
```

启动成功后预期访问：

- `http://127.0.0.1:5173`

## 10. 当前你现在能做什么

在完整工程代码生成之前，你现在可以先做两件事：

### 10.1 查看静态原型

直接打开 [demo.html](/D:/Desktop/虚拟现实与数据可视化/final-project/demo.html)。

### 10.2 核对原始数据

确认以下文件可正常读取：

- [data/count_df.csv](/D:/Desktop/虚拟现实与数据可视化/final-project/data/count_df.csv)
- [data/metro_city_flow.csv](/D:/Desktop/虚拟现实与数据可视化/final-project/data/metro_city_flow.csv)
- [data/station_info.json](/D:/Desktop/虚拟现实与数据可视化/final-project/data/station_info.json)

## 11. 当前阶段结论

当前仓库已经具备：

- 原型页面
- 原始数据
- 设计文档

当前仓库尚不具备：

- 可直接运行的前后端代码
- MySQL 建表与导入脚本
- 数据清洗脚本

因此，当前 README 已经改成后续开发的统一约束文档。接下来生成代码时，我会严格按本 README 和 `docs/项目结构设计.md` 的结构落盘，确保你后面可以直接运行。
