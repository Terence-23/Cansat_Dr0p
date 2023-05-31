from psteering import Servo


def main():
    ser = Servo()
    ser_pos = ser.left
    ser_step = -2* ser.right - ser.left
    ser.rotate(ser.left)
    while input() != 'n':
        
        ser_pos += ser_step
        ser_step /= -2
        ser.rotate(ser_pos + ser_step)
        
        
    print(ser_step)

if __name__ == '__main__':
    main()