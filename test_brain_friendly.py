import brain_friendly
from brain_friendly import eval_program


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
