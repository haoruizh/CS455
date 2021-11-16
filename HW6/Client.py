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
def checksum(string):
    # In this function we make the checksum of our packet
    # hint: see icmpPing lab
    count_sum = 0
    countTo = (len(str) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = ord(str[count + 1]) * 256 + ord(str[count])
        count_sum = count_sum + thisVal
        count_sum = count_sum & 0xffffffff
        count = count + 2
    if countTo < len(str):
        count_sum = count_sum + ord(str[len(str) - 1])
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
    packet = header + data
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)

            #Fill in start
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_DGRAM, icmp)
            #Fill in end
            
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    print(" * * * Request timed out.")
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print(" * * * Request timed out.")
            except timeout:
                continue

            else:
                
                #Fill in start
                #Fetch the icmp type from the IP packet
                icmpPacket = recvPacket[20:28]
                types, code, checksum, own_id, sequence_num = struct.unpack("BBHHH",icmpPacket)
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
                break
            finally:
                mySocket.close()
get_route("google.com")