#include "CanComm.h"

const uint8_t len = sizeof(packetBuf);

void radioSetup(){
    
}

void preparePacket(){
    
    // 250 bytes
    char buf[RH_RF95_MAX_MESSAGE_LEN];

    buf[0] = '1';
    // temp(f), press(i32), humidity(f), GPS_long, GPS_lat;
    uint32_t temp = (uint32_t) bme.temperature;
    uint32_t press = (uint32_t) bme.pressure;
    uint32_t humidity = (uint32_t) bme.humidity;

    // char tempbuf[4] = {(temp & byteMask4), (temp & byteMask3), (temp & byteMask2), (temp & byteMask)};
    char* tempbuf = (char*)(&temp);
    char* pressbuf = (char*)(&press);
    char* humiditybuf = (char*)(&humidity);


    for (int i=0; i < 4; ++i){
        buf[1+i] = tempbuf[i];
    } for (int i=0; i< 4; ++i){
        buf[5+i] = pressbuf[i];
    } for (int i=0;i<4; ++i){
        buf[9+i] = humiditybuf[i];
    }


    strcpy(packetBuf, buf);
}

void sendPacket(){

}