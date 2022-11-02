import sys
import os

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from apps.linked_list import process_linked_list

def test_process_linked_list_add_numbers():
    ll = process_linked_list()
    assert ll.head.data == 10
    assert ll.head.next.data == 20