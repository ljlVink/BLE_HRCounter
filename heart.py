import asyncio
from bleak import BleakClient, BleakScanner
import yaml
from aiohttp import web
import sys,os
import aiohttp_cors

HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

latest_heart_rate = None


def heart_rate_data_handler(sensor,data):
    global latest_heart_rate
    if len(data) >= 2:
        heart_rate = data[1]
        latest_heart_rate = heart_rate
        print(f"Heart Rate: {heart_rate} bpm")
    else:
        print("Received incomplete heart rate data.")

async def start_http_server(port:int):
    async def handle_get(request):
        if latest_heart_rate is not None:
            return web.json_response({"bpm": latest_heart_rate})
        else:
            return web.json_response({"bpm": -1})
    async def handle_index(request):
        # 设置文件路径
        index_path = os.path.join(os.path.dirname(__file__), "index.html")
        return web.FileResponse(index_path)
    app = web.Application()
    app.router.add_get("/", handle_get)
    app.router.add_get("/hr",handle_index)
    cors = aiohttp_cors.setup(app)
    for route in list(app.router.routes()):
        cors.add(route, {
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"HTTP server started at http://0.0.0.0:{port}")

async def monitor_heart_rate(target_mac_addr:str):
    while True:
        try:
            devices = await BleakScanner.discover()
            target_device = next((d for d in devices if d.address == target_mac_addr), None)

            if not target_device:
                print("Target device not found. Retrying in 5 seconds...")
                await asyncio.sleep(5)
                continue

            async with BleakClient(target_mac_addr) as client:
                services = client.services
                if HEART_RATE_SERVICE_UUID not in [service.uuid for service in services]:
                    print("Device does not support heart rate service.")
                    return

                await client.start_notify(HEART_RATE_MEASUREMENT_CHAR_UUID, heart_rate_data_handler)
                print("Subscribed to heart rate data notifications.")

                while client.is_connected:
                    await asyncio.sleep(1)

        except Exception as e:
            print(f"An error occurred: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def main(target_mac_addr : str,port : int):
    await asyncio.gather(
        start_http_server(port),
        monitor_heart_rate(target_mac_addr)
    )

async def scan_ble_devices():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    if not devices:
        print("No devices found.")
    else:
        print("Found devices:")
        for device in devices:
            print(f"Name: {device.name}, Address: {device.address}")

if __name__ == "__main__":
    try:
        with open("config.yaml",'r',encoding="utf-8") as f:
            result=yaml.load(f.read(),Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("config.yaml not found!")
    bleaddr = result['bleAddr']
    port = result['ServerPort']
    scan_mode = result['ScanMode']
    if isinstance(scan_mode,bool) and scan_mode:
        try:
            asyncio.run(scan_ble_devices())
        except:
            sys.exit(0)
        sys.exit(0)

    if bleaddr == None:
        print("config.yaml parse bleaddr error! please check config.")
        sys.exit(0)
    print(f"HeartListener will start listen BLE Device: {bleaddr}")
    if isinstance(port,int):
        print(f"HeartServer will listen on port: {port}")
        print(f"HeartRateOverlay available on http://127.0.0.1:{port}/hr")
    else :
        port = 5652
        print(f"HeartServer will listen on default port: {port}")
    
    try:
        asyncio.run(main(bleaddr,port))
    except KeyboardInterrupt:
        print("Program stopped by user.")
