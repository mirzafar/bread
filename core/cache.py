import functools
from typing import Optional, Union

import aioredis
from aioredis import Redis

from settings import settings


class Cache:

    def __init__(self):
        self.pool: Optional[Redis] = None
        self.connection = None

    async def initialize(self, loop):
        self.pool = await aioredis.from_url(
            settings['redis'],
            db=1
        )

    def __getattr__(self, attr):
        return functools.partial(getattr(self.pool, attr))


cache: Union[aioredis.Redis, Cache] = Cache()
