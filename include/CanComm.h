#ifndef CanComm_
#define CanComm_
#include <RH_RF95.h>
#include "collectData.h"

extern char packetBuf[RH_RF95_MAX_MESSAGE_LEN];
extern const uint8_t len;

void radioSetup();
void preparePacket();
void sendPacket();

#endif
