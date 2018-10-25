import SN3236
import MPR121
import time

def User_Callback(channel) :
    value = touch.MPR121_Get()
    value_tmp = value
    i = 0
    if(value_tmp == 0) :
        a = 0
    else :
        for i in range(0,12,1) :
            tmp = value_tmp >> i
            if(tmp & 0x01) :
                a = i + 1
    # i = int((value / 2048) * 16)
    a_ture = a - 4
    led_value = [0,0,0] * (10 - a_ture) + SN3236.SN3236_P * a_ture +[0,0,0] * 2
    leds.SN3236_Show(led_value)

leds = SN3236.SN3236()
leds.SN3236_PwrOn()
touch = MPR121.MPR121(25,"IRQ",User_Callback)



while(1) :
    time.sleep(5)
