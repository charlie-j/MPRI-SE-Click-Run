import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src')
from map import *

def test_gen_one():
    """
    This function try to generate the one column pattern
    """
    new_map = Map(None,None)
    for i in range(1000):
        new_map.gen_one()

