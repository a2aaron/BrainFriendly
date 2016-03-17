import brain_friendly
from brain_friendly import eval_program

import StringIO


def test_plus():
    assert eval_program('+', 0, [0]) == [1]
    assert eval_program('+++++', 0, [0]) == [5]


def test_minus():
    assert eval_program('-', 0, [0]) == [-1]
    assert eval_program('-----', 0, [0]) == [-5]

    assert eval_program('-+', 0, [0]) == [0]
    assert eval_program('++--+--+', 0, [0]) == [0]


def test_arrows():
    assert eval_program('>+', 0, [0]*2) == [0, 1]
    assert eval_program('>>>+', 0, [0]*5) == [0, 0, 0, 1, 0]
    assert eval_program('><+', 0, [0]*2) == [1, 0]
    assert eval_program('>><+><<++', 0, [0]*3) == [2, 1, 0]


def test_saturate_buffer():
    assert eval_program('<<<+', 0, [0]*3) == [1, 0, 0]
    assert eval_program('>>>+', 0, [0]*3) == [0, 0, 1]
    assert eval_program('>>><+', 0, [0]*3) == [0, 1, 0]
    assert eval_program('<<<>+', 0, [0]*3) == [0, 1, 0]


def test_output():
    # Passing no output should work fine
    eval_program('.', 0, [0])
    eval_program('.', 0, [0], output=None)

    output = StringIO.StringIO()
    eval_program('.', 0, [0], output=output)
    output.seek(0)
    assert output.read() == '\0'

    # You can print multiple times from the same location
    output = StringIO.StringIO()
    eval_program('..', 0, [0], output=output)
    output.seek(0)
    assert output.read() == '\0\0'

    output = StringIO.StringIO()
    eval_program('.+.', 0, [0], output=output)
    output.seek(0)
    assert output.read() == '\x00\x01'

    # Output should be in the range [0, 255]
    output = StringIO.StringIO()
    eval_program('-.', 0, [0], output=output)
    output.seek(0)
    assert output.read() == '\xFF'
