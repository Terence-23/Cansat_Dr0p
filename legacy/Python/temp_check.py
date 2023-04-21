import sensor
import board

bme = sensor.BME(i2c=board.I2C())
print(bme.getTemp())
