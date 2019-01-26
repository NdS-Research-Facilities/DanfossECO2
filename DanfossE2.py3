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

global key
global data
global debug
global readOK

#deco2_service_Battery            = CBUUID.UUIDWithString_(u'Battery')
#deco2_service_Device_Information = CBUUID.UUIDWithString_(u'Device Information')
deco2_service_10010000           = CBUUID.UUIDWithString_(u'10010000-2749-0001-0000-00805F9B042F')
deco2_service_10020000           = CBUUID.UUIDWithString_(u'10020000-2749-0001-0000-00805F9B042F')

deco2_service = CBUUID.UUIDWithString_(u'10020000-2749-0001-0000-00805F9B042F')



deco2_ch_BatteryLevel   = CBUUID.UUIDWithString_(u'10020001-2749-0001-0000-00805F9B042F') #in %
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
        self.key = 'add77f7ef2ecbd6477ee3bc5046f47d0'

    def centralManagerDidUpdateState_(self, manager):
        self.manager = manager
        manager.scanForPeripheralsWithServices_options_([],None)

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        self.peripheral = peripheral
        if debug:
            ###print( '-- ' + str(peripheral.UUID())
            item="."
            print( item )
        if '06ED5B8B-4794-4469-9C50-EEA3DDA0C9F2' in repr(peripheral.UUID()):
            #print( ">> " + str(peripheral.UUID())
            ###item=">"
            ###print( item
            manager.connectPeripheral_options_(peripheral, None)
            manager.stopScan()

    def centralManager_didDisconnectPeripheral_error_(self, manager, peripheral, error):
        print( repr(error) )


    def centralManager_didConnectPeripheral_(self, manager, peripheral):
        #print( "centralManager_didConnectPeripheral_()"
        #print( repr(peripheral.UUID())
        if debug:
            print( "found EC2" )
        peripheral.setDelegate_(self)
        self.peripheral.discoverServices_([deco2_service_10020000])

    def centralManager_didFailToConnectPeripheral_error_(self, manager, peripheral, error):
        if error is not None: print( str(error) )

    def centralManager_didDisconnectPeripheral_error_(self, manager, peripheral, error):
        if error is not None: print( str(error) )
        AppHelper.stopEventLoop()


    def peripheral_didDiscoverServices_(self, peripheral, services):
        #print( "peripheral_didDiscoverServices_()"
        #print( ">>>>"
        if debug:
            print( str(self.peripheral.services()) )
            print( "Connecting . . . " )
        for srv in self.peripheral.services():
            if debug:
                print( "Discovered services:" )
                print( str(srv) )
            self.service = srv #which service selection
            #self.peripheral.discoverCharacteristics_forService_([deco2_characteristic_data_PIN,deco2_characteristic_data_KEY,deco2_characteristic_data_TMP], self.service)
            #self.peripheral.discoverCharacteristics_forService_([deco2_characteristic_data_PIN,deco2_characteristic_data_TMP,deco2_characteristic_data_NME], self.service)
            self.peripheral.discoverCharacteristics_forService_([deco2_ch_PIN], self.service)


            #self.service = self.peripheral.services()[2] #which service selection
            #self.peripheral.discoverCharacteristics_forService_([deco2_characteristic_data_SET], self.service)
            #self.service = self.peripheral.services()[0] #which service selection
            #self.service = self.peripheral.services()[1] #which service selection
            ####self.service = self.peripheral.services()[2] #which service selection
            

            #self.peripheral.discoverCharacteristics_forService_([], self.service)

            #self.peripheral.discoverCharacteristics_forService_([deco2_characteristic_data_PIN], self.service)
            #self.peripheral.discoverCharacteristics_forService_([deco2_characteristic_data_B], self.service)
            #self.peripheral.discoverCharacteristics_forService_([deco2_characteristic_data_6], self.service)

    def peripheral_didDiscoverCharacteristicsForService_error_(self, peripheral, service, error):
        payloadBytes = b'' 
        if debug:
            print( "peripheral_didDiscoverCharacteristicsForService_error_()" )
            print( "A:"+str(self) )
            print( "B:"+str(peripheral) )
            print( "C:"+str(service) )
            #print( service.characteristics()
            #print( error
            print( "State: "+str(peripheral.state()) )
        for characteristic in service.characteristics():
            if characteristic is not None:
                if debug: print( str(characteristic) )
                if "10020001-2749-0001-0000-00805F9B042F" in str(characteristic):
                    if self.pin is None:
                        if debug: print( "pin characteristic found" )
                        self.pin=characteristic
                        #if str(peripheral.state())!='2':
                        if debug: print( "write PIN" )
                        pinnr =str.encode('0000')
                        payloadBytes = NSData.dataWithBytes_length_(pinnr, len(pinnr))
                        print(payloadBytes)
                        self.peripheral.writeValue_forCharacteristic_type_(payloadBytes,self.pin,1)

                chars=['10020001-2749-0001-0000-00805F9B042F','10020002-2749-0001-0000-00805F9B042F','10020003-2749-0001-0000-00805F9B042F','10020005-2749-0001-0000-00805F9B042F','10020006-2749-0001-0000-00805F9B042F','10020008-2749-0001-0000-00805F9B042F','1002000A-2749-0001-0000-00805F9B042F','1002000B-2749-0001-0000-00805F9B042F']
                if str(characteristic.UUID()) in chars:
                    if debug: print( "characteristic found: " + str(characteristic.UUID()) )
                    peripheral.readValueForCharacteristic_(characteristic)


    def peripheral_didWriteValueForCharacteristic_error_(self, peripheral, characteristic, error):
        if debug: print( "State : "+str(peripheral.state()) )
        if debug: print( "Char  : "+str(characteristic) )
        #print( "peripheral_didWriteValueForCharacteristic_error_"
        #print( characteristic.UUID(), error
        #print( 
        #print( self.service.characteristics()[4]
        #peripheral.readValueForCharacteristic_(self.service.characteristics()[0])
        
        #self.peripheral.discoverCharacteristics_forService_([deco2_characteristic_data_TMP,deco2_characteristic_data_NME,deco2_characteristic_data_CDE,deco2_characteristic_data_SET,deco2_characteristic_data_TME], self.service)
        #self.peripheral.discoverCharacteristics_forService_([deco2_ch_Temp,deco2_ch_Name,deco2_ch_Settings,deco2_ch_CODE], self.service)
        if "10020001-2749-0001-0000-00805F9B042F" in str(characteristic):
            if debug: print( "PIN sent" )
            self.peripheral.discoverCharacteristics_forService_([deco2_ch_Name], self.service)

        if "10020005-2749-0001-0000-00805F9B042F" in str(characteristic):
            if debug: print( "Temp written" )
            #self.peripheral.discoverCharacteristics_forService_([deco2_ch_Temp], self.service)
            self.manager.cancelPeripheralConnection_(self.peripheral)




    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self, peripheral, characteristic, error):
        if debug: 
            print( "peripheral_didUpdateNotificationStateForCharacteristic_error_" )
            print( characteristic.UUID(), error )
            print( )

    def peripheral_didUpdateValueForCharacteristic_error_(self, peripheral, characteristic, error):
        payloadBytes = b'' 
        if debug: print( "peripheral_didUpdateValueForCharacteristic_error_()" )
        #print( characteristic.UUID(), characteristic, error
        #print( str(characteristic.value())
        #print( str(characteristic.value()).encode("hex")

        if str(characteristic.UUID()) == "1002000B-2749-0001-0000-00805F9B042F" and self.key is None: 
            self.key=str(characteristic.value()).encode("hex")

        if str(characteristic.UUID()) == "10020005-2749-0001-0000-00805F9B042F":
            if debug: print( "temps char read" )
            print(str(bytes(characteristic.value()).hex()))
            sp,ct = danfossDecryptTemp(str(bytes(characteristic.value()).hex()),self.key)
            print( "SP:"+str(sp)," CT:"+str(ct)) #SetPoint and CurrentTemp returned
            tmpnew=bytes(danfossEncryptTemp('25.5',self.key))
            payloadBytes = NSData.dataWithBytes_length_(tmpnew, len(tmpnew))
            if debug: print(payloadBytes)
            self.peripheral.writeValue_forCharacteristic_type_(payloadBytes,characteristic,1)


        if str(characteristic.UUID()) == "10020002-2749-0001-0000-00805F9B042F":
            if debug: #HIER BEZIG ########################################################################################
                print( "code char read" )
                print(str(bytes(characteristic.value()).hex()))
                #p2 print( danfossDecryptGeneric(str(characteristic.value()).encode("hex"),self.key) )
                print(danfossDecryptGeneric(bytes(characteristic.value()).hex(),self.key))
                print( )

        if str(characteristic.UUID()) == "10020003-2749-0001-0000-00805F9B042F":
            if debug: 
                print( "settings char read" )
                #print( str(characteristic.value())
                #print( str(characteristic.value()).encode("hex")
                #P2: print( danfossDecryptGeneric(str(characteristic.value()).encode("hex"),self.key) )
                print( danfossDecryptGeneric(bytes(characteristic.value()).hex(),self.key).hex())
                print( )
                self.manager.cancelPeripheralConnection_(self.peripheral)


        if str(characteristic.UUID()) == "10020006-2749-0001-0000-00805F9B042F":
            if debug: 
                print( "name char read" )
                print( str(bytes(characteristic.value()).hex()))
                print( danfossDecryptGeneric(bytes(characteristic.value()).hex(),self.key).hex())
                print( )
                

        if str(characteristic.UUID()) == "10020008-2749-0001-0000-00805F9B042F":
            if debug: 
                print("time char read" )
                #print( str(characteristic.value())
                print(str(bytes(characteristic.value()).hex()))
            time_local,time_offset  = danfossDecryptTime(bytes(characteristic.value()).hex(),self.key)
            print('return')
            print( 'local time : '+datetime.datetime.fromtimestamp(time_local).strftime('%Y-%m-%d %H:%M:%S') )
            print( 'UTC time   : '+datetime.datetime.fromtimestamp(time_local-time_offset).strftime('%Y-%m-%d %H:%M:%S') )


        if str(characteristic.UUID()) == "1002000A-2749-0001-0000-00805F9B042F":
            if debug: 
                print( "locale char read" )
                print( str(characteristic.value()) )
                print( str(characteristic.value()).encode("hex") )
                print( danfossDecryptGeneric(str(characteristic.value()).encode("hex"),self.key) )
                print( )



        print('test')

        '''
        if self.pin is None or self.temps is None or self.key is None:
            print()
            if debug: print( "keep going")
        else:
            print()
            if debug: 
                sp,ct = danfossDecryptTemp(self.temps,self.key)
                print( "SP:"+str(sp)," CT:"+str(ct)) #SetPoint and CurrentTemp returned
                ###############self.manager.cancelPeripheralConnection_(self.peripheral)
        
        if error is None:
            print( "Read EC2" )
            if debug:
                print( characteristic.UUID(), characteristic, error )
                print( str(characteristic.value()).encode("hex"), str(characteristic.value()) )
            key = "add77f7ef2ecbd6477ee3bc5046f47d0" #key nds 
            st,ct = danfossDecryptTemp(str(characteristic.value()).encode("hex"),key)
            print( "SetPoint: "+str(st)," CurrentTemp: "+str(ct) 
            if self.peripheral is not None and readOK:
                readOK=False
                self.manager.cancelPeripheralConnection_(self.peripheral)
        '''


def danfossEncryptTemp(data,key):
    print( "danfossEncryptTemp(): "+ data, key )
    #data=text for temp e.g. '23.5'
    keystruct=bytearray.fromhex(key)
    u=float(data)*2.0 #1/2 degree accuracy
    arr = struct.pack('<q',int(u)) #convert to long int
    datastruct=arr[5:8]+arr[0:5] #swap places
    e=xxtea.encrypt(bytes(datastruct),bytes(keystruct),padding=False,rounds=32)
    w0=struct.unpack('8b',(e[4:8]+e[0:4]))
    w1 = struct.pack('8b',*w0[::-1])
    return w1


def danfossDecryptTemp(data,key):
    print( "danfossDecryptTemp(): "+ data, key )
    keystruct=bytearray.fromhex(key) #make a bytearray of key
    datastruct=bytearray.fromhex((data[8:16]+data[0:8])) #get data in right endiannesss
    datastruct=datastruct[::-1] #and reverse
    c=xxtea.decrypt(bytes(datastruct),bytes(keystruct),padding=False,rounds=32) 
    d=c[4:8]+c[0:4] #swap ints
    e=d[::-1] #reverse
    xx,yy=struct.unpack('2b',e[0:2]) #unpack into 2 ints
    return (xx/2.0),(yy/2.0)


def danfossDecryptTime(data,key):
    # IN[8],K[16] >> OUT[8]
    # format OUT = TTTTSSSS where T=offset from UTC in seconds, and S = UNIX epoch in seconds
    if debug: print( "danfossDecryptTime(): "+data, key )
    keystruct=bytearray.fromhex(key) #make a bytearray of key
    datastruct=bytearray.fromhex((data[8:16]+data[0:8])) #get data in right endiannesss
    datastruct=datastruct[::-1] #and reverse
    c=xxtea.decrypt(bytes(datastruct),bytes(keystruct),padding=False,rounds=32) 
    out_data=c[::-1] #reverse
    if debug: print( '{}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{}'.format(*bytes(out_data).hex()) )
    offset_to_UTC  = int(bytearray(out_data[0:4]).hex(),16)
    time_local     = int(bytearray(out_data[4:8]).hex(),16)
    return time_local,offset_to_UTC


def danfossDecryptGeneric(data,key):
    # IN[32 x hex as string],K[32 x hex as string] > OUT[16 x hex as string]
    ###################################################################################################################
    if debug: print( "danfossDecryptGeneric(): "+data,len(data),key,len(key) )
    keystruct=bytearray.fromhex(key) #make a bytearray of key
    datastruct=bytearray.fromhex(data) #get data in right endiannesss
    #datastruct=datastruct[::-1] #and reverse
    c=xxtea.decrypt(bytes(datastruct),bytes(keystruct),padding=False,rounds=32) 
    #out_data=c[::-1] #reverse
    if debug: print( '{}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{} {}{}'.format(*bytes(out_data).hex()) )
    return out_data
########################################################################################################################################

if "__main__" == __name__:
    try:
        central_manager = CBCentralManager.alloc()
        central_manager.initWithDelegate_queue_options_(BleClass(), None, None)
        AppHelper.runConsoleEventLoop()
    except:
        print( "Exception in user code:" )
        print( '-'*60 )
        traceback.print(_exc(file=sys.stdout) )
        print( '-'*60 )
