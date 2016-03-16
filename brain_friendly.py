# The input BF program.
bf_program_string = "++++++>----"
# Current pointer location.
bf_index = 0
# Array of byte cells (currently 30,000).
bf_array = [0]*30000


def eval_program(program_string, index, array):
    for command in program_string:
        # Python doesn't have switch statements?
        if command == "+":
            # Cells are signed 8-bit values
            if array[index] == 127:
                array[index] = -128
            else:
                array[index] += 1
        elif command == "-":
            if array[index] == -128:
                array[index] = 127
            else:
                array[index] -= 1
        elif command == ">":
            index += 1
        elif command == "<":
            if index == 0:
                # No wraparround on the array.
                pass
            else:
                index -= 1
    return array

bf_array[0] = 127 # This is to show an example of cell-wrapping.
bf_array[1] = -128

bf_array = eval_program(bf_program_string, bf_index, bf_array)

print(bf_array[0:10])