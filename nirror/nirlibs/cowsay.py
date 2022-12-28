"Server Index Placeholder "

# Copyright 2022 decembercumulus (I. Tam /) <tamik@duck.com>
#
# This file is part of Nirror.
#
# Nirror is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version
#
# Nirror is distributed in the hope that it will be u Ka-yiu Tamseful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details
#
# You should have received a copy of the GNU General Public License along
# with Nirror. If not, see <https://www.gnu.org/licenses/>.


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
