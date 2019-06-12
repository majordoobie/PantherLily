import coc
import asyncio

client = coc.Client('sgtmajorjay@gmail.com', 'xUjpuw-jyrxe5-mydjum')

# zulu = 2Y28CGP8
# elephino = 8YGOCQRY
# misfits = P0Q8VRC8

async def get_some_player(tag):
    player = await client.get_player(tag)

    print(player.name)
    # alternatively,
    print(str(player))


async def main():
    clans = ["#2Y28CGP8", "#8YGOCQRY", "#P0Q8VRC8"]
    all_tags = []

    player = client.get_player("#9P9PRYQJ")
    print(player)
    async for clan in client.get_clans(clans):
        for member in clan.members:
            all_tags.append(member.tag)

    async for player in client.get_players(all_tags):
        print(player.tag)
        print(player.name)
        print(player.clan_rank)
        # print(clan.retrived)
        # print(clan.tags)
        # print(clan)
    #await get_some_player('#9P9PRYQJ')
    #await get_five_clans('name')
    await client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())