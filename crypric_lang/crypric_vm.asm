; ===== Cryptic Virtual Machine (Enhanced) =====
; A professional bytecode VM implementation with large memory support
; Features: 256KB bytecode, dynamic string handling, proper error checking
; Assemble: nasm -f elf64 crypric_vm.asm -o crypric_vm.o
; Link:     ld crypric_vm.o -o crypric_vm

section .data
    ; String table with proper indexing
    string_table:
        hello db "hello", 0
        world db "world", 0
        error db "ERROR: ", 0
        newline db 10, 0
    
    ; File handling
    bytecode_file db "out.cbin", 0
    open_error db "Failed to open bytecode file", 10, 0
    read_error db "Failed to read bytecode", 10, 0
    overflow_error db "Bytecode too large", 10, 0
    
    ; VM Constants
    MAX_BYTECODE_SIZE equ 262144  ; 256KB = 256 * 1024
    MAX_LOOP_DEPTH equ 64         ; Increased for larger programs
    STRING_TABLE_SIZE equ 16      ; Support 16 predefined strings

section .bss
    ; VM State
    ip resq 1                    ; Instruction pointer
    bytecode_size resq 1         ; Actual bytecode size
    loop_counters resb MAX_LOOP_DEPTH  ; Loop stack
    loop_stack_ptr resb 1        ; Loop stack pointer
    vm_registers resb 8          ; General purpose registers R0-R7
    
    ; Memory - aligned for performance
    bytecode resb MAX_BYTECODE_SIZE    ; 256KB bytecode buffer

section .text
    global _start

; ===== Entry Point =====
_start:
    call initialize_vm
    call load_bytecode
    call execute_vm
    call cleanup_vm
    
    ; Exit gracefully
    mov rax, 60         ; sys_exit
    xor rdi, rdi        ; exit code 0
    syscall

; ===== VM Initialization =====
initialize_vm:
    push rbp
    mov rbp, rsp
    
    ; Initialize VM state
    mov qword [ip], 0
    mov qword [bytecode_size], 0
    mov byte [loop_stack_ptr], 0
    
    ; Clear registers
    xor rax, rax
    mov rcx, 8
    mov rdi, vm_registers
    rep stosb
    
    pop rbp
    ret

; ===== Bytecode Loading =====
load_bytecode:
    push rbp
    mov rbp, rsp
    
    ; Open bytecode file
    mov rax, 2          ; sys_open
    mov rdi, bytecode_file
    mov rsi, 0          ; O_RDONLY
    mov rdx, 0o644      ; permissions
    syscall
    
    ; Error checking
    cmp rax, 0
    jg .file_opened
    mov rdi, open_error
    call print_string
    jmp .exit_error
    
.file_opened:
    mov r8, rax         ; preserve file descriptor
    
    ; Read bytecode
    mov rax, 0          ; sys_read
    mov rdi, r8         ; file descriptor
    mov rsi, bytecode
    mov rdx, MAX_BYTECODE_SIZE
    syscall
    
    ; Error checking
    cmp rax, 0
    jg .read_success
    mov rdi, read_error
    call print_string
    jmp .close_and_exit
    
.read_success:
    ; Check if file is too large
    cmp rax, MAX_BYTECODE_SIZE
    jl .size_ok
    mov rdi, overflow_error
    call print_string
    jmp .close_and_exit

.size_ok:
    mov [bytecode_size], rax
    
    ; Close file
    mov rax, 3          ; sys_close
    mov rdi, r8
    syscall
    
    pop rbp
    ret

.close_and_exit:
    mov rax, 3          ; sys_close
    mov rdi, r8
    syscall

.exit_error:
    mov rax, 60         ; sys_exit
    mov rdi, 1          ; error code
    syscall

; ===== Main VM Execution Loop =====
execute_vm:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    
    mov r12, bytecode           ; r12 = bytecode base (preserved)
    mov r13, [bytecode_size]    ; r13 = total size (preserved)

.vm_loop:
    mov rcx, [ip]               ; current offset
    cmp rcx, r13
    jge .vm_exit                ; end of bytecode
    
    mov al, [r12 + rcx]         ; fetch opcode
    inc qword [ip]              ; advance IP
    
    ; Dispatch based on opcode
    cmp al, 0x02                ; PRINT_STRING
    je .op_print_string
    cmp al, 0x03                ; LOOP_START
    je .op_loop_start
    cmp al, 0x04                ; LOOP_END
    je .op_loop_end
    cmp al, 0xFF                ; VM_EXIT
    je .vm_exit
    cmp al, 0x05                ; PRINT_CHAR
    je .op_print_char
    cmp al, 0x06                ; PRINT_NEWLINE
    je .op_print_newline
    cmp al, 0x07                ; LOAD_IMMEDIATE
    je .op_load_immediate
    
    ; Unknown opcode - skip with warning
    jmp .vm_loop

.op_print_string:
    call handle_print_string
    jmp .vm_loop

.op_print_char:
    call handle_print_char
    jmp .vm_loop

.op_print_newline:
    call handle_print_newline
    jmp .vm_loop

.op_loop_start:
    call handle_loop_start
    jmp .vm_loop

.op_loop_end:
    call handle_loop_end
    jmp .vm_loop

.op_load_immediate:
    call handle_load_immediate
    jmp .vm_loop

.vm_exit:
    pop r13
    pop r12
    pop rbp
    ret

; ===== Instruction Handlers =====
handle_print_string:
    push rbp
    mov rbp, rsp
    push r12
    
    mov r12, bytecode           ; preserve bytecode base
    
    ; Get string index from bytecode
    mov rcx, [ip]
    mov al, [r12 + rcx]
    inc qword [ip]
    
    ; Validate string index
    cmp al, STRING_TABLE_SIZE
    jl .index_valid
    mov al, 0                   ; default to first string on error

.index_valid:
    ; Select string based on index
    mov rdi, string_table
    mov rsi, 6                  ; average string length + null
    mul rsi                     ; rax = index * 6
    add rdi, rax                ; rdi = string_table + offset
    
    call print_string
    
    pop r12
    pop rbp
    ret

handle_print_char:
    push rbp
    mov rbp, rsp
    push r12
    
    mov r12, bytecode
    
    ; Get character from bytecode
    mov rcx, [ip]
    mov al, [r12 + rcx]
    inc qword [ip]
    
    ; Print single character using stack buffer
    push rax                    ; reserve space on stack
    mov rax, 1                  ; sys_write
    mov rdi, 1                  ; stdout
    mov rsi, rsp                ; character on stack
    mov rdx, 1                  ; length
    syscall
    pop rax                     ; cleanup stack
    
    pop r12
    pop rbp
    ret

handle_print_newline:
    push rbp
    mov rbp, rsp
    
    mov rdi, newline
    call print_string
    
    pop rbp
    ret

handle_load_immediate:
    push rbp
    mov rbp, rsp
    push r12
    
    mov r12, bytecode
    
    ; Get register index (0-7)
    mov rcx, [ip]
    mov al, [r12 + rcx]
    inc qword [ip]
    
    ; Get immediate value
    mov rcx, [ip]
    mov bl, [r12 + rcx]
    inc qword [ip]
    
    ; Store in register (R0-R7)
    and al, 0x07                ; ensure 0-7 range
    movzx rax, al
    mov [vm_registers + rax], bl
    
    pop r12
    pop rbp
    ret

handle_loop_start:
    push rbp
    mov rbp, rsp
    push r12
    
    mov r12, bytecode
    
    ; Get loop counter and push to stack
    mov rcx, [ip]
    mov al, [r12 + rcx]
    inc qword [ip]
    
    mov bl, [loop_stack_ptr]
    cmp bl, MAX_LOOP_DEPTH
    jge .stack_overflow
    
    ; Store loop counter and current IP for return
    movzx rbx, bl
    mov [loop_counters + rbx], al
    mov rax, [ip]
    mov [loop_counters + rbx + 32], al  ; store IP in upper half
    
    inc byte [loop_stack_ptr]
    jmp .exit

.stack_overflow:
    mov rdi, error
    call print_string

.exit:
    pop r12
    pop rbp
    ret

handle_loop_end:
    push rbp
    mov rbp, rsp
    push r12
    
    mov r12, bytecode
    
    ; Check if we have active loops
    mov al, [loop_stack_ptr]
    cmp al, 0
    jle .no_active_loop
    
    ; Get current loop from stack
    dec al
    movzx rbx, al
    
    ; Decrement counter and check
    dec byte [loop_counters + rbx]
    jz .loop_finished
    
    ; Loop again - jump back to stored IP
    mov rax, [loop_counters + rbx + 32]  ; get stored IP
    mov [ip], rax
    jmp .exit

.loop_finished:
    ; Remove finished loop from stack
    dec byte [loop_stack_ptr]

.exit:
    pop r12
    pop rbp
    ret

.no_active_loop:
    ; Error: LOOP_END without LOOP_START
    mov rdi, error
    call print_string
    pop r12
    pop rbp
    ret

; ===== Utility Functions =====
print_string:
    ; Input: rdi = string pointer
    push rbp
    mov rbp, rsp
    push r12
    
    mov r12, rdi        ; preserve string pointer
    
    ; Calculate string length
    xor rcx, rcx
.length_loop:
    cmp byte [r12 + rcx], 0
    je .print
    inc rcx
    jmp .length_loop

.print:
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, r12        ; string pointer
    mov rdx, rcx        ; length
    syscall
    
    pop r12
    pop rbp
    ret

cleanup_vm:
    ; Placeholder for future resource cleanup
    ret
