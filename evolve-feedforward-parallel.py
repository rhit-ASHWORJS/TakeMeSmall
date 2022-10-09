"""
A parallel version of XOR using neat.parallel.

Since XOR is a simple experiment, a parallel version probably won't run any
faster than the single-process version, due to the overhead of
inter-process communication.

If your evaluation function is what's taking up most of your processing time
(and you should check by using a profiler while running single-process),
you should see a significant performance improvement by evaluating in parallel.

This example is only intended to show how to do a parallel experiment
in neat-python.  You can of course roll your own parallelism mechanism
or inherit from ParallelEvaluator if you need to do something more complicated.
"""

from __future__ import print_function

import math
import os
import time
import smallchess

import neat

import visualize

# 2-input XOR inputs and expected outputs.
xor_inputs = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
xor_outputs = [   (0.0,),     (1.0,),     (1.0,),     (0.0,)]


"""
This function will be run in parallel by ParallelEvaluator.  It takes two
arguments (a single genome and the genome class configuration data) and
should return one float (that genome's fitness).

Note that this function needs to be in module scope for multiprocessing.Pool
(which is what ParallelEvaluator uses) to find it.  Because of this, make
sure you check for __main__ before executing any code (as we do here in the
last few lines in the file), otherwise you'll have made a fork bomb
instead of a neuroevolution demo. :)
"""
samplesize = 100
def eval_genome(genome, config):
    fitness = 0
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    for game in range(samplesize):
        #play a game v.s. random bot
        board = [['b1','b2','b3'],['  ','  ','  '],['  ','  ','  '],['  ','  ','  '],['  ','  ','  '],['w1','w2','w3']]

        #net plays black, so bot makes 1st move
        winner = ""
        turn = "w"
        turnNum = 0
        while(winner == "" and turnNum <= 50):
            if(turn == "w"):
                smallchess.makeRandomAgroMove(board, "w")
                turn = "b"
            elif(turn == "b"):
                output = net.activate(smallchess.flatBoardInts(board))
                moveList = smallchess.getValidMoveList(board, "b")
                wantList = []
                for move in moveList:
                    want = 0
                    movedata = move.split(" ")

                    #piecewant
                    want = want + output[int(movedata[0][1])]

                    #movewant
                    pos = smallchess.getPositionOfPiece(board, movedata[0])
                    movenum = 0
                    i = int(movedata[1])
                    j = int(movedata[2])
                    oi = int(pos[0])
                    oj = int(pos[1])
                    if(oi < i):
                        if(oj < j):
                            movenum = 7
                        if(oj == j):
                            movenum = 6
                        if(oj > j):
                            movenum = 5
                    if(oi == i):
                        if(oj < j):
                            movenum = 8
                        if(oj > j):
                            movenum = 4
                    if(oi > i):
                        if(oj < j):
                            movenum = 9
                        if(oj == j):
                            movenum = 10
                        if(oj > j):
                            movenum = 3
                    want = want + output[movenum]
                    wantList.append(want)

                wantMost = 0
                for i in range(len(wantList)):
                    if(wantList[i] > wantList[wantMost]):
                        wantMost = i
                
                movedata = moveList[wantMost].split(" ")
                # print("----")
                # print(output)
                # print(moveList)
                # print(wantList)
                # print(wantMost)
                smallchess.makeMoveOnBoard(board, movedata[0], movedata[1], movedata[2])
                turn = "w"
            turnNum = turnNum + 1
            winner = smallchess.detectWinner(board)
        
        if(winner == "b"):
            fitness = fitness + 1
        elif(winner != "w"):
            fitness = fitness + 0.01
        else:
            fitness = fitness + 0.0001
    return fitness

def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 300 generations.
    pe = neat.ParallelEvaluator(20, eval_genome)
    winner = p.run(pe.evaluate, 300)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    # output = winner_net.activate(xi)
    # print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))
    print("winner found")

    #I wish to fight this so called, 'winner'
    ####################################
    playing = True
    board = [['b1','b2','b3'],['  ','  ','  '],['  ','  ','  '],['  ','  ','  '],['  ','  ','  '],['w1','w2','w3']]
    for row in board:
        print(row)
    print("moves for w: " + str(smallchess.getValidMoveList(board, "w")))
    # print("moves for b: " + str(getValidMoveList(board, "b")))
    while(True):
        move = input("Make a move\n")

        if(move == "rda"):
            move = smallchess.getRandomAgroMove(board, "w")
        elif(move == "rd"):
            move = smallchess.getRandomMove(board, "w")
        elif(move == "quit"):
            break
        if(move.count(" ")==0):
            move = smallchess.getRandomMove(board, "w")
        moveList = move.split(" ")
        smallchess.makeMoveOnBoard(board, moveList[0], moveList[1], moveList[2])
        # for row in board:
        #     print(row)
        # print("moves for w: " + str(getValidMoveList(board, "w")))
        # print("moves for b: " + str(getValidMoveList(board, "b")))
        # print("------------------")
        if(len(smallchess.getValidMoveList(board, "b"))==0):
            print("Oh no!  You lost!")
            print(smallchess.detectWinner(board))
            board = [['b1','b2','b3'],['  ','  ','  '],['  ','  ','  '],['  ','  ','  '],['  ','  ','  '],['w1','w2','w3']]
            for row in board:
                print(row)
            print("moves for w: " + str(smallchess.getValidMoveList(board, "w")))
            continue
        output = winner_net.activate(smallchess.flatBoardInts(board))
        moveList = smallchess.getValidMoveList(board, "b")
        wantList = []
        for move in moveList:
            want = 0
            movedata = move.split(" ")

            #piecewant
            want = want + output[int(movedata[0][1])]

            #movewant
            pos = smallchess.getPositionOfPiece(board, movedata[0])
            movenum = 0
            i = int(movedata[1])
            j = int(movedata[2])
            oi = int(pos[0])
            oj = int(pos[1])
            if(oi < i):
                if(oj < j):
                    movenum = 7
                if(oj == j):
                    movenum = 6
                if(oj > j):
                    movenum = 5
            if(oi == i):
                if(oj < j):
                    movenum = 8
                if(oj > j):
                    movenum = 4
            if(oi > i):
                if(oj < j):
                    movenum = 9
                if(oj == j):
                    movenum = 10
                if(oj > j):
                    movenum = 3
            want = want + output[movenum]
            wantList.append(want)

        wantMost = 0
        for i in range(len(wantList)):
            if(wantList[i] > wantList[wantMost]):
                wantMost = i
        
        movedata = moveList[wantMost].split(" ")
        # print("----")
        # print(output)
        # print(moveList)
        # print(wantList)
        # print(wantMost)
        smallchess.makeMoveOnBoard(board, movedata[0], movedata[1], movedata[2])
        for row in board:
            print(row)
        if(len(smallchess.getValidMoveList(board, "w"))==0):
            print("Awesome!  You Win!")
            print(smallchess.detectWinner(board))
            board = [['b1','b2','b3'],['  ','  ','  '],['  ','  ','  '],['  ','  ','  '],['  ','  ','  '],['w1','w2','w3']]
            for row in board:
                print(row)
            print("moves for w: " + str(smallchess.getValidMoveList(board, "w")))
            continue
        print("moves for w: " + str(smallchess.getValidMoveList(board, "w")))
        #####################################

    node_names = {-1:'A', -2: 'B', 0:'A XOR B'}
    visualize.draw_net(config, winner, True, node_names = node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)