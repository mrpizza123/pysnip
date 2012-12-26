#       These commands are standard pyspades commands optimized for BUILD servers.
#       gt is goto that drops you from the top of build area. Must have no fall damage.
#       gts is a silent goto command.  Remove "@admin" to make public.
#       letsfly is a public fly command that only works for the person using it.
#        - Prevents annoying use of fly command on other players.

#       Customizations developed on SuperCool Build plus Platforms by JohnRambozo.
#       Stop by anytime or email johnrambozosc@gmail.com with questions or comments.

from pyspades.common import coordinates, to_coordinates
from pyspades.server import orientation_data
from commands import add, admin, get_player
from map import Map
from pyspades.constants import *
import commands
from twisted.internet import reactor

def gt(connection, value):
    if connection not in connection.protocol.players:
        raise KeyError()
    move_helper(connection, connection.name, value, silent = connection.invisible)
add(gt)
        
@admin
def gts(connection, value):
    if connection not in connection.protocol.players:
        raise KeyError()
    move_helper(connection, connection.name, value, silent = True)
add(gts)
        
def move_helper(connection, player, value, silent = False):
    player = get_player(connection.protocol, player)
    x, y = coordinates(value)
    x += 32
    y += 32
    player.set_location((x, y, - 2))
    if connection is player:
        message = ('%s ' + ('silently ' if silent else '') + 'teleported to '
            'location %s')
        message = message % (player.name, value.upper())
    else:
        message = ('%s ' + ('silently ' if silent else '') + 'teleported %s '
            'to location %s')
        message = message % (connection.name, player.name, value.upper())
    if silent:
        connection.protocol.irc_say('* ' + message)
    else:
        connection.protocol.send_chat(message, irc = True)    

def fly(connection):
    if connection not in connection.protocol.players:
        raise ValueError()
    player = connection
    player.fly = not player.fly
    message = 'now flying' if player.fly else 'no longer flying'
    connection.protocol.irc_say('* %s is %s' % (player.name, message))
    if connection is player:
        return "You're %s." % message
    else:
        player.send_chat("You're %s." % message)
        if connection in connection.protocol.players:
            return '%s is %s.' % (player.name, message)
add(fly)

@admin
def godme(connection):
    if connection not in connection.protocol.players:
        raise ValueError()
    connection.god = not connection.god
    if connection.protocol.set_god_build:
        connection.god_build = connection.god
    else:
        connection.god_build = False
    if connection.god:
        message = '%s entered BUILD MODE!' % connection.name
    else:
        message = '%s has become a mere tourist.' % connection.name
    connection.protocol.send_chat(message, irc = True)  
add(godme)



def apply_script(protocol, connection, config):
        return protocol, connection
