# 🌐 Real-Time Cisco Network Telemetry & Monitoring System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![InfluxDB](https://img.shields.io/badge/InfluxDB-v2.9-purple?style=for-the-badge&logo=influxdb&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Live_Dashboard-orange?style=for-the-badge&logo=grafana&logoColor=white)
![Cisco](https://img.shields.io/badge/Cisco-GNS3_Emulation-049fd9?style=for-the-badge&logo=cisco&logoColor=white)

## 📖 Project Overview
A scalable Network Management System (NMS) designed to extract live performance metrics (CPU and RAM utilization) from a fleet of Cisco enterprise routers. This project automates SNMP data polling using Python, stores the telemetry data in an InfluxDB Time-Series Database, and visualizes the network health via a custom-built, real-time Grafana dashboard.

## ✨ Key Features
* **Automated Data Ingestion:** Python (`pysnmp`) script running in the background to poll network data every 5 seconds without manual intervention.
* **Time-Series Optimization:** Utilizes InfluxDB for highly efficient, time-stamped metric storage, far superior to traditional relational databases for this use case.
* **Live Network Visualization:** Interactive Grafana dashboard using **Flux** queries to display active CPU and Memory gauge charts.
* **Network Emulation:** Fully simulated enterprise topology using Cisco C7200 routers within GNS3, bridged to the local host via a Microsoft Loopback Adapter.

---

## 🏗️ Architecture & Data Flow

```text
  [ Cisco C7200 Routers (GNS3) ] 
       (R1, R2, R3, R4)
               │ 
               │  SNMPv2c Polling (UDP Port 161)
               ▼
  [ Python Data Collector ]  <-- (pysnmp, influxdb-client)
               │ 
               │  HTTP Write API
               ▼
  [ InfluxDB Time-Series DB ] <-- (Bucket: RouterMetrics)
               │ 
               │  Flux Queries (Port 8086)
               ▼
  [ Grafana Live Dashboard ]  <-- (Port 3000)
