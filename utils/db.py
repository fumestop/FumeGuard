from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from datetime import datetime

if TYPE_CHECKING:
    import aiomysql


async def guild_exists(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select GUILD_ID from guilds where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchone()

    if not res:
        return False

    return True


async def add_guild(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "insert into guilds (GUILD_ID) values (%s);", (guild_id,)
            )


async def is_blacklisted_user(pool: aiomysql.Pool, user_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select USER_ID from user_blacklist where USER_ID = %s;", (user_id,)
            )

            res = await cur.fetchone()

    if not res or not res[0]:
        return False

    return True


async def is_blacklisted_guild(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select GUILD_ID from guild_blacklist where GUILD_ID = %s;",
                (guild_id,),
            )

            res = await cur.fetchone()

    if not res or not res[0]:
        return False

    return True


async def is_premium_user(pool: aiomysql.Pool, user_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select PREMIUM from users where USER_ID = %s;", (user_id,)
            )

            res = await cur.fetchone()

    if not res or not res[0]:
        return False

    return True


async def is_premium_guild(pool: aiomysql.Pool, user_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select PREMIUM from guilds where GUILD_ID = %s;", (user_id,)
            )

            res = await cur.fetchone()

    if not res or not res[0]:
        return False

    return True


async def get_mod_log_channel(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select MOD_LOG_CHANNEL from guilds where GUILD_ID = %s;",
                (guild_id,),
            )

            res = await cur.fetchone()

    return None if not res else res[0]


async def update_mod_log_channel(
    pool: aiomysql.Pool, guild_id: int, channel_id: Optional[int] = None
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set MOD_LOG_CHANNEL = %s where GUILD_ID = %s;",
                (channel_id, guild_id),
            )


async def get_member_log_channel(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select MEMBER_LOG_CHANNEL from guilds where GUILD_ID = %s;",
                (guild_id,),
            )

            res = await cur.fetchone()

    return None if not res else res[0]


async def update_member_log_channel(
    pool: aiomysql.Pool, guild_id: int, channel_id: Optional[int] = None
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set MEMBER_LOG_CHANNEL = %s where GUILD_ID = %s;",
                (channel_id, guild_id),
            )


async def get_welcome_message(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select WELCOME_MESSAGE from guilds where GUILD_ID = %s;",
                (guild_id,),
            )

            res = await cur.fetchone()

    return None if not res else res[0]


async def update_welcome_message(
    pool: aiomysql.Pool, guild_id: int, message: Optional[str] = None
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set WELCOME_MESSAGE = %s where GUILD_ID = %s;",
                (message, guild_id),
            )


async def get_case_number(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select CASE_NUMBER from guilds where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchone()

    return 1 if not res[0] else res[0]


async def increment_case_number(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set CASE_NUMBER = CASE_NUMBER + 1 where GUILD_ID = %s;",
                (guild_id,),
            )


async def is_afk(pool: aiomysql.Pool, user_id: int, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select USER_ID from afk where USER_ID = %s and GUILD_ID = %s;",
                (user_id, guild_id),
            )
            res = await cur.fetchone()

    return True if res else False


async def set_afk(
    pool: aiomysql.Pool, user_id: int, guild_id: int, reason: Optional[str] = None
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "insert into afk (USER_ID, GUILD_ID, START, REASON) values (%s, %s, %s, %s);",
                (user_id, guild_id, datetime.now(), reason),
            )


async def get_afk_details(pool: aiomysql.Pool, user_id: int, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select * from afk where USER_ID = %s and GUILD_ID = %s;",
                (user_id, guild_id),
            )
            res = await cur.fetchone()

    return {"user_id": res[0], "guild_id": res[1], "start": res[2], "reason": res[3]}


async def get_afk_members(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select USER_ID from afk where GUILD_ID = %s;", (guild_id,)
            )
            res = await cur.fetchall()

    return res


async def remove_afk(pool: aiomysql.Pool, user_id: int, guild_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "delete from afk where USER_ID = %s and GUILD_ID = %s;",
                (user_id, guild_id),
            )
            res = await cur.fetchone()

    return res


async def automod_enable(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set AUTOMOD = 1 where GUILD_ID = %s;", (guild_id,)
            )


async def automod_disable(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set AUTOMOD = 0 where GUILD_ID = %s;", (guild_id,)
            )


async def automod_status(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select AUTOMOD from guilds where GUILD_ID = %s;", (guild_id,)
            )
            res = await cur.fetchone()

    return True if res[0] else False


async def automod_get_allowed_link_roles(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select AUTOMOD_LINK_SEND_ROLES from guilds where GUILD_ID = %s;",
                guild_id,
            )
            res = await cur.fetchone()

    return res[0].split("|") if res[0] else []


async def automod_update_allowed_link_roles(
    pool: aiomysql.Pool, guild_id: int, role_id: str, add: bool = True
):
    allowed_role_ids = await automod_get_allowed_link_roles(pool, guild_id)

    if add:
        allowed_role_ids.append(role_id)

    else:
        allowed_role_ids.remove(role_id)

    allowed_role_ids = "|".join(allowed_role_ids)

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set AUTOMOD_LINK_SEND_ROLES = %s where GUILD_ID = %s;",
                (allowed_role_ids, guild_id),
            )


async def automod_get_allowed_embed_roles(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select AUTOMOD_LINK_EMBED_ROLES from guilds where GUILD_ID = %s;",
                guild_id,
            )
            res = await cur.fetchone()

    return res[0].split("|") if res[0] else None


async def automod_update_allowed_embed_roles(
    pool: aiomysql.Pool, guild_id: int, role_id: str, add: bool = True
):
    allowed_role_ids = await automod_get_allowed_embed_roles(pool, guild_id)

    if add:
        allowed_role_ids.append(role_id)

    else:
        allowed_role_ids.remove(role_id)

    allowed_role_ids = "|".join(allowed_role_ids)

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set AUTOMOD_LINK_EMBED_ROLES = %s where GUILD_ID = %s;",
                (allowed_role_ids, guild_id),
            )
