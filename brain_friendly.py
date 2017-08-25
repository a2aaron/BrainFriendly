import sys
import io
import random
# The input BF program.
bf_program_string = '[][]'
# Current pointer location.
bf_index = 0
# Array of byte cells (currently 30,000 but can expand with program).
bf_memory = [0]*30000

try:
    _ = unicode
except:
    unicode = str



def eval_program(program, index, memory, input=None, output=None, failout=None):
    steps = 0
    program_index = 0
    # Stack for "[" and "]" commands.
    brace_pairs = get_brace_matches(program)
    did_fail = False
    while program_index < len(program):
        command = program[program_index]
        if command == '+' or command == ord('+'):
            memory[index] = increment_command(memory[index])
        elif command == '-' or command == ord('-'):
            memory[index] = decrement_command(memory[index])
        elif command == '>' or command == ord('>'):
            index += 1
            # Expand the memory buffer if we hit memory limits
            # Most normal sized programs should not hit this,
            # but very large ones might.
            if index >= len(memory):
                # Add at least one memory cell
                memory.extend([0]*(1 + index - len(memory)))
        elif command == '<' or command == ord('<'):
            if index > 0:
                index -= 1
        elif command == '.' or command == ord('.'):
            if output:
                # The output byte must be in range(256)
                output.write(bytearray([memory[index] % 256]))
        elif command == ',' or command == ord(','):
            if input:
                memory[index] = ord(input.read(1))
                # The internal bytes are in the range [-128, 127].
                # This sends 128 -> -128, and 255 -> -1
                if memory[index] > 127:
                    memory[index] -= 256

        elif command == '[' or command == ord('['):
            # "[" jumps past the matching "[" if the current cell is 0.
            if memory[index] == 0:
                    program_index = brace_pairs[program_index]

        elif command == ']' or command == ord(']'):
            # "]" jumps back to the matching "[" if the current cell is NOT 0
            if memory[index] != 0:
                program_index = brace_pairs[program_index]
        program_index += 1  # Next command
        steps += 1
        print("({}) {}: {}".format(command, steps, memory))

        if failout is not None and steps > failout:
            did_fail = True
            break
    if did_fail:
        print("{}: FAILOUT".format(program))
    else:
        print("{}: {}".format(program, steps))
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
        if instruction == '[' or instruction == ord('['):
            brace_stack.append(index)
        elif instruction == ']' or instruction == ord(']'):
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
    if filename == '-':
        program = sys.stdin.read()
        if not isinstance(program, bytes):
            program = program.encode('utf8')
        program = program.split(b'!')
        in_stream = io.BytesIO(b'!'.join(program[1:]))
        program = program[0]
    else:
        with open(filename, 'r') as f:
            program = f.read()
        try:
            in_stream = sys.stdin.buffer  # Python 3
        except AttributeError:
            in_stream = sys.stdin  # Python 2

    return eval_program(program, index, memory, in_stream, output)


def main(args):
    if len(args) > 1:
        filename = args[1]
    else:
        filename = '-'  # Represents stdin

    try:
        output = sys.stdout.buffer  # Python 3
    except AttributeError:
        output = sys.stdout  # Python 2
    # Array of byte cells (currently 30,000).
    bf_memory = [0]*30000
    return eval_file(filename, 0, bf_memory, output=output)

def bf_generator_no_output(length):
    # A program array stores a program numerically
    # ex: [0, 1, 2, 3, 4, 5] is "[]><-+"
    program_array = [0] * length

    def array_to_program(array):
        program = ""
        for number in array:
            program += {
                0: '+',
                1: '-',
                2: '>',
                3: '<',
                4: '[',
                5: ']'
            }[number]
        return program

    def increment(array):
        new_array = array
        carry_flag = True
        for index, value in enumerate(reversed(array)):
            if carry_flag:
                new_value = array[index] + 1
                new_array[index] = new_value % 6
                carry_flag = new_value == 6
        return new_array

    while True:
        program = array_to_program(program_array)
        try:
            get_brace_matches(program) # Throws ValueError if not a valid BF program
            yield program
        except ValueError:
            pass
        
        program_array = increment(program_array)
        if program_array == [0]*length:
            break
    raise StopIteration


def random_bf_no_output(length):
    loop_depth = 0
    program = ""
    instruction_list = ['+', '-', '>', '<', '+', '-', '>', '<', '[', ']']
    for i in range(0, length):
        instruction = random.choice(instruction_list)
        # Don't emit ] if no matching [
        if loop_depth <= 0 and instruction == ']':
            instruction = '['

        if instruction == '[':
            loop_depth += 1
        elif instruction == ']':
            loop_depth -= 1
        program += instruction
    for i in range(0, loop_depth):
        program += ']'
    return program


if __name__ == '__main__':
    # main(sys.argv)
    # for program in bf_generator_no_output(6):
        # eval_program(program, 0, [0]*10, input=None, output=None, failout=1000000)
    eval_program("+[><+]", 0, [0]*10, input=None, output=None, failout=1000000)

__version__ = '0.1.0'