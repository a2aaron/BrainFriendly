import brain_friendly
from brain_friendly import eval_program, eval_file, get_brace_matches

import pytest
import os
import io
import sys


# Tests for '+', '-', '>', and '<'
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


# Tests for '[' and ']'
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

    # 'Copy value' program.
    # Copies the current cell's value into the next two cells
    assert eval_program('[>+>+<<-]', 1, [0, 3, 0, 0]) == [0, 0, 3, 3]

    # 'Move value' program.
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
    # Modified 'hello world' program (without I/O). Taken from Esolang Wiki
    # Does not print anything and is a truncated program.
    # https://esolangs.org/wiki/Brainfuck#Examples
    program = '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]'
    assert eval_program(program, 0, [0]*7) == [0, 0, 72, 104, 88, 32, 8]

    # Slightly modified 'multiplication' program. Taken from StackOverflow
    # Takes two numbers in cell 0 and 1 and outputs their product in cell 2.
    # http://stackoverflow.com/a/26708313
    program2 = '[>[->+>+<<]>>[-<<+>>]<<<-]>[-]'
    assert eval_program(program2, 0, [3, 5, 0, 0]) == [0, 0, 15, 0]


# Tests for '.' and ','
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
    prefix = 'test_programs/hello_world/'
    test_cases = [('commented.bf',  b'Hello World!\n'),
                  ('no_comma.bf',   b'Hello World!\n'),
                  ('no_comma2.bf',  b'Hello World!\n'),
                  ('lowercase.bf',  b'hello world'),
                  ('no_newline.bf', b'Hello, World!')]
    for filename, file_output in test_cases:
        filepath = os.path.join(prefix, filename)
        output = io.BytesIO()
        eval_file(filepath, 0, [0]*100, output=output)
        output.seek(0)
        assert output.getvalue() == file_output

    # Visit the following link to find items that will fail non-wrapping, etc.
    # http://codegolf.stackexchange.com/questions/55422/hello-world/68494#68494


# Test reading from a file
def test_empty_file():
    assert eval_file('test_programs/empty.bf', 0, [0]) == [0]


def test_simple_file():
    output = [1, 2, 3, -2, 1]  # This is so pep8 doesn't yell at me.
    assert eval_file('test_programs/simple.bf', 0, [0]*5) == output


def test_multiply_file():
    output = [0, 0, 15, 0]  # This is so pep8 doesn't yell at me.
    assert eval_file('test_programs/multiply.bf', 0, [3, 5, 0, 0]) == output


def test_squares_file():
    # Output is a sequence of square numbers between 0 and 10000 with a newline
    output = io.BytesIO()
    eval_file('test_programs/squares.bf', 0, [0]*30000, output=output)
    output.seek(0)
    x = 0
    while x * x < 10000:
        assert output.readline() == str(x * x).encode('ascii') + b'\n'
        x += 1


def test_bottles_of_beer_file():
    output = io.BytesIO()
    eval_file('test_programs/bottles_of_beer.bf', 0, [0]*30000, output=output)
    output.seek(0)
    with open('test_programs/bottles_output.txt', 'rb') as f:
        f.readline() == output.readline()
