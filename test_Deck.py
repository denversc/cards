import sys
import threading
import unittest

from cards import Card
from cards import Deck
from multiprocessing import RLock

################################################################################

class Test__init__(unittest.TestCase):
    """
    Unit tests for Deck.__init__()
    """

    def test_noargs(self):
        # if no args are given then the deck should be initialized to 52 cards
        x = Deck()
        self.assertEqual(len(x), 52)
        expected_elements = list(Deck.iter_cards())
        self.assertListEqual(x, expected_elements)
        rlock_type = type(threading.RLock())
        self.assertIs(type(x.lock), rlock_type)

    def test_1arg(self):
        # if no args are given then the deck should be initialized to 52 cards
        x = Deck([Card(Card.SPADE, 2), Card(Card.DIAMOND, 3)])
        self.assertEqual(len(x), 2)
        expected_elements = [Card(Card.SPADE, 2), Card(Card.DIAMOND, 3)]
        self.assertListEqual(x, expected_elements)
        rlock_type = type(threading.RLock())
        self.assertIs(type(x.lock), rlock_type)

################################################################################

class Test_reset(unittest.TestCase):
    """
    Unit tests for Deck.reset()
    """

    def test_empty_deck(self):
        x = Deck()
        x[:] = []
        self.do_test_reset(x)

    def test_full_deck(self):
        x = Deck()
        self.do_test_reset(x)

    def test_partial_deck(self):
        x = Deck()
        x[:] = x[:len(x)/2]
        self.do_test_reset(x)

    def test_extra_deck(self):
        x = Deck()
        x[:] = x * 2
        self.do_test_reset(x)

    def do_test_reset(self, deck):
        deck.reset()
        expected = list(Deck.iter_cards())
        self.assertListEqual(deck, expected)

################################################################################

class Test_pop(unittest.TestCase):
    """
    Unit tests for Deck.pop()
    """

    def test_empty_deck(self):
        x = Deck()
        x[:] = []
        with self.assertRaises(IndexError):
            x.draw()
        self.assertListEqual(x, [])

    def test_deck_length1(self):
        x = Deck()
        card = Card("a", "b")
        x[:] = [card]
        actual = x.draw()
        self.assertEqual(actual, card)
        self.assertListEqual(x, [])

    def test_deck_length2(self):
        x = Deck()
        card1 = Card("a", "b")
        card2 = Card("c", "d")
        x[:] = [card1, card2]
        actual = x.draw()
        self.assertEqual(actual, card2)
        self.assertListEqual(x, [card1])

    def test_deck_full(self):
        x = Deck()
        x.reset()
        expected_state_after = x[:-1]
        expected_card = x[-1]
        actual_card = x.draw()
        self.assertEqual(actual_card, expected_card)
        self.assertListEqual(x, expected_state_after)

################################################################################

class Test_shuffle(unittest.TestCase):
    """
    Unit tests for Deck.shuffle()
    """

    def test_full(self):
        x = Deck()
        x.reset()
        before = list(x)
        x.shuffle()
        after = list(x)
        self.assertTrue(before != after)
        self.assertSetEqual(set(x), set(before))

    def test_empty(self):
        x = Deck()
        x[:] = []
        x.shuffle()
        self.assertEqual(x, [])

    def test_1element(self):
        card = Card("a", "b")
        x = Deck([card])
        x.shuffle()
        self.assertEqual(x, [card])

    def test_2elements(self):
        card1 = Card("a", "b")
        card2 = Card("c", "d")
        x = Deck([card1, card2])
        x.shuffle()
        # NOTE: don't check order because it has a 50% chance of not changing
        self.assertSetEqual(set(x), set([card1, card2]))

################################################################################

class Test_shuffle_3waycut(unittest.TestCase):
    """
    Unit tests for Deck.shuffle_3waycut()
    """

    # Allow long diffs when tests fail
    maxDiff = None

    def test_empty(self):
        x = Deck()
        x[:] = []
        x.shuffle_3waycut()
        self.assertEqual(x, [])

    def test_1element(self):
        card = Card("a", "b")
        x = Deck([card])
        x.shuffle_3waycut()
        self.assertEqual(x, [card])

    def test_2elements(self):
        card1 = Card("a", "b")
        card2 = Card("c", "d")
        x = Deck([card1, card2])
        x.shuffle_3waycut()
        self.assertSetEqual(set(x), set([card1, card2]))

    def test_3elements(self):
        card1 = Card("a", "b")
        card2 = Card("c", "d")
        card3 = Card("e", "f")
        x = Deck([card1, card2, card3])
        x.shuffle_3waycut()
        self.assertSetEqual(set(x), set([card1, card2, card3]))

    def test_full(self):
        x = Deck()
        split_1 = 20
        split_2 = 30
        chunk1 = x[:split_1]
        chunk2 = x[split_1:split_2]
        chunk3 = x[split_2:]
        before = set(x)
        x.shuffle_3waycut(split_index_1=split_1, split_index_2=split_2)
        after = set(x)
        self.assertSetEqual(before, after)

        # make sure that each chunk is preserved in the deck
        chunks = [chunk1, chunk2, chunk3]
        for chunk in chunks:
            index = x.index(chunk[0])
            sublist = x[index:index+len(chunk)]
            self.assertListEqual(sublist, chunk)

################################################################################

class Test_shuffle_riffle(unittest.TestCase):
    """
    Unit tests for Deck.shuffle_riffle()
    Riffle is fairly random, so there is not much that we can do to test the
    correctness of the algorithm; so we mostly just make sure that it doesn't
    blow up in the boundary cases and that no elements are added or removed.
    """

    # Allow long diffs when tests fail
    maxDiff = None

    def test_empty(self):
        x = Deck()
        x[:] = []
        x.shuffle_riffle()
        self.assertEqual(x, [])

    def test_1element(self):
        card = Card("a", "b")
        x = Deck([card])
        x.shuffle_riffle()
        self.assertEqual(x, [card])

    def test_2elements(self):
        card1 = Card("a", "b")
        card2 = Card("c", "d")
        x = Deck([card1, card2])
        x.shuffle_riffle()
        self.assertSetEqual(set(x), set([card1, card2]))

    def test_3elements(self):
        card1 = Card("a", "b")
        card2 = Card("c", "d")
        card3 = Card("e", "f")
        x = Deck([card1, card2, card3])
        x.shuffle_riffle()
        self.assertSetEqual(set(x), set([card1, card2, card3]))

    def test_full(self):
        x = Deck()
        before = set(x)
        after = set(x)
        x.shuffle_riffle()
        self.assertSetEqual(before, after)

################################################################################

class Test_iter_cards(unittest.TestCase):
    """
    Unit tests for Deck.iter_cards()
    """

    def test_next(self):
        x = Deck.iter_cards()
        result = next(x) # make sure it is actually iterable
        self.assertIsNotNone(result)

    def test_count(self):
        x = Deck.iter_cards()
        count = 0
        for unused in x:
            count += 1
        self.assertEqual(count, 52)

    def test_type(self):
        x = Deck.iter_cards()
        for card in x:
            self.assertIsInstance(card, Card)

    def test_values(self):
        suits_left = set([Card.SPADE, Card.HEART, Card.DIAMOND, Card.CLUB])
        x = Deck.iter_cards()
        while suits_left:
            card = next(x)
            self.assertIn(card.suit, suits_left)
            suits_left.remove(card.suit)
            expected_suit = card.suit
            self.assertEqual(card.rank, 13)
            for rank in (12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1):
                card = next(x)
                self.assertEqual(card.rank, rank)
                self.assertEqual(card.suit, expected_suit)
        with self.assertRaises(StopIteration):
            next(x)

################################################################################

class Test_context_manager(unittest.TestCase):
    """
    Unit tests for Deck.__enter__() and __exit__()
    """

    def setUp(self):
        self.acquire_func = MockFunction()
        self.release_func = MockFunction()
        self.deck = Deck()
        self.deck.lock.acquire = self.acquire_func
        self.deck.lock.release = self.release_func

    def test(self):
        with self.deck as cm:
            self.assertIs(cm, self.deck)
            self.assertListEqual(self.acquire_func.invocations, [((), {})])
            self.assertListEqual(self.release_func.invocations, [])
        self.assertListEqual(self.acquire_func.invocations, [((), {})])
        self.assertListEqual(self.release_func.invocations, [((), {})])

    def test_enter(self):
        result = self.deck.__enter__()
        self.assertIs(result, self.deck)
        self.assertListEqual(self.acquire_func.invocations, [((), {})])

    def test_exit_noexception(self):
        result = self.deck.__exit__(None, None, None)
        self.assertIsNone(result)
        self.assertListEqual(self.release_func.invocations, [((), {})])

    def test_exit_exception(self):
        try:
            raise Exception()
        except:
            (exc_type, exc_value, traceback) = sys.exc_info()
        result = self.deck.__exit__(exc_type, exc_value, traceback)
        self.assertIsNone(result)
        self.assertListEqual(self.release_func.invocations, [((), {})])

################################################################################

class MockFunction(object):

    def __init__(self):
        self.invocations = []

    def __call__(self, *args, **kwargs):
        self.invocations.append((args, kwargs))
