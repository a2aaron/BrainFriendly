import sys
import io


def eval_program(program, index, memory, input=None, output=None):
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
                memory[index] = ord(input.read(1))
                # The internal bytes are in the range [-128, 127].
                # This sends 128 -> -128, and 255 -> -1
                if memory[index] > 127:
                    memory[index] -= 256

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
    if filename == '-':
        program = sys.stdin.read().encode('utf8')
    else:
        with open(filename, 'r') as f:
            program = f.read()

    return eval_program(program, index, memory, input, output)


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
    eval_file(filename, 0, bf_memory, output=output)


if __name__ == '__main__':
    main(sys.argv)
