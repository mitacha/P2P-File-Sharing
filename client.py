import socket
#from thread import *
import sys
import threading
from threading import Thread
import pickle

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
	print 'Failed to create socket. Error code: ' + str(msg[0]) + ' ,Error message: '+ msg[1]
	sys.exit()

sListen=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

portL = pickle.load(open("port","rb"))
pickle.dump(portL+1,open("port","wb"))

try:
	sListen.bind(('',portL))
except socket.error, msg:
	print 'Bind failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]
	sys.exit()
sListen.listen(10)
print "Socket now listening"




def client(host, port, s, portL):
	try:
		remote_ip = socket.gethostbyname(host)
	except socket.gaierror:
		print 'Hostname couldn\'t be resolved. Exiting'
		sys.exit()
	
	
	
	
	s.connect((remote_ip, port))
	
	
	print 'Socket connected to ' + host + ' on ip ' + remote_ip
	
	
	reply = s.recv(4096)
	
	print reply
	
	while 1:
		input = raw_input(">> ")
		#input = input.lstrip()
		#input = input.rstrip()
		if not input:
			continue
		elif input[0] is 'U':
			fileName = raw_input('Enter file name: ')
			filePath = raw_input('Enter path: ')
			message = 'SHARE_FILES\n'+fileName+' '+filePath
	
		elif input[0] is 'R':
			nickname = raw_input('Enter a nickname: ')
			message = 'REGISTER\n'+nickname
		
		elif input[0] is 'S':
			fileName = raw_input('Enter file name to be searched: ')
			message = 'SEARCH\n'+fileName
			try:
				s.sendall(message)
			except socket.error:
				print 'Send failed'
				sys.exit()
			reply = s.recv(4096)
			if reply.split('\n')[0] == 'ERROR':
				print reply.split('\n')[1]
				sys.exit()

			usersHavingFile = eval(reply)
			if not usersHavingFile:
				conn.sendall('File not found')		
				continue
			
			message = 'The following users have the file:\n'
			for user in usersHavingFile.keys():
				#print 'hi'
				message = message + usersHavingFile[user]['nick'] + ' (' + user + ') (' + usersHavingFile[user]['filePath'] + ')\n'
			print message
			response = raw_input('Write \"Q\" followed by a space followed by the client IP for downloading file from that client')
			response = response.strip()
			
			if response[0] == 'Q':
				s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				peerIP = response.split(' ')[1]
				s1.connect((peerIP, portL))
				queryMessage = 'DOWNLOAD\n' + fileName + '\n' + usersHavingFile[peerIP]['filePath']
				try:
					s1.sendall(queryMessage)
				except socket.error:
					print 'Send failed'
					sys.exit()
				fw = open(fileName+'Received','wb+')
				flag = 0
				chunk = s1.recv(100)
				while chunk != 'SHUT_WR':
					s1.send('received')
					if chunk.split('\n')[0] == 'ERROR':
						print chunk.split('\n')[0]+' '+chunk.split('\n')[1]
						flag = 1
						break
					fw.write(chunk)
					chunk = s1.recv(100)
				if flag != 1:
					#s1.send('hello')
					print "\nFile saved in the receivedFiles folder inside your current folder"
				fw.close()
				s1.close()
			
			continue
		elif input is 'T':
			message = 'TEST'
		elif input is 'E':
			break
		else:
			print 'Unknown command'
			continue
	
		try:
			s.sendall(message)
		except socket.error:
			print 'Send failed'
			sys.exit()
		
		#print 'Message sent successfully'
		
		reply = s.recv(4096)
		
		print reply
	
	s.close()


###########################################


def listenForSharing(sListen):
	
	while 1:
		conn, addr = sListen.accept()
		data = conn.recv(1024)
		#print conn, addr
		#print data
		if data.split('\n')[0]=='DOWNLOAD':
			fileName = data.split('\n')[1]
			filePath = data.split('\n')[2]
			#print fileName
			#print filePath
			print filePath+fileName
			try:
				fr = open(filePath+fileName,'rb')
			except:
				conn.sendall('ERROR\nNo such file available')
				continue
			chunk = fr.read()
			conn.send(chunk)
			ack = conn.recv(100)
			#while chunk:
			#	conn.send(chunk)
    		#	print 'chunk: \"' + chunk + '\" sent'
    		#	chunk = fr.read()
    		#	ack=conn.recv(100)
    		#	print ack
    		conn.sendall('SHUT_WR')
	sListen.close()
###########################################


try:
	host = sys.argv[1]
	port = int(sys.argv[2])
	#host = 'localhost'
	#port = 55555 
	print host
	print port
	
	
	if __name__ == '__main__':
	    Thread(target = client, args = (host,port,s,portL) ).start()
	    Thread(target = listenForSharing, args = (sListen,) ).start()
#start_new_thread(client,(host,port,s))
#start_new_thread(listenForSharing,(sListen,))
except:
	sListen.close()

