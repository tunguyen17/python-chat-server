#!/usr/bin/env python
"""
    Python client
"""

#import socket for creating point of connection
import socket
#import thread
from threading import Thread
#import sys for standard inputs
import sys

class Client(object):
    def __init__(self, inputPort = 4213):
        'A client class that can communicate with a server'
        #host name of server
        self.host = 'localhost'
        #server port
        #If there is an inline-command the first argument is the port
        try:
            self.port = inputPort if len(sys.argv)<2 else int(sys.argv[1])
        except ValueError:
            print '\033[91mInvalid input for port number.\033[0m'
            sys.exit(0) #quit the program immediately

        #maximum size of data sent
        self.size = 1024
        #key from server for verification
        self.key = '123234123'
        #creating a socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Status of client
        self.run = True


    def client_send(self):
        'Method to send data. We run this as a thread.'
        print 'Sending thread started'
        #sending loop
        while self.run:
            #input message from raw_input
            message = raw_input()

            #checking terminaltion condition
            if message == 'quit()':
                #Tell the server that client is quiting
                self.client.send(message)
                #Close connection, kill the socket
                print 'Socket killed. Disconnected from server'
                self.client.close()
                #terminate the sending loop
                self.run = False
            #sending message
            else:
                #handeling socket.Error exception
                try:
                    #send message
                    self.client.send(message)
                except socket.error:
                    print '\033[91m' + 'Unable to send message to server.' + '\033[0m'
                    #terminate the sending loop
                    self.run = False
        print 'Sending thread ended'

    def client_recieve(self):
        print 'Recieving socket started'
        #recieving loop
        while self.run:
            #catching exception when recieving data
            try:
                data = self.client.recv(self.size)
            except:
                print('\033[91m' + 'Server not responding!' + '\033[0m')
                #terminate the sending + recieving thread
                self.run = False
            #server response the quiting message from user
            if data == '!#@quit**':
                #terminate the sending + recieving thread
                self.run = False
            #server closing flag
            elif data == '!#@Server**quit*##':
                print '\033[91m' + 'Server closed!' + '\033[0m'
                print 'Socket killed.'
                print 'Please press ENTER to close sending thread'
                self.client.close()
                #terminate the sending + recieving thread
                self.run = False
            elif data:
                print '\033[1;32m' , '      ', data, '\033[1;m'
        print 'Recieving thread stopped'

#################################################

    def connect(self):
        'Method to connect to server. Return True if connection established'

        print('\033[94m' + 'Connecting to server at ' + str(self.host) + ':' + str(self.port) + '\033[0m')
        try:
            #attempting to connect to server
            self.client.connect((self.host,self.port))

            #testing server connection
            self.client.send('ping')
            #server response to test
            data = self.client.recv(self.size)

            #Checking if server is requesting key
            if data == '!#@KeyRequest1213**':
                self.client.send(self.key)

            #Response from server
            data = self.client.recv(self.size)

            #Checking server response
            if data == 'Client validated!':
                #printing server response
                print data
                print('\33[94m ' + 'Connected to chat server. ') + '\33[0m'
                return True
            else:
                self.client.close()
                print 'ERROR:' , data
                return False
        except socket.error:
            print('\33[91m ' + 'Unable to connect to server' + '\33[0m')

    def start(self):
        #Sending username to server
        usr = raw_input("Username: ")
        self.client.send(usr)
        data = self.client.recv(self.size)

        #checking if username is valid
        while data!='!#@useraccepted**':
            print data
            usr = raw_input("Username: ")
            self.client.send(usr)
            data = self.client.recv(self.size)

        #Starting thread for sending and recieving
        thRcv = Thread(target = self.client_recieve)
        thSnd = Thread(target = self.client_send)
        thSnd.start()
        thRcv.start()

#Main method
def main():
    student = Client()
    if student.connect():
        student.start()

#Only run the method within its own module
if __name__ == '__main__':
    main()
