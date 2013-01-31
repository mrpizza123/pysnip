###Badmin is an bot admin.  He'll do a variety of common admin tasks so you don't have to.
###He might not always get it right, but he'll get it done, and isn't that what really matters?
###-Requirements: blockinfo.py (for grief detection), ratio.py (for k/d ratio), aimbot2.py (hit accuracy)
###-Modified by Color to take out auto-kick, aimbot detection, slur detection, auto stuff, keep warn.

from twisted.internet import reactor
from pyspades.common import prettify_timespan
from pyspades.constants import *
from pyspades.collision import distance_3d_vector
from commands import add, admin, get_player
import re
BADMIN_VERSION = 9
#Settings for auto-griefcheck
SCORE_GRIEF_ENABLED = True
#any votekicks under uncertain will be cancelled
SCORE_GRIEF_WARN = 3

grief_pattern = re.compile(".*(gr.*f.*(ing|er)|grief|destroy).*", re.IGNORECASE)

def grief_match(player, msg):
	return (not grief_pattern.match(msg) is None)

@admin
def badmin(connection, var=None):
    if var == None:
        return ("@Badmin (r%s): Grief Votekick Protection(GV) [%s]" 
		% (BADMIN_VERSION, SCORE_GRIEF_ENABLED))
add(badmin)

@admin
def investigate(connection, player):
    player = get_player(connection.protocol, player)
    score = score_grief(connection, player)
    kdr = round(player.ratio_kills/float(max(1,player.ratio_deaths)))
    percent = round(check_percent(player))
    message = "Results for %s: Grief Score - %s / KDR - %s / Hit Acc. - %s" % (player.name, score, kdr, percent)
add(investigate)

def score_grief(connection, player, time=None): #302 = blue (0), #303 = green (1)
    print "start score grief"
    color = connection not in connection.protocol.players and connection.colors
    minutes = float(time or 2)
    if minutes < 0.0:
        raise ValueError()
    time = reactor.seconds() - minutes * 60.0
    blocks_removed = player.blocks_removed or []
    blocks = [b[1] for b in blocks_removed if b[0] >= time]
    player_name = player.name
    team_id = player.team.id #0=blue, 1=green
    print "name/team set"
    gscore = 0 #griefscore
    map_blocks = 0
    team_blocks = 0
    enemy_blocks = 0
    team_harmed = 0
    enemy_harmed = 0
    print "init values set"
    if len(blocks):
        print "len blocks = true, blocks found"
        total_blocks = len(blocks)
        info = blocks
        for info in blocks:
            if info:
                name, team = info
                if name != player_name and team == team_id:
                    team_blocks+= 1
                elif team != team_id:
                    enemy_blocks+=1
            else:
                map_blocks+= 1
        print "second for done"
        infos = set(blocks)
        infos.discard(None)
        for name, team in infos:
            if name != player_name and team == team_id:
                team_harmed += 1
            elif team != team_id:
                enemy_harmed += 1
        print "third for done"
    else:
        print "len blocks = false, no blocks found"
        total_blocks = 0

    #heuristic checks start here
    #if they didn't break any blocks at all, they probably aren't griefing.
    if total_blocks == 0:
        print "no blocks, ending"
        return 0
    #checks on team blocks destroyed
    if team_blocks > 0 and team_blocks <= 5:
        gscore += 1
    elif team_blocks > 5 and team_blocks <= 10:
        gscore += 2
    elif team_blocks > 20 and team_blocks <= 100:
        gscore += 4
    elif team_blocks > 25 and team_blocks <= 100:
        gscore += 6
    elif team_blocks > 50:
        gscore += 10
    print "team blocks set"
    #team / total ratio checks
    if total_blocks != 0:
        ttr = (float(team_blocks) / float(total_blocks)) * 100
    if ttr > 5 and ttr <= 20:
        gscore += 1
    elif ttr > 20 and ttr <= 50:
        gscore += 2
    elif ttr > 35 and ttr <= 100:
        gscore += 4
    elif ttr > 80:
        gscore += 6
    print "ttr set"
    #teammates harmed check
    if team_harmed == 1:
        gscore += 1
    elif team_harmed > 2 and team_harmed <= 9:
        gscore += 4
    print "team harmed set"
    print "mb: %s, tb: %s, eb: %s, Tb: %s, th: %s, ttr: %s, eh: %s, gs: %s" % (map_blocks, team_blocks, enemy_blocks, total_blocks, team_harmed, ttr, enemy_harmed, gscore)
    return gscore

def check_percent(self):
    if self.weapon == RIFLE_WEAPON:
        if self.semi_hits == 0 or self.semi_count == 0:
            return 0;
        else:
            return (float(self.semi_hits)/float(self.semi_count)) * 100
    elif self.weapon == SMG_WEAPON:
        if self.smg_hits == 0 or self.smg_count == 0:
            return 0;
        else:
            return (float(self.smg_hits)/float(self.smg_count)) * 100
    elif self.weapon == SHOTGUN_WEAPON:
        if self.shotgun_hits == 0 or self.shotgun_count == 0:
            return 0;
        else:
            return float(self.shotgun_hits)/float(self.shotgun_count)

def apply_script(protocol, config):
    def badmin_punish(connection, punishment='warn', reason = "Being a meany face"):
        connection.protocol.irc_say("* @Badmin: %s is being punished. Type: %s (Reason: %s)" % (connection.name, punishment, reason))
        if punishment == "warn":
            connection.protocol.send_chat(" @Badmin: Hey %s, %s" % (connection.name, reason))
    
	class BadminProtocol(protocol):
        if grief_match(self, reason) and SCORE_GRIEF_ENABLED == True:
            #print "made grief check"
                score = score_grief(connection, player)
            if score >= SCORE_GRIEF_WARN:
                badmin_punish(player, "warn", "Stop Griefing! (GS: %s)" % score)
        return protocol.start_votekick(self, connection, player, reason)
    
    return BadminProtocol