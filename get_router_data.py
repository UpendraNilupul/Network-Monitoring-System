
import time
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Configuration
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "YOUR_INFLUXDB_TOKEN_HERE"  
INFLUX_ORG = "JaffnaUni"
INFLUX_BUCKET = "RouterMetrics"

# Initialize the InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

routers = ['192.168.100.2', '192.168.100.3', '192.168.100.4', '192.168.100.5']
community = 'public'

def get_snmp_data(ip, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161), timeout=5, retries=3),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )
    if errorIndication or errorStatus:
        return None
    return int(varBinds[0][1])

print("Monitoring started... Press Ctrl+C to stop.")

# Continuously send data to the database every 5 seconds
try:
    while True:
        for ip in routers:
            cpu_oid = '1.3.6.1.4.1.9.9.109.1.1.1.1.5.1'
            ram_used_oid = '1.3.6.1.4.1.9.9.48.1.1.1.5.1'
            ram_free_oid = '1.3.6.1.4.1.9.9.48.1.1.1.6.1'

            cpu = get_snmp_data(ip, cpu_oid)
            ram_used = get_snmp_data(ip, ram_used_oid)
            ram_free = get_snmp_data(ip, ram_free_oid)

            if cpu is not None and ram_used is not None and ram_free is not None:
                total_ram = ram_used + ram_free
                ram_percentage = round((ram_used / total_ram) * 100, 2)

                # Create a data point for InfluxDB
                point = Point("router_metrics") \
                    .tag("router_ip", ip) \
                    .field("cpu_usage", float(cpu)) \
                    .field("ram_usage", float(ram_percentage))

                write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
                print(f"Logged to DB: Router {ip} -> CPU: {cpu}% | RAM: {ram_percentage}%")
            else:
                print(f"Failed to fetch data from Router {ip}")

        print("--- Cycle completed. Waiting for next cycle... ---")
        time.sleep(5)

except KeyboardInterrupt:
    print("Monitoring stopped.")
    client.close()
