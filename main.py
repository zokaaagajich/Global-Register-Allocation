#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import graphColoring as gc
import livenessAnalysis as la


def spilledVarsWriteToFile(inPath, outPath, spilled_vertexes, coloring):

    spilled_occurrence = {k:False for k in spilled_vertexes}

    #open input file
    inFile = open(inPath, 'r')

    instructions = inFile.readlines()
    new_instructions = []
    for instr in instructions:

        varFromMemory = []
        varToMemory = []
        for spilled in spilled_vertexes:
            if instr.find(spilled) != -1:
                if spilled_occurrence[spilled] == False:
                    varToMemory.append(spilled)
                    spilled_occurrence[spilled] = True
                else:
                    varFromMemory.append(spilled)

        #other occurrences
        for spilled in varFromMemory:
            new_instructions.append("x: {} := M[{}_loc]\n".format(spilled, spilled))

        new_instructions.append(instr)

        #first occurrences
        for spilled in varToMemory:
            new_instructions.append("x: M[{}_loc] := {}\n".format(spilled, spilled))

    inFile.close()

    #replace all variables that is not spilled with their allocated register
    instructions = []
    for instr in new_instructions:
        for k, v in coloring.items():
            instr = instr.replace(' ' + k, ' r' + str(v))
        instructions.append(instr)

    changeInstrNumerationAndWrite(instructions, outPath)


def changeInstrNumerationAndWrite(instructions, outPath):
    #open output file and write new instructions
    outFile = open(outPath, 'w')

    #change numeration
    for num, instr in enumerate(instructions):
        new_instr = instr

        #change goto number
        if instr.find('goto') != -1:
            gotoNum = int(instr.split(' ')[-1])
            new_goto = numOfInsertedInstr(gotoNum, instructions) + gotoNum
            new_instr = instr.rsplit(' ', 1)[0] + ' ' + str(new_goto) + '\n'

        #remove instruction number
        instr = new_instr.split(':', 1)[1].lstrip()
        #new number apply
        instr = str(num+1) + ": " + instr
        outFile.write(instr)

    outFile.close()


def numOfInsertedInstr(currentInstrNum, instructions):
    num = 0
    for instr in instructions:
        i = instr.split(':', 1)[0].strip()
        if i == 'x':
            num += 1
        elif int(i) >= currentInstrNum:
            return num
    return num



def main():
    #parsing arguments of command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--visual', action = "store_true")
    parser.add_argument('path', help = "path to input json file")
    args = parser.parse_args()

    #open input code, do liveness analysis and get adjacents list for graph
    graph = la.modelGraph(la.livenessAnalysis(args.path))

    outPath = "outputCode.txt"

    g = gc.Graph(graph)
    print("Initial graph:")
    print(g)

    #number of colors for graph coloring
    k = 2
    #optional: set color for some vertexes
    #coloring = {'a': 0, 'f':0}
    if args.visual:
        colored_graph, spilled_vertexes = gc.visual_graph_coloring(g, k)
    else:
        colored_graph, spilled_vertexes = g.spill(k)

    print("Number of colors used: ", gc.used_colors(colored_graph))
    print("Graph coloring: ", colored_graph)
    print("Spilled: ", spilled_vertexes)
    spilledVarsWriteToFile(args.path, outPath, spilled_vertexes, colored_graph)
    print("OUTPUT FILE: ", outPath)

if __name__ == "__main__":
    main()
