Crypric Programming Language - Demo
-----------------------------------

How to Use:
1. Compile the VM:
   nasm -f elf64 crypric_vm.asm -o crypric_vm.o
   ld crypric_vm.o -o crypric_vm

2. Write code in example.cryp, for example:
   fn main() {
       print('hello');
   }

   loop 1 {
       shvm main
   }

   return 0

3. Compile the Crypric code to bytecode:
   python3 compile.py example.cryp hello.cbin

4. Run the VM (currently uses hardcoded bytecode in ASM for demo):
   ./crypric_vm
   
5.ccrp is used to covert to binary