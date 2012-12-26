from pyspades.server import block_action
from pyspades.collision import distance_3d_vector
from commands import add, admin
from map import Map
from pyspades.constants import *
import commands

@admin
def offset(connection, value = None):
        connection.offseting = value
        return 'placing offset blocks %s higher' % connection.offseting
add(offset)

def apply_script(protocol, connection, config):
    class offsetMakerConnection(connection):
        offseting = None
        def on_block_build(self, x, y, z):
            if self.offseting is not None:
                offset_z = z - int(self.offseting) + 1
                if x > 0 and x < 512 and y > 0 and y < 512 and offset_z > 0 and offset_z < 63:
                    block_action.x = x
                    block_action.y = y
                    block_action.z = offset_z
                    block_action.player_id = self.player_id
                    block_action.value = BUILD_BLOCK
                    self.protocol.send_contained(block_action, save = True)
                    self.protocol.map.set_point(x, y, offset_z, self.color+(255,), user = False)
            return connection.on_block_build(self, x, y, z)
    return protocol, offsetMakerConnection
