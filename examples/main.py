import asyncio
import ewelink
from dotenv import load_dotenv
import os


async def main():
    load_dotenv(".env")
    client: ewelink.Client = ewelink.Client(os.getenv("EWELINK_PASSWORD"), os.getenv("EWELINK_USERNAME"), region="eu")
    await client.login()
    print(f"client version {client.region}")
    print(f"client user info: {client.user.info}")
    print(f"client devices {client.devices}")

    device = client.get_device('1000ce120a')

    print(f"device params {device.params}")
    # Raw device specific properties
    # can be accessed easily like: device.params.switch or device.params['startup'] (a subclass of dict)

    print(f"device state : {device.state}")
    print(f"device created_at: {device.created_at}")
    print("Brand Name: ", device.brand.name, "Logo URL: ", device.brand.logo.url)
    print("Device online? ", device.online)

    # try:
    #     await device.on()
    # except Exception as e:
    #     print("Device is offline!")
    await client.http.session.close()

if __name__ == '__main__':
    asyncio.run(main())
