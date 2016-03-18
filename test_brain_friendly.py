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

def test_trivial_loops():
    # All of these loops should exit immediately since the current cell is zero.
    assert eval_program('[]', 0, [0]) == [0]
    assert eval_program('[[]]', 0, [0]) == [0]
    assert eval_program('[[[]]]', 0, [0]) == [0]
    assert eval_program('[][]', 0, [0]) == [0]
    assert eval_program('[][][]', 0, [0]) == [0]
    assert eval_program('[][][][]', 0, [0]) == [0]
    assert eval_program('[[[][][[]]][][[][][[][]]][]]', 0, [0]) == [0]

def test_simple_loops():
    assert eval_program('+++>[]', 0, [0,0]) == [3,0]
    assert eval_program('[]>++', 0, [0,0]) == [0,2]

    # "Copy value" program.
    # Copies the current cell's value into the next two cells
    assert eval_program('[>+>+<<-]', 1, [0,3,0,0]) == [0,0,3,3]

    # "Move value" program.
    # Moves the current cell two cells right.
    assert eval_program('>>[-]<<[->>+<<]', 0, [5,0,0]) == [0,0,5]


def test_bracket_jump():
    # If the value at the current cell is 0
    # Then [ should jump past the matching ]
    assert eval_program('[++]', 0, [0,0]) == [0,0]
    # Initalizes the cells as [1,-2,0] with the pointer at cell 1
    # [+] should run until cell 1 is zero
    # Then the pointer should move to cell 2 and make it -1.
    assert eval_program('+>--[+]>-', 0, [0,0,0]) == [1,0,-1]

def test_set_zero():
    # [+] and [-] should set the current cell to zero
    # Since there is under/overflow, this should always work.
    assert eval_program('[-]>[+]', 0, [-1,1]) == [0,0]
    assert eval_program('[-]<[+]', 1, [100,-100]) == [0,0]

def test_nested_loops():
    # Modified "hello world" program (without I/O). Taken from Esolang Wiki
    # Does not print anything and is a truncated program.
    # https://esolangs.org/wiki/Brainfuck#Examples
    program = '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]'
    assert eval_program(program, 0, [0]*7) == [0,0,72,104,88,32,8]

    # Slightly modified "multiplication" program. Taken from StackOverflow
    # Takes two numbers in cell 0 and 1 and outputs their product in cell 2.
    # http://stackoverflow.com/a/26708313
    assert eval_program('[>[->+>+<<]>>[-<<+>>]<<<-]>[-]', 0, [3,5,0,0]) == [0,0,15,0]

