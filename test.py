import asyncio
import coc


@coc.ClanEvents.member_donations()
async def member_donation(old_stats: coc.ClanMember, new_stats: coc.ClanMember) -> None:
    received = new_stats.received - old_stats.received
    donated = new_stats.donations - old_stats.donations
    print(f"{new_stats.name} donated {donated} and received {received} donations")


@coc.ClanEvents.member_join()
async def on_clan_member_join(member, clan):
    print(f"{member.name} has joined {clan.name}")


async def main(client: coc.EventsClient):
    # Create a login session
    await client.login("sgtmajorjay@gmail.com",
                       "!soXyCa3oTG_7rGGYEH9g!!F-iDwjT*2")

    clan = "#2Y28CGP8"
    client.add_clan_updates(clan)

    clan_obj = await client.get_clan(clan)
    for player in clan_obj.members:
        client.add_player_updates(player.tag)

    # Register all the call back functions
    client.add_events(member_donation, on_clan_member_join)


if __name__ == '__main__':
    client = coc.EventsClient()

    # Manually create loop object instead of asyncio.run() for Events
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(client))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass  # Ignore keyboard interrupt
    finally:
        # Loop over all tasks and cancel them properly to clean up
        loop.run_until_complete(client.close_client())
        for task in asyncio.all_tasks(loop):
            task.cancel()
        # Take the time to clean up generators
        loop.run_until_complete(loop.shutdown_asyncgens())
        # Close loop
        loop.close()