from tvhm import tvhapi
from tvhm.htspapi.tvh import htsmsg
htsp = tvhapi.asyncMetadata(None)
htsp.authenticate('public', 'public')
uuid='db7bfd686222d8f7339306e725f3c89f'
htsp.send('api', {'path': 'idnode/load', 'args': {'uuid': uuid}})
htsp.recv()


htsp.send('getChannel', {'channelId': 1827825508})
htsp.recv()


# ARD Olympia 4:
# uuid=db7bfd686222d8f7339306e725f3c89f
# channelId=1761442779

# diff with bin2int: 77284473

# 3:  channelId=1420430278, uuid=c60baad4e43a106852776ce220cf9b11

print "should be: 1761442779"
htsmsg.uuid2int("db7bfd686222d8f7339306e725f3c89f")
