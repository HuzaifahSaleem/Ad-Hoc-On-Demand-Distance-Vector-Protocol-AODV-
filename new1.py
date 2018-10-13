  
import sys
from socket import* 
from threading import* 
import time
import pickle

neighbours = dict() # a dictionary of neighbours containing name as key and a list each having cost and port number
distvect = dict() # key is the destination and value is the cost
forwarding_table = dict () # next hop to destination carrying shortest path
topology = list() # store list of all known nodes in the network
neighbour_distance_vector = dict () # a dictionary of dictionaries storing distance vectors of all neighbours of the node[
check = True 
count = 0  


IP = "127.0.0.1"


nameofnode = sys.argv[1]                      #command line arguments 'name of router (yourself)'
serverport = sys.argv[2]                      #your port where you listen
filename = sys.argv[3]                      #the config file name in .txt format 

with open(filename, 'r') as f6:               #read the file 

   # print(nameofnode, serverport)
	for line in f6:
		f = line.split()
		if len(f) != 1:                       # start parsing from second line, line by line
			Router = f[0]                     # 0'th element is name of each nieghbouring router
			Cost = f[1]                       # 1st element is the cost to your neighbour
			PortNo = f[2]                     # 2nd element is the port number that this neighbour listens at
			neighbours [f[0]] = [float(f[1]), int(f[2])]       # append data of this neighbour in your dictionary called neighbour
			#print('\n')
	f6.close()

distvect[nameofnode] = 0                     # to get to our own self the distance is zero
forwarding_table[nameofnode] = nameofnode   # we hop to ourselves to go to ourselves

# topology.append(nameofnode)                  # add yourself to the list of known nodes in the network

for n1 in neighbours:                         # for every node in your nieghbours update distance vector
	distvect[n1] = neighbours[n1][0]           # updt your own distvect to each of ur neighbrs w/ cost u get frm txt file
	forwarding_table[n1] = n1                  # update your forwarding table to your nieghbour
	topology.append(n1)                       # a list of all nodes that nameofnode knows of
	neighbour_distance_vector[n1] = dict()    # initialize every element of your dictionary of dictionaries at each key



def bellmanford():
	global check, count

	print('bellman ford enter')
        
	while 1:
		if check:
			check = False
			for t1 in topology:
				if t1 in forwarding_table:
					path = forwarding_table[t1]       # initialize string path (e.g. path is AEF)                                        
                                        
					if t1 in distvect:
						minimum = distvect[t1]
					else:
						minimum = float('infinity')                           # minimum distance to y infinite

					for NDV in neighbour_distance_vector:
						if t1 in neighbour_distance_vector[NDV]:
							if neighbour_distance_vector[NDV][t1] + neighbours[NDV][0] < minimum:
								minimum = neighbour_distance_vector[NDV][t1] + neighbours[NDV][0]
								path = NDV
					distvect[t1] = minimum
					forwarding_table[t1] = ' '
					forwarding_table[t1] = path

			#print('\n\nI am router', nameofnode)
			for x in topology:                                                                                                 # display
				if x != nameofnode:                 
					if x in forwarding_table:
                                                if forwarding_table[x] == x:
                                                        print('I am router', nameofnode, 'Least cost to router ', x, ' is', distvect[x], ' and least cost path to router', x, ':', nameofnode, forwarding_table[x])
                                                else:
                                                        print('I am router', nameofnode, 'Least cost to router ', x, ' is', distvect[x], ' and least cost path to router', x, ':', nameofnode, forwarding_table[x], x)


                        
			print('Number of times BellmanFord called:', count)
			print('\n')
			count = count + 1
			
 


def send_distvect():
	global check
	Socket = socket(AF_INET, SOCK_DGRAM)  #makes a socket to be reused each time sending

	#print('sending distvect')

	while 1:
		#print('\nSending')
		time.sleep(10.0) #send packet every 10 seconds

		mydistvect = (nameofnode, distvect)   #sends data to neighbour's neighbour_distance_vector dictionary  
		mypacket = pickle.dumps(mydistvect)

		for i in neighbours:                  #send your dictance vector to each of your neighbours
			port = int(neighbours[i][1])      #get port of neighbour to send to 
			Socket.sendto(mypacket,(IP, port))    #send packet to port and IP localhost
	Socket.close()                            #close socket 


def receive_distvect():
	global check
	Socket = socket(AF_INET, SOCK_DGRAM)  #makes a socket to be reused each time sending
	Socket.bind((IP,int(serverport)))         #this is my IP and my listening port

	#print('receive distvect')

	while 1:
		#print('\nReceiving')
		data, clientAddr = Socket.recvfrom(2048)   #max 2048 bytes of data to be rcvd and assigned to data and client addr variables
		
		pktrcvd = pickle.loads(data)                #get data from packet and store into variable 

		identity = pktrcvd[0]  #identity of node that is sending the distance vector so we can append it in our neighbour_distance_vector dictionary

		# checks if received distvect and already present distvect of this neighbour

		if identity in neighbour_distance_vector:
				neighbour_distance_vector[identity] = pktrcvd[1]  # update neighbour ka distance vector
				check = True
		else:
			neighbour_distance_vector[identity] = pktrcvd[1]
			check = False

		for x1 in pktrcvd[1]:  # now for every neighbour of the neighbour
			if x1 not in topology:  # if this node is not known to me
				topology.append(x1)  # add it in my list of known nodes of the network
				forwarding_table[x1] = ''

		time.sleep(0.1)

def main():
	
	t1 = Thread(target=send_distvect, args=list())
	t2 = Thread(target=receive_distvect, args=list())
	t3 = Thread(target=bellmanford, args=list())

	t1.start()
	t2.start()
	t3.start()

	
main() 










