import time, sys
from pygame import mixer

# pygame.init()
mixer.init()

sound = mixer.Sound("knocking_a_wooden_door2.mp3")
sound.play()

time.sleep(5)