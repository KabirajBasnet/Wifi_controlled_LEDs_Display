import serial
import time
import vlc
import struct
import keyboard
import random
import math

# Serial Connection
ser = serial.Serial('COM5', 115200, timeout=1)

#time.sleep(2)  # Let ESP32 reset

player = vlc.MediaPlayer(r"C:\Desktop\LED Lights v4 2.mp3")


# No: of Suits...
suits = 12



TRAIL = 12


paused = False
playing = False


redbrightness = 0
direction = 1





print("P = Play | Space = Pause/Resume | S = Stop | ← / → = Seek | M = Manual Mode | Q = Quit")

SEEK_STEP = 5  # seconds

# --- Playback functions ---
def play():
    global playing, paused
    player.play()
      #ptime.sleep(0.3)  # allow VLC to start
    playing = True
    paused = False

def pause_resume():
    global paused, played_time, start
    if paused:
        player.play()
        start = time.time()
        paused = False
    else:
        player.pause()
        paused = True
        
        #played_time = current_position
        #pausetime  = now

def stop():
    global playing, paused
    player.stop()   
    playing = False
    paused = False

def seek(delta):
    current = player.get_time()   # ms
    if current < 0:
        return
    player.set_time(current + delta * 1000)

packet_id = 0
def send_data(strip_id, pattern, r, g, b, dresspart, hop_count = 3 ):
    hop_count = 0
    global packet_id
    '''strip_id = 255
    pattern = 1
    r = 255
    g = 255
    b = 255
    dresspart = 0
    '''
    #origin_id = 0
    #sender_id = 0
    packet_id +=1
    
    # Pack into 7 bytes (uint8_t = 'B')
    packet = struct.pack(
    '<6B',
    strip_id,
    pattern,
    r,
    g,
    b,
    dresspart
    )
    ser.write(packet)

    print("Sent:", list(packet))

#arrowstripid = 10

head = 1
def arrowanime(strip_idarrow,r,g,b,directionarrow,step =5):
    global TRAIL,head,direction
    BASE_R = r
    BASE_G = g
    BASE_B = b

    for j in range(1,11):

        if directionarrow == 1:
            distance = strip_idarrow - j
        else:
            distance = j - strip_idarrow

        #print(distance, directionarrow)
        if 0 <= distance < TRAIL:
            brightness = (TRAIL - distance) / TRAIL
            r = int(BASE_R * brightness)
            g = int(BASE_G * brightness)
            b = int(BASE_B * brightness)
            send_data(j, 1, r, g, b, 0)
        else:
            send_data(j, 1, 0, 0, 0, 0)

        # move head
        head += direction

        # reverse at ends
        if head >= 10:
            direction = -1
        elif head <= 1:
            direction = 1
        


# Animations Definings

last_sendgalaxy = 0
INTERVALgalaxy = 0.07

last_sendravana = 0
INTERVALravana = 0.01

last_sendrama = 0
INTERVALrama = 0.008

last_sendravan = 0
INTERVALravan = 0.005


def galaxyanime():
    nowgalaxy = time.monotonic()
    global last_sendgalaxy, INTERVALgalaxy
    if nowgalaxy - last_sendgalaxy >= INTERVALgalaxy:
        strip_id1 = random.randrange(1,int((suits+1)/2),1)
        strip_id2 = random.randrange(int((suits+1)/2),suits+1,1)
        pattern = 1
        r = 100
        g = 100
        b = 100
        send_data(strip_id1, pattern, r , g, b,0)
        send_data(strip_id2, pattern, r , g, b,0)
        last_sendgalaxy = nowgalaxy
        for j in range(1,suits+1,1):
            if j != strip_id1 and j != strip_id2:
                send_data(j, 1, 0 , 0, 0, 0)
    send_data(20,4,0,0,0,0)
    send_data(21,4,0,0,0,0)
    send_data(22,4,0,0,0,0)
    send_data(23,4,0,0,0,0)
    #send_data()




# Narsimha animation variables


suitsl = [1,2,3,4,5,6,7,8,9,10,11,12,20,23]

TAIL_LENGTH = 6                 # Also used for krishna animation
FRAME_DELAY = 0.075 # seconds   # Also used for krishna animation

flow_head = 0
last_update = time.time()

color_phase = 0.0
COLOR_SPEED = 0.7   # slower = smoother

def get_cycling_color():
    global color_phase, COLOR_SPEED

    color_phase += COLOR_SPEED * 0.05   # small step
    if color_phase > 2 * math.pi:
        color_phase -= 2 * math.pi

    # sine wave goes 0 → 1 → 0
    t = (math.sin(color_phase) + 1) / 2

    # interpolate yellow ↔ orange
    r = 255
    g = int(120 - t * 80)   # 220 → 140
    b = 0

    return (r, g, b)


def scale_color(color, scale):
    return tuple(int(c * scale) for c in color)

def narsimhaanime():
#def update_flow(send_cmd):
    global flow_head, last_update

    now = time.time()
    if now - last_update < FRAME_DELAY:
        return   # ⛔ not time yet (non-blocking)

    last_update = now

    base_color = get_cycling_color()

    for i in range(TAIL_LENGTH):
        idx = (flow_head - i) % len(suitsl)

        brightness = (TAIL_LENGTH - i) / TAIL_LENGTH
        
        r, g, b = scale_color(base_color, brightness)

        suit_id = suitsl[idx]
        if suit_id != 20 and suit_id != 23:
            send_data(suit_id,1, r, g, b, 0)

    send_data(20,5,0,0,0,0)
    send_data(21,5,0,0,0,0)
    send_data(22,5,0,0,0,0)
    send_data(23,5,0,0,0,0)

    flow_head = (flow_head + 1) % len(suitsl)



FRAME_DELAYprahalad = 0.075
BASE_COLORprahalad = (0, 0, 255)

def prahaladanime():
    global left_head, right_head, last_update, BASE_COLORprahalad, FRAME_DELAYprahalad

    now = time.time()
    if now - last_update < FRAME_DELAYprahalad:
        return   # ⛔ non-blocking

    last_update = now

    # -------- LEFT SIDE (1 → 6) --------
    for i in range(TAIL_LENGTH):
        suit_num = left_head - i
        if suit_num < 1 or suit_num > 6:
            continue

        brightness = (TAIL_LENGTH - i) / TAIL_LENGTH
        r, g, b = scale_color(BASE_COLORprahalad, brightness)

        suit_id = suitsl[suit_num]
        send_data(suit_id, 1, r, g, b, 0)

        send_data(20, 1, r, g, b, 0)
        send_data(21, 1, r, g, b, 0)
        send_data(22, 1, r, g, b, 0)
        send_data(23, 1, r, g, b, 0)

    # -------- RIGHT SIDE (12 → 7) --------
    for i in range(TAIL_LENGTH):
        suit_num = right_head + i
        if suit_num > 12 or suit_num < 7:
            continue

        brightness = (TAIL_LENGTH - i) / TAIL_LENGTH
        r, g, b = scale_color(BASE_COLORprahalad, brightness)

        suit_id = suitsl[suit_num-1]
        send_data(suit_id, 1, r, g, b, 0)

        send_data(20, 1, r, g, b, 0)
        send_data(21, 1, r, g, b, 0)
        send_data(22, 1, r, g, b, 0)
        send_data(23, 1, r, g, b, 0)

    # -------- MOVE HEADS --------
    if left_head < 6:
        left_head += 1

    if right_head > 7:
        right_head -= 1




def ravanaanime1():
    nowravana = time.monotonic()
    global last_sendravana, last_sendravan, INTERVALravana, INTERVALravan
    if nowravana - last_sendravana >= INTERVALravana:
        strip_id1 = random.randrange(1,int((suits+1)/2),1)
        strip_id2 = random.randrange(int((suits+1)/2),suits+1,1)
        strip_id3 = random.randrange(20,24,1)
        pattern = 1
        r = 255
        g = 0
        b = 0
        send_data(strip_id1, pattern, r , g, b, 0)
        send_data(strip_id2, pattern, r , g, b, 0)
        send_data(strip_id3, pattern, r , g, b, 0)

        last_sendravana = nowravana
        for j in range(1,suits+1):
            if j != strip_id1 and j != strip_id2:
                send_data(j, 1, 0 , 0, 0, 0)
        for i in [20,21,22,23,24]:
            if i != strip_id3:
                send_data(i,1,0,0,0,0)
def ravanaanime2():
    nowravan = time.monotonic()
    global last_sendravana, last_sendravan, INTERVALravana, INTERVALravan, redbrightness,direction
    if nowravan-last_sendravan >= INTERVALravan:
        redbrightness += 2 * direction
        # Clamp + reverse
        if redbrightness >= 255:
            redbrightness = 255
            direction = -1
        elif redbrightness <= 0:
            redbrightness = 0
            direction = 1
        #strip_id = 255
        pattern = 1
        r = redbrightness
        g = 0
        b = 0
        dresspart = 0
        send_data(255, pattern, r, g, b, 0)
        send_data(20,pattern, r,g,b,0)
        send_data(21,pattern, r,g,b,0)
        send_data(22,pattern, r,g,b,0)
        send_data(23,pattern, r,g,b,0)
        last_sendravan = nowravan


# Rama Animation
bluebrightness = 0
direction = 1

# animation states
RAMA_STARTUP = 0
RAMA_LOOP = 1
rama_state = RAMA_STARTUP

# timing
last_sendrama = 0
STARTUP_INTERVAL = 0.02   # slower fade-in
INTERVALrama = 0.01       # normal animation speed
def ramaanime():
    global bluebrightness, direction, rama_state, last_sendrama,RAMA_LOOP
    global STARTUP_INTERVAL,INTERVALrama,RAMA_STARTUP
    nowrama = time.monotonic()

    # -------- PHASE 1: Slow fade-in (0 → 255) --------
    if rama_state == RAMA_STARTUP:
        if nowrama - last_sendrama >= STARTUP_INTERVAL:
            last_sendrama = nowrama

            bluebrightness += 1   # slower step

            if bluebrightness >= 255:
                bluebrightness = 255
                direction = -1
                rama_state = RAMA_LOOP   # switch to main animation

            send_data(255, 1, 0, 0, bluebrightness,0)
            send_data(20,1,0,0,bluebrightness,0)
            send_data(21,1,0,0,bluebrightness,0)
            send_data(22,1,0,0,bluebrightness,0)
            send_data(23,1,0,0,bluebrightness,0)

    # -------- PHASE 2: Normal breathing animation --------
    elif rama_state == RAMA_LOOP:
        if nowrama - last_sendrama >= INTERVALrama:
            last_sendrama = nowrama

            bluebrightness += 2 * direction

            # Clamp + reverse
            if bluebrightness >= 255:
                bluebrightness = 255
                direction = -1
            elif bluebrightness <= 0:
                bluebrightness = 0
                direction = 1

            send_data(255, 1,0, 0, bluebrightness,0 )
            send_data(20,1,0,0,bluebrightness,0)
            send_data(21,1,0,0,bluebrightness,0)
            send_data(22,1,0,0,bluebrightness,0)
            send_data(23,1,0,0,bluebrightness,0)

last_sendhanuman = 0
INTERVALhanuman = 0.02   # speed
phase = 0.0

def hanumananime():
    global last_sendhanuman, phase, INTERVALhanuman

    now = time.monotonic()
    if now - last_sendhanuman < INTERVALhanuman:
        return
    last_sendhanuman = now

    # Sine wave: 0 → 1 → 0
    t = (math.sin(phase) + 1) / 2

    r = 255
    g = int(80 * t)+20
    b = 0

    send_data(255,1,r, g, b,0)

    phase += 0.08

    #Swamianime()
    

# Krishna anime
BASE_COLOR = (0, 150, 255)

left_head = 1
right_head = 12
krish_direction = 1   # 1 = inward, -1 = outward

last_update = 0
FRAME_DELAYkrish = 0.075

def krishnaanime():
    global left_head, right_head, krish_direction
    global last_update, BASE_COLOR, FRAME_DELAYkrish

    now = time.time()
    if now - last_update < FRAME_DELAYkrish:
        return  # ⛔ non-blocking
    last_update = now

    # -------- LEFT SIDE --------
    for i in range(TAIL_LENGTH):
        suit_num = left_head - i
        if suit_num < 1 or suit_num > 12:
            continue

        brightness = (TAIL_LENGTH - i) / TAIL_LENGTH
        r, g, b = scale_color(BASE_COLOR, brightness)

        send_data(suitsl[suit_num-1], 1, r, g, b, 0)
        send_data(23,1,r,g,b,0)
        send_data(21,1,r,g,b,0)

    # -------- RIGHT SIDE --------
    for i in range(TAIL_LENGTH):
        suit_num = right_head + i
        if suit_num < 1 or suit_num > 12:
            continue

        brightness = (TAIL_LENGTH - i) / TAIL_LENGTH
        r, g, b = scale_color(BASE_COLOR, brightness)

        send_data(suitsl[suit_num-1], 1, r, g, b, 0)
        send_data(23,1,r,g,b,0)
        send_data(21,1,r,g,b,0)

    # -------- MOVE HEADS --------
    if krish_direction == 1:  # INWARD
        if left_head < 6:
            left_head += 1
        if right_head > 7:
            right_head -= 1

        # reached center → reverse
        if left_head == 6 and right_head == 7:
            krish_direction = -1

    else:  # OUTWARD
        if left_head > 1:
            left_head -= 1
        if right_head < 12:
            right_head += 1

        # reached ends → reverse
        if left_head == 1 and right_head == 12:
            krish_direction = 1



last_sendswami = 0
INTERVALswami = 0.005
def Swamianime():
    global last_sendswami, INTERVALswami,redbrightness,direction
    nowswami = time.monotonic()
    if nowswami-last_sendswami >= INTERVALswami:
        redbrightness += 2 * direction
        # Clamp + reverse
        if redbrightness >= 255:
            redbrightness = 255
            direction = -1
        elif redbrightness <= 0:
            redbrightness = 0
            direction = 1
        strip_id = 255
        pattern = 1
        r = redbrightness
        g = redbrightness*0.098039
        b = 0
        dresspart = 0
        send_data(strip_id, pattern, r, int(g), b, dresspart)
        send_data(20,1,int(r),int(g),int(b),0)
        send_data(21,1,int(r),int(g),int(b),0)
        send_data(22,1,int(r),int(g),int(b),0)
        send_data(23,1,int(r),int(g),int(b),0)
        last_sendswami = nowswami


# Battle Animations

#Battle 1

delaybattle1 = 0.008
last_sendbattle1 = 0
INTERVALbattle1 = 0.005
r_or_b = random.randint(0, 1)
bluebrightness = 0

def battle1(INTERVALbattle1 = 0.005):
    global last_sendbattle1,direction,delaybattle1, bluebrightness,redbrightness,r_or_b

    nowbattle1 = time.monotonic()

    if nowbattle1 - last_sendbattle1 >= INTERVALbattle1:

        # -------- RED FADE --------
        if r_or_b == 0:
            redbrightness += 2 * direction

            if redbrightness >= 255:
                redbrightness = 255
                direction = -1

            elif redbrightness <= 0:
                redbrightness = 0
                direction = 1
                r_or_b = 1        # switch to blue

            r = redbrightness
            g = 0
            b = 0

        # -------- BLUE FADE --------
        else:
            bluebrightness += 2 * direction

            if bluebrightness >= 255:
                bluebrightness = 255
                direction = -1

            elif bluebrightness <= 0:
                bluebrightness = 0
                direction = 1
                r_or_b = 0        # switch back to red

            r = 0
            g = 0
            b = bluebrightness

        send_data(255, 1, r, g, b, 0)
        send_data(20,1,r,g,b,0)
        send_data(21,1,r,g,b,0)
        send_data(22,1,r,g,b,0)
        send_data(23,1,r,g,b,0)

        last_sendbattle1 = nowbattle1


FRAME_DELAYbattle = 0.5
DRESSPART = 0
offsetbatle = 0
last_updatebattle = time.time()

RED  = (255, 0, 0)
BLUE = (0, 0, 255)
def battle():
    global offsetbatle, last_updatebattle,FRAME_DELAYbattle,RED,BLUE

    now = time.time()
    if now - last_updatebattle < FRAME_DELAYbattle:
        return   # ⛔ non-blocking

    last_updatebattle = now

    for i, suit_id in enumerate(suitsl):
        # alternate colors + move pattern
        if (i + offsetbatle) % 2 == 0:
            r, g, b = RED
        else:
            r, g, b = BLUE

        send_data(suit_id,1, r, g, b, 0)

    offsetbatle = (offsetbatle + 1) % 2   # shift pattern
    for j in [20,21,22,23]:
        if (j+offsetbatle)%2 == 0:
            r,g,b = RED
        else:
            r,g,b = BLUE
        send_data(j,1, r, g, b, 0)

def battle2():
    nowravana = time.monotonic()
    global last_sendravana, last_sendravan, INTERVALravana, INTERVALravan
    if nowravana - last_sendravana >= INTERVALravana:
        strip_id1 = random.randrange(1,int((suits+1)/2),1)
        strip_id2 = random.randrange(int((suits+1)/2),suits+1,1)
        strip_id3 = random.randrange(20,24,1)
        pattern = 1
        r = 0
        g = 0
        b = 255
        send_data(strip_id1, pattern, r , g, b, 0)
        send_data(strip_id2, pattern, r , g, b, 0)
        send_data(strip_id3, pattern, r , g, b, 0)
        last_sendravana = nowravana
        for j in range(1,suits+1):
            if j != strip_id1 and j != strip_id2:
                send_data(j, 1, 0 , 0, 0, 0)
        for i in [20,21,22,23]:
            if i != strip_id3:
                send_data(i, 1, 0 , 0, 0, 0)
    


    


# Chaser for Heart

TAIL_LENGTH_heart = 3
FRAME_DELAY_heart = 1
#DRESSPART = 0

BASE_COLOR_heart = (150, 0, 70) 

center_left = (len(suitsl) // 2) - 1   # index 4
center_right = len(suitsl) // 2        # index 5

step = 0
last_update = time.time()
#chaser_pos = 0
#last_update = time.time()
def scale_colorheart(color, scale):
    return tuple(int(c * scale) for c in color)
def heartanime():
    #def chaser_with_trail():
    global chaser_pos, last_update,step

    now = time.time()
    if now - last_update < FRAME_DELAY:
        return   # ⛔ no blocking

    last_update = now

    # Optional clear (use if ESP does not fade automatically)
    # for suit in suits:
    #     send_data(suit, 0, 0, 0, DRESSPART)

    for i in range(TAIL_LENGTH_heart):
        brightness = (TAIL_LENGTH_heart - i) / TAIL_LENGTH_heart
        r, g, b = scale_color(BASE_COLOR_heart, brightness)

        left_idx = center_left - (step - i)
        right_idx = center_right + (step - i)

        if 0 <= left_idx < len(suitsl):
            send_data(suitsl[left_idx],1, r, g, b, 0)

        if 0 <= right_idx < len(suitsl):
            send_data(suitsl[right_idx],1, r, g, b, 0)

    step += 1

    # reset when reaching ends
    if center_left - step < 0 and center_right + step >= len(suitsl):
        step = 0


# ---------------- CONFIG ----------------
NUM_SUITS = 12

# 1-based indexing
CENTER_LEFT  = NUM_SUITS // 2        # 6
CENTER_RIGHT = (NUM_SUITS // 2) + 1  # 7

# Max distance from center (ENDS)
MAX_STEP = max(CENTER_LEFT - 1, NUM_SUITS - CENTER_RIGHT)

INTERVALv2 = 0.02     # animation speed
MAX_LEVEL = 150       # brightness cap
LEVEL_STEP = 5

# ---------------- PHASES ----------------
PHASE_BLUE  = 0
PHASE_GREEN = 1
PHASE_RED   = 2
PHASE_DONE  = 3

phasev = PHASE_BLUE

# ---------------- STATE ----------------
step_index = MAX_STEP   # start from ends
level = 0
last_updatev = 0

# Floor LEDs (kept as you had them)
floorr = 0
floorg = 0
floorb = 0

# ---------------- HELPERS ----------------
def active_suits(step):
    """
    Returns suits that should be ON.
    Ends first → center last.
    """
    suits = []
    for s in range(1, NUM_SUITS + 1):
        dist = min(abs(s - CENTER_LEFT), abs(s - CENTER_RIGHT))
        if dist >= step:
            suits.append(s)
    return suits


# ---------------- MAIN ANIMATION ----------------
def vishwarupa():
    global phasev, step_index, level, last_updatev
    global floorr, floorg, floorb

    now = time.monotonic()
    if now - last_updatev < INTERVALv2:
        return
    last_updatev = now

    # ---- brightness ramp ----
    level += LEVEL_STEP
    if level > MAX_LEVEL:
        level = MAX_LEVEL

    # ---- color selection ----
    r = g = b = 0

    if phasev == PHASE_BLUE:
        b = level
    elif phasev == PHASE_GREEN:
        b = MAX_LEVEL
        g = level
    elif phasev == PHASE_RED:
        b = MAX_LEVEL
        g = MAX_LEVEL
        r = level
    elif phasev == PHASE_DONE:
        r = g = b = MAX_LEVEL

    # ---- send to active suits ----
    suitsv = active_suits(step_index)
    for s in suitsv:
        send_data(s, 1, r, g, b, 0)

    # ---- step collapse logic ----
    if level >= MAX_LEVEL:
        level = 0
        step_index -= 1

        # reached center → next phase
        if step_index < 0:
            step_index = MAX_STEP
            phasev += 1

            if phasev > PHASE_DONE:
                phasev = PHASE_DONE
                #print("done")

    # ---- floor LEDs (unchanged behavior) ----
    send_data(20, 1, floorr, floorg, floorb, 0)
    send_data(21, 1, floorr, floorg, floorb, 0)
    send_data(22, 1, floorr, floorg, floorb, 0)
    send_data(23, 1, floorr, floorg, floorb, 0)

    floorr = min(floorr + 1, 170)
    floorg = min(floorg + 1, 170)
    floorb = min(floorb + 1, 170)


last_sendv = 0
INTERVALv = 0.01
def vishwarupa2():
    nowv = time.monotonic()
    global last_sendv, INTERVALv,direction,redbrightness
    if nowv-last_sendv >= INTERVALv:
        redbrightness += 2 * direction
        # Clamp + reverse
        if redbrightness >= 150:
            redbrightness = 150
            direction = -1
        elif redbrightness <= 0:
            redbrightness = 0
            direction = 1
        strip_id = 255
        pattern = 1
        r = redbrightness
        g = redbrightness
        b = redbrightness
        dresspart = 0
        send_data(strip_id, pattern, r, int(g), b, dresspart)
        send_data(20,1,r,g,b,0)
        send_data(21,1,r,g,b,0)
        send_data(22,1,r,g,b,0)
        send_data(23,1,r,g,b,0)
        last_sendv = nowv


last_sendgold = 0
INTERVALgold = 0.005
def goldblink():
    nowgold = time.monotonic()
    global last_sendgold, INTERVALgold,direction,redbrightness
    if nowgold-last_sendgold >= INTERVALgold:
        redbrightness += 2 * direction
        # Clamp + reverse
        if redbrightness >= 239:
            redbrightness = 239
            direction = -1
        elif redbrightness <= 80:
            redbrightness = 80
            direction = 1
        strip_id = 255
        pattern = 1
        r = redbrightness   
        g = redbrightness*0.3
        b = redbrightness*0.1
        # (255,180,40)

        dresspart = 0
        send_data(strip_id, pattern, r, int(g), int(b), dresspart)
        last_sendgold = nowgold




played_time = 0
current_position = 0

INTERVAL = 0.1
last_send = 0
current_id = 1

INTERVAL3 = 0.1
last_send3 = 0
INTERVAL4 = 0.01
last_send4 = 0

last_sendarrow = 0
INTERVALARROW = 0.1
directionarrow = 1
strip_idarrow = 1

rpat = 100
gpat = 50
bpat = 200



#For song
pauseno = 1
position = 0

start = 0


# Main Loop
while True:
    if keyboard.is_pressed('m'):
        while True:
            try:
                inputdata = input("Enter Manual Values (Order is 'Strip_id','Pattern','R','G','B','dresspart')")
                if inputdata == 'ravan':
                
                    last_sendravan = 0
                    INTERVALravan = 0.005
                
                    while True:
                        nowravan = time.monotonic()
                        if nowravan-last_sendravan >= INTERVALravan:
                            redbrightness += 2 * direction
                            # Clamp + reverse
                            if redbrightness >= 255:
                                redbrightness = 255
                                direction = -1
                            elif redbrightness <= 0:
                                redbrightness = 0
                                direction = 1
                            #strip_id = 255
                            pattern = 1
                            r = redbrightness
                            g = 0
                            b = 0
                            dresspart = 0
                            for strip_id in range(5,8):
                                send_data(strip_id, pattern, r, g, b, dresspart)
                            last_sendravan = nowravan
                        if keyboard.is_pressed('q'):
                            send_data(255,1,0,0,0,0)
                            break

                elif inputdata == 'ram':
                    last_sendram = 0
                    INTERVALram = 0.005
                
                    while True:
                        nowram = time.monotonic()
                        if nowram-last_sendram >= INTERVALram:
                            redbrightness += 2 * direction
                            # Clamp + reverse
                            if redbrightness >= 255:
                                redbrightness = 255
                                direction = -1
                            elif redbrightness <= 0:
                                redbrightness = 0
                                direction = 1
                            #strip_id = 255
                            pattern = 1
                            r = 0
                            g = 0
                            b = redbrightness
                            dresspart = 0
                            for strip_id in range(2,5):
                                send_data(strip_id, pattern, r, g, b, dresspart)
                            last_sendram = nowram
                        if keyboard.is_pressed('q'):
                            send_data(255,1,0,0,0,0)
                            break

                elif inputdata == 'raman':
                    last_sendraman = 0
                    INTERVALraman = 0.01
                    
                
                    while True:
                        nowraman = time.monotonic()
                        if nowraman-last_sendraman >= INTERVALraman:
                            redbrightness += 2 * direction
                            
                            # Clamp + reverse
                            if redbrightness >= 255:
                                redbrightness = 255
                                direction = -1
                            elif redbrightness <= 0:
                                redbrightness = 0
                                direction = 1
                            #strip_id = 255
                            pattern = 1
                            r = redbrightness
                            g = 0
                            b = redbrightness
                            dresspart = 0
                            for strip_id in range(2,5):
                                send_data(strip_id, pattern, 0, g, b, dresspart)
                            for strip_id in range(5,8):
                                send_data(strip_id, pattern, r, g, 0, dresspart)
                            last_sendraman = nowraman
                        if keyboard.is_pressed('q'):
                            send_data(255,1,0,0,0,0)
                            break

                elif inputdata == 'swami':
                    last_sendswami = 0
                    INTERVALswami = 0.005
                
                    while True:
                        nowswami = time.monotonic()
                        if nowswami-last_sendswami >= INTERVALswami:
                            redbrightness += 2 * direction
                            # Clamp + reverse
                            if redbrightness >= 255:
                                redbrightness = 255
                                direction = -1
                            elif redbrightness <= 0:
                                redbrightness = 0
                                direction = 1
                            strip_id = 255
                            pattern = 1
                            r = redbrightness
                            g = redbrightness*0.098039
                            b = 0
                            dresspart = 0
                            send_data(strip_id, pattern, r, int(g), b, dresspart)
                            last_sendswami = nowswami
                        if keyboard.is_pressed('q'):
                            send_data(255,1,0,0,0,0)
                            break

                elif inputdata == 'A':
                    break

                elif inputdata != 'A':   
                    inputpacket = inputdata.split()
                    #hop_count = 0
                    strip_id = int(inputpacket[0])
                    pattern = int(inputpacket[1])
                    r = int(inputpacket[2])
                    g = int(inputpacket[3])
                    b = int(inputpacket[4])
                    dresspart = int(inputpacket[5])
                    
                    send_data(strip_id, pattern, r,g,b,dresspart)
            except Exception as e:
                print("Error: ",e)

    # Keys for playing music:
    if keyboard.is_pressed('p') and not playing:
        start = time.time()
        play()
        #time.sleep(0.3)

    if keyboard.is_pressed('space') and playing:
        pause_resume()
        time.sleep(0.3)

    if keyboard.is_pressed('s'):
        stop()
        time.sleep(0.3)

    if keyboard.is_pressed('q'):
        break


    #nowtime = time.time()
    #print(nowtime)

    '''    if playing and not paused:
        current_position = (nowtime - start) + position


    if paused and pauseno == 1:
        position = current_position
        pauseno = 0
    elif paused == False:
        pauseno = 1
    '''

    if keyboard.is_pressed('right'):
        seek(+SEEK_STEP)
        #position = position+ SEEK_STEP
        time.sleep(0.3)

    if keyboard.is_pressed('left'):
        seek(-SEEK_STEP)
        #position = position- SEEK_STEP
        #if position == 0:
        #    current_position = position
        time.sleep(0.3)

    position = player.get_position() * 100
    #print(position)  # e.g. 0.35 → 35% played

# Animation Sequence
    if position >= 0 and position < 7.8 and playing and not paused:
        galaxyanime()
        #print(position)
    elif position >= 7.9 and position < 13.5 and not paused:
        narsimhaanime()

    elif position >= 14 and position < 19 and playing and not paused:
        prahaladanime()

    elif position >= 19.5 and position < 23 and playing and not paused:
        ravanaanime2()

    elif position >= 23 and position < 25.5 and playing and not paused:
        ravanaanime1()

    elif position >= 25.9 and position < 29.8 and playing and not paused:
        #send_data(255,1,0,0,0,0)
        ramaanime()

    elif position >= 30 and position < 33 and playing and not paused:
        battle1()

    elif position >= 33.5 and position < 38.4 and playing and not paused:
        hanumananime()
        send_data(20,6,0,0,0,0)
        send_data(21,6,0,0,0,0)
        send_data(22,6,0,0,0,0)
        send_data(23,6,0,0,0,0)

    elif position >= 39 and position < 43.2 and playing and not paused:
        battle2()

    elif position >= 43.2 and position < 47.5 and playing and not paused:
        ravanaanime1()

    elif position >= 47.5 and position < 58.4 and playing and not paused:
        battle1(0.0001)
        
    elif position >= 58.5 and position < 67.8 and playing and not paused:
        krishnaanime()
        # Krishna flute

    elif position >= 67.9 and position < 77.86 and playing and not paused:
        #print(phase)
        if phasev != PHASE_DONE:    
            vishwarupa()
        else:
            vishwarupa2()

    elif position >= 77.86 and position < 85 and playing and not paused:
        Swamianime()
        # Swami

    elif position >= 85 and position < 99 and playing and not paused:
        goldblink()
        send_data(20,7,0,0,0,0)
        send_data(21,7,0,0,0,0)
        send_data(22,7,0,0,0,0)
        send_data(23,7,0,0,0,0)

    elif not paused and position < 98:
        send_data(255,1,0,0,0,0)

    elif not paused:
        send_data(20,7,0,0,0,0)
        send_data(21,7,0,0,0,0)
        send_data(22,7,0,0,0,0)
        send_data(23,7,0,0,0,0)


    '''    if position < 0:
        position =0
        
        current_position = 0

    if current_position < 0:
        #nowtime = start
        nowtime = start
        current_position = 0'''

    #current_position = max(0, min(current_position, 600))


    #print("Time elapsed: ",current_position)



    '''if playing and not paused:
        current_position = (now - start) + played_time
    elif paused:
        played_time = current_position
'''
    #print("Time elapsed: ",current_position)


    #now = time.time()
    # Sequence Code Here:
    if keyboard.is_pressed('l'):
        start = time.time()
        start = round(start,1)
        while True:

            now = time.time()
            now = round(now,1)

            timestamp = now-start
            if timestamp == 1:
                hop_count = 3
                strip_id = 255
                pattern = 1
                r = 255
                g = 255
                b = 255
                dresspart = 0
                # Pack into 7 bytes (uint8_t = 'B')
                send_data(strip_id, pattern, r,g,b,dresspart)

                time.sleep(1)

                hop_count = 3
                strip_id = 255
                pattern = 1
                r = 0
                g = 0
                b = 0
                dresspart = 0
                # Pack into 7 bytes (uint8_t = 'B')
                send_data(strip_id, pattern, r,g,b,dresspart)
            
            if timestamp >= 3 and timestamp < 10:
                '''for id in range(1,10):
                    strip_id = id
                    pattern = 1
                    r = 0
                    g = 255
                    b = 255
                    dresspart = 0

                    send_data(strip_id, pattern, r,g,b,dresspart)

                    time.sleep(0.05)'''

                nowpt2 = time.monotonic()

                if nowpt2 - last_send >= INTERVAL:
                    strip_id = current_id
                    pattern = 1
                    r, g, b = rpat, gpat, bpat
                    dresspart = 0

                    send_data(strip_id, pattern, r , g, b, dresspart)

                    current_id += 1
                    if current_id > suits:
                        current_id = 1
                        rpat = random.randrange(0,256,1)
                        gpat = random.randrange(0,256,1)
                        bpat = random.randrange(0,256,1)

                    last_send = nowpt2
                    

            elif timestamp >= 10 and timestamp <13:
                nowpt3 = time.monotonic()

                if nowpt3 - last_send3 >= INTERVAL3:
                    strip_id = random.randrange(1,11,1)
                    pattern = 1
                    r = 255
                    g = 255
                    b = 255
                    send_data(strip_id, pattern, r , g, b, dresspart)
                    last_send3 = nowpt3
                    for j in range(1,11):
                        if j is not strip_id:
                            send_data(j, 1, 0 , 0, 0, dresspart)

            elif timestamp >= 13 and timestamp < 15:
                nowpt4 = time.monotonic()
                if nowpt4-last_send4 >= INTERVAL4:
                    redbrightness += 5 * direction
                    # Clamp + reverse
                    if redbrightness >= 255:
                        redbrightness = 255
                        direction = -1
                    elif redbrightness <= 0:
                        redbrightness = 0
                        direction = 1
                    strip_id = 255
                    pattern = 1
                    r = redbrightness
                    g = int(r/1.545454)
                    b = 0
                    dresspart = 0
                    send_data(strip_id, pattern, r, g, b, dresspart)
                    last_send4 = nowpt4

            elif timestamp >= 15 and timestamp < 17:
                nowpt4 = time.monotonic()
                if nowpt4-last_send4 >= INTERVAL4:
                    redbrightness += 2 * direction
                    # Clamp + reverse
                    if redbrightness >= 255:
                        redbrightness = 255
                        direction = -1
                    elif redbrightness <= 0:
                        redbrightness = 0
                        direction = 1
                    strip_id = 255
                    pattern = 1
                    r = 0
                    g = redbrightness
                    b = redbrightness
                    dresspart = 0
                    send_data(strip_id, pattern, r, g, b, dresspart)
                    last_send4 = nowpt4

            elif timestamp >= 17 and timestamp < 20:
                nowpt4 = time.monotonic()
                if nowpt4-last_send4 >= INTERVAL4:
                    redbrightness += 5 * direction
                    # Clamp + reverse
                    if redbrightness >= 255:
                        redbrightness = 255
                        direction = -1
                    elif redbrightness <= 0:
                        redbrightness = 0
                        direction = 1
                    strip_id = 255
                    pattern = 1
                    r = redbrightness
                    g = 0
                    b = redbrightness
                    dresspart = 0
                    send_data(strip_id, pattern, r, g, b, dresspart)
                    last_send4 = nowpt4

            elif timestamp >=20 and timestamp < 30:
                nowarrow = time.monotonic()
                if nowarrow-last_sendarrow >= INTERVALARROW: 
                    if strip_idarrow >= suits:
                        r = random.randrange(0,256,1)
                        g = random.randrange(0,256,1)
                        b = random.randrange(0,256,1)
                        directionarrow = -1
                    if strip_idarrow <= 0:
                        r = random.randrange(0,256,1)
                        g = random.randrange(0,256,1)
                        b = random.randrange(0,256,1)
                        directionarrow = 1
                    arrowanime(strip_idarrow,r,g,b,directionarrow)
                    strip_idarrow = strip_idarrow+directionarrow
                    #print(strip_idarrow)
                    last_sendarrow = nowarrow
                    

            # Off after x secs
            elif timestamp >= 30:
                send_data(255, 1, 0, 0, 0, 0)        
                break
            if keyboard.is_pressed('q'):
                send_data(255,1,0,0,0,0)
                break

    '''if playing and not paused:
        current_position = (now - start) + played_time
    elif paused:
        played_time = current_position
'''
    #print("Time elapsed: ",current_position)
    
    '''if playing == True and paused == False:
        now = time.time()'''
        

player.stop()