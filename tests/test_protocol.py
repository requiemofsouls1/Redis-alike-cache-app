import pytest

from app.protocol import parse_line, ProtocolError


def test_parse_basic():
    cmd, args = parse_line('SET a 1')
    assert cmd == 'SET' and args == ['a', '1']


def test_parse_ignores_spaces_and_case():
    cmd, args = parse_line('    gEt     a    ')
    assert cmd == 'GET' and args == ['a']


def test_parse_empty_raises():
    with pytest.raises(ProtocolError):
        parse_line('    ')