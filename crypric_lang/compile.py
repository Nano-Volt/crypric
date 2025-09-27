
import sys

# Opcodes mapping
OPCODES = {
    "FN_DEF": 0x01,
    "PRINT": 0x02,
    "LOOP_START": 0x03,
    "LOOP_END": 0x04,
    "SHVM": 0x05,
    "RETURN": 0xFF,
}

def compile_crypic(source_code):
    bytecode = bytearray()

    lines = source_code.splitlines()
    function_ids = {"main": 1}
    string_ids = {"hello": 1}

    in_main = False
    for line in lines:
        line = line.strip()
        if line.startswith("fn main"):
            bytecode.append(OPCODES["FN_DEF"])
            bytecode.append(0x01)
            in_main = True

        elif "print('hello')" in line:
            bytecode.append(OPCODES["PRINT"])
            bytecode.append(0x01)

        elif line.startswith("loop"):
            count = int(line.split()[1])
            bytecode.append(OPCODES["LOOP_START"])
            bytecode.append(count)

        elif line.startswith("shvm main"):
            bytecode.append(OPCODES["SHVM"])
            bytecode.append(0x01)

        elif line.startswith("}"):
            if in_main:
                bytecode.append(OPCODES["RETURN"])
                in_main = False
            else:
                bytecode.append(OPCODES["LOOP_END"])

        elif line.startswith("return"):
            bytecode.append(OPCODES["RETURN"])

    return bytecode

def main():
    if len(sys.argv) != 3:
        print("Usage: python compile.py <source.cryp> <output.cbin>")
        sys.exit(1)

    source_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(source_file, "r") as f:
        source_code = f.read()

    bytecode = compile_crypic(source_code)

    with open(output_file, "wb") as f:
        f.write(bytecode)

    print(f"Compiled {source_file} -> {output_file}")

if __name__ == "__main__":
    main()
