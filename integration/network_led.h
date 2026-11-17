#pragma once
#include <stdint.h>

// Photo marks the user LED IO8. Active-low is a board-revision assumption until
// visually confirmed; set false if this revision lights when GPIO8 is HIGH.
constexpr uint8_t NETWORK_LED_PIN = 8;
constexpr bool NETWORK_LED_ACTIVE_LOW = true;

// Pure, wrap-safe timing: 0=connecting/off, 1=home Wi-Fi, 2=recovery AP.
constexpr bool networkLedOn(uint32_t elapsed, uint8_t state) {
  return state == 1 ? ((elapsed % 8000U) < 160U ||
                      ((elapsed % 8000U) >= 340U && (elapsed % 8000U) < 500U)) :
         state == 2 ? (elapsed % 3000U) < 1800U : false;
}
static_assert(networkLedOn(0,1) && !networkLedOn(160,1) &&
              networkLedOn(340,1) && !networkLedOn(500,1), "Double-flash timing");
static_assert(networkLedOn(1799,2) && !networkLedOn(1800,2) &&
              networkLedOn(3000,2) && !networkLedOn(0,0), "AP pulse timing");
