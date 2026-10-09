# 🌐 Real-Time Cisco Network Telemetry & Monitoring System

A scalable Network Monitoring System (NMS) designed to extract real-time performance metrics (CPU and RAM usage) from Cisco routers using **SNMPv2c**, ingest the metrics into an **InfluxDB Time-Series Database**, and visualize live statistics using **Grafana**.

---

## 📌 Architecture Overview

```text
[ Cisco C7200 Routers (GNS3) ] 
               │  (SNMP Polling / UDP Port 161)
               ▼
[ Python Collector (pysnmp) ]
               │  (Write API / HTTP)
               ▼
[ InfluxDB (Time-Series DB) ]
               │  (Flux Query / Port 8086)
               ▼
[ Grafana Dashboard (Port 3000) ]
