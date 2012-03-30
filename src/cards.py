################################################################################
# cards.py
# By: Denver Coneybeare
# March 27, 2012
################################################################################

from __future__ import print_function

import argparse
import BaseHTTPServer
import httplib
import random
import sys
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
        print("Starting HTTP server on port {}".format(self.http_server_port))
        http_server.run()


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
        return "Card({}, {})".format(self.suit, self.rank)

################################################################################

class Deck(list):
    """
    A deck of cards.  This class is a specialization of the built-in list type
    for holding the cards in a deck of cards.  Each element of the list must be
    a Card object.  The "bottom" of the deck is index 0.  Instances of this
    class are *not* thread-safe.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of this class.
        All positional and keyword arguments are passed verbatim to the
        constructor of the superclass.
        If no positional or keyword arguments are given, then the list is
        initialized by reset().
        """
        super(list, self).__init__(*args, **kwargs)
        if not args and not kwargs:
            self.reset()


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

    @staticmethod
    def iter_cards():
        """
        A generator function that yields each of the unique cards in a 52-card
        deck as Card objects.
        """
        for suit in (Card.CLUB, Card.DIAMOND, Card.HEART, Card.SPADE):
            for rank in xrange(1, 14):
                yield Card(suit, rank)


################################################################################

class MyHttpServer():
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
        self.tcp_port = tcp_port


    def run(self):
        """
        Starts and runs the HTTP server.
        This method blocks until the HTTP server shuts down.
        """
        address = ("", self.tcp_port)
        server = BaseHTTPServer.HTTPServer(server_address=address,
            RequestHandlerClass=self.MyRequestHandler)
        server.serve_forever()


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
                self.send_response(httplib.OK)
                self.respond_default()
            elif path == "/stop":
                self.send_response(httplib.OK)
                self.respond_stop()
            else:
                self.send_error(httplib.NOT_FOUND)


        def respond_default(self):
            """
            Responds to the default request.
            This method must be invoked after send_response() but before
            end_headers().
            """
            self.send_header("Content-Type", "text/html; charset=UTF-8")
            self.end_headers()
            self.write("<html>")
            self.write("<head>")
            self.write("<title>", newline=False)
            self.write_escaped("Cards")
            self.write("</title>")
            self.write("</head>")
            self.write("<body>")

            for key in sorted(dir(self)):
                value = getattr(self, key)
                self.write_escaped("{}: {}".format(key, value))
                self.write("<br/>")

            self.write("</body>")
            self.write("</html>")


        def respond_stop(self):
            """
            Responds to a request to shut down the HTTP server.
            This method must be invoked after send_response() but before
            end_headers().
            """
            self.send_header("Content-Type", "text/plain; charset=UTF-8")
            self.end_headers()
            self.write("Shutting down HTTP server...")
            self.wfile.flush()
            self.server.shutdown()


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
