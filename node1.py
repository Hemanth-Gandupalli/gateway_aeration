import time
from datetime import datetime,timedelta
import json
import os, sys
import struct

currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(currentdir)))
from LoRaRF import SX127x
import time
from gpiozero import CPUTemperature
busId = 0; csId = 0
resetPin = 22; irqPin = -1; txenPin = -1; rxenPin = -1
LoRa = SX127x()
print("Begin LoRa radio")
if not LoRa.begin(busId, csId, resetPin, irqPin, txenPin, rxenPin) :
    raise Exception("Something wrong, can't begin LoRa radio")

print("Set frequency to 433 Mhz")
LoRa.setFrequency(433000000)


print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
LoRa.setSpreadingFactor(7)
LoRa.setBandwidth(125000)
LoRa.setCodeRate(4/5)

print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
LoRa.setHeaderType(LoRa.HEADER_EXPLICIT)
LoRa.setPreambleLength(12)
LoRa.setPayloadLength(15)
LoRa.setCrcEnable(True)

print("Set syncronize word to 0x34")
LoRa.setSyncWord(0x34)
print("\n-- LoRa Node3 --\n")
send_slot=[[0,1],[6,7],[12,13],[18,19],[24,25],[30,31],[36,37],[42,43],[48,49],[54,55]]
recv_slot=[[1,2],[7,8],[13,14],[19,20],[25,26],[31,32],[37,38],[43,44],[49,50],[55,56]]
sleep = [[2,6],[8,12],[14,18],[20,24],[26,30],[32,36],[38,42],[44,48],[50,54],[56,60]]
while True:
    for i, slot in enumerate(recv_slot):
            current_min = datetime.now().minute
            if slot[0] <= current_min < slot[1]:
                print("--------Node 1 shifts to Recieving mode-------")
                LoRa.setRxGain(LoRa.RX_GAIN_POWER_SAVING, LoRa.RX_GAIN_AUTO)
                LoRa.request()
                LoRa.wait(5)
                try:
                    rcv_data=[]
                    while LoRa.available():
                        rcv_data.append(LoRa.read())
                    print(rcv_data)
                    rcv_data = bytes(rcv_data)
                    unstruct_data = struct.unpack('7f',rcv_data)
                    print("Recieved data--->",unstruct_data)
                    with open("dataR.json","r") as f:
                        data = json.load(f)
                    for i,j in enumerate(data):
                        data[j] = unstruct_data[i]
                    with open("dataR.json","w") as f:
                        json.dump(data,f)
                except Exception as e:
                    print(e)        
                status = LoRa.status()
                if status == LoRa.STATUS_CRC_ERR : print("CRC error")
                elif status == LoRa.STATUS_HEADER_ERR : print("Packet header error")
                time.sleep(5)
                #LoRa.reset()
                
    for i, slot in enumerate(send_slot):
        current_min = datetime.now().minute
        if slot[0] <= current_min < slot[1]:
            print("--------Node 1 shifts to sending mode-------")
            with open ("dataS.json","r") as f:
                data = json.load(f)
            print("json data -->",data)
            datalist = []
            for i in data:
                datalist.append(data[i])
            struct_data = struct.pack('7f',datalist[0],datalist[1],datalist[2],datalist[3],datalist[4],datalist[5],datalist[6])
            print("bytes_data ",struct_data)
            message = list(struct_data)
            print("struct_data --> ",message)
            LoRa.setTxPower(17, LoRa.TX_POWER_PA_BOOST)
            LoRa.beginPacket()
            LoRa.write(message,len(message))
            LoRa.endPacket()
            LoRa.wait()
            print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(LoRa.transmitTime(), LoRa.dataRate()))
            time.sleep(5)

    for i, slot in enumerate(sleep):
        current_min = datetime.now().minute
        if slot[0] <= current_min < slot[1]:
            print("---------Node 1 goes to sleep----------")
            time.sleep(242)

