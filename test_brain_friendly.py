import brain_friendly
from brain_friendly import eval_program, get_brace_matches

import pytest
import io


# Tests for "+", "-", ">", and "<"
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


# Tests for "[" and "]"
def test_trivial_loops():
    # Since the current cell is zero.
    # All of these loops should exit immediately
    assert eval_program('[]', 0, [0]) == [0]
    assert eval_program('[[]]', 0, [0]) == [0]
    assert eval_program('[[[]]]', 0, [0]) == [0]
    assert eval_program('[][]', 0, [0]) == [0]
    assert eval_program('[][][]', 0, [0]) == [0]
    assert eval_program('[][][][]', 0, [0]) == [0]
    assert eval_program('[[[][][[]]][][[][][[][]]][]]', 0, [0]) == [0]


def test_simple_loops():
    assert eval_program('+++>[]', 0, [0, 0]) == [3, 0]
    assert eval_program('[]>++', 0, [0, 0]) == [0, 2]

    # "Copy value" program.
    # Copies the current cell's value into the next two cells
    assert eval_program('[>+>+<<-]', 1, [0, 3, 0, 0]) == [0, 0, 3, 3]

    # "Move value" program.
    # Moves the current cell two cells right.
    assert eval_program('>>[-]<<[->>+<<]', 0, [5, 0, 0]) == [0, 0, 5]


def test_bracket_jump():
    # If the value at the current cell is 0
    # Then [ should jump past the matching ]
    assert eval_program('[++]', 0, [0, 0]) == [0, 0]
    # Initalizes the cells as [1,-2,0] with the pointer at cell 1
    # [+] should run until cell 1 is zero
    # Then the pointer should move to cell 2 and make it -1.
    assert eval_program('+>--[+]>-', 0, [0, 0, 0]) == [1, 0, -1]


def test_set_zero():
    # [+] and [-] should set the current cell to zero
    # Since there is under/overflow, this should always work.
    assert eval_program('[-]>[+]', 0, [-1, 1]) == [0, 0]
    assert eval_program('[-]<[+]', 1, [100, -100]) == [0, 0]


def test_nested_loops():
    # Modified "hello world" program (without I/O). Taken from Esolang Wiki
    # Does not print anything and is a truncated program.
    # https://esolangs.org/wiki/Brainfuck#Examples
    program = '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]'
    assert eval_program(program, 0, [0]*7) == [0, 0, 72, 104, 88, 32, 8]

    # Slightly modified "multiplication" program. Taken from StackOverflow
    # Takes two numbers in cell 0 and 1 and outputs their product in cell 2.
    # http://stackoverflow.com/a/26708313
    program2 = '[>[->+>+<<]>>[-<<+>>]<<<-]>[-]'
    assert eval_program(program2, 0, [3, 5, 0, 0]) == [0, 0, 15, 0]


# Tests for "." and ","
def test_output():
    # Passing no output should work fine
    eval_program('.', 0, [0])
    eval_program('.', 0, [0], output=None)

    output = io.BytesIO()
    eval_program('.', 0, [0], output=output)
    output.seek(0)
    assert output.read() == b'\0'

    # You can print multiple times from the same location
    output = io.BytesIO()
    eval_program('..', 0, [0], output=output)
    output.seek(0)
    assert output.read() == b'\0\0'

    output = io.BytesIO()
    eval_program('.+.', 0, [0], output=output)
    output.seek(0)
    assert output.read() == b'\x00\x01'

    # Output should be in the range [0, 255]
    output = io.BytesIO()
    eval_program('-.', 0, [0], output=output)
    output.seek(0)
    assert output.read() == b'\xFF'


def test_input():
    # Passing no input should work fine
    eval_program(',', 0, [0])
    eval_program(',', 0, [0], input=None)

    input = io.BytesIO(b'h')
    assert eval_program(',', 0, [0], input=input) == [ord('h')]

    # Not consuming the whole buffer should be safe
    input = io.BytesIO(b'hello')
    assert eval_program(',', 0, [0], input=input) == [ord('h')]

    # Repeatedly reading should override
    input = io.BytesIO(b'hello')
    assert eval_program(',,,,,', 0, [0], input=input) == [ord('o')]

    input = io.BytesIO(b'hello')
    value = eval_program(',>,>,>,>,', 0, [0]*5, input=input)
    assert value == [ord(c) for c in 'hello']

    # Input:  [0, 1, ..., 127,  128,  129, ..., 255]
    # Stored: [0, 1, ..., 127, -128, -127, ...,  -1]
    input = io.BytesIO(bytearray([127]))
    assert eval_program(',', 0, [0], input=input) == [127]

    input = io.BytesIO(bytearray([128]))
    assert eval_program(',', 0, [0], input=input) == [-128]

    input = io.BytesIO(bytearray([255]))
    assert eval_program(',', 0, [0], input=input) == [-1]


def test_io_roundtrip():
    for byte in range(256):
        input = io.BytesIO(bytearray([byte]))
        output = io.BytesIO()
        value = eval_program(',.', 0, [0], input=input, output=output)
        if byte < 128:
            assert value == [byte]
        else:
            assert value == [byte - 256]
        assert input.getvalue() == output.getvalue()


# Test brace matching
def test_trival_braces():
    assert get_brace_matches('') == {}
    assert get_brace_matches('+-><') == {}
    assert get_brace_matches('+-<>[]+-<>') == {4: 5, 5: 4}
    assert get_brace_matches('[+-><]') == {0: 5, 5: 0}


def test_complex_braces():
    assert get_brace_matches('[[]]') == {0: 3, 1: 2, 2: 1, 3: 0}
    assert get_brace_matches('[][]') == {0: 1, 1: 0, 2: 3, 3: 2}
    assert get_brace_matches('[[][]]') == {0: 5, 1: 2, 2: 1, 3: 4, 4: 3, 5: 0}


def test_invalid_braces():
    test_cases = ['[', '[[', ']', ']]', '][', '[[]', '[]]', '][[']
    for test_case in test_cases:
        with pytest.raises(ValueError):
            get_brace_matches(test_case)


# Full program testing
def test_hello_world():
    program = ('++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]'
               '>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.')
    output = io.BytesIO()
    eval_program(program, 0, [0]*100, output=output)
    assert output.getvalue() == b'Hello World!\n'

    program = ('>++++++++[-<+++++++++>]<.>>+>-[+]++>++>+++[>[->+++<<+++>]<<]'
               '>-----.>->+++..+++.>-.<<+[>[+>+]>>]<--------------.>>.+++.'
               '------.--------.>+.>+.')
    output = io.BytesIO()
    eval_program(program, 0, [0]*100, output=output)
    assert output.getvalue() == b'Hello World!\n'

    # http://codegolf.stackexchange.com/questions/55422/hello-world/68494#68494
    program = ('--->->->>+>+>>+[++++[>+++[>++++>-->+++<<<-]<-]<+++]'
               '>>>.>-->-.>..+>++++>+++.+>-->[>-.<<]')
    output = io.BytesIO()
    eval_program(program, 0, [0]*100, output=output)
    assert output.getvalue() == b'Hello, World!'

    program = '''\
+++++ +++               Set Cell #0 to 8
[
    >++++               Add 4 to Cell #1; this will always set Cell #1 to 4
    [                   as the cell will be cleared by the loop
        >++             Add 4*2 to Cell #2
        >+++            Add 4*3 to Cell #3
        >+++            Add 4*3 to Cell #4
        >+              Add 4 to Cell #5
        <<<<-           Decrement the loop counter in Cell #1
    ]                   Loop till Cell #1 is zero
    >+                  Add 1 to Cell #2
    >+                  Add 1 to Cell #3
    >-                  Subtract 1 from Cell #4
    >>+                 Add 1 to Cell #6
    [<]                 Move back to the first zero cell you find; this will
                        be Cell #1 which was cleared by the previous loop
    <-                  Decrement the loop Counter in Cell #0
]                       Loop till Cell #0 is zero

The result of this is:
Cell No :   0   1   2   3   4   5   6
Contents:   0   0  72 104  88  32   8
Pointer :   ^

>>.                     Cell #2 has value 72 which is 'H'
>---.                   Subtract 3 from Cell #3 to get 101 which is 'e'
+++++ ++..+++.          Likewise for 'llo' from Cell #3
>>.                     Cell #5 is 32 for the space
<-.                     Subtract 1 from Cell #4 for 87 to give a 'W'
<.                      Cell #3 was set to 'o' from the end of 'Hello'
+++.----- -.----- ---.  Cell #3 for 'rl' and 'd'
>>+.                    Add 1 to Cell #5 gives us an exclamation point
>++.                    And finally a newline from Cell #6'''
    output = io.BytesIO()
    eval_program(program, 0, [0]*100, output=output)
    assert output.getvalue() == b'Hello World!\n'

    # Visit the following link to find items that will fail non-wrapping, etc.
    # http://codegolf.stackexchange.com/questions/55422/hello-world/68494#68494
