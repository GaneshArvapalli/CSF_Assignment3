# Simple counter program in SCRAM assembly.

start:	LDA	count
	ADD	one
	STA	count
	JMP	start

count:	DAT	0	# counter variable
one:	DAT	1	# constant 1
