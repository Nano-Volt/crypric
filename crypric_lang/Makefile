NA = nasm -f elf64
target = crypric_vm.asm
format = -o crypric_vm.o
ld = ld
ltarget = crypric_vm.o -o crypric_vm
rm = crypric_vm.o
rm2 = crypric_vm

all: 
	$(NA) $(target) $(format)
	$(ld) $(ltarget)

clean:
	rm -rf $(rm)
	rm -rf $(rm2)