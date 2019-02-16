import requests, sys

class ClashConnectAPI:
    def __init__(self, token):
        """
        Constructor for creating a connection to coc

        Attributes:
            requests    (obj):  requests module for making get requests
            token       (str):  Token used to authenticate to CoC servers
            base_url    (str):  Base url to reach several api calls
        """
        self.requests = requests
        self.token = token
        self.base_url = "https://api.clashofclans.com/v1"

    def get_request(self, uri):
        """
        Every method calls this method to make the actual connection to CoC apis

        Parameter:
            uri:       (str):   uri formatted by the methods bellow

        Returns:
            json of the response data
        """
        headers = {
            'Accept': "application/json",
            'Authorization': "Bearer " + self.token
            }

        url = self.base_url + uri
        try:
            response = self.requests.get(url, headers=headers, timeout=30)
            return response
        except:
            e = sys.exc_info()[0]
            return "Error: {}".format(e)

    
    def get_member(self, members_tag):
        """
        Get player information not in clan api

        Parameter:
            members_tag     (str):      Clash tag of the user

        EXAMPLE:
            obj.get_member("#123LGM")
        """
        return self.get_request('/players/%23' + members_tag.lstrip("#").upper())



    def get_clan(self, clan_tag):
        """
        Returns Clan information such as War frequency, name, tag, streaks etc.

        membersList is a limited list of player information. More information such as
        achievements are provided in the get_member() call.

        Parameters:
            clan_tag       (str):       Tag of the clan
        """
        return self.get_request('/clans/%23{}'.format(clan_tag.lstrip("#").upper()))

    def get_clanMembers(self, clan_tag):
        """
        Returns the memberList portion of get_clan while ignoring the clan information

        Parameters:
            clan_tag       (str):       Tag of the clan
        """
        return self.get_request('/clans/%23{}/members'.format(clan_tag.lstrip("#").upper()))

    def get_clanWarLog(self, clan_tag):
        """
        Returns last war status. Win/Lost/Damage Percentage/stars won

        Parameters:
            clan_tag       (str):       Tag of the clan
        """
        return self.get_request('/clans/%23{}/warlog'.format(clan_tag.lstrip("#").upper()))

    def get_clanCurrentWar(self, clan_tag):
        """
        Gives you stats on the current war like who attack who and for how many stars

        Parameters:
            clan_tag       (str):       Tag of the clan
        """
        return self.get_request('/clans/%23{}/currentwar'.format(clan_tag.lstrip("#").upper()))

    def get_clanLeagueGroup(self, clan_tag):
        """
        Returns 2 import things. 1 all the clans invovled in the clan wars and 2 the wartag.
        The issue is that you can't tell what the wartag represents, so you have to query
        each one to see what clans are invovled. 

        res.json()['rounds']
        
        Parameters:
            clan_tag       (str):       Tag of the clan
        """
        return self.get_request('/clans/%23{}/currentwar/leaguegroup'.format(clan_tag.lstrip("#").upper()))

    def get_clanLeagueWars(self, war_tag):
        """
        This one requires the clan_war tag that you get from get_clanLeagueGroup
        It's currently not working. Doesn't return roster numbers or peoples accurate position

        ARGS:
            war_tag       (str):       Unique tag of the war
        """
        return self.get_request('/clanwarleagues/wars/%23{}'.format(war_tag.lstrip("#").upper()))
      