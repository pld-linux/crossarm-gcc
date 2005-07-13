
		.set	SYSTEM_MODE,		0x1F
		.set	UNDEFINED_MODE,		0x1B
		.set	ABORT_MODE,		0x17
		.set	SUPERVISOR_MODE,	0x13
		.set	IRQ_MODE,		0x12
		.set	FIQ_MODE,		0x11
		.set	USER_MODE,		0x10

		.text
		.arm
		.org	0
		.align	0

# exception vectors

		b	reset_handler
		ldr	pc, undefined_instruction_handler_addr
		ldr	pc, software_interrupt_handler_addr
		ldr	pc, prefetch_abort_handler_addr
		ldr	pc, data_abort_handler_addr
		ldr	pc, endless_loop	/* ARM-reserved vector */
		ldr	pc, irq_handler_addr
		ldr	pc, fiq_handler_addr

undefined_instruction_handler_addr:	.long	undefined_instruction_handler
software_interrupt_handler_addr:	.long	software_interrupt_handler
prefetch_abort_handler_addr:		.long	prefetch_abort_handler
data_abort_handler_addr:		.long	data_abort_handler
irq_handler_addr:			.long	irq_handler
fiq_handler_addr:			.long	fiq_handler

.global	reset_handler
reset_handler:

		msr	cpsr_c, #UNDEFINED_MODE
		ldr	sp, =__UNDEFINED_SP__
		msr	cpsr_c, #ABORT_MODE
		ldr	sp, =__ABORT_SP__
		msr	cpsr_c, #IRQ_MODE
		ldr	sp, =__IRQ_SP__
		msr	cpsr_c, #FIQ_MODE
		ldr	sp, =__FIQ_SP__
		msr	cpsr_c, #SUPERVISOR_MODE
		ldr	sp, =__SUPERVISOR_SP__

# setup a default stack limit (when compiled with "-mapcs-stack-check").
#		sub	sl, sp, #__USER_STACK_SIZE__

# relocate .data(rw) section (copy from FLASH to RAM).

		ldr	r1, =__text_end__
		ldr	r2, =__data_start__
		ldr	r3, =__data_end__

reset_handler_L01:

		cmp	r2, r3
		ldrlo	r0, [r1], #4
		strlo	r0, [r2], #4
		blo	reset_handler_L01

# clear .bss(rw) section.

		mov	r0, #0
		ldr	r1, =__bss_start__
		ldr	r2, =__bss_end__

reset_handler_L02:

		cmp	r1, r2
		strlo	r0, [r1], #4
		blo	reset_handler_L02

# set up arguments to main() and call.

		mov	r0, #0
		mov	r1, #0
		bl	main

.global endless_loop
endless_loop:
		b	endless_loop

		.end
