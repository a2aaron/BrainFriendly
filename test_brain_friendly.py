import brain_friendly
from brain_friendly import eval_program

import io


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
