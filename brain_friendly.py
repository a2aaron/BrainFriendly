import sys
import io

# The input BF program.
bf_program_string = '[][]'
# Current pointer location.
bf_index = 0
# Array of byte cells (currently 30,000).
bf_memory = [0] * 30000


def eval_program(program, index, memory, input=None, output=None, EOF=0):
    program_index = 0
    # Stack for "[" and "]" commands.
    brace_pairs = get_brace_matches(program)
    while program_index < len(program):
        command = program[program_index]
        if command == '+':
            memory[index] = increment_command(memory[index])
        elif command == '-':
            memory[index] = decrement_command(memory[index])
        elif command == '>':
            if index + 1 < len(memory):
                index += 1
        elif command == '<':
            if index > 0:
                index -= 1
        elif command == '.':
            if output:
                # The output byte must be in range(256)
                output.write(bytearray([memory[index] % 256]))
        elif command == ',':
            if input:
                try:
                    memory[index] = ord(input.read(1))
                    # The internal bytes are in the range [-128, 127].
                    # This sends 128 -> -128, and 255 -> -1
                    if memory[index] > 127:
                        memory[index] -= 256
                except TypeError:
                    if EOF is None:
                        pass
                    else:
                        memory[index] = EOF

        elif command == '[':
            # "[" jumps past the matching "[" if the current cell is 0.
            if memory[index] == 0:
                program_index = brace_pairs[program_index]

        elif command == ']':
            # "]" jumps back to the matching "[" if the current cell is NOT 0
            if memory[index] != 0:
                program_index = brace_pairs[program_index]
        program_index += 1  # Next command
    return memory


def increment_command(value):
    if value == 127:
        return -128
    else:
        return value + 1


def decrement_command(value):
    if value == -128:
        return 127
    else:
        return value - 1


def get_brace_matches(program):
    '''
    Returns a dictionary containing the pairs for left and right brace indexes.
    If the program is malformed, then ValueError is raised.
    '''
    brace_pairs = {}
    brace_stack = []

    for index, instruction in enumerate(program):
        if instruction == '[':
            brace_stack.append(index)
        elif instruction == ']':
            if not brace_stack:  # Sanity check
                raise ValueError("Malformed BF program (too many \"]\"s)")
            left_index = brace_stack.pop()
            # Add left AND right brace pairs.
            brace_pairs[left_index] = index
            brace_pairs[index] = left_index

    if brace_stack:  # Sanity check if brace_stack is empty
        raise ValueError("Malformed BF program (too many \"[\"s)")
    else:
        return brace_pairs


def eval_file(filename, index, memory, input=None, output=None):
    with open(filename, 'r') as f:
        program = f.read()
        return eval_program(program, index, memory, input, output)


def try_parse_int(string):
    try:
        return int(string)
    except ValueError:
        return None


def eval_stdin():
    # TODO: write tests
    # TODO: instead of asking for input seperately, just use "!".
    # programs to look at:
    # http://www.brain------------------------------------------------------fuck.com/programs.html

    program_string = "Type a BF program. Comments are fine"
    EOF_string = "What should EOF return? (newline for no change on EOF)\n"
    input_string = "Type your program input.\n"

    # The main reason for the version checking is because
    # input() tries to execute Python code in Python 2 while
    # input() is the same as raw_input() in Python 3.
    if (sys.version_info > (3, 0)):
        program = input(program_string)
        EOF = try_parse_int(input(EOF_string))
        stringIO_input = io.StringIO(input(input_string))
        output = sys.stdout.buffer
    else:
        program = raw_input(program_string)
        EOF = try_parse_int(raw_input(EOF_string))
        # Yes, StringIO must be in unicode for Python 2.
        stringIO_input = io.StringIO(unicode(raw_input(input_string)))
        output = sys.stdout

    eval_program(program, bf_index, bf_memory, stringIO_input, output, EOF)
    print("\n")

if __name__ == '__main__':
    eval_stdin()
