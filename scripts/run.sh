#!/bin/bash
sudo python main.py \
  --led-gpio-mapping=adafruit-hat-pwm \
  --led-brightness=20 \
  --led-slowdown-gpio=2