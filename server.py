#!/usr/bin/env python
"""
    Python server
"""
#import soket to use as point of connection
import socket
#import select to deal with multiple client(socket connection)
import select
#import sys to enable access to standard input
import sys
#import time
import time

class Server(object):
    'A server class that allow user to connect to'
    def __init__(self, portInput = 4213):
        'Create a server object. Default port 4213'
        #class atribute
        #The bind method will fill the in the address of the current machine
        self.host = ''
        #Unique port number for connection
        try:
            self.port = int(sys.argv[1]) if len(sys.argv) > 1 else portInput
        except ValueError:
            print 'Invalid command-line argument'
        #max number of client waiting to be processed
        self.backlog = 1
        #maximum size of the data recieved from client
        self.size = 1024
        #Status of the server
        self.run = True
        #keys for identification
        self.key = '123234123'
        #trusted socket clients
        self.trust = []
        #name of trusted socket
        self.users = {}
        #file for recording the message
        self.data = open('data.txt','w')

        ########Creating The Server Socket########
        try:
            #Create a new socket that use TCP and TPv4
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #protect the SERVER username
            self.users.update({self.server: 'SERVER'})
            #bind the socket to the host
            while 1:
                try:
                    self.server.bind((self.host, self.port))
                    break
                except socket.error, (e, mess):
                    print(mess)
                    while 1:
                        try:
                            self.port = int(raw_input('Enter a different port: '))
                            break
                        except ValueError:
                            print 'Please enter an int'
            self.record(self.server, 'Server created')
            print 'Server created:'
            print self.host, ':', self.port
            #setting the number of listener
            self.server.listen(self.backlog)
            #input for select and input from keyboard
            self.input = [self.server, sys.stdin]
        except socket.error, (value, message):
            #Safely close the socket if there is an error during the previous process
            if self.server:
                #close socket
                self.server.close()
                #exit the program because of an error
                sys.exit(1)
            print "ERROR! Unable to open socket: ", message

        #end of the __init__ method

    def accept(self):
        'Return a list of socket requesting to connect to the server'
        #accept return a tuple (client, address)
            #client is a socket object to connect with the client
            #address is is the address of the client
        return self.server.accept()

    def boardcast(self, client, message, flag = True):
        'boardcast message to all the other clients'
        #flag is true when the message comes from user
        #flag is false when the message comes form the system
        self.record(client, message)
        #iterate throught the sockets in the trusted socket clients
        for s in self.trust:
            #Sending message to other clients in the server
            if s!=client:
                #broadcasting user message
                if flag:
                    s.send(self.users[client] + ': ' +message)
                #broadcasting system message
                else:
                    s.send(message)

    #Method overriding
    def boardcastServer(self, message):
        'broadcast message from sever'
        #record the message to data
        self.record(self.server, message)
        for s in self.trust:
            try:
                serMess = '\033[90m' + 'SERVER: ' + message + '\033[0m'
                s.send(serMess)
            except socket.error:
                pass

    def uClose(self, sock):
        'closing connection to specific client'
        try:
            sock.send('!#@quit**')
        except socket.error:
            #socket does not exist, just pass
            pass
        #print message to server terminal
        print self.users[sock], ' disconnected!'

        #delete socket from the list of user
        del self.users[sock]
        #print the new list of user
        print self.users

        #remove user from trusted sockets
        self.trust.remove(sock)
        #remove client from trusted
        self.input.remove(sock)

        #closing connection
        sock.close()

    def close(self):
        'closing connections to all clients'
        #broadcasting closing message + closing connection
        cMessage = '!#@Server**quit*##'
        self.record(self.server, 'Server closed')
        for s in self.trust:
            s.send(cMessage)
            s.close()
        #Closing server connection
        self.server.close()
        #Closing record file
        self.data.close()
        cMessage = '\033[91m' + 'Server closed!' + '\033[0m'
    #end of class

    def record(self, socket, message):
        'Record the message'
        t = time.asctime( time.localtime(time.time()) )
        special = ' *--* ' if socket == self.server else ''
        line = special + t + ' | ' + self.users[socket] + ' : ' + message + '\n'
        self.data.write(line)
        self.data.flush()

def main():
    'Main method of the server class'
    #initialize server
    wally = Server()
    #starting to accept incoming connection
    print('\033[94m' + 'Server initialized.' + '\033[0m')
    while wally.run:
        #select is used for handeling multiple clients that bind to the server
        #select syntax:
            #select.select(<input>, <output>, <exception>) -> return a subset of the inputs that contains the object that is ready to go with
        inputReady, outputReady, exceptReady = select.select(wally.input, [], [])

        #iterate throught the available sockets
        for s in inputReady:
            #handle server
                #see if there is any client socket requesting connection
            if s == wally.server:
                client, address = wally.accept()
                #append client to list of inputs
                wally.input.append(client)

            #handling input from keyboard
            elif s == sys.stdin:
                kb = sys.stdin.readline()
                if kb[:6] == 'quit()':
                    #Keyboard input will exit the while loop
                    wally.run = False
                else:
                    wally.boardcastServer(kb)
            #handle input from client socket
            else:
                #handeling trusted sockets
                if s in wally.trust:
                    try:
                        #recv, intake data with maximun size as size
                        data = s.recv(wally.size)
                    except socket.error, (e, message):
                        #handeling users who quit unexpectedly
                        print 'Unable to recieve message from', wally.users[s]
                        wally.uClose(s)
                    #if ther is data, procede to process the information
                    if data:
                        #client requesting quitting the server
                        if data == 'quit()':
                            #notify other users
                            qMes = '\033[91m ' + wally.users[s] + ' disconnected' + '\033[0m'
                            wally.boardcast(s, qMes, False)
                            #closing connection to that user
                            wally.uClose(s)
                        #broadcasting message from user
                        else:
                            wally.boardcast(s, data)
                    #there is no data, close the connection and remove the socket from the input
                    else:
                        pass
                #input not from trusted list
                else:
                    #Recieving the unauthorize data.
                        #Discard right away
                    print s, 'is requesting connection to server'
                    s.recv(wally.size)
                    print 'Requesting key for validation'
                    s.send('!#@KeyRequest1213**')
                    #Recieving key
                    socketKey = s.recv(wally.size)
                    #key from client match
                    if socketKey == wally.key:
                        print 'trusted', s
                        wally.trust.append(s)
                        s.send('Client validated!')
                        usr = s.recv(wally.size)
                        while usr in wally.users.values():
                            s.send("Username exist. Please pick another one.")
                            usr = s.recv(wally.size)
                        wally.users.update({s: usr})
                        s.send('!#@useraccepted**')
                        qMes = '\033[92m ' + wally.users[s] + ' Connected to the server' + '\033[0m'
                        wally.boardcast(s, qMes, False)
                        print wally.users
                    #recieve an invalid key. Closing connection.
                    else:
                        s.send('Invalid Key')
                        s.close()
                        wally.input.remove(s)

    #Loop stoped.
    #closing connections to clients
    wally.close()

#only run if the code is execute on the current module
if __name__ == "__main__":
    main()
