# The input BF program.
bf_program_string = "++++++>----"
# Current pointer location.
bf_index = 0
# Array of byte cells (currently 30,000).
bf_array = [0]*30000


def eval_program(program_string, index, array):
    for command in program_string:
        if command == "+":
            # Cells are signed 8-bit values
            array[index] = increment_command(array[index])
        elif command == "-":
            array[index] = decrement_command(array[index])
        elif command == ">":
            if index+1 < len(array):
                index += 1
        elif command == "<":
            if index > 0:
                index -= 1
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


if __name__ == '__main__':
    bf_array = eval_program(bf_program_string, bf_index, bf_array)
    print(bf_array[0:10])
