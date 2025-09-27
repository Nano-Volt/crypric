Crypric Language - Project Description (VM + Compiler Prototype)
================================================================

Overview
--------
Crypric is a tiny educational language prototype (initially called "crypric")
with a small VM (written in NASM) and a tiny compiler (written in Python).
The goal is to demonstrate a full flow:
  Crypric source (.cryp) -> compiled bytecode (.cbin) -> executed by crypric_vm

This prototype is minimal on purpose so you can learn and extend it incrementally.

Files included
--------------
- crypric_vm.asm    : NASM assembly VM (demo uses hardcoded bytecode & string table)
- compile.py        : Basic Python compiler that converts example.cryp -> hello.cbin
- example.cryp      : Example Crypric source (fn main, print, loop, shvm, return)
- README.txt        : This document

Design & Bytecode format
------------------------
The VM executes a simple sequence of bytes (instructions + small immediate operands).
Each opcode is a 1-byte numeric code, followed by zero or more small immediate operands (here u8).

Prototype opcode set:
  0x01 FN_DEF    u8 func_id       ; declare function with id
  0x02 PRINT     u8 string_id     ; print string with id from string table
  0x03 LOOP_START u8 count        ; start loop block (repeat count times)
  0x04 LOOP_END                   ; end loop block (decrements counter; jumps if not done)
  0x05 SHVM      u8 func_id       ; call/run function with id
  0xFF RETURN                    ; program return / exit

Notes:
- In this simple design immediate arguments are one byte (u8). For larger code you would use 32-bit operands.
- For functions and labels a real compiler needs a two-pass approach:
    Pass1: parse and assign addresses to functions/labels
    Pass2: emit code and resolve label addresses into operands

Crypric language example
------------------------
Source (example.cryp):
fn main() {
    print('hello');
}

loop 1 {
    shvm main
}

return 0

What the compiler does (conceptually):
- Define function "main" (id 1)
- In main: print string 'hello' (use string pool id 1)
- End main (return)
- Start a loop repeating 1 time:
    - shvm main  -> invoke the function main
- End loop
- return 0

How to run (Linux)
-------------------
1) Assemble and link VM:
   nasm -f elf64 crypric_vm.asm -o crypric_vm.o
   ld crypric_vm.o -o crypric_vm

2) Compile crypric source to bytecode:
   python3 compile.py example.cryp hello.cbin

3) Run VM:
   (Current demo VM contains a hardcoded bytecode table. To run external files you must
    update the asm to read the binary file into memory or modify the ASM to accept stdin/argv)
   ./crypric_vm

Extending the system
--------------------
1. Make VM read a .cbin file:
   - Replace hardcoded `bytecode db ...` with a loader that reads file into .bss buffer using sys_read/open.
   - Add an entry in _start to parse argv and open the file.

2. Improve compiler:
   - Use a proper lexer and parser to support arbitrary identifiers, strings, numbers, nesting.
   - Implement two-pass assemble for labels and function addresses.
   - Support string pool and variable table.

3. Expand opcodes:
   - arithmetic (ADD, SUB, MUL, DIV)
   - LOAD/STORE for variables
   - conditional jumps (JZ/JNZ)
   - CALL/RET with stack frames for nested functions

4. Bootstrapping:
   - Later rewrite the compiler in Crypric itself (self-hosting) or port the VM to C for cross-platform builds.

Contact
-------
If you're stuck or want help extending a part (e.g., making the VM read a file, adding CALL/RET, or building a real parser),
ask me — I’ll code it step-by-step with explanations.
