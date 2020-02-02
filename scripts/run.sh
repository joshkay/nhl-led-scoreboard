#!/bin/bash
sudo python3 main.py \
  --led-gpio-mapping=adafruit-hat-pwm \
  --led-brightness=20 \
  --led-slowdown-gpio=2