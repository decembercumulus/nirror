"Server Index Placeholder "

import random


nix =  (r" _______________ " + "\n"
        r"( Nirror works! )" + "\n"
        r" --------------- " + "\n"
        r"       o                   " + "\n"
        r"        o    \\  \\ //     " + "\n"
        r"         o  ==\\__\\/ //   " + "\n"
        r"              //   \\//    " + "\n"
        r"           ==//     //==   " + "\n"
        r"            //\\___//      " + "\n"
        r"           // /\\  \\==    " + "\n"
        r"             // \\  \\     " + "\n")


cow =  (r" _______________       " + "\n"
        r"( Nirror works! )      " + "\n"
        r" ---------------       " + "\n"
        r"        o   ^__^              " + "\n"
        r"         o  (==)\_______      " + "\n"
        r"            (__)\       )\/\  " + "\n"
        r"                ||----w |     " + "\n"
        r"                ||     ||     " + "\n")


def cowsay():
    return random.choice([nix,cow])
