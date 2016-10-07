#!/usr/bin/env python
"""
    Python client

    Support command-line argument:
    -h [host name]
    -p [port number]

    If no command-line argument is provided the program will use the default values
    [host name] = 'localhost'
    [port number] = '4213'
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
        self.port = inputPort

        #If there is an inline-command the first argument is the port
        self.cmdln = sys.argv
        if 1<len(self.cmdln)<6:
            hFlag = True
            pFlag = True

            for i in range(len(self.cmdln)):
                #find the host flag
                if self.cmdln[i] == '-h' and hFlag:
                    try:
                        self.host = self.cmdln[i+1]
                        hFlag = False
                    #exception to catch the case when user does not input anything after flag
                    except IndexError:
                        print '\033[91mInvalid host name\033[0m'
                        sys.exit(0)
                #find the port flag
                if self.cmdln[i] == '-p' and pFlag:
                    try:
                        print 'hi'
                        self.port = int(self.cmdln[i+1])
                        pFlag = False
                    #exception to catch the case when user does not input anything after flag and input a non number as port
                    except (IndexError, ValueError):
                        print '\033[91mInvalid port number\033[0m'
                        sys.exit(0)
                    break
        print 'Server address: ', self.host, ':', self.port

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
                print 'Please press ENTER to close sending thread'
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

        #testing connection
        self.client.send('SERVER')
        data = self.client.recv(self.size)

        #Sending username to server
        #checking if username is valid
        while data!='!#@useraccepted**':
            usr = raw_input("Username: ")
            while len(usr) < 1:
                print 'Invalid username.'
                usr = raw_input("Username: ")
            self.client.send(usr)
            data = self.client.recv(self.size)
            print data

        #Starting thread for sending and recieving
        thRcv = Thread(target = self.client_recieve)
        thSnd = Thread(target = self.client_send)
        thSnd.start()
        thRcv.start()

        #waiting for the sending and recieving thread to reach terminal condition
        thSnd.join()
        thRcv.join()

        #close socket
        self.client.close()
        print 'Socket killed. Disconnected from server'

#Main method
def main():
    student = Client()
    if student.connect():
        student.start()

#Only run the method within its own module
if __name__ == '__main__':
    main()
