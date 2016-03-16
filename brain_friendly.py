# The input BF program.
bf_program_string = "+>+>+>+>++>>-->>++<--<<<<++++++--"
# Current pointer location.
bf_index = 0
# Array of byte cells (currently 30,000).
bf_array = [0]*30000


def eval_program(program_string, index, array):
    for command in program_string:
        if command == "+":
            array[index] += 1
        elif command == "-":
            array[index] -= 1
        elif command == ">":
            if index+1 < len(array):
                index += 1
        elif command == "<":
            if index > 0:
                index -= 1
    return array

if __name__ == '__main__':
    print(eval_program(bf_program_string, bf_index, bf_array))
