#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, traceback, time, datetime
import struct

from Foundation import *
from PyObjCTools import AppHelper
from datetime import timedelta

import binascii
import xxtea
import codecs
import marshal

global key
global data
global debug
global readOK

#deco2_service_Battery            = CBUUID.UUIDWithString_(u'Battery')
#deco2_service_Device_Information = CBUUID.UUIDWithString_(u'Device Information')
deco2_service_10010000           = CBUUID.UUIDWithString_(u'10010000-2749-0001-0000-00805F9B042F')
deco2_service_10020000           = CBUUID.UUIDWithString_(u'10020000-2749-0001-0000-00805F9B042F')

deco2_service                    = CBUUID.UUIDWithString_(u'10020000-2749-0001-0000-00805F9B042F')



#deco2_ch_BatteryLevel   = CBUUID.UUIDWithString_(u'10020001-2749-0001-0000-00805F9B042F') #in %
deco2_ch_PIN            = CBUUID.UUIDWithString_(u'10020001-2749-0001-0000-00805F9B042F')
deco2_ch_KEY            = CBUUID.UUIDWithString_(u'1002000B-2749-0001-0000-00805F9B042F')

deco2_ch_Temp           = CBUUID.UUIDWithString_(u'10020005-2749-0001-0000-00805F9B042F') #2xTemp
deco2_ch_CODE           = CBUUID.UUIDWithString_(u'10020002-2749-0001-0000-00805F9B042F') #CODE
deco2_ch_Settings       = CBUUID.UUIDWithString_(u'10020003-2749-0001-0000-00805F9B042F') #SETTINGS
deco2_ch_Name           = CBUUID.UUIDWithString_(u'10020006-2749-0001-0000-00805F9B042F') #NAME
deco2_ch_Time           = CBUUID.UUIDWithString_(u'10020008-2749-0001-0000-00805F9B042F') #TIME
deco2_ch_Locale         = CBUUID.UUIDWithString_(u'1002000A-2749-0001-0000-00805F9B042F') #LOCALE


class BleClass(object):
    global readOK
    global debug
    readOK = False
    #debug = False
    debug = True

    def __init__(self):
        self.manager = None
        self.peripheral = None

        self.service = None

        self.pin = None
        self.readOK = False
        self.temps = None
        #self.key = 'add77f7ef2ecbd6477ee3bc5046f47d0'


    def centralManagerDidUpdateState_(self, manager):
        self.manager = manager
        manager.scanForPeripheralsWithServices_options_(None,None)


    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        self.peripheral = peripheral
        if debug:
            item="."
            print( item +str(peripheral.UUID() ))
        if 'eTRV' in str(peripheral.name()):
            print(str(peripheral.name()))
            e2[peripheral.UUID()]=danfossECO2(peripheral.UUID())
            print(e2)
            manager.connectPeripheral_options_(peripheral, None)
            manager.stopScan()


    def centralManager_didDisconnectPeripheral_error_(self, manager, peripheral, error):
        print( repr(error) )


    def centralManager_didConnectPeripheral_(self, manager, peripheral):
        #print( "centralManager_didConnectPeripheral_()"
        #print( repr(peripheral.UUID())
        if debug:
            print( "connected to ECO2" )
        peripheral.setDelegate_(self)
        self.peripheral.discoverServices_([deco2_service_10020000])


    def centralManager_didFailToConnectPeripheral_error_(self, manager, peripheral, error):
        if error is not None: print( str(error) )
        AppHelper.stopEventLoop()


    def centralManager_didDisconnectPeripheral_error_(self, manager, peripheral, error):
        if error is not None: print( str(error) )
        AppHelper.stopEventLoop()


    def peripheral_didDiscoverServices_(self, peripheral, services):
        if debug:
            print( str(self.peripheral.services()) )
            print( "Enumerating Services . . . " )
        for srv in self.peripheral.services():
            if debug:
                print( "Discovered services:" )
                print( str(srv) )
            self.service = srv #which service selection
            self.peripheral.discoverCharacteristics_forService_([deco2_ch_KEY,deco2_ch_PIN], self.service) #first get key and pin


    def peripheral_didDiscoverCharacteristicsForService_error_(self, peripheral, service, error):
        payloadBytes = b'' 
        if debug:
            print( "peripheral_didDiscoverCharacteristicsForService_error_()" )
            #print( "A:"+str(self) )
            #print( "B:"+str(peripheral) )
            #print( "C:"+str(service) )
            #print( service.characteristics()
            #print( error
            #print( "State: "+str(peripheral.state()) )
        for characteristic in service.characteristics():
            if characteristic is not None:
                if debug: print( str(characteristic) )
                if "10020001-2749-0001-0000-00805F9B042F" in str(characteristic): #pin_char
                    if e2[peripheral.UUID()].pin_char is None:
                    #if self.pin is None:
                        if debug: print( "pin characteristic found" )
                        e2[peripheral.UUID()].pin_char=characteristic #object
                        print(str(peripheral.state()))
                        #if str(peripheral.state())!='2':
                        if debug: print( "write PIN now" )
                        e2[peripheral.UUID()].pin_code='0000'

                        pinnr =str.encode(e2[peripheral.UUID()].pin_code)
                        payloadBytes = NSData.dataWithBytes_length_(pinnr, len(pinnr))
                        print(payloadBytes)
                        self.peripheral.writeValue_forCharacteristic_type_(payloadBytes,e2[peripheral.UUID()].pin_char,1)

                chars=['10020001-2749-0001-0000-00805F9B042F','10020002-2749-0001-0000-00805F9B042F','10020003-2749-0001-0000-00805F9B042F','10020005-2749-0001-0000-00805F9B042F','10020006-2749-0001-0000-00805F9B042F','10020008-2749-0001-0000-00805F9B042F','1002000A-2749-0001-0000-00805F9B042F','1002000B-2749-0001-0000-00805F9B042F']
                if str(characteristic.UUID()) in chars:
                    if debug: print( "characteristic found: " + str(characteristic.UUID()) )
                    peripheral.readValueForCharacteristic_(characteristic)


    def peripheral_didWriteValueForCharacteristic_error_(self, peripheral, characteristic, error):
        if debug: print( "Value written")
        #if debug: print( "State : "+str(peripheral.state()) )
        if debug: print( "Char  : "+str(characteristic) )

        if "10020001-2749-0001-0000-00805F9B042F" in str(characteristic):
            if debug: print( "PIN sent" )
            self.peripheral.discoverCharacteristics_forService_([deco2_ch_Time,deco2_ch_Temp,deco2_ch_Name], self.service) #here's where we define which service to read

        if "10020005-2749-0001-0000-00805F9B042F" in str(characteristic):
            if debug: print( "Temp written" )
            #self.peripheral.discoverCharacteristics_forService_([deco2_ch_Temp], self.service)
            #self.manager.cancelPeripheralConnection_(self.peripheral)


    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self, peripheral, characteristic, error):
        if debug: 
            print( "peripheral_didUpdateNotificationStateForCharacteristic_error_" )
            print( characteristic.UUID(), error )
            print( )


    def peripheral_didUpdateValueForCharacteristic_error_(self, peripheral, characteristic, error):
        payloadBytes = b'' 
        if debug: print( "peripheral_didUpdateValueForCharacteristic_error_()" )

        if str(characteristic.UUID()) == "1002000B-2749-0001-0000-00805F9B042F" and e2[peripheral.UUID()].key is None: 
            e2[peripheral.UUID()].key=str(bytes(characteristic.value()).hex())
            print()
            print('KEY RETRIEVED: '+e2[peripheral.UUID()].key)
            print()

        if str(characteristic.UUID()) == "10020005-2749-0001-0000-00805F9B042F":
            if debug: print( "temps char read" )
            print(str(bytes(characteristic.value()).hex()))
            sp,ct = e2[peripheral.UUID()].decryptTemp(str(bytes(characteristic.value()).hex()))
            print( "SP:"+str(sp)," CT:"+str(ct)) #SetPoint and CurrentTemp returned
            tmpnew=bytes(e2[peripheral.UUID()].encryptTemp('25.5'))
            payloadBytes = NSData.dataWithBytes_length_(tmpnew, len(tmpnew))
            if debug: print(payloadBytes)
            self.peripheral.writeValue_forCharacteristic_type_(payloadBytes,characteristic,1)


        if str(characteristic.UUID()) == "10020002-2749-0001-0000-00805F9B042F":
            if debug:
                print( "code char read" )
                print(str(bytes(characteristic.value()).hex()))
                #p2 print( danfossDecryptGeneric(str(characteristic.value()).encode("hex"),self.key) )
                #print(danfossDecryptGeneric(bytes(characteristic.value()).hex()))
                print( )

        if str(characteristic.UUID()) == "10020003-2749-0001-0000-00805F9B042F":
            if debug: 
                print( "settings char read" )
                #print( str(characteristic.value())
                #print( str(characteristic.value()).encode("hex")
                #P2: print( danfossDecryptGeneric(str(characteristic.value()).encode("hex"),self.key) )
                #print( danfossDecryptGeneric(bytes(characteristic.value()).hex(),self.key).hex())
                print( )
                #self.manager.cancelPeripheralConnection_(self.peripheral)


        if str(characteristic.UUID()) == "10020006-2749-0001-0000-00805F9B042F":
            if debug: 
                print( "name char read" )
                print( str(bytes(characteristic.value()).hex()))
                print( str(bytes(characteristic.value())))
                print( str(e2[peripheral.UUID()].decryptGeneric(bytes(characteristic.value()).hex()).hex()))
                print('')
                #self.manager.cancelPeripheralConnection_(self.peripheral)
                

        if str(characteristic.UUID()) == "10020008-2749-0001-0000-00805F9B042F":
            if debug: 
                print("time char read" )
                #print( str(characteristic.value())
                print(str(bytes(characteristic.value()).hex()))
            time_local,time_offset  = e2[peripheral.UUID()].decryptTime(bytes(characteristic.value()).hex())
            print('return')
            print( 'local time : '+datetime.datetime.fromtimestamp(time_local).strftime('%Y-%m-%d %H:%M:%S') )
            print( 'UTC time   : '+datetime.datetime.fromtimestamp(time_local-time_offset).strftime('%Y-%m-%d %H:%M:%S') )


        if str(characteristic.UUID()) == "1002000A-2749-0001-0000-00805F9B042F":
            if debug: 
                print( "locale char read" )
                print( str(characteristic.value()) )
                print( str(characteristic.value()).encode("hex") )
                print( e2[peripheral.UUID()].decryptGeneric(str(characteristic.value()).encode("hex")) )
                print( )
            print('1002000A')


class danfossECO2():

    def __init__(self,deviceuuid):
        self.deviceuuid = deviceuuid
        self.key_char   = None
        self.key        = None
        self.pin_char   = None
        self.pin_code   = None
        
        #self.key = 'add77f7ef2ecbd6477ee3bc5046f47d0'
        print('init: ',self.deviceuuid)


    def encryptTemp(self,data):
        if self.key==None: return False
        if debug: print( "encryptTemp(): "+ data, self.key )
        #data=text for temp e.g. '23.5'
        keystruct=bytearray.fromhex(str(self.key))
        u=float(data)*2.0 #1/2 degree accuracy
        arr = struct.pack('<q',int(u)) #convert to long int
        datastruct=arr[5:8]+arr[0:5] #swap places
        e=xxtea.encrypt(bytes(datastruct),bytes(keystruct),padding=False,rounds=32)
        w0=struct.unpack('8b',(e[4:8]+e[0:4]))
        w1 = struct.pack('8b',*w0[::-1])
        return w1
    
    
    def decryptTemp(self,data):
        if self.key==None: return False
        if debug: print( "danfossDecryptTemp(): "+ data, self.key )
        keystruct=bytearray.fromhex(str(self.key)) #make a bytearray of key
        datastruct=bytearray.fromhex((data[8:16]+data[0:8])) #get data in right endiannesss
        datastruct=datastruct[::-1] #and reverse
        c=xxtea.decrypt(bytes(datastruct),bytes(keystruct),padding=False,rounds=32) 
        d=c[4:8]+c[0:4] #swap ints
        e=d[::-1] #reverse
        xx,yy=struct.unpack('2b',e[0:2]) #unpack into 2 ints
        return (xx/2.0),(yy/2.0)


    def decryptTime(self,data):
        # IN[8],K[16] >> OUT[8]
        # format OUT = TTTTSSSS where T=offset from UTC in seconds, and S = UNIX epoch in seconds
        if self.key==None: return False
        if debug: print( "decryptTime(): "+data, self.key )
        keystruct=bytearray.fromhex(str(self.key)) #make a bytearray of key
        datastruct=bytearray.fromhex((data[8:16]+data[0:8])) #get data in right endiannesss
        datastruct=datastruct[::-1] #and reverse
        c=xxtea.decrypt(bytes(datastruct),bytes(keystruct),padding=False,rounds=32) 
        out_data=c[::-1] #reverse
        if debug: print( '{}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{}'.format(*bytes(out_data).hex()) )
        offset_to_UTC  = int(bytearray(out_data[0:4]).hex(),16)
        time_local     = int(bytearray(out_data[4:8]).hex(),16)
        return time_local,offset_to_UTC


    def decryptGeneric(self,data):
        # IN[32 x hex as string],K[32 x hex as string] > OUT[16 x hex as string]
        ###################################################################################################################
        if self.key==None: return False
        if debug: print( "decryptGeneric(): "+str(data),len(str(data)),str(self.key))
        keystruct=bytearray.fromhex(str(self.key)) #make a bytearray of key
        datastruct=bytearray.fromhex(str(data)) #get data in right endiannesss
        #datastruct=datastruct[::-1] #and reverse
        out_data=xxtea.decrypt(bytes(datastruct),bytes(keystruct),padding=False,rounds=32) 
        #out_data=c[::-1] #reverse
        if debug: print( '{}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{}'.format(*bytes(out_data).hex()) )
        return out_data
    ########################################################################################################################################

    def __str__(self):
        return


if "__main__" == __name__:
    try:
        e2={}
        central_manager = CBCentralManager.alloc()
        central_manager.initWithDelegate_queue_options_(BleClass(), None, None)
        #e2['06ED5B8B-4794-4469-9C50-EEA3DDA0C9F2']=danfossECO2('06ED5B8B-4794-4469-9C50-EEA3DDA0C9F2')
        #e2.key='add77f7ef2ecbd6477ee3bc5046f47d0'
        #print(e2)


        AppHelper.runConsoleEventLoop()
    except:
        print( "Exception in user code:" )
        print( '-'*60 )
        traceback.print(_exc(file=sys.stdout) )
        print( '-'*60 )
