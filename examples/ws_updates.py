import asyncio
import ewelink
from dotenv import load_dotenv
import os


async def cb_ws_updates(message):
    await asyncio.sleep(0.01)
    print(f"async call: {message}")


async def main():
    load_dotenv(".env")
    client: ewelink.Client = ewelink.Client(os.getenv("EWELINK_PASSWORD"), os.getenv("EWELINK_USERNAME"), region="eu")
    await client.login()
    device = client.get_device("1000ce120a")
    params: dict = device.raw_data["params"]
    switch = params["switch"]
    main_switch = params["mainSwitch"]
    device_type = params["deviceType"]
    current_temperature = params["currentTemperature"]
    targets = params["targets"]

    print(f"Current temperature: {current_temperature}")
    print(f"switch: {switch}")
    print(f"main_switch: {main_switch}")
    print(f"device_type: {device_type}")
    print(f"targets: {targets}")

    # try:
    #     await device.on()
    # except Exception as e:
    #     print("Device is offline!")

    # params = {
        # "mainSwitch": "off",
        # "deviceType": "normal",
        # "controlType":9
        # "switch": "on",
        # "mainSwitch": "on",
        # "deviceType": "temperature",
        # "targets": [
        #     {"targetHigh": 30, "reaction": {"switch": "off"}},
        #     {"targetLow": 20, "reaction": {"switch": "on"}}
        # ],
        # "params": ""
    # }
    params_on = {
        "deviceType": "temperature",
        "mainSwitch": "on",
        "controlType": 9,
        "targets": [
            {"targetHigh": "63", "reaction": {"switch": "off"}},
            {"targetLow": "53", "reaction": {"switch": "on"}}
        ]
    }
    params = params_on
    client.ws.listeners.append(cb_ws_updates)

    # resp = await client.ws.update_device_status("1000ce120a", **params)
    # print(f"update targets resp {resp}")
    await asyncio.sleep(120000)
    await client.http.session.close()

if __name__ == '__main__':
    asyncio.run(main())
