This directory contains the images of each card in a deck and the deck back.
These images were taken from kdegames-4.8.0.tar.bz2 downloaded from
http://download.kde.org/stable/4.8.0/src/kdegames-4.8.0.tar.bz2

It's not entirely clear what license these files are released under, but being
that KDE, the package of which kdegames-4.8.0 is a part, is open source and
released under the GNU public license.  Please refer to kdegames-4.8.0.tar.bz2
for details about the licensing terms.

Only 2 files were actually taken from kdegames-4.8.0.tar.bz2:

standard.svg, from kdegames-4.8.0/libkdegames/carddecks/svg-standard/standard.svgz
deck.svg, from kdegames-4.8.0/libkdegames/carddecks/decks/deck12.svgz

First, cards.png was created using Gimp from standard.svg.  Then, all of the
card_suit_rank.png files were created by running split_cards_png.py, which runs
the command "cygconvert.exe" which is a renamed version of convert.exe from the
ImageMagick package, which is used to extract regions of cards.png into the
individual cards.

Finally, deck.png was created using Gimp from deck.svg.
