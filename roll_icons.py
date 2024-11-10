import random
import os
import time
import filecmp

EMO_FACES = ['😁','😅','😂','😇','😉','😍','🥰','😘','😗','😛','😜','🤨','🤓','😎','🥸','🤩','🥳','😞','🥺','😡','😢','😭','🤬','🤯','😳','🥵','🥶','😱','🫣','🫢','🫠','😶','🫥','😐','😬','🙄','😵','😲','😴','🤢','🤠','🤑','😈','😷']
EMO_THINGS = ['🤡','💩','👻','💀','🤖','🎃','😺','👍','🖕','💪','🦷','👶','🤷','🐶','🐱','🐭','🐰','🦊','🐻','🐸','🐵','🐒','🐔','🦉','🐌','🐙','🦀','🍎','🍐','🍊','🍋','🍌','🍓','🌶️','🥑','🧄','🧅','🍞','🍗','🚗','🧩','☕️','🧊','🍄','🌳','🌷','🌞','🌝','🌎','🔥','🌪️','⛄️','☂️','🌪️','⭐️','☁️','💧','❄️','🪨','🍁','🐲','🪴','☘️','🐚','🐷','🦑','🐳','🐬','🌵','🙎','🙋','🤚','👽','👹','🧠','🎩','🪼','🦐','🦈','🦭','🫧','🍉','🍒','🍕','🌮','🫖','🍺','🎲','🏆']
EMO_ALL = EMO_FACES + EMO_THINGS

#for i in range(100,200):
#    while True:
#        e1 = random.choice(EMO_FACES)
#        e2 = random.choice(EMO_THINGS)
#        print(f"{e1} + {e2}")
#        time.sleep(2)
#        os.system(f"wget https://emojik.vercel.app/s/{e1}_{e2}?size=128 -O static/icon_{i}.png")
#        if not filecmp.cmp(f'static/icon_{i}.png', 'static/notfound.png'):
#            break

id = 0
n = 0

while id < 200:
    n = n+1
    e1 = EMO_ALL[(n * 29) % len(EMO_ALL)]
    e2 = EMO_THINGS[(n * 29) % len(EMO_THINGS)]
    print(f"{e1} + {e2}")
    time.sleep(1)
    os.system(f"wget https://emojik.vercel.app/s/{e1}_{e2}?size=128 -O static/icon_{id}.png")
    if not filecmp.cmp(f'static/icon_{id}.png', 'static/notfound.png'):
        id += 1
