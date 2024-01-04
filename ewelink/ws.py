import aiohttp, time, random, asyncio, json

from typing import AnyStr, TypedDict, List, Callable, Union, Coroutine

from .models import ClientUser
from .exceptions import DeviceOffline
from .constants import Constants
from .http import HttpClient


class DeviceInterface:
    id: str
    online: bool


Response = TypedDict(
    "Response",
    {
        'error': int,
        'deviceid': str,
        'apikey': str,
        'sequence': str | None,
        'params': dict[str, list[dict[str, AnyStr]] | AnyStr]
    }
)


class WebSocketClient:
    http: HttpClient
    heartbeat: int
    ws: aiohttp.ClientWebSocketResponse | None
    session: aiohttp.ClientSession
    user: ClientUser
    devices: dict[str, DeviceInterface]
    listeners: List[Union[Coroutine, Callable[[str], None]]] = []
    _ping_task: asyncio.Task[None] | None = None
    _poll_task: asyncio.Task[None] | None = None

    def __init__(self, http: HttpClient, user: ClientUser) -> None:
        self.http = http
        self.user = user
        self.devices = {}
        self.heartbeat = 90
        self.session = http.session
        self.ws = None

    def set_devices(self, devices: dict[str, DeviceInterface]):
        self.devices = devices

    async def create_websocket(self, domain: str, port: int | str):
        self.ws = await self.session.ws_connect(f'wss://{domain}:{port}/api/ws')
        await self.ws.send_json({
            "action": "userOnline",
            "version": 8,
            "ts": int(time.time()),
            "at": self.http.token,
            "userAgent": "app",
            "apikey": self.user.api_key,
            "appid": Constants.APP_ID,
            "nonce": "".join(random.choice("abcdefghijklmnopqrstuvwxyz1234567890") for _ in range(8)),
            "sequence": str(time.time() * 1000)
        })
        response: dict[str, str | int | dict[str, int]] = await self.ws.receive_json()
        if not response.get('error'):
            if config := response.get('config', {}):
                if isinstance(config, dict):
                    if hb_interval := response['config'].get('hbInterval', ''):
                        if isinstance(hb_interval, int): self.heartbeat = hb_interval + 7
        self._ping_task = self.http.loop.create_task(self.ping_hb())
        self._poll_task = self.http.loop.create_task(self.poll_event())

    async def update_device_status(self, deviceid: str, **kwargs: list[dict[str, AnyStr]] | AnyStr) -> None:
        await self.ws.send_json({
            "action": "update",
            "deviceid": deviceid,
            "apikey": self.user.api_key,
            "userAgent": "app",
            "sequence": str(time.time() * 1000),
            "params": kwargs
        })

    async def poll_event(self):
        while True:
            try:
                msg = await self.ws.receive_str()
            except TypeError as e:
                break
            if msg == 'pong':
                continue
            for listener in self.listeners:
                if asyncio.iscoroutinefunction(listener):
                    await listener(msg)
                else:
                    listener(msg)

    async def ping_hb(self):
        while True:
            await asyncio.sleep(self.heartbeat)
            await self.ws.send_str("ping")

    async def close(self):
        await self.ws.close()

    @property
    def closed(self) -> bool:
        return self.ws.closed
