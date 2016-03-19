# The input BF program.
bf_program_string = '[][]'
# Current pointer location.
bf_index = 0
# Array of byte cells (currently 30,000).
bf_array = [0]*30000

def eval_program(program, index, array, input=None, output=None):
    program_index = 0
    # Stack for "[" and "]" commands.
    brace_dict = get_brace_matches(program)
    while program_index != len(program):
        command = program[program_index]
        if command == "+":
            array[index] = increment_command(array[index])
        elif command == "-":
            array[index] = decrement_command(array[index])
        elif command == ">":
            if index+1 < len(array):
                index += 1
        elif command == "<":
            if index > 0:
                index -= 1
        elif command == ".":
            if output:
                # The output byte must be in range(256)
                output.write(bytearray([array[index] % 256]))
        elif command == ',':
            if input:
                array[index] = ord(input.read(1))
                # The internal bytes are in the range [-128, 127].
                # This sends 128 -> -128, and 255 -> -1
                if array[index] > 127:
                    array[index] -= 256

        elif command == "[":
            # "[" jumps past the matching "[" if the current cell is 0.
            if array[index] == 0:
                    program_index = brace_dict[program_index]

        elif command == "]":
            # "]" jumps back to the matching "[" if the current cell is NOT 0
            if array[index] != 0:
                program_index = brace_dict[program_index]
        # Next command
        program_index += 1                    
    return array


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
    brace_dict = dict()
    brace_stack = list()

    for index in range(len(program)):
        if program[index] == "[":
            brace_stack.append(index)
        elif program[index] == "]":
            if len(brace_stack) == 0: #sanity check
                raise ValueError("Malformed BF program (too many \"]\"s)")
            left_index = brace_stack.pop()
            #add left AND right brace pairs.
            brace_dict[left_index] = index
            brace_dict[index] = left_index

    if len(brace_stack) == 0: #sanity check
        return brace_dict
    else:
        raise ValueError("Malformed BF program (too many \"[\"s)")

if __name__ == '__main__':
    bf_array = eval_program(bf_program_string, bf_index, bf_array)
    print(bf_array[0:10])
