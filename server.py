from socket import *
import struct
import sys
import random
import time
import string

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
#server.bind(('34.67.93.93'), serverPort)
serverSocket.bind(('localhost', serverPort))
print("""Server ready""")

def server_exit():
    serverSocket.close()
    print("------------")
    print("Closing connection and exiting the server.")
    sys.exit()

print(f"""
------------
Phase A
------------
""")
data = b"Hello World!!!"
expected_pcode = 0
expected_entity = 1
data_length = len(data)
remainder = data_length % 4
padding = (4 - remainder) % 4
expected_data = data + b'\x00' * padding
expected_data_len = len(expected_data)

check = False
packet, clientAddress = serverSocket.recvfrom(1024)
data_len, pcode, entity, data = struct.unpack(f"!IHH{len(expected_data)}s", packet)

# Check Phase A packet values.
if (data_len != expected_data_len):
    print(f"{data_len} != {expected_data_len}")
    print("Packet's entity values does not match expectation. Closing the connection.")
    server_exit()

if (pcode != expected_pcode):
    print("Packet's pcode does not match the expected value. Closing connection")
    server_exit()

if (entity != expected_entity):
    print("Packet entity does not match expected value. Closing connection.")
    server_exit()

if (len(packet) % 4 != 0):
    print("Packet size is not divisible by 4. Closing the connection.")
    server_exit()

if (data != expected_data):
    print("Data is not the expected string.")
    server_exit()
else:
    entity = 2
    check = True

while check:
    try:
        repeat = random.randint(5, 20)
        udp_port = random.randint(20000, 30000)
        length = random.randint(50, 100)
        codeA = random.randint(100, 400)
        #repeat = 5
        #udp_port = 20000
        #length = 50
        #codeA = 100

        message = struct.pack(f"!IHHIIHH", data_len, pcode, entity, repeat, udp_port, length, codeA)
        serverSocket.sendto(message, clientAddress)
        print("Message sent!")
        check = False

    except Exception as e:
        print(f"An error has occured: {str(e)}")
        server_exit()


# Phase B
print(
f"""
------------
Phase B
------------
"""
)
serverSocket2 = socket(AF_INET, SOCK_DGRAM)
serverSocket2.bind(("", udp_port))

expected_packet_id = 0
acked_packet_id = -1
pad_len = (4 - length % 4) % 4
data = bytearray(length + pad_len)
ex_data_length = len(data) + 4
entity = 2

while expected_packet_id < repeat:
    try:
        packet, clientAddress = serverSocket2.recvfrom(2048)
        data_length, pcode, entity, packet_id, data = struct.unpack(f'!IHHI{ex_data_length}s', packet)

        # Check
        if data_length != ex_data_length:
            continue
        if packet_id == expected_packet_id:
            acked_packet_id = expected_packet_id
            acked_packet = struct.pack(f"!IHHI", data_length, pcode, entity, acked_packet_id)
            if random.random() > 0.01:
                serverSocket2.sendto(acked_packet, clientAddress)
                expected_packet_id += 1
                print(f"Packet {packet_id} sent!")
        else:
            continue

    except Exception as e:
        print(f"An error has occured: {str(e)}")
        server_exit()

# Phase B-2
# After server recieves all packets, send packet to client
tcp_port = random.randint(20000, 30000)
codeB = random.randint(100, 400)
#tcp_port = 20000
#codeB = 100

b2packet = struct.pack(f"!IHHII", data_length, pcode, entity, tcp_port, codeB)
serverSocket2.sendto(b2packet, clientAddress)

# Phase C
print(
f"""
------------
Phase C
------------
"""
)
serverSocket3 = socket(AF_INET, SOCK_STREAM)
serverSocket3.bind(("", tcp_port))
serverSocket3.listen(5)
print("TCP server awaiting connection...")

clientSocket, clientAddress = serverSocket3.accept()
print("TCP server established connection with TCP client.")

pcode = codeB
repeat2 = random.randint(5, 20)
len2 = random.randint(50, 100)
codeC = random.randint(100, 400)
Char = random.choice(string.ascii_letters).upper().encode()

packet = struct.pack(f"!IHHIIIc", data_length, pcode, entity, repeat2, len2, codeC, Char)
clientSocket.send(packet)
print("Packet sent!")

# Phase D
print(
f"""
------------
Phase D 
------------
"""
)
pad_len = (4 - len2 % 4) % 4
data = Char * len2 
ex_data_length = len(data) + 4
entity = 2
for _ in range(random.randint(5, 20)):
    packet = clientSocket.recv(1024)
    data_length, pcode, entity = struct.unpack("!IHH{ex_data_length}s", packet[0])
    print(f"Received packet {_ + 1}!")

codeD = random.randint(100, 400)
tfpacket = struct.pack("!IHHI", data_length, pcode, entity, codeD)
clientSocket.send(tfpacket)
print("Sent final packet!!")

server_exit()




