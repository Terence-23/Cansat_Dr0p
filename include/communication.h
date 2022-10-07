
#include "Point.h"
#include <SPI.h>
#include <RH_RF95.h>

// for feather m0  
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3


// prepare down packet

char* prepare_packet();

// send & recieve packet

char* transfer_data(char* packet);

// decode response packet

Point decode_packet(char* packet);