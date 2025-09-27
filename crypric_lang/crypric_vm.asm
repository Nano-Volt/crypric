; ===== Crypric Virtual Machine =====
; Rust-like syntax support: print string from bytecode
; Assemble: nasm -f elf64 crypric_vm.asm -o crypric_vm.o
; Link:     ld crypric_vm.o -o crypric_vm

section .data
strings:
hello db "hello",0

section .bss
ip resq 1             ; Instruction pointer
loop_counter resb 1    ; Simple loop counter
bytecode resb 256      ; Reserve space for bytecode

section .text
global _start

_start:
    ; Open out.cbin
    mov rax, 2          ; sys_open
    mov rdi, out_file   ; filename
    mov rsi, 0          ; O_RDONLY
    syscall
    mov rdi, rax        ; file descriptor

    ; Read bytecode into buffer
    mov rax, 0          ; sys_read
    mov rsi, bytecode   ; buffer
    mov rdx, 256        ; max bytes
    syscall
    mov rcx, rax        ; rcx = bytes read

    mov rsi, bytecode   ; rsi = bytecode start
    call run_vm

    ; Exit program
    mov rax, 60
    xor rdi, rdi
    syscall

out_file: db "out.cbin",0

; ===== VM Execution =====
run_vm:
    mov rbx, rcx        ; rbx = bytecode length
    xor rdx, rdx        ; rdx = offset
.next_instruction:
    cmp rdx, rbx
    jge .return
    mov al, [rsi+rdx]   ; load current opcode
    cmp al, 0x02        ; PRINT
    je .print
    cmp al, 0x03        ; LOOP_START
    je .loop_start
    cmp al, 0x04        ; LOOP_END
    je .loop_end
    cmp al, 0xFF        ; RETURN
    je .return
    jmp .next_byte

.print:
    mov rdi, strings    ; print "hello" for index 1
    call print_string
    add rdx, 2
    jmp .next_instruction

.loop_start:
    mov bl, [rsi+rdx+1]
    mov [loop_counter], bl
    add rdx, 2
    jmp .next_instruction

.loop_end:
    mov bl, [loop_counter]
    dec bl
    mov [loop_counter], bl
    cmp bl, 0
    jne .loop_repeat
    add rdx, 1
    jmp .next_instruction

.loop_repeat:
    sub rdx, 2
    jmp .next_instruction

.return:
    ret

.next_byte:
    inc rdx
    jmp .next_instruction

; ===== Utilities =====
print_string:
    mov rdx, 5
    mov rax, 1
    mov rdi, 1
    syscall
    ret
