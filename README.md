Panther Lily is a Dockerized bot used to manage [Clash of Clans](https://supercell.com/en/games/clashofclans/)
players in a clan. It is capable of tracking their activity by monitoring
how many donations a user makes in a week. It can also show trophy and
donation gain leaderboards. 

The bot maintains a Postgres database with the most up to date information
using the [coc.py](https://cocpy.readthedocs.io/en/latest/) library. This
allows for instant response to users by avoiding direct endpoint 
connections. 

What do you get?
```angular2html
- Track user donations
- Show in clan leader boards
- Track user clan locations
- Keep notes on users who you have removed for future addition decisions
- Assign discord bots and rename users based on their CoC accounts
- Create war donation assignment boards
```