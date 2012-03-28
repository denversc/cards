################################################################################
# cards.py
# By: Denver Coneybeare
# March 27, 2012
################################################################################

from __future__ import print_function

import argparse
import sys

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
    else:
        args = tuple(args) # create a local copy

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

    def __init__(self, http_port=8080):
        self.http_port = http_port


    def run(self):
        print("HTTP Port: {}".format(self.http_port))

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
            http_port = self.port
            return CardsApplication(http_port)


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
