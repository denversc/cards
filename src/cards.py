################################################################################
# cards.py
# By: Denver Coneybeare
# March 27, 2012
################################################################################

from __future__ import print_function

import argparse
import BaseHTTPServer
import httplib
import os
import random
import sys
import threading
import urlparse

################################################################################

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_ARGS = 2

################################################################################

def main(prog=None, args=None):
    """
    The main entry point of the cards application.
    *prog* must be a string whose value is the name of the program to display
    to the user when referring to this application; the default value is None,
    in which case sys.argv[0] will be used.
    *args* must be an iterable of strings whose values are the arguments to the
    program; the default value is None, in which case sys.argv[1:] will be used.
    Returns an integer whose value is an exit code suitable for specifying to
    sys.exit() to convey the result of the application.
    """
    if prog is None:
        prog = sys.argv[0]
    if args is None:
        args = sys.argv[1:]

    # parse the arguments then run the application
    arg_parser = MyArgumentParser(prog=prog)
    try:
        app = arg_parser.parse_args(args)
    except arg_parser.Error as e:
        exit_code = e.exit_code
        if exit_code == EXIT_SUCCESS:
            message = str(e)
            if message and message != str(None):
                print(message)
        elif exit_code == EXIT_ARGS:
            print("ERROR: invalid command-line arguments: {}".format(e),
                file=sys.stderr)
            print("Run with --help for help")
        else:
            print("ERROR: {}".format(e), file=sys.stderr)
    else:
        del arg_parser # allow GC
        try:
            app.run()
        except app.Error as e:
            print("ERROR: {}".format(e))
            exit_code = EXIT_ERROR
        else:
            exit_code = EXIT_SUCCESS

    return exit_code

################################################################################

class CardsApplication(object):
    """
    The cards applications.  Simply invoke this object's run() method to run
    the application.
    """

    def __init__(self, http_server_port=8080):
        """
        Initializes a new instance of this class.
        *http_server_port* must be an integer whose value is the TCP port to
        which the HTTP server will bind (default: 8080).
        """
        self.http_server_port = http_server_port


    def run(self):
        """
        Runs this application.
        Raises self.Error on error.
        """
        http_server = MyHttpServer(self.http_server_port)
        print("To use the application, browse to http://localhost:{}"
            .format(self.http_server_port))
        http_server.serve_forever()


    class Error(Exception):
        """
        Exception raised if an error occurs in the application.
        """
        pass

################################################################################

class Card(object):
    """
    Represents a card in a standard deck of cards.
    A card has 2 properties: a suit and a rank.
    Instances of this class may be compared for equality using the == operator.
    """

    SPADE = "spade"
    HEART = "heart"
    CLUB = "club"
    DIAMOND = "diamond"

    RANK_NAMES = {
        1: "ace",
        11: "jack",
        12: "queen",
        13: "king",
    }

    SUIT_NAMES = {
        SPADE: "spades",
        HEART: "hearts",
        CLUB: "clubs",
        DIAMOND: "diamonds",
    }

    def __init__(self, suit, rank):
        """
        Initializes a new instance of this class.
        *suit* is the suit of the card, and must be equal to one of the
        following constants defined in this class: SPADE, HEART, CLUB, DIAMOND.
        *rank* must be an integer whose value is the rank of the card; the
        valid range is 1 to 13, inclusive, where 1 is the ace, 11 is the Jack,
        12 is the Queen, and 13 is the king.
        """
        self.suit = suit
        self.rank = rank


    def __eq__(self, other):
        """
        Compares another object to this object for equality.
        The object is considered to be "equal" if it has both a "suit" and a
        "rank" attribute with values that compare equal using the == operator
        to the corresponding attributes of this object.
        """
        try:
            other_suit = other.suit
            other_rank = other.rank
        except AttributeError:
            return False
        else:
            return self.suit == other_suit and self.rank == other_rank


    def __str__(self):
        """
        Creates a human-friendly string representation of this object, and
        returns it.  For example, if rank==1 and suit==CLUBS then "ace of clubs"
        is returned.
        """
        if self.rank in self.RANK_NAMES:
            rank_name = self.RANK_NAMES[self.rank]
        else:
            rank_name = self.rank

        if self.suit in self.SUIT_NAMES:
            suit_name = self.SUIT_NAMES[self.suit]
        else:
            suit_name = self.suit

        return "{} of {}".format(rank_name, suit_name)


    def __repr__(self):
        """
        Creates a Python-friendly string representation of this object, and
        returns it.  For example, if rank==1 and suit==CLUBS then Card(clubs, 1)
        is returned.
        """
        return "Card({!r}, {!r})".format(self.suit, self.rank)

################################################################################

class Deck(list):
    """
    A deck of cards.  This class is a specialization of the built-in list type
    for holding the cards in a deck of cards.  Each element of the list must be
    a Card object.  The "bottom" of the deck is index 0.  Instances of this
    class are *not* thread-safe; however, this class has a "lock" attribute that
    can be acquired by multiple threads to safely perform concurrent access.
    This class also implements the context manager protocol to better implement
    acquiring the lock with the "with" statement.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of this class.
        All positional and keyword arguments are passed verbatim to the
        constructor of the superclass.
        If no positional or keyword arguments are given, then the list is
        initialized by reset().
        """
        super(Deck, self).__init__(*args, **kwargs)
        if not args and not kwargs:
            self.reset()
        self.lock = threading.RLock()


    def reset(self):
        """
        Resets the deck back to the "factory" state.
        All cards in this deck will be discarded and the deck will be
        re-populated with the 13 different-ranked cards of each suit in
        ascending order.
        """
        self[:] = self.iter_cards()


    def draw(self):
        """
        Draws a card from this deck.
        The Card object at the highest index of this list is removed and
        returned.  IndexError is raised if this list is empty.
        """
        return self.pop()


    def shuffle(self):
        """
        Shuffles the cards in this deck using complete randomness.
        """
        random.shuffle(self)


    def shuffle_3waycut(self):
        """
        Shuffles the cards in this deck using a "3-way cut" style.
        This is done by dividing the deck into 3 piles of random size and then
        recombining them in a random order.
        Raises AssertionError if len(self) is less than 3, because in this
        scenario the 3-way-cut is not possible.
        """
        assert len(self) >= 3, "len(self)=={}".format(len(self))
        split_index_1 = random.randint(0, len(self) - 2)
        split_index_2 = random.randint(split_index_1, len(self) - 1)
        chunk1 = self[:split_index_1]
        chunk2 = self[split_index_1:split_index_2]
        chunk3 = self[split_index_2:]
        chunks = [chunk1, chunk2, chunk3]
        random.shuffle(chunks)
        del self[:]
        for chunk in chunks:
            self.extend(chunk)


    def shuffle_riffle(self):
        """
        Shuffles the cards in the deck using the "riffle" technique.
        According to Wikipedia, riffle is a shuffling technique "in which half
        of the deck is held in each hand with the thumbs inward, then cards are
        released by the thumbs so that they fall to the table interleaved.
        """
        num_cards = len(self)

        if num_cards <= 1:
            return # nothing to do if deck is empty or only has 1 card

        mid = num_cards / 2
        leeway = num_cards / 10
        mid_left = mid - leeway
        if mid_left < 1:
            mid_left = 1
        mid_right = mid + leeway
        if mid_right > num_cards - 1:
            mid_right = num_cards - 1

        split_index = random.randint(mid_left, mid_right)
        left = self[:split_index]
        right = self[split_index:]

        del self[:]
        while left or right:
            size_difference = len(right) - len(left)

            if size_difference > -5:
                n = random.randint(1, 3)
                while right and n > 0:
                    self.append(right.pop(0))
                    n -= 1

            if size_difference < 5:
                n = random.randint(1, 3)
                while left and n > 0:
                    self.append(left.pop(0))
                    n -= 1


    @staticmethod
    def iter_cards():
        """
        A generator function that yields each of the unique cards in a 52-card
        deck as Card objects.
        """
        for suit in (Card.CLUB, Card.DIAMOND, Card.HEART, Card.SPADE):
            for rank in (13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1):
                yield Card(suit, rank)


    def __enter__(self):
        """
        Acquire the lock when we are "entered" with the "with" statement.
        """
        self.lock.acquire()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        """
        Release the lock when the "with" statement exits.
        """
        self.lock.release()

################################################################################

class MyHttpServer(BaseHTTPServer.HTTPServer):
    """
    The HTTP server that provides the user interface for this application.
    """

    def __init__(self, tcp_port):
        """
        Initializes a new instance of this class.
        *tcp_port* must be an integer whose value is the TCP port to which the
        HTTP server will bind and to which it will listen for and handle
        requests.
        """
        self.deck = Deck()
        self.discard = None
        self.message = None
        address = ("", tcp_port)
        BaseHTTPServer.HTTPServer.__init__(self, server_address=address,
            RequestHandlerClass=self.MyRequestHandler)


    class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        """
        The HTTP request handler used by run().
        """

        def do_GET(self):
            """
            Handles GET requests.
            """
            parsed_url = urlparse.urlparse(self.path)
            path = parsed_url.path

            if path == "/":
                self.do_send_html()
            elif path == "/draw":
                self.do_draw()
            elif path == "/reset":
                self.do_reset()
            elif path == "/shuffle_random":
                self.do_shuffle_random()
            elif path == "/shuffle_3waycut":
                self.do_shuffle_3waycut()
            elif path == "/shuffle_riffle":
                self.do_shuffle_riffle()
            elif path == "/find":
                self.do_find()
            elif path == "/findimpl":
                self.do_findimpl()
            elif path == "/shutdown":
                self.do_shutdown()
            elif path.startswith("/res/"):
                res_filename = path[5:]
                self.do_resource(res_filename)
            else:
                self.send_error(httplib.NOT_FOUND)


        def do_POST(self):
            """
            Handles POST requests, by simply calling self.do_GET().
            """
            return self.do_GET()


        def do_send_html(self):
            """
            Responds to the default request.
            """
            self.send_response(httplib.OK)

            self.send_header("Content-Type", "text/html; charset=UTF-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.write("<html>")
            self.write("<head>")
            self.write('<script type="text/javascript">')
            self.write(self.DEFAULT_JAVASCRIPT)
            self.write("</script>")
            self.write("<title>", newline=False)
            self.write_escaped("Cards")
            self.write("</title>")
            self.write("</head>")
            self.write('<body>')
            self.write('<h2>Deck of Cards</h2>')
            self.write('<p>Click on the deck to draw a card</p>')

            with self.server.deck:
                deck_filename = self.get_deck_filename()
                discard_filename = self.get_discard_filename()
                cards_remaining_html = self.get_cards_remaining_html()
                message = self.server.message
                self.server.message = None

            self.write("<div>")
            self.write('<img id="deck" src="{}" '
                'onclick=\'sendRequest("draw")\' width="212" height="287" />'
                .format(deck_filename))
            self.write('<img id="discard" src="{}" '
                'width="212" height="287" />'
                .format(discard_filename))
            self.write("</div>")

            self.write('<div id="cards_remaining">')
            self.write(cards_remaining_html)
            self.write("</div>")
            self.write('<div id="message">')
            if message:
                self.write_escaped(message)
            else:
                self.write("&nbsp;")
            self.write("</div>")

            self.write('<form name="find" action="find" />')

            self.write('<input type="button" value="Reset" '
                'onclick=\'sendRequest("reset")\'/><br/>')
            self.write('<input type="button" value="Shuffle (Random)" '
                'onclick=\'sendRequest("shuffle_random")\'/><br/>')
            self.write('<input type="button" value="Shuffle (3-way-cut)" '
                'onclick=\'sendRequest("shuffle_3waycut")\'/><br/>')
            self.write('<input type="button" value="Shuffle (Riffle)" '
                'onclick=\'sendRequest("shuffle_riffle")\'/><br/>')
            self.write('<input type="submit" value="Find Card" '
                'onclick=\'document.forms["find"].submit()\' /><br/>')
            self.write('<input type="button" value="Shutdown" '
                'onclick=\'sendRequest("shutdown")\'/><br/>')

            self.write("</body>")
            self.write("</html>")


        def do_find(self):
            """
            Responds to the "find" request.
            """
            self.send_response(httplib.OK)

            self.send_header("Content-Type", "text/html; charset=UTF-8")
            self.send_header("Cache-Control", "public")
            self.end_headers()
            self.write("<html>")
            self.write("<head>")
            self.write("<title>", newline=False)
            self.write_escaped("Find a Card")
            self.write("</title>")
            self.write("</head>")
            self.write('<body>')
            self.write("<h2>Find a Card</h2>")

            self.write_escaped("Click on the card to find:")
            self.write('<form action="findimpl" method="post">')
            deck = Deck()
            for (index, card) in enumerate(reversed(deck)):
                if index % 13 == 0:
                    self.write("<div/>")
                filename = self.get_card_filename(card)
                self.write('<input type="image" width="71" height="96" '
                    'src="{}" name="{}" />'.format(filename, card))
            self.write("</form>")

            self.write("</body>")
            self.write("</html>")


        def do_findimpl(self):
            """
            Responds to the "findimpl" request.
            """
            self.send_response(httplib.OK)
            self.send_header("Content-Type", "text/html; charset=UTF-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            # parse the key/value pairs from the POST message
            content_length_str = self.headers["content-length"]
            content_length = int(content_length_str)
            line = self.rfile.read(content_length)
            params = urlparse.parse_qs(line, keep_blank_values=True)

            # find the card and store the message
            (card_index, card) = self.find_card(params)
            if card is None:
                message = None
            elif card_index < 0:
                message = "{} not found in deck".format(card)
            else:
                message = "{} found in deck at position {}".format(card,
                    card_index)

            with self.server.deck:
                self.server.message = message

            # send a quick JavaScript trick to redirect back to the main page
            self.write("<html>")
            self.write('<body onload=\'document.forms["redirect"].submit()\'>')
            self.write('<form name="redirect" action="/">')
            self.write("</form>")
            self.write("</body>")
            self.write("</html>")



        def do_shutdown(self):
            """
            Responds to a request to shut down the HTTP server.
            """
            self.send_ajax_response(message="HTTP server shut down")

            # must call shutdown in a separate thread to avoid deadlock
            threading.Thread(target=self.server.shutdown).start()


        def do_draw(self):
            """
            Responds to a request to draw a card.
            """
            deck = self.server.deck
            with deck:
                if len(deck) > 0:
                    discard = deck.draw()
                    self.server.discard = discard
                self.send_ajax_response()


        def do_reset(self):
            """
            Responds to a request to reset the deck.
            """
            deck = self.server.deck
            with deck:
                deck.reset()
                deck.shuffle()
                self.server.discard = None
                self.send_ajax_response("Deck has been reset and shuffled")


        def do_shuffle_random(self):
            """
            Responds to a request to do a "random" shuffle.
            """
            deck = self.server.deck
            with deck:
                deck.shuffle()
                self.send_ajax_response("Shuffled using \"random\" algorithm")


        def do_shuffle_3waycut(self):
            """
            Responds to a request to do a "3-way-cut" shuffle.
            """
            deck = self.server.deck
            with deck:
                deck.shuffle_3waycut()
                self.send_ajax_response("Shuffled using \"3-way-cut\" algorithm")


        def do_shuffle_riffle(self):
            """
            Responds to a request to do a "riffle" shuffle.
            """
            deck = self.server.deck
            with deck:
                deck.shuffle_riffle()
                self.send_ajax_response("Shuffled using \"Riffle\" algorithm")


        def do_resource(self, filename):
            """
            Responds to a request to serve a file from the "res" directory.
            *filename* must be a string whose value is the path of the file
            whose contents to respond with.
            """
            path = os.path.join("res", filename)
            try:
                f = open(path, "rb")
            except (IOError, OSError):
                self.send_error(httplib.NOT_FOUND)
            else:
                self.send_response(httplib.OK)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Cache-Control", "public")
                self.end_headers()
                while True:
                    data = f.read(16384)
                    if not data:
                        break
                    self.wfile.write(data)


        def find_card(self, params):
            """
            Finds a card in the deck and returns its index.
            *params* must be a dict that was specified to do_send_html().
            """
            deck = Deck()
            card = None
            for cur_card in deck:
                key = "{}.x".format(cur_card)
                if key in params:
                    card = cur_card
                    break

            deck = self.server.deck
            with deck:
                if not card:
                    index = -1
                else:
                    try:
                        index = deck.index(card)
                        index = len(deck) - index
                    except ValueError:
                        index = -1

            return (index, card)


        def get_discard_filename(self):
            """
            Returns the filename of the card image in the discard pile.
            """
            with self.server.deck:
                discard = self.server.discard
            if discard is None:
                filename = "res/deck_blank.png"
            else:
                filename = self.get_card_filename(discard)
            return filename


        def get_cards_remaining_html(self):
            """
            Returns a string whose value is valid HTML that specifies how many
            cards are left in the deck.
            """
            with self.server.deck:
                num_cards = len(self.server.deck)
            return "Cards Remaining: {}".format(num_cards)


        def get_deck_filename(self):
            """
            Returns the filename of the deck image.
            """
            with self.server.deck:
                deck_len = len(self.server.deck)
            filename = "res/deck.png" if deck_len else "res/deck_empty.png"
            return filename


        @staticmethod
        def get_card_filename(card):
            """
            Returns the filename of the resource image for the given card.
            *card* must be a Card object whose image filename to return.
            Returns a string whose value is the path of the image to embed in
            the HTML document for the given card.
            """
            suit = card.suit
            if suit == Card.DIAMOND:
                suit_id = "diamonds"
            elif suit == Card.HEART:
                suit_id = "hearts"
            elif suit == Card.CLUB:
                suit_id = "clubs"
            elif suit == Card.SPADE:
                suit_id = "spades"
            else:
                suit_id = "{}".format(suit)

            rank = card.rank
            if rank == 1:
                rank_id = "ace"
            elif rank == 11:
                rank_id = "jack"
            elif rank == 12:
                rank_id = "queen"
            elif rank == 13:
                rank_id = "king"
            else:
                rank_id = "{}".format(rank)

            filename = "res/card_{}_{}.png".format(suit_id, rank_id)
            return filename


        def send_ajax_response(self, message=None):
            """
            Writes the state of the application for XMLHttpRequest responses,
            including the HTTP response code, HTTP headers, and body.
            *message* must be a string whose value is a message to display on
            the client; may be None (the default) to not display a message.
            """
            self.send_response(httplib.OK)
            self.send_header("Content-Type", "text/xml; charset=UTF-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            with self.server.deck:
                deck_filename = self.get_deck_filename()
                discard_filename = self.get_discard_filename()
                cards_remaining_html = self.get_cards_remaining_html()

            self.write("<state>")
            self.write("<deck-filename>{0}</deck-filename>"
                .format(deck_filename))
            self.write("<discard-filename>{0}</discard-filename>"
                .format(discard_filename))
            self.write("<cards-remaining>{0}</cards-remaining>"
                .format(cards_remaining_html))
            if message is not None:
                self.write("<message>{}</message>".format(message))
            self.write("</state>")


        def write(self, s, newline=True):
            """
            Writes a string to self.wfile, encoding it in UTF-8 first.
            *s* must be a string whose UTF-8 encoding to write to the output
            file.
            *newline* is evaluated as a boolean; if it evaluates to True
            (the default) then a \n character is written after the given string;
            if False, then no newline character is printed.
            """
            s_encoded = s.encode("UTF-8")
            self.wfile.write(s_encoded)
            if newline:
                self.wfile.write("\n".encode("UTF-8"))


        def write_escaped(self, s, newline=True):
            """
            Writes a string to self.wfile, first escaping any special HTML
            characters.  After escaping HTMl characters, this method invokes
            self.write() with the resulting string and the given newline.
            """
            s = s.replace("&", "&amp;")
            s = s.replace("'", "&apos;")
            s = s.replace('"', "&quot;")
            s = s.replace("<", "&lt;")
            s = s.replace(">", "&gt;")
            self.write(s, newline=newline)


        DEFAULT_JAVASCRIPT = ur"""
            function sendRequest(action) {
                var request = new XMLHttpRequest();

                request.onreadystatechange = function handleOnReadyStateChange() {
                    if (request.readyState == 4) {
                        var doc = request.responseXML;

                        var messageDivElement = document.getElementById("message");
                        messageDivElement.innerHTML = "&nbsp;";
                        var messageElements = doc.getElementsByTagName("message");
                        for (var i=0; i<messageElements.length; i++) {
                            var messageElement = messageElements[i];
                            var message = messageElement.childNodes[0].nodeValue
                            messageDivElement.innerHTML = message;
                        }

                        var deckFilenameElements = doc.getElementsByTagName("deck-filename");
                        if (deckFilenameElements.length > 0) {
                            var deckFilenameElement = deckFilenameElements[0];
                            var deckFilename = deckFilenameElement.childNodes[0].nodeValue;
                            var deckElement = document.getElementById("deck");
                            deckElement.setAttribute("src", deckFilename);
                        }

                        var discardFilenameElements = doc.getElementsByTagName("discard-filename");
                        if (discardFilenameElements.length > 0) {
                            var discardFilenameElement = discardFilenameElements[0];
                            var discardFilename = discardFilenameElement.childNodes[0].nodeValue;
                            var discardElement = document.getElementById("discard");
                            discardElement.setAttribute("src", discardFilename);
                        }

                        var cardsRemainingElements = doc.getElementsByTagName("cards-remaining");
                        if (cardsRemainingElements.length > 0) {
                            var cardsRemainingElement = cardsRemainingElements[0];
                            var cardsRemainingTxt = cardsRemainingElement.childNodes[0].nodeValue;
                            var divElement = document.getElementById("cards_remaining");
                            divElement.innerHTML = cardsRemainingTxt
                        }
                    }
                }

                // to prevent client-side caching (such as in Internet Explorer)
                // use POST instead of GET and send some ever-changing data
                request.open("POST", action, false);
                request.send("cache-killer=" + new Date());
            }
        """

################################################################################

class MyArgumentParser(argparse.ArgumentParser):
    """
    The command-line argument parser for the cards application.
    """

    USAGE = "%(prog)s [options]"

    def __init__(self, prog):
        """
        Initializes a new instance of this class.
        """
        argparse.ArgumentParser.__init__(self, prog=prog, usage=self.USAGE)
        self._add_arguments()


    def _add_arguments(self):
        """
        Adds the arguments to this ArgumentParser.
        This method is called by __init__() and is not normally called from
        any other context.
        """

        self.add_argument("-p", "--port",
            type=int,
            default=8080,
            help="""The HTTP port for the HTTP server to bind to.
            (default: %(default)i)"""
        )


    def parse_args(self, args):
        """
        Parses the given arguments.
        *args* must be an iterable of strings, the arguments to parse.
        Returns a newly-created CardsApplication object if parsing is
        successful.  Otherwise, raises self.Error if parsing fails.
        """
        args = tuple(args) # create a local copy for safety
        namespace = self.MyNamespace()
        argparse.ArgumentParser.parse_args(self, args=args, namespace=namespace)
        app = namespace.create_application()
        return app


    def exit(self, status=EXIT_SUCCESS, message=None):
        """
        Raises self.Error to exit the program.
        *status* must be an integer whose value is the exit code to specify
        in the raised exception (default: EXIT_SUCCESS).
        *message* must be a string whose value is a message for the raised
        exception (default: None).
        This method overrides the one defined in the superclass to raise an
        exception instead of calling sys.exit().
        """
        raise self.Error(message=message, exit_code=status)


    def error(self, message):
        """
        Shorthand for self.exit(status=EXIT_ARGS, message=message).
        This method overrides the one defined in the superclass to raise an
        exception instead of ultimately calling sys.exit().
        """
        self.exit(status=EXIT_ARGS, message=message)


    class MyNamespace(argparse.Namespace):
        """
        The namespace used by parse_args() when parsing args.
        """

        def create_application(self):
            """
            Creates and returns a new instance of CardsApplication based on this
            object's attributes.
            This method is intended to be called after parsing the arguments
            in parse_args().
            """
            http_server_port = self.port
            return CardsApplication(http_server_port)


    class Error(Exception):
        """
        Exception raised if an error occurs parsing the arguments.
        """

        def __init__(self, message, exit_code):
            """
            Initializes a new instance of this class.
            *message* must be a string whose value is a message to give to the
            constructor of the superclass.
            *exit_code* must be an integer whose value is an appropriate exit
            code to give to sys.exit() as a result of this exception.
            """
            Exception.__init__(self, message)
            self.exit_code = exit_code

################################################################################

if __name__ == "__main__":
    try:
        retval = main()
    except KeyboardInterrupt:
        # gracefully handle CTRL+C, well, more gracefully than a stack trace
        print("ERROR: application terminated by keyboard interrupt",
            file=sys.stdout)
        retval = EXIT_ERROR
    sys.exit(retval)
