import os
import time
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-super-secret-admin-token-123456789")
INFLUX_ORG = os.getenv("INFLUX_ORG", "JaffnaUni")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "RouterMetrics")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

routers = ['192.168.100.2', '192.168.100.3', '192.168.100.4', '192.168.100.5']
community = 'public'
prev_traffic = {}

def get_snmp_data(ip, oid):
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((ip, 161), timeout=2, retries=1),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )
        if errorIndication or errorStatus:
            return None
        return int(varBinds[0][1])
    except Exception:
        return None

print("Dockerized Collector Started... Monitoring routers.")

try:
    while True:
        current_time = time.time()
        for ip in routers:
            cpu_oid = '1.3.6.1.4.1.9.9.109.1.1.1.1.5.1'
            ram_used_oid = '1.3.6.1.4.1.9.9.48.1.1.1.5.1'
            ram_free_oid = '1.3.6.1.4.1.9.9.48.1.1.1.6.1'
            in_octets_oid = '1.3.6.1.2.1.2.2.1.10.1'
            out_octets_oid = '1.3.6.1.2.1.2.2.1.16.1'
            status_oid = '1.3.6.1.2.1.2.2.1.8.1'

            cpu = get_snmp_data(ip, cpu_oid)
            ram_used = get_snmp_data(ip, ram_used_oid)
            ram_free = get_snmp_data(ip, ram_free_oid)
            in_octets = get_snmp_data(ip, in_octets_oid)
            out_octets = get_snmp_data(ip, out_octets_oid)
            if_status = get_snmp_data(ip, status_oid)

            if cpu is not None and ram_used is not None and ram_free is not None:
                total_ram = ram_used + ram_free
                ram_percentage = round((ram_used / total_ram) * 100, 2)

                in_mbps = 0.0
                out_mbps = 0.0
                if ip in prev_traffic and in_octets is not None and out_octets is not None:
                    prev_in, prev_out, prev_time = prev_traffic[ip]
                    time_diff = current_time - prev_time
                    if time_diff > 0:
                        in_mbps = round(max(0, (in_octets - prev_in) * 8 / (time_diff * 1000000)), 2)
                        out_mbps = round(max(0, (out_octets - prev_out) * 8 / (time_diff * 1000000)), 2)

                if in_octets is not None and out_octets is not None:
                    prev_traffic[ip] = (in_octets, out_octets, current_time)

                point = Point("router_metrics") \
                    .tag("router_ip", ip) \
                    .field("cpu_usage", float(cpu)) \
                    .field("ram_usage", float(ram_percentage)) \
                    .field("download_mbps", float(in_mbps)) \
                    .field("upload_mbps", float(out_mbps)) \
                    .field("interface_status", int(if_status if if_status is not None else 1))

                write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
                print(f"[{ip}] UP -> CPU: {cpu}% | RAM: {ram_percentage}%")
            else:
                point = Point("router_metrics") \
                    .tag("router_ip", ip) \
                    .field("cpu_usage", 0.0) \
                    .field("ram_usage", 0.0) \
                    .field("download_mbps", 0.0) \
                    .field("upload_mbps", 0.0) \
                    .field("interface_status", 2)

                write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
                print(f"[{ip}] DOWN -> Logged to DB")

        time.sleep(5)

except KeyboardInterrupt:
    client.close()