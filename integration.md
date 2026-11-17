# Integrating into Mzansi firmware and Android

## Firmware

Build the assets, then copy `integration/mzansi_gpio_html.h` alongside the main
Arduino sketch. Include it in the `.ino` (not in the async bridge):

```cpp
#include "mzansi_gpio_html.h"
```

Add this to the existing **synchronous port 80** WebServer route setup:

```cpp
web.on("/gpio-mzansi", HTTP_GET, []() {
  web.sendHeader("Cache-Control", "no-store");
  web.sendHeader("Content-Encoding", "gzip");
  web.send_P(200, "text/html; charset=utf-8",
    reinterpret_cast<const char *>(MZANSI_GPIO_HTML_GZ),
    sizeof(MZANSI_GPIO_HTML_GZ));
});
```

Keep GPIOViewer 1.7.1, its bridge, port 8080 and original `/` route unchanged.
Do not include its header in the `.ino`: its async HTTP enums conflict with the
synchronous WebServer header. Keep `GPIOViewer::begin()` opt-in and STA-only.
The new page contains no credentials. It validates `/api/status` with the key
entered by the operator and reads the existing stream cross-port using its CORS.

Add a normal link `/gpio-mzansi` to the dashboard navigation. Keep the existing
original-viewer launch link. Increment the firmware version so the existing
version history records the installation.

## Android

Add a distinct mode `mzansi-gpio` before the existing `gpio` option. Both require
the existing API-key validation and an active `gpioViewer` in `/api/status`.
For `mzansi-gpio`, load `http://HOST/gpio-mzansi` on port 80. For `gpio`, retain
`http://HOST:8080/`. Keep the IP-first -> mode -> API-key order. Inject the key
into the existing same-origin sessionStorage flow for the new page just as for
the dashboard. Do not put an API key in a URL or a persistent preference.

The installed integration uses Android app 1.3.0, versionCode 4. The public
standalone repository provides the reusable viewer rather than the user's
device credentials or complete private device configuration.

## Onboard LED

`integration/network_led.h` contains the non-blocking pattern function and
compile-time timing checks. The photo labels the user LED IO8; active-low is an
explicit assumption until visually confirmed. The generic C3 board profile's
`LED_BUILTIN` can be a synthetic RGB alias, so the integration uses GPIO8 directly.
Initialize only after boot. Register pin 8 as OUTPUT in the existing viewer
bridge without reapplying modes to already active UART/SPI pins.

Home Wi-Fi: ON 160 ms, OFF 180 ms, ON 160 ms, OFF until the next eight-second
cycle. Recovery hotspot: ON 1,800 ms, OFF 1,200 ms, repeating. Connecting: OFF.
Wi-Fi state means router association, not proof that a phone is viewing the page
or that Internet access exists. Do not repurpose GPIO8 for another load while
this status LED is enabled; it is also a C3 strapping pin.
