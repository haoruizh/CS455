from socket import *
import os
import sys
import struct
import time
import select
import binascii
from typing import Sequence

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise
def checksum(str):
    # In this function we make the checksum of our packet
    # hint: see icmpPing lab
    str = bytearray(str)
    count_sum = 0
    countTo = (len(str) // 2) * 2
    
    for count in range (0, countTo, 2):
        thisVal = str[count + 1] * 256 + str[count]
        count_sum = count_sum + thisVal
        count_sum = count_sum & 0xffffffff
        
    if countTo < len(str):
        count_sum = count_sum + str[-1]
        count_sum = count_sum & 0xffffffff
        
    count_sum = (count_sum >> 16) + (count_sum & 0xffff)
    count_sum = count_sum + (count_sum >> 16)
    calc = ~count_sum
    calc = calc & 0xffff
    calc = calc >> 8 | (calc << 8 & 0xff00)
    return calc


def build_packet():
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.
    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.
    # Don’t send the packet yet , just return the final packet in this function.
    # So the function ending should look like this
    myCheckSum = 0
    myID = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myCheckSum, myID,1)
    data = struct.pack("d", time.time())
    
    myCheckSum = checksum(header + data)
    if sys.platform == 'darwin':
        myCheckSum = htons(myCheckSum) & 0xffff
    else:
        myCheckSum = htons(myCheckSum)
    
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0 , myCheckSum, myID, 1)
    packet = header + data
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
            #Fill in start
            # Make a raw socket named mySocket
            mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
            #Fill in end
            
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], TIMEOUT)
                howLongInSelect = (time.time() - startedSelect)
                
                if whatReady[0] == []: # Timeout
                    print(" * * * Request timed out.")
                
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                
                if timeLeft <= 0:
                    print(" * * * Request timed out.")
                
            except timeout:
                return
                continue

            else:
                
                #Fill in start
                #Fetch the icmp type from the IP packet
                icmpHeader= recvPacket[20:28]
                types, code, checksum, own_id, sequence_num = struct.unpack("bbHHh",icmpHeader)
                #Fill in end
                
                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl, (timeReceived -t)*1000, addr[0]))
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl, (timeReceived-t)*1000, addr[0]))
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl,(timeReceived - timeSent)*1000, addr[0]))
                    return
                else:
                    print("error")
            finally:
                mySocket.close()

print ("Google:")
get_route("www.google.com")
print("Youtube")
get_route("www.youtube.com")
print("WSU")
get_route("www.wsu.edu")
print("AMAZON")
get_route("www.amazon.com")