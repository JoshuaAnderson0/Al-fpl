import asyncio
import aiohttp

from typing import Dict

from player import Player


async def validate_get_request_async(
    response: aiohttp.ClientResponse,
    on_fail_func,
    *args,
    **kwargs
) -> any:
    if response.status == 429:
        await asyncio.sleep(0.01)
        return await on_fail_func(*args, **kwargs)
    elif response.status != 200:
        return {}
    return await response.json()


class API:
    ROOT_URI      = 'https://fantasy.premierleague.com/api/'
    BOOTSTRAP_URI = ROOT_URI + 'bootstrap-static/'
    FIXTURE_URI   = ROOT_URI + 'fixtures/'
    PLAYER_URI    = ROOT_URI + 'element-summary/'
    LIMIT         = asyncio.Semaphore(50)

    @staticmethod
    async def login_async(session: aiohttp.ClientSession, password: str, email: str):
        url = API.ROOT_URI + 'login'
        payload = {
            'password': password,
            'login': email,
            'redirect_uri': API.ROOT_URI + 'a/login',
            'app': 'plfpl-web'
        }

        async with API.LIMIT:
            async with session.post(url, data=payload) as response:
                print(response.status)
                if response.status == 200:
                    return response.json()
                return None

    @staticmethod
    async def get_bootstrap_data_async(session: aiohttp.ClientSession) -> Dict[str, object]:
        async with API.LIMIT:
            async with session.get(API.BOOTSTRAP_URI) as response: 
                return await validate_get_request_async(response, API.get_bootstrap_data_async, session)

    @staticmethod
    async def get_player_data_async(
        session: aiohttp.ClientSession,
        player_id: int,
        bootstrap: Dict[str, object]
    ) -> Player:
        async with API.LIMIT:
            async with session.get(API.PLAYER_URI + str(player_id)) as response:
                data = await validate_get_request_async(
                    response,
                    API.get_player_data_async,
                    session,
                    player_id,
                    bootstrap
                )
                if type(data) == Player:
                    return data
                return Player.from_json(player_id - 1, data, bootstrap)
