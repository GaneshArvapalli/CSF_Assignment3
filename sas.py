#!/usr/bin/env python3

# scram.py - Really simple virtual machine for binary .scram files.
#
# Hacked by Ganesh Arvapalli <garvapa1@jhu.edu> for
# 600.233: Computer Systems Fundamentals, Fall 2012.
# Ported to Python 3, Summer 2016.
#
# Usage: python3 sas.py < input.s > output.scram
#
# Reads an instruction file representing SCRAM
# standard input. This file can be at *most* 16 bytes long since we
# only have 16 bytes of memory available.
#
# The SCRAM starts running code at address 0. After each and every
# instruction, all of main memory as well as AC and PC is dumped to
# standard output.

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

MAX = None  # maximum # of instructions to execute


def createListOfCommands(lines):
    """strips unnecessary whitespace and new lines and returns list of commands"""
    bigList = []
    for j in range(0, len(lines)):
        tempList = lines[j].split("\t")
        tempList = [cmd for line in tempList for cmd in line.split("\n")]
        tempList = [cmd for line in tempList for cmd in line.split()] 
        bigList.append(tempList)
    bigList = [cmd for sublist in bigList for cmd in sublist] #flattens the array
    return bigList


def removeComments(fileName):
    """remove comments from all lines"""
    lines = open(fileName).readlines()
    for i in range(0, len(lines)):
        if "#" in lines[i]:
            lines[i] = lines[i].split("#")[0]
    return lines


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


def getReferences(commands):
    references = {} 
    for i in range(len(commands)):
        if ":" in commands[i]:
            if i + 2 < len(commands) and commands[i+1].upper() == "DAT":
                 references[commands[i]] = commands[i+2]
    return references


def addToMemory(commands, references):
    address = 0
    #print(bin(address & 0xff))
    for i in range(len(commands)):
        if address > 15:
            sys.stderr.write("Memory out of space. Ending program early...\n")
            break
        if ":" in commands[i]:
            if i + 1 < len(commands) and "DAT".lower() == commands[i+1].lower():
                try:
                    MEMORY[address] = bin(int(commands[i+2]))
                except:
                    sys.stderr.write("Error! Data not found!\n")
            else:
                MEMORY[address] = bin(address & 0xffffffff)
                references[commands[i]] = bin(address & 0xffffffff)
        #elif commands[i].upper() == "LDA" or commands[i].upper() == "LDI":
        elif commands[i] in list(encoding.keys()) and commands[i].upper() != "HLT":
            b = encoding[commands[i]] & 0xffff
            b = b << 4
            if str(type(commands[i+1])) == "str": 
                try:
                    b += int(references[commands[i+1]]) & 0xffff
                    MEMORY[address] = bin(b)
                    i += 1
                except:
                    sys.stderr.write("Error! Address for " + commands[i+1] + " not found!\n")
            elif str(type(commands[i+1])) == "int":
                try:
                    if int(commands[i+1]) < 15:
                        MEMORY[address] = bin(int(commands[i+1]) & 0xffff)
                    else:
                        sys.stderr.write("Error! Data longer than 4 bits!\n")
                except:
                    sys.stderr.write("Error! Op code not followed by int or address!\n")
        elif commands[i].upper() == "HLT":
            print("HLT recognized")
        elif commands[i].upper() == "DAT":
            i+=1
            print(1)
        elif commands[i] not in list(references.keys()):
            sys.stderr.write("Error! " + commands[i] + " is an unrecognizable operation!\n")
        address+=1

def main():
    """Write binary program from file input format it for SCRAM"""
    #ls = removeComments(str(sys.argv[1]))
    ls = removeComments("loop.s")
    cmds = createListOfCommands(ls)
    print(cmds)
    references = getReferences(cmds)
    print(references)
    addToMemory(cmds, references)
    print(MEMORY)
    #f = open(sys.argv[2], "wb")
    f = open("binaryTest.scram", "wb")
    for i in range(0, len(MEMORY)):
        print(type(MEMORY[i]))
        f.write(bytes(MEMORY[i]))
    f.close()

    """if len(binary) > SIZE:
        print("Program too long, truncated from {:d} to {:d} bytes.".format(
            len(binary), SIZE))
        binary = binary[:SIZE]

    for i in range(len(binary)):
        MEMORY[i] = int(binary[i]) & 0xff

    run()"""

if __name__ == "__main__":
    main()
