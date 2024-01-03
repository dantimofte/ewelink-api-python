import asyncio
import ewelink


async def main():
    client: ewelink.Client = ewelink.Client("", "", region="eu")
    await client.login()
    device = client.get_device('1000ce120a')

    print(f"device params {device.params}")
    # Raw device specific properties
    # can be accessed easily like: device.params.switch or device.params['startup'] (a subclass of dict)

    print(f"device state : {device.state}")
    print(f"device created_at: {device.created_at}")
    print("Brand Name: ", device.brand.name, "Logo URL: ", device.brand.logo.url)
    print("Device online? ", device.online)

    try:
        await device.on()
    except Exception as e:
        print("Device is offline!")

    params = {
        "targets": [
            {"targetHigh": 30, "reaction": {"switch": "off"}},
            {"targetHigh": 20, "reaction": {"switch": "on"}}
        ]
    }
    resp = await client.ws.update_device_status("1000ce120a", params=params)
    print(f"update targets resp {resp}")

    await client.http.session.close()

if __name__ == '__main__':
    asyncio.run(main())
