import json
import asyncio

import aiomysql

with open("config.json") as json_file:
    data = json.load(json_file)
    db_name = data["db_name"]
    db_user = data["db_user"]
    db_password = data["db_password"]
    db_host = data["db_host"]
    db_port = data["db_port"]


async def guild_exists(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(
                f"select GUILD_ID from guilds where GUILD_ID = {guild_id};"
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    if not res:
        return False

    return True


async def add_guild(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(f"insert into guilds values ({guild_id});")

    pool.close()
    await pool.wait_closed()


async def is_premium_user(user_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(f"select PREMIUM from users where USER_ID = {user_id};")

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    if not res or not res[0]:
        return False

    return True


async def is_premium_guild(user_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(f"select PREMIUM from guilds where GUILD_ID = {user_id};")

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    if not res or not res[0]:
        return False

    return True


async def get_mod_log_channel(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(
                f"select MOD_LOG_CHANNEL from guilds where GUILD_ID={guild_id};"
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return None if not res else res[0]


async def update_mod_log_channel(guild_id: int, channel_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(
                f"update guilds set MOD_LOG_CHANNEL = {channel_id} where GUILD_ID={guild_id};"
            )

    pool.close()
    await pool.wait_closed()


async def get_member_log_channel(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(
                f"select MEMBER_LOG_CHANNEL from guilds where GUILD_ID={guild_id};"
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return None if not res else res[0]


async def update_member_log_channel(guild_id: int, channel_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(
                f"update guilds set MEMBER_LOG_CHANNEL = {channel_id} where GUILD_ID={guild_id};"
            )

    pool.close()
    await pool.wait_closed()


async def get_case_id(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(f"select CASE_ID from guilds where GUILD_ID={guild_id};")

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return 1 if not res[0] else res[0]


async def update_case_id(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(
                f"update guilds set CASE_ID = CASE_ID + 1 where GUILD_ID={guild_id};"
            )

    pool.close()
    await pool.wait_closed()


async def get_welcome_message(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(
                f"select WELCOME_MSG from guilds where GUILD_ID={guild_id};"
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return None if not res else res[0]


async def update_welcome_message(guild_id: int, welcome_msg: str):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # noinspection SqlNoDataSourceInspection
            await cur.execute(
                f"update guilds set WELCOME_MSG = {welcome_msg} where GUILD_ID={guild_id};"
            )

    pool.close()
    await pool.wait_closed()
