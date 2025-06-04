import socket
import logging

server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'your twitch username'
token = 'oauth:your token'
channel = 'channel'

sock = socket.socket()
sock.connect((server, port))

sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))

while True:
    resp = sock.recv(2048).decode('utf-8')
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler('chat.log', encoding='utf-8')])


    logging.info(resp)