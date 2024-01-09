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
recv_slot=[[0,1],[3,4],[6,7],[9,10],[12,13],[15,16],[18,19],[21,22],[24,25],[27,28],[30,31],[33,34],[36,37],[39,40],[42,43],[45,46],[48,49],[51,52],[54,55],[57,58]]
send_slot= [[1,3],[4,6],[7,9],[10,12],[13,15],[16,18],[19,21],[22,24],[25,27],[28,30],[31,33],[34,36],[37,39],[40,42],[43,45],[46,48],[49,51],[52,54],[55,57],[58,60]]
while True:
    for i, slot in enumerate(recv_slot):
            current_min = datetime.now().minute
            if slot[0] <= current_min < slot[1]:
                print("-------------recieve---------------")
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
                    print(unstruct_data)
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
            else:
                for i, slot in enumerate(send_slot):
                    current_min = datetime.now().minute
                    if slot[0] <= current_min < slot[1]:
                        print("--------sending-------")
                        with open ("dataS.json","r") as f:
                            data = json.load(f)
                        print("json data -->",data)
                        datalist = []
                        for i in data:
                            datalist.append(data[i])
                        struct_data = struct.pack('7f',datalist[0],datalist[1],datalist[2],datalist[3],datalist[4],datalist[5],datalist[6])
                        print("datalist[0] ",datalist[0])
                        print("datalist[1] ",datalist[1])
                        print("datalist[3] ",datalist[3])
                        print("datalist[6] ",datalist[6])
                        print("struct_data ",struct_data)
                        message = list(struct_data)
                        print("message --> ",message)
                        LoRa.setTxPower(17, LoRa.TX_POWER_PA_BOOST)
                        LoRa.beginPacket()
                        LoRa.write(message,len(message))
                        LoRa.endPacket()
                        LoRa.wait()
                        print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(LoRa.transmitTime(), LoRa.dataRate()))
                        time.sleep(5)