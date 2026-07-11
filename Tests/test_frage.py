import sys 
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "GameLogik"))

import unittest
from frage import Frage
from diffictuly import Difficulty

class TestFrage(unittest.TestCase):

    def test