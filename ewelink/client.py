import asyncio
from dataclasses import dataclass
from typing import TypeVar, Type, Callable, Coroutine, Any

from .http import HttpClient
from .models import ClientUser, Device, Devices, Region
from .state import Connection
from .ws import WebSocketClient

T = TypeVar("T")
V = TypeVar("V")
ClientT = TypeVar("ClientT", bound="Client")
GatewayT = TypeVar("GatewayT", bound="Gateway")


@dataclass
class Gateway:
    domain: str
    port: int | str

    @classmethod
    def from_dict(cls: Type[GatewayT], data: dict[str, str | int]) -> GatewayT:
        return cls(domain=data.get("domain"), port=data.get("port"))


class Client:
    http: HttpClient
    gateway: Gateway | None = None
    ws: WebSocketClient | None
    _devices: dict[str, Device] = {}
    user: ClientUser | None
    loop: asyncio.AbstractEventLoop

    def __init__(self, password: str, email: str | None = None, phone: str | int | None = None, *, region: str = 'eu'):
        super().__init__()
        self.http = HttpClient(password=password, email=email, phone=phone, region=region)
        self.ws = None
        self.user = None

    async def login(self):
        self.loop = asyncio.get_event_loop()
        await self.http.create_session(loop=self.loop)
        self.user = ClientUser(data=await self.http.login(), http=self.http)
        self.ws = WebSocketClient(http=self.http, user = self.user)
        self.gateway = Gateway.from_dict(await self.http.get_gateway())
        await self.ws.create_websocket(self.gateway.domain, self.gateway.port)
        self._devices = {
            device['deviceid']: Device(data=device, state=self._get_state())
            for device in (await self.http.get_devices()).get('devicelist', [])
        }
        self.ws.set_devices(self._devices)

    def _get_state(self) -> Connection:
        return Connection(ws=self.ws, http=self.http)

    def get_device(self, device_id: str) -> Device | None:
        return self.devices.get(device_id)

    @property
    def devices(self):
        return Devices(self._devices.values())

    @property
    def region(self):
        return Region[self.http.region.upper()]

    async def dispose(self):
        await self.ws.close()
        await self.http.session.close()
