import copy
import unittest

from cards import Card

################################################################################

class TestConstants(unittest.TestCase):
    """
    Unit tests for the class-level attributes of Card.
    """

    def test_SPADE(self):
        self.assertEqual(Card.SPADE, "spade")

    def test_HEART(self):
        self.assertEqual(Card.HEART, "heart")

    def test_CLUB(self):
        self.assertEqual(Card.CLUB, "club")

    def test_DIAMOND(self):
        self.assertEqual(Card.DIAMOND, "diamond")

    def test_RANK_NAMES(self):
        expected = {
            1: "ace",
            11: "jack",
            12: "queen",
            13: "king",
        }
        self.assertDictEqual(Card.RANK_NAMES, expected)

    def test_SUIT_NAMES(self):
        expected = {
            "spade": "spades",
            "heart": "hearts",
            "club": "clubs",
            "diamond": "diamonds",
        }
        self.assertDictEqual(Card.SUIT_NAMES, expected)

################################################################################

class Test__init__(unittest.TestCase):
    """
    Unit tests for Card.__init__()
    """

    def test_positional_arguments(self):
        suit = object()
        rank = object()
        x = Card(suit, rank)
        self.assertIs(x.suit, suit)
        self.assertIs(x.rank, rank)

    def test_keyword_arguments(self):
        suit = object()
        rank = object()
        x = Card(suit=suit, rank=rank)
        self.assertIs(x.suit, suit)
        self.assertIs(x.rank, rank)

################################################################################

class Test__eq__(unittest.TestCase):
    """
    Unit tests for Card.__eq__()
    """

    def test_identical_shallow(self):
        x1 = Card("a", "b")
        x2 = copy.copy(x1)
        self.assertTrue(x1 == x2)

    def test_identical_deep(self):
        x1 = Card("a", "b")
        x2 = copy.deepcopy(x1)
        self.assertTrue(x1 == x2)

    def test_different_suit(self):
        x1 = Card("a", "b")
        x2 = Card("c", "b")
        self.assertFalse(x1 == x2)

    def test_different_rank(self):
        x1 = Card("a", "b")
        x2 = Card("a", "c")
        self.assertFalse(x1 == x2)

    def test_different_suit_and_rank(self):
        x1 = Card("a", "b")
        x2 = Card("c", "d")
        self.assertFalse(x1 == x2)

    def test_missing_suit(self):
        x1 = Card("a", "b")
        x2 = Card("a", "b")
        del x2.suit
        self.assertFalse(x1 == x2)

    def test_missing_rank(self):
        x1 = Card("a", "b")
        x2 = Card("a", "b")
        del x2.rank
        self.assertFalse(x1 == x2)

    def test_missing_suit_and_rank(self):
        x1 = Card("a", "b")
        x2 = Card("a", "b")
        del x2.suit
        del x2.rank
        self.assertFalse(x1 == x2)

    def test_None(self):
        x = Card("a", "b")
        self.assertFalse(x == None)

################################################################################

class Test__str__(unittest.TestCase):
    """
    Unit tests for Card.__str__()
    """

    def test_invalid_suit_and_rank(self):
        x = Card("a", "b")
        actual = str(x)
        self.assertEqual(actual, "b of a")

    def test_invalid_suit(self):
        x = Card("a", 2)
        actual = str(x)
        self.assertEqual(actual, "2 of a")

    def test_invalid_rank(self):
        x = Card(Card.SPADE, -50)
        actual = str(x)
        self.assertEqual(actual, "-50 of spades")

    def test_spades(self):
        x = Card(Card.SPADE, 2)
        actual = str(x)
        self.assertEqual(actual, "2 of spades")

    def test_diamonds(self):
        x = Card(Card.DIAMOND, 2)
        actual = str(x)
        self.assertEqual(actual, "2 of diamonds")

    def test_hearts(self):
        x = Card(Card.HEART, 2)
        actual = str(x)
        self.assertEqual(actual, "2 of hearts")

    def test_clubs(self):
        x = Card(Card.CLUB, 2)
        actual = str(x)
        self.assertEqual(actual, "2 of clubs")

    def test_ace(self):
        x = Card(Card.CLUB, 1)
        actual = str(x)
        self.assertEqual(actual, "ace of clubs")

    def test_jack(self):
        x = Card(Card.CLUB, 11)
        actual = str(x)
        self.assertEqual(actual, "jack of clubs")

    def test_queen(self):
        x = Card(Card.CLUB, 12)
        actual = str(x)
        self.assertEqual(actual, "queen of clubs")

    def test_king(self):
        x = Card(Card.CLUB, 13)
        actual = str(x)
        self.assertEqual(actual, "king of clubs")

    def test_numeric_ranks(self):
        for rank in (2, 3, 4, 5, 6, 7, 8, 9, 10):
            x = Card(Card.CLUB, rank)
            actual = str(x)
            expected = "{} of clubs".format(rank)
            self.assertEqual(actual, expected)

################################################################################

class Test__repr__(unittest.TestCase):
    """
    Unit tests for Card.__repr__()
    """

    def test_invalid_suit_and_rank(self):
        x = Card("a", "b")
        actual = repr(x)
        self.assertEqual(actual, "Card('a', 'b')")

    def test_invalid_suit(self):
        x = Card("a", 2)
        actual = repr(x)
        self.assertEqual(actual, "Card('a', 2)")

    def test_invalid_rank(self):
        x = Card(Card.SPADE, -50)
        actual = repr(x)
        self.assertEqual(actual, "Card('spade', -50)")

    def test_spades(self):
        x = Card(Card.SPADE, 2)
        actual = repr(x)
        self.assertEqual(actual, "Card('spade', 2)")

    def test_diamonds(self):
        x = Card(Card.DIAMOND, 2)
        actual = repr(x)
        self.assertEqual(actual, "Card('diamond', 2)")

    def test_hearts(self):
        x = Card(Card.HEART, 2)
        actual = repr(x)
        self.assertEqual(actual, "Card('heart', 2)")

    def test_clubs(self):
        x = Card(Card.CLUB, 2)
        actual = repr(x)
        self.assertEqual(actual, "Card('club', 2)")

    def test_ace(self):
        x = Card(Card.CLUB, 1)
        actual = repr(x)
        self.assertEqual(actual, "Card('club', 1)")

    def test_jack(self):
        x = Card(Card.CLUB, 11)
        actual = repr(x)
        self.assertEqual(actual, "Card('club', 11)")

    def test_queen(self):
        x = Card(Card.CLUB, 12)
        actual = repr(x)
        self.assertEqual(actual, "Card('club', 12)")

    def test_king(self):
        x = Card(Card.CLUB, 13)
        actual = repr(x)
        self.assertEqual(actual, "Card('club', 13)")

    def test_numeric_ranks(self):
        for rank in (2, 3, 4, 5, 6, 7, 8, 9, 10):
            x = Card(Card.CLUB, rank)
            actual = repr(x)
            expected = "Card('club', {})".format(rank)
            self.assertEqual(actual, expected)
