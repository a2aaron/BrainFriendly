# The input BF program.
bf_program_string = "++++++>----"
# Current pointer location.
bf_index = 0
# Array of byte cells (currently 30,000).
bf_array = [0]*30000


def eval_program(program, index, array):
    program_index = 0
    # Stack for "[" and "]" commands.
    bracket_stack = list()
    while program_index != len(program):
        command = program[program_index]
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
        elif command == "[":
            # "[" jumps past the matching "[" if the current cell is 0.

            # Pushing this is fine even if the current cell is 0
            # Because it will be poped when we jump to the "]"
            bracket_stack.append(program_index)

            # Search for next "]"
            if array[index] == 0:
                bracket_count = 0
                while bracket_count != -1 :
                    program_index += 1
                    if program[program_index] == "[":
                        bracket_count += 1
                    elif program[program_index] == "]":
                        bracket_count -= 1
                    
        elif command == "]":
            # "]" jumps back to the matching "[" if the current cell is NOT 0
            if array[index] != 0:
                #Go to matching "["
                program_index = bracket_stack[-1]
            else:
                # Fall out of loop, pop matching "["
                bracket_stack.pop()
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


if __name__ == '__main__':
    bf_array = eval_program(bf_program_string, bf_index, bf_array)
    print(bf_array[0:10])
