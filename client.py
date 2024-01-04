from socket import * 
import struct
import sys
import random
import time

#serverName = '34.67.93.93'
serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

def check_server_response(response):
    data_len, pcode, entity = struct.unpack_from('!IHH', response)
    if pcode == 555:
        response = response[8:]
        print(response.decode())
        sys.exit()
    return

# Phase A
data = b'Hello World!!!'
length = len(data)
remainder = length % 4
padding = (4 - remainder) % 4

data = data + b'\x00' * padding
data_len = len(data)
pcode  = 0
entity = 1

phaseA_packet = struct.pack(f"!IHH{len(data)}s", data_len, pcode, entity, data)

print(f"""
------------
Phase A
------------   
Client sends packet:
    data_len = {data_len}
    pcode = {pcode}
    entity = {entity}
    data = {data}""")

clientSocket.sendto(phaseA_packet, (serverName, serverPort))
packet = clientSocket.recvfrom(2048)
data_len, pcode, entity, repeat, udp_port, length, codeA = struct.unpack("!IHHIIHH", packet[0])

print(f"""
Server response:
    data_len = {data_len}
    pcode = {pcode}
    entity = {entity}
    repeat = {repeat}
    udp_port = {udp_port}
    len = {length} 
    codeA = {codeA}
""")

# Phase B
pcode = codeA
entity = 1
packet_id = 0
print(
f"""
------------
Phase B
------------
"""
)

clientSocket.settimeout(5)
while packet_id < repeat:
    waiting_for_ack = True

    pad_len = (4 - length % 4) % 4
    data = bytearray(length + pad_len)
    data_length = len(data) + 4
    
    phaseB_packet = struct.pack(f'!IHHI{data_length}s', data_length, pcode, entity, packet_id, data)
    while waiting_for_ack:
        try:
            clientSocket.sendto(phaseB_packet, (serverName, udp_port))
            acked_packet, server_address = clientSocket.recvfrom(2048)
            waiting_for_ack = False
        except:
            print("Timeout")
            continue
        
        acked_dataLen, acked_pcode, acked_entity, acked_packetId = struct.unpack("!IHHI", acked_packet)

    print(
f"""
Retrieved acknowledged packet from server. ID: {packet_id} = ACK: {acked_packetId}
    data_length = {data_length}
    pcode = {pcode}
    entity = {entity}
    acked_packet_id = {acked_packetId}
""")
    packet_id += 1

# Phase B-1
b2packet, serverAddress = clientSocket.recvfrom(1024)
data_length, pcode, entity, tcp_port, codeB = struct.unpack('!IHHII', b2packet)

print(
f"""
Phase B-2 Recieved:
    data_length = {data_length}
    pcode = {pcode}
    entity = {entity}
    tcp_port = {tcp_port}
    codeB = {codeB}
"""
)

# Phase C
print(
f"""
------------
Phase C
------------
"""
)
time.sleep(3)
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, tcp_port))

packet = clientSocket.recv(1024)
data_length, pcode, entity, repeat2, len2, codeC, Char = struct.unpack(f"!IHHIIIc", packet)

print(
f"""
Recieved from TCP server:
    data_length = {data_length}
    pcode = {pcode}
    entity = {entity}
    repeat2 = {repeat2}
    len2 = {len2}
    codeC = {codeC}
    Char = {Char}
"""
)

# Phase D
print(
f"""
------------
Phase D 
------------
"""
)
pad_len = (4 - len2 % 4) % 4
data = Char * (len2 + pad_len) 
data_length = len(data) 

print(f"""
       data_length = {data_length}
       data = {data}
       len(data) = {len(data)}
       """)
for i in range(repeat2):
    packet = struct.pack(f"!IHH{data_length}s", data_length, codeC, 1, data)
    clientSocket.send(packet)
    # check_server_response( clientSocket.recv(2048))
    # break

tfpacket = clientSocket.recv(2048)
print("Received tfpacket")
data_length, pcode, entity, codeD = struct.unpack("!IHHI", tfpacket)

print(f"""Recieved from server: {codeD}""")
    
