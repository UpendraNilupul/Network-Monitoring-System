# 🌐 Real-Time Cisco Network Telemetry & Monitoring System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![InfluxDB](https://img.shields.io/badge/InfluxDB-v2.x-purple?style=for-the-badge&logo=influxdb&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Live_Dashboard-orange?style=for-the-badge&logo=grafana&logoColor=white)
![Cisco](https://img.shields.io/badge/Cisco-GNS3_Emulation-049fd9?style=for-the-badge&logo=cisco&logoColor=white)
![SNMP](https://img.shields.io/badge/Protocol-SNMPv2c-brightgreen?style=for-the-badge)

## 📖 Project Overview
An enterprise-grade Network Management System (NMS) designed to poll, process, store, and visualize real-time performance and telemetry data across a fleet of Cisco routers. 

Built using Python (`pysnmp`), InfluxDB Time-Series Database, and Grafana, this project delivers sub-second network observability, real-time throughput calculations, interface state monitoring, and automated offline fault-handling logic.

---

## 📸 Live Dashboard Preview

![Grafana Dashboard](<screenshots/All No shutdown.png>)
<screenshots/All No shutdown.png>
<screenshots/All No shutdown.png>

---

## ✨ Key Features

- **Automated SNMP Telemetry Pipeline:** Continuous background polling (5-second cycle) via SNMPv2c across all active network nodes.
- **Dynamic Bandwidth Tracking (Throughput in Mbps):** Polls raw interface Inbound/Outbound Octets (`ifInOctets` / `ifOutOctets`) and performs dynamic rate calculation using time deltas ($\Delta t$):
  $$\text{Throughput (Mbps)} = \frac{(\text{Current Octets} - \text{Previous Octets}) \times 8}{\Delta t \times 10^6}$$
- **Fault-Tolerant Availability State:** Implements continuous heartbeat logging (`1 = UP`, `2 = DOWN`). Even when a node is unreachable or powered down, the pipeline writes fallback metrics ($0\%$ CPU/RAM and `DOWN` state) to prevent panels from disappearing from the dashboard.
- **Hardware Utilization Metrics:** Direct retrieval and transformation of Cisco enterprise MIBs for CPU load and memory usage (Used vs. Free memory calculation).
- **Time-Series Optimization:** InfluxDB 2.x bucket structure with tag-based indexing (`router_ip`) for rapid Flux query execution.
- **NOC-Ready Grafana Visualization:**
  - **Router CPU Usage:** Color-coded multi-bar gauge panels with percentage thresholds.
  - **Router RAM Utilization:** Dynamic gauge dials representing allocated memory.
  - **Network Traffic (In/Out):** Dedicated time-series graphs for Download and Upload traffic rates.
  - **Router Availability Status:** Real-time health stat cards mapped with instant Green/Red visual alerts.

---

## 🏗️ Architecture & Telemetry Pipeline

```text
 ┌─────────────────────────────────────────────────────────────────┐
 │               Cisco Enterprise Routers (GNS3)                   │
 │                [R1: .2]  [R2: .3]  [R3: .4]  [R4: .5]          │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
                                 │ SNMP GET Requests (UDP 161)
                                 │ [CPU, RAM, In/Out Octets, Port State]
                                 ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │                   Python Data Collector Engine                  │
 │                      (get_router_data.py)                       │
 │  - Delta Byte Calculation -> Mbps                               │
 │  - Failure handling: logs DOWN (2) on timeout                   │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
                                 │ HTTP Line Protocol / Influx Client API
                                 ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │                InfluxDB 2.x Time-Series Database                │
 │                     (Bucket: RouterMetrics)                     │
 └───────────────────────────────┬─────────────────────────────────┘
                                 │
                                 │ Flux Queries (Port 8086)
                                 ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │                 Grafana NOC Real-Time Dashboard                 │
 │             [CPU Bars] [RAM Gauges] [Traffic] [Node Health]     │
 └─────────────────────────────────────────────────────────────────┘
