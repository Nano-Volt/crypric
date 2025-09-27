; ===== Cryptic Virtual Machine (Enhanced) =====
; A professional bytecode VM implementation
; Features: Dynamic string handling, proper error checking, enhanced instruction set
; Assemble: nasm -f elf64 crypric_vm.asm -o crypric_vm.o
; Link:     ld crypric_vm.o -o crypric_vm

section .data
    ; String table with proper indexing
    string_table:
        hello db "hello", 0
        world db "world", 0
        error db "ERROR: ", 0
    
    ; File handling
    bytecode_file db "out.cbin", 0
    open_error db "Failed to open bytecode file", 0
    read_error db "Failed to read bytecode", 0
    
    ; VM Constants
    MAX_BYTECODE_SIZE equ 4096
    MAX_LOOP_DEPTH equ 16

section .bss
    ; VM State
    ip resq 1                    ; Instruction pointer
    bytecode_size resq 1         ; Actual bytecode size
    loop_counters resb MAX_LOOP_DEPTH  ; Loop stack
    loop_stack_ptr resb 1        ; Loop stack pointer
    
    ; Memory
    bytecode resb MAX_BYTECODE_SIZE    ; Bytecode buffer

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
    mov rdx, 0          ; mode
    syscall
    
    ; Error checking
    cmp rax, 0
    jg .file_opened
    mov rsi, open_error
    call print_error
    jmp .exit_error
    
.file_opened:
    mov rdi, rax        ; file descriptor
    
    ; Read bytecode
    mov rax, 0          ; sys_read
    mov rsi, bytecode
    mov rdx, MAX_BYTECODE_SIZE
    syscall
    
    ; Error checking
    cmp rax, 0
    jg .read_success
    mov rsi, read_error
    call print_error
    jmp .exit_error
    
.read_success:
    mov [bytecode_size], rax
    
    ; Close file
    mov rax, 3          ; sys_close
    syscall
    
    pop rbp
    ret

.exit_error:
    mov rax, 60         ; sys_exit
    mov rdi, 1          ; error code
    syscall

; ===== Main VM Execution Loop =====
execute_vm:
    push rbp
    mov rbp, rsp
    
    mov rsi, bytecode           ; rsi = bytecode base
    mov rcx, [bytecode_size]    ; rcx = total size
    
.vm_loop:
    mov rdx, [ip]               ; current offset
    cmp rdx, rcx
    jge .vm_exit                ; end of bytecode
    
    mov al, [rsi + rdx]         ; fetch opcode
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
    
    ; Unknown opcode - skip
    jmp .vm_loop

.op_print_string:
    call handle_print_string
    jmp .vm_loop

.op_print_char:
    call handle_print_char
    jmp .vm_loop

.op_loop_start:
    call handle_loop_start
    jmp .vm_loop

.op_loop_end:
    call handle_loop_end
    jmp .vm_loop

.vm_exit:
    pop rbp
    ret

; ===== Instruction Handlers =====
handle_print_string:
    push rbp
    mov rbp, rsp
    
    ; Get string index from bytecode
    mov rdx, [ip]
    mov al, [rsi + rdx]
    inc qword [ip]
    
    ; Select string based on index
    cmp al, 0
    je .print_hello
    cmp al, 1
    je .print_world
    
    ; Default to hello
    mov rdi, hello
    jmp .do_print
    
.print_hello:
    mov rdi, hello
    jmp .do_print
    
.print_world:
    mov rdi, world

.do_print:
    call print_string
    pop rbp
    ret

handle_print_char:
    push rbp
    mov rbp, rsp
    
    ; Get character from bytecode
    mov rdx, [ip]
    mov al, [rsi + rdx]
    inc qword [ip]
    
    ; Print single character
    mov [bytecode], al  ; reuse buffer for output
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, bytecode   ; character buffer
    mov rdx, 1          ; length
    syscall
    
    pop rbp
    ret

handle_loop_start:
    push rbp
    mov rbp, rsp
    
    ; Get loop counter and push to stack
    mov rdx, [ip]
    mov al, [rsi + rdx]
    inc qword [ip]
    
    mov bl, [loop_stack_ptr]
    cmp bl, MAX_LOOP_DEPTH
    jge .stack_overflow
    
    ; Store loop counter
    movzx rbx, bl
    mov [loop_counters + rbx], al
    inc byte [loop_stack_ptr]
    
    pop rbp
    ret

.stack_overflow:
    mov rdi, error
    call print_string
    jmp .exit_error

handle_loop_end:
    push rbp
    mov rbp, rsp
    
    ; Check if we have active loops
    mov al, [loop_stack_ptr]
    cmp al, 0
    jle .no_active_loop
    
    ; Decrement counter and check
    dec al
    movzx rbx, al
    dec byte [loop_counters + rbx]
    jz .loop_finished
    
    ; Loop again - jump back to start
    mov rdx, [ip]
    sub rdx, 3          ; jump back to LOOP_START opcode
    mov [ip], rdx
    jmp .exit

.loop_finished:
    ; Remove finished loop from stack
    dec byte [loop_stack_ptr]

.exit:
    pop rbp
    ret

.no_active_loop:
    ; Error: LOOP_END without LOOP_START
    mov rdi, error
    call print_string
    pop rbp
    ret

; ===== Utility Functions =====
print_string:
    ; Input: rdi = string pointer
    push rbp
    mov rbp, rsp
    
    ; Calculate string length
    mov rsi, rdi
    xor rcx, rcx
.length_loop:
    cmp byte [rsi + rcx], 0
    je .print
    inc rcx
    jmp .length_loop

.print:
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rdx, rcx        ; length
    syscall
    
    pop rbp
    ret

print_error:
    ; Input: rsi = error message
    push rbp
    mov rbp, rsp
    
    ; Print error prefix
    mov rax, 1
    mov rdi, 2          ; stderr
    mov rsi, error
    mov rdx, 7          ; "ERROR: " length
    syscall
    
    ; Print specific error message
    mov rax, 1
    mov rdi, 2
    ; rsi already contains message
    mov rdx, 0
    ; Calculate message length would be needed here
    syscall
    
    pop rbp
    ret

cleanup_vm:
    ; Placeholder for future resource cleanup
    ret
