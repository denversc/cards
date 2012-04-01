import subprocess

ranks = ("ace", "king", "queen", "jack", 10, 9, 8, 7, 6, 5, 4, 3, 2)
suits = ("spades", "hearts", "clubs", "diamonds")

y = 0
for row in range(4):
    x = 0
    for col in range(13):
        x_off = x * 216
        y_off = y * 288
        rank_name = ranks[x]
        suit_name = suits[y]
        geometry_str = "212x287+{}+{}".format(x_off, y_off)
        filename = "card_{}_{}.png".format(suit_name, rank_name)
        
        args = ["cygconvert", "cards.png", "-crop", geometry_str, filename]
        print(subprocess.list2cmdline(args))
        subprocess.Popen(args).wait()


        x += 1
    y += 1
