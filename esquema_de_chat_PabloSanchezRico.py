#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 09:18:15 2023

@author: Pablo Sánchez Rico
"""

from multiprocessing.connection import Listener
from multiprocessing import Process, Manager
from multiprocessing.connection import Client
import sys
from time import time, sleep
import traceback
from random import random


def send_msg_all(pid, msg, clients):
    for client, client_info in clients.items():
        print (f"sending {msg} tp {client_info}")
        with Client(address=(client_info['address'],
                             client_info['port']),
                    authkey=client_info['authkey']) as conn:
            if not client == pid:
                conn.send((pid,msg))
            else:
                conn.send(f"message {msg} processed")
                
                
def serve_client(conn, pid, clients):
    connected = True
    while connected: 
        try:
            m = conn.recv()
            print(f'received message:{m}: from {pid}')
            if m == "quit":
                connected = False
                conn.close()
            else:
                send_msg_all(pid, m, clients)
        except EOFError:
            print ('connection abruptly closed by client')
            connected = False
    del clients[pid]
    send_msg_all(pid, f"quit_client {pid}", clients)
    print (pid, 'connection closed')
    
def main(ip_address):
    with Listener(addess=(ip_address, 6000),
                  authkey=b'secret password server') as listener:
        print('listener starting')
        
        m = Manager()
        clients = m.dict()
        
        while True:
            print ('accepting conections')
            try:
                conn = listener.accept()
                print ('connection accepted from', listener.last_accepted)
                client_info = conn.recv()
                pid = listener.last_accepted()
                clients[pid] = client_info
                
                send_msg_all(pid, f"new client {pid}", clients)
                
                p = Process(target=serve_client, args=(conn,listener.last_accepted, clients))
                p.start()
            except Exception as e:
                traceback.print_exc()
                
        print ('end server')
        
if __name__ == '__main__':
    ip_address = '127.0.0.1'
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
    
def client_listener(info):
    print(f"Openning listener at {info}")
    cl = Listener(address=(info['address'], info['port']),
                  authkey=info['authkey'])
    print ('.......... client listener starting')
    print ('.......... accepting connections')
    while True:
        conn = cl.accept()
        print ('............... connection accepted from', cl.last_accepted)
        m = conn.recv()
        print ('....................... mesage received from server', m)

def main(server_address, info):
    print ('trying to connect')
    with Client(address=(server_address, 6000),
                authkey=b'secret password server') as conn:
        cl = Process(target=client_listener, args=(info,))
        cl.start()
        conn.send(info)
        connected = True
        while connected:
            value = input("Send message ('quit' quit connection)?")
            print ("connection continued...")
            conn.send(value)
            connected = value!= 'quit'
        cl.terminate()
    print ("end client")
    
if __name__ == '__main__':
    server_address = '127.0.0.1'
    client_address = '127.0.0.1'
    client_port = 6001
    
    if len(sys.argv) > 1:
        client_port =int(sys.argv[1])
    if len(sys.argv) > 2:
        client_address = sys.argv[2]
    if len(sys.argv) > 3:
        server_address = sys.argv[3]
    info = {
        'address' : client_address,
        'port' : client_port,
        'authkey': b'secret client server'
        }
    main(server_address, info)
         
             



