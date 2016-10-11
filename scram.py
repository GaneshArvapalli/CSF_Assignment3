#!/usr/bin/env python3

# scram.py - Really simple virtual machine for binary .scram files.
#
# Hacked by Peter H. Froehlich <phf@acm.org> for
# 600.333/433: Computer Systems Fundamentals, Fall 2012.
# Ported to Python 3, Summer 2016.
#
# Usage: python scram.py <input.scram [max]
#
# Reads a *binary* file representing all of the SCRAM's memory from
# standard input. This file can be at *most* 16 bytes long since we
# only have 16 bytes of memory available.
#
# The SCRAM starts running code at address 0. After each and every
# instruction, all of main memory as well as AC and PC is dumped to
# standard output.
#
# The SCRAM stops when encountering either the HLT instruction or
# some kind of illegal instruction. If a number is given on the
# command line, the SCRAM stops after that many instructions.

import sys

# the bit pattern for each SCRAM instruction
encoding = {
    "HLT": 0b0000, "LDA": 0b0001, "LDI": 0b0010,
    "STA": 0b0011, "STI": 0b0100, "ADD": 0b0101,
    "SUB": 0b0110, "JMP": 0b0111, "JMZ": 0b1000,
}

# reverse mapping from bit patterns to SCRAM instructions
decoding = dict([[v, k] for k, v in encoding.items()])

# size of main memory in bytes
SIZE = 16

# content of main memory, we load the binary program here
MEMORY = [0x00 for _ in range(SIZE)]

# scram registers: accumulator and program counter
AC = 0
PC = 0

MAX = None  # maximum # of instructions to execute
IC = 0  # instruction counter


if len(sys.argv) > 1:
    MAX = int(sys.argv[1])


def dump():
    """Dump state of SCRAM to stdout."""
    print("AC: 0x{:02x} PC: 0x{:02x}\tMEM: ".format(AC, PC), end="")
    for i in range(SIZE):
        print("0x{:02x} ".format(MEMORY[i]), end="")  # ugly space before EOL
    print()


def upper(b):
    """Return upper four bits of byte b."""
    return (b >> 4) & 0x0f


def lower(b):
    """Return lower four bits of byte b."""
    return b & 0x0f


def run():
    """Run the SCRAM until we're done."""
    global AC, PC, IC
    while True:
        dump()
        inst = MEMORY[PC]
        PC += 1

        code = upper(inst)
        addr = lower(inst)

        if decoding[code] == "HLT":
            print("HLT encountered @", PC-1)
            break
        elif decoding[code] == "LDA":
            AC = MEMORY[addr]
        elif decoding[code] == "LDI":
            t = MEMORY[addr] & 0x0f
            AC = MEMORY[t]
        elif decoding[code] == "STA":
            MEMORY[addr] = AC
        elif decoding[code] == "STI":
            t = MEMORY[addr] & 0x0f
            MEMORY[t] = AC
        elif decoding[code] == "ADD":
            AC = (AC + MEMORY[addr]) & 0xff
        elif decoding[code] == "SUB":
            AC = (AC - MEMORY[addr]) & 0xff
        elif decoding[code] == "JMP":
            PC = addr
        elif decoding[code] == "JMZ":
            if AC == 0:
                PC = addr
        else:
            print("illegal instruction encountered @", PC-1)
            break

        IC += 1
        if MAX and IC >= MAX:
            print("maximum number of instructions reached")
            break


def main():
    """Read binary program from stdin and run it."""
    # using the internal buffer is a bad hack but avoids UTF-8 issues
    binary = sys.stdin.buffer.read()

    if len(binary) > SIZE:
        print("Program too long, truncated from {:d} to {:d} bytes.".format(
            len(binary), SIZE))
        binary = binary[:SIZE]

    for i in range(len(binary)):
        MEMORY[i] = int(binary[i]) & 0xff

    run()


if __name__ == "__main__":
    main()
