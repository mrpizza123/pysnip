import json
from commands import *
import re

deuce_test_name_pattern = re.compile("deuce([0-9]$|[1-2][0-9]|3[0-1])$")
duplicate_test_name_pattern = re.compile(".*(\d)$")

@alias('namealias')
@admin
def namealias(connection, value):
	try:
            	aliases = json.load(open('aliases.txt', 'rb'))
        except IOError:
            	aliases = []
	player = get_player(connection.protocol, value)
	player_name = player.name.lower()
	for ip in aliases:
		if player.address[0] == ip[0]:
			del ip[0]
			aliaslist = filter( lambda a: a.lower() != player_name and (duplicate_test_name_pattern.match(a) is not None or a != player_name[:-1]), ip)
			if len(aliaslist) == 0:
				return 'No know aliases of %s' % player.name
			return 'Known aliases of %s: %s' % (player.name,', '.join(map(str,aliaslist)))
add(namealias)

@alias('ipalias')
def alias(connection, value):
	try:
            	aliases = json.load(open('aliases.txt', 'rb'))
        except IOError:
            	aliases = []
	ip = value
	for ip in aliases:
		if player.address[0] == ip[0]:
			del ip[0]
	        aliaslist = filter( lambda a: a.lower() != player_name and (duplicate_test_name_pattern.match(a) is not None or a != player_name[:-1]), ip)
			if len(aliaslist) == 0:
				return 'No know aliases of %s' % ip
	        return 'Known aliases of %s: %s' % (ip,', '.join(map(str,aliaslist)))
add(ipalias)


def apply_script(protocol, connection, config):
    class Alias(connection):
        def on_login(self, name):
		test_name = name.lower()
		if duplicate_test_name_pattern.match(test_name) is not None and test_name[:-1] in [p.name.lower() for p in self.protocol.players.values()]:
			test_name = test_name[:-1]
		if deuce_test_name_pattern.match(test_name) is None:
        		try:
            			self.protocol.aliases = json.load(open('aliases.txt', 'rb'))
        		except IOError:
            			self.protocol.aliases = []
			if len(self.protocol.aliases) == 0:
				self.protocol.aliases.append((self.address[0], self.name[:len(test_name)]))
			else:
				for ip in self.protocol.aliases:
					if ip[0] == self.address[0]:
						for alias in ip:
							if alias.lower() == test_name:
								connection.on_login(self, name)
								return
						ip.append(self.name[:len(test_name)])
						json.dump(self.protocol.aliases, open('aliases.txt', 'wb'))
						connection.on_login(self, name)
						return
				self.protocol.aliases.append((self.address[0], self.name[:len(test_name)]))
			json.dump(self.protocol.aliases, open('aliases.txt', 'wb'))
		connection.on_login(self, name)
    return protocol, Alias