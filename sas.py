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
                MEMORY[address] = bin(address & 0xff)
                references[commands[i].replace(":", "")] = bin(address & 0xff)
        #elif commands[i].upper() == "LDA" or commands[i].upper() == "LDI":
        elif commands[i] in list(encoding.keys()) and commands[i].upper() != "HLT":
            print(commands[i])
            b = encoding[commands[i]] & 0xf
            b = b << 4
            if (commands[i+1]+":") in list(references.keys()): 
                try:
                    b += int(references[(commands[i+1]+":")]) & 0xff
                    MEMORY[address] = bin(b)
                    print(bin(b))
                    i += 1
                except:
                    sys.stderr.write("Error! Address for " + commands[i+1] + " not found!\n")
            elif str(type(commands[i+1])) == "int":
                try:
                    if int(commands[i+1]) < 15:
                        MEMORY[address] = bin(int(commands[i+1]) & 0xff)
                        i+=1
                    else:
                        sys.stderr.write("Error! Data longer than 4 bits!\n")
                except:
                    sys.stderr.write("Error! Op code not followed by int or address!\n")
            address+=1
        elif commands[i].upper() == "HLT":
            MEMORY[address] = bin(encoding["HLT"]) << 4
            print("HLT recognized")
            address+=1
        elif commands[i].upper() == "DAT":
            i+=1
        elif (commands[i]+":") not in list(references.keys()):
            if commands[i] not in list(references.keys()):
                if i-1 > 0 and commands[i-1].upper() != "DAT":
                    sys.stderr.write("Error! " + commands[i] + " is an unrecognizable operation!\n")


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
    for i in MEMORY:
        print(type(i))
        temp = int(i, 2)
        print(temp)
        #f.write(bytes(temp))
    #for i in range(0, len(MEMORY)):
    #    if str(type(MEMORY[i])) == "bytes":
    #        f.write(bytes(MEMORY[i]))
    f.close()

    """for i in range(len(binary)):
        MEMORY[i] = int(binary[i]) & 0xff
    """
if __name__ == "__main__":
    main()
