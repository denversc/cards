Cards
By: Denver Coneybeare
April 03, 2012

This application lets you perform some very simple operations on a deck of cards.
To run the application, you must have Python 2.7 installed and your PATH
environment variable must be set up so that you can run the "python" command.

To run the application, run:

    python cards.py

This will start an HTTP sever on port 8080.  Then, open a web browser and
browse to http://localhost:8080.  You need to have JavaScript enabled in the
browser.

To use a different TCP port, use the --port argument; for example, to use port
9999 instead of 8080, run:

    python cards.py --port 9999

You can also specify -h or --help for a detailed help listing.

There are also unit tests available in the test_XXX.py files. To run the
complete suite of unit tests, run:

    python -m unittest discover

You should see output like this:

    C:\>python.exe -m unittest discover
    .........................................................................
    ----------------------------------------------------------------------
    Ran 73 tests in 0.032s

    OK
