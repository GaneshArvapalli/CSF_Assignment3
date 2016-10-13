#!/usr/bin/env python3

# sas.py - Code to byte assembler for SCRAM.
#
# Ganesh Arvapalli <garvapa1@jhu.edu>
# 600.233: Computer Systems Fundamentals, Fall 2016.
#
# Usage: python3 sas.py input.s > output.scram
#
# Reads an instruction file representing SCRAM
# standard input with op codes and data.

import sys

# the bit pattern for each SCRAM instruction
encoding = {
    "HLT": 0b0000, "LDA": 0b0001, "LDI": 0b0010,
    "STA": 0b0011, "STI": 0b0100, "ADD": 0b0101,
    "SUB": 0b0110, "JMP": 0b0111, "JMZ": 0b1000,
}


# size of main memory in bytes
SIZE = 16

# content of main memory, we load the binary program here
MEMORY = [0x00 for _ in range(SIZE)]


def createListOfCommands(lines):
    """strips unnecessary whitespace and returns list of commands"""
    bigList = []
    for j in range(0, len(lines)):
        tempList = lines[j].split("\t")
        tempList = [cmd for line in tempList for cmd in line.split("\n")]
        tempList = [cmd for line in tempList for cmd in line.split()]
        bigList.append(tempList)
    # next we flatten the array
    bigList = [cmd for sublist in bigList for cmd in sublist]
    return bigList


def removeComments(fileName):
    """remove comments from all lines"""
    lines = open(fileName).readlines()
    for i in range(0, len(lines)):
        if "#" in lines[i]:
            lines[i] = lines[i].split("#")[0]
    return lines


def getReferences(commands):
    """If a command has DAT after it, stores it in an address"""
    references = {}
    for i in range(len(commands)):
        if ":" in commands[i]:
            if i + 2 < len(commands) and commands[i+1].upper() == "DAT":
                references[commands[i]] = commands[i+2]
    return references


def addToMemory(commands, references):
    """Pretend we have an actual memory and add op codes/data to it"""
    global address
    address = 0
    encKeys = list(encoding.keys())
    for i in range(len(commands)):
        if address > 15:
            sys.stderr.write("Memory out of space. Ending program early...\n")
            break
        if ":" in commands[i]:
            if i + 1 < len(commands) and "DAT" == commands[i+1].upper():
                try:
                    MEMORY[address] = bin(int(commands[i+2]))
                except:
                    sys.stderr.write("Error! Data not found!\n")
            else:
                references[commands[i].replace(":", "")] = address
                address += 1
        elif commands[i] in encKeys and commands[i].upper() != "HLT":
            b = encoding[commands[i]] & 0xf
            b = b << 4
            if (commands[i+1]+":") in list(references.keys()):
                try:
                    b += int(references[(commands[i+1]+":")]) & 0xff
                    MEMORY[address] = bin(b)
                    i += 1
                    address += 1
                except:
                    s = "Error! " + commands[i+1]
                    sys.stderr.write(s + " address not found!\n")
            elif commands[i+1] in list(references.keys()):
                try:
                    b += references[commands[i+1]] & 0xff
                    MEMORY[address] = bin(b)
                    i += 1
                    address += 1
                except:
                    s = "Error! " + commands[i+1]
                    sys.stderr.write(s + " address not found!\n")
            else:
                try:
                    if int(commands[i+1]) < 15:
                        b += int(commands[i+1]) & 0xf
                        MEMORY[address] = bin(b)
                        i += 1
                        address += 1
                    else:
                        sys.stderr.write("Error! Data longer than 4 bits!\n")
                except:
                    s = "Error! Op code not followed by int/address!\n"
                    sys.stderr.write(s)
        elif commands[i].upper() == "HLT":
            b = encoding["HLT"] << 4
            MEMORY[address] = bin(b)
            address += 1
        elif commands[i].upper() == "DAT":
            try:
                if int(commands[i+1]) < 2 ^ 8 - 1:
                    MEMORY[address] = bin(int(commands[i+1]) & 0xff)
                    i += 1
                    address += 1
                else:
                    sys.stderr.write("Error! DAT not followed by 8-bit int!")
            except:
                sys.stderr.write("Error! DAT not followed by int!")
        elif (commands[i]+":") not in list(references.keys()):
            if commands[i] not in list(references.keys()):
                if i-1 > 0 and commands[i-1].upper() != "DAT":
                    if commands[i-1] not in list(encoding.keys()):
                        s = "Error! " + commands[i]
                        sys.stderr.write(s + " is unrecognized operation!\n")


def main():
    """Write binary program from file input format it for SCRAM"""
    filename = sys.argv[-1]

    # The first pass is to recognize commands and clean up the file
    ls = removeComments(filename)
    cmds = createListOfCommands(ls)
    references = getReferences(cmds)

    # The bulk of the processing is done here
    addToMemory(cmds, references)

    # Only print out the MEMORY if it's not part of a JMP/JMZ
    for i in range(0, address):
        if type(MEMORY[i]) is str:
            print(chr(int(MEMORY[i][2:], 2)), end="")


if __name__ == "__main__":
    main()
