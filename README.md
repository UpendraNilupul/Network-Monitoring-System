# 🌐 Real-Time Cisco Network Telemetry & Monitoring System

![Docker Compose](https://img.shields.io/badge/Docker_Compose-v2-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white)
![InfluxDB](https://img.shields.io/badge/InfluxDB-v2.7-purple?style=for-the-badge&logo=influxdb&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Live_Dashboard-orange?style=for-the-badge&logo=grafana&logoColor=white)
![Cisco](https://img.shields.io/badge/Cisco-GNS3_C7200-049fd9?style=for-the-badge&logo=cisco&logoColor=white)
![SNMP](https://img.shields.io/badge/Protocol-SNMPv2c-brightgreen?style=for-the-badge)

## 📖 Overview
An enterprise-grade, containerized Network Telemetry and Observability pipeline designed to extract, process, store, and visualize real-time performance metrics across a fleet of Cisco enterprise routers.

The entire stack—**InfluxDB Time-Series Database**, **Grafana Analytics Engine**, and the **Custom Python SNMP Collector Daemon**—is orchestrated via **Docker Compose**, enabling complete, isolated, one-command deployment.

---

## 📸 Live Dashboard Preview

| Normal State (All Nodes UP) | Single Node Outage (R1 DOWN) | Full Network Outage (All DOWN) |
| :---: | :---: | :---: |
| ![All Nodes UP](<screenshots/All No shutdown.png>) | ![R1 Down](<screenshots/R1 Down.png>) | ![All Down](<screenshots/shutdown all.png>) |

---

## ✨ Key Capabilities

- **Turnkey Containerized Deployment:** Run the complete observability infrastructure (InfluxDB, Grafana, and Collector) with `docker compose up -d`.
- **Dynamic Bandwidth Tracking (Mbps):** Polling 32-bit interface counters (`ifInOctets` / `ifOutOctets`) and calculating dynamic rate-of-change across time deltas ($\Delta t$):
  $$\text{Throughput (Mbps)} = \frac{(\text{Current Octets} - \text{Previous Octets}) \times 8}{\Delta t \times 10^6}$$
- **Fault-Tolerant State Persistence:** Continuous node status heartbeats (`1 = UP`, `2 = DOWN`). In the event of network disruption or router shutdown, fallback records ($0\%$ CPU/RAM, status `2`) are written to InfluxDB to retain historic metrics and prevent panel drops.
- **Hardware Utilization Monitoring:** Direct retrieval of Cisco enterprise MIBs to compute real-time CPU utilization and RAM allocation percentage (Used vs. Free memory pool).
- **Decoupled Credential Management:** All sensitive tokens, organizations, and database buckets are managed via environment variables (`.env`).

---

## 🏗️ System Architecture & Data Pipeline

```text
 ┌─────────────────────────────────────────────────────────────┐
 │               Cisco Enterprise Routers (GNS3)               │
 │           [R1: .2]   [R2: .3]   [R3: .4]   [R4: .5]         │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                │ SNMP GET (UDP 161)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                      DOCKER COMPOSE                         │
 │                                                             │
 │  ┌───────────────────────────────────────────────────────┐  │
 │  │        python_snmp_collector (Docker Container)       │  │
 │  │  - Delta Octet throughput calculation                 │  │
 │  │  - SNMP timeout detection & DOWN state injection      │  │
 │  └───────────────────────────┬───────────────────────────┘  │
 │                              │ Line Protocol / Influx API    │
 │                              ▼                              │
 │  ┌───────────────────────────────────────────────────────┐  │
 │  │             influxdb_nms (Port 18086/8086)            │  │
 │  │  - Bucket: RouterMetrics                              │  │
 │  └───────────────────────────┬───────────────────────────┘  │
 │                              │ Flux Query Engine            │
 │                              ▼                              │
 │  ┌───────────────────────────────────────────────────────┐  │
 │  │              grafana_nms (Port 3000)                  │  │
 │  │  - CPU & RAM Gauges, Traffic Graphs, Health Stat Cards│  │
 │  └───────────────────────────────────────────────────────┘  │
 └─────────────────────────────────────────────────────────────┘
