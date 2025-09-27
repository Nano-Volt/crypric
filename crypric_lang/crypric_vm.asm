
; ===== Crypric Virtual Machine =====
; Assemble: nasm -f elf64 crypric_vm.asm -o crypric_vm.o
; Link:     ld crypric_vm.o -o crypric_vm

section .data
bytecode db 0x01,0x01,0x02,0x01,0xFF,0x03,0x01,0x05,0x01,0x04,0xFF

strings:
hello db "hello",0

section .bss
ip resq 1             ; Instruction pointer
loop_counter resb 1    ; Simple loop counter

section .text
global _start

_start:
    mov rsi, bytecode  ; rsi = bytecode start
    call run_vm

    ; Exit program
    mov rax, 60
    xor rdi, rdi
    syscall

; ===== VM Execution =====
run_vm:
    .next_instruction:
        mov al, [rsi]     ; load current opcode
        cmp al, 0x01       ; FN_DEF
        je .fn_def
        cmp al, 0x02       ; PRINT
        je .print
        cmp al, 0x03       ; LOOP_START
        je .loop_start
        cmp al, 0x04       ; LOOP_END
        je .loop_end
        cmp al, 0x05       ; SHVM
        je .shvm
        cmp al, 0xFF       ; RETURN
        je .return

        jmp .next_byte

    .fn_def:
        add rsi, 2
        jmp .next_instruction

    .print:
        mov rdi, strings
        call print_string
        add rsi, 2
        jmp .next_instruction

    .loop_start:
        mov bl, [rsi+1]
        mov [loop_counter], bl
        add rsi, 2
        jmp .next_instruction

    .loop_end:
        mov bl, [loop_counter]
        dec bl
        mov [loop_counter], bl
        cmp bl, 0
        jne .loop_repeat
        add rsi, 1
        jmp .next_instruction

    .loop_repeat:
        sub rsi, 2        ; jump back to start of loop body
        jmp .next_instruction

    .shvm:
        ; for now, just call main manually
        mov rsi, bytecode
        jmp .next_instruction

    .return:
        ret

    .next_byte:
        inc rsi
        jmp .next_instruction

; ===== Utilities =====
print_string:
    mov rdx, 5
    mov rax, 1
    mov rdi, 1
    syscall
    ret
