import socket
import sys
from thread import *
import functions


host = ''
port = 55555

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Socket created'
try:
	s.bind((host,port))
except socket.error, msg:
	print 'Bind failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]
	sys.exit()

print 'Socket bind complete'


s.listen(10)
print 'Socket now listening'
activePeers = []
users = {}
def clientthread(conn,addr):
	conn.send('Welcome to the server. Select an option\n 1. (R)egister\n 2. (U)pload files\n 3. (S)earch for a file\n 4. (E)xit')
	activePeers.append(addr[0])
	#print activePeers
	while 1: 
	    data = conn.recv(1024)
	    #reply = 'OK...' + data
	    if not data:
	    	break

	    if data.split('\n')[0] == 'REGISTER':
	    	functions.register(conn, addr, data.split('\n')[1])
	    elif data.split('\n')[0] == 'SHARE_FILES':
	    	functions.share(conn,addr,data.split('\n')[1])
	    elif data.split('\n')[0] == 'SEARCH':
	    	functions.search(conn,addr,data.split('\n')[1],activePeers)
	    elif data == 'TEST':
	    	functions.checkDB(conn)

	activePeers.remove(addr[0])
	conn.close()


while 1:
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])

	start_new_thread(clientthread, (conn,addr))


s.close()