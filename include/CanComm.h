#ifndef CanComm_
#define CanComm_
#include <RH_RF95.h>
// #include "collectData.h"

#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3
#define RF95_FREQ 433

extern char packetBuf[RH_RF95_MAX_MESSAGE_LEN];
extern uint8_t recvBuf[RH_RF95_MAX_MESSAGE_LEN];
extern uint8_t len;
extern RH_RF95 rf95;
extern double GPS_lat, GPS_long;

void radioSetup();
void preparePacket(float temp, int32_t press, float humidity);
void sendPacket();
void decode(char* packet);

#endif
