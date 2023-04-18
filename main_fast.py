import random # For generating random numbers
import sys # We will use sys.exit to exit the program
import pygame
from pygame.locals import * # Basic pygame imports

import pygad
import threading

class PygadThread(threading.Thread):

    def __init__(self):
        super().__init__()

    def run(self):
        ga_instance = pygad.GA(num_generations=20,
                       sol_per_pop=10,
                       num_parents_mating=5,
                       num_genes=1,
                       fitness_func=fitness_func,
                       init_range_low=100.0,
                       init_range_high=200.0,
                       random_mutation_min_val=50.0,
                       random_mutation_max_val=350.0,
                       mutation_by_replacement=True,
                       on_generation=on_generation,
                       suppress_warnings=True)

        ga_instance.run()

last_gen_best_solution = 0
def on_generation(ga_inst):
    global last_gen_best_solution, playery

    best_sol, best_sol_fit, _ = ga_inst.best_solution()

    if playery > best_sol:
        # Go up
        playery = playery - 15
        # GAME_SOUNDS['wing'].play()
    elif playery < best_sol:
        # Go down
        playery = playery + 15
        # GAME_SOUNDS['wing'].play()

    last_gen_best_solution = best_sol

def closest_pipe(playerx, pipes):
    pipe0X = abs(playerx - pipes[0]['x'])
    pipe1X = abs(playerx - pipes[1]['x'])

    if pipe0X < pipe1X:
        return 0
    else:
        return 1

def fitness_func(ga_instance, solution, solution_idx):
    global playery, pipeHeight, playerx, upperPipes, lowerPipes, GAME_SPRITES, GROUNDY

    if type(solution) is int:
        pass
    else:
        solution = solution[0]

    if solution < 0:
        return -8888

    if solution > GROUNDY - 25:
        return -9999

    fitness_ground = abs(solution - GROUNDY)
    if fitness_ground < 50:
        fitness_ground = (-1.0/fitness_ground) * 999999
    
    nearest_upper_pipe = upperPipes[closest_pipe(playerx, upperPipes)]
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    fitness_upper = abs(solution - (pipeHeight + nearest_upper_pipe['y']))
    if(solution < pipeHeight + nearest_upper_pipe['y'] + 50 and abs(playerx - nearest_upper_pipe['x']) < GAME_SPRITES['pipe'][0].get_width() + 50):
        fitness_upper = (-1.0/fitness_upper) * 999999
    else:
        fitness_upper = fitness_upper

    nearest_lower_pipe = lowerPipes[closest_pipe(playerx, lowerPipes)]
    fitness_lower = abs(solution + GAME_SPRITES['player'].get_height() - nearest_lower_pipe['y']) # + abs(playerx - pipe['x']) - GAME_SPRITES['pipe'][0].get_width()
    if (solution + GAME_SPRITES['player'].get_height() > nearest_lower_pipe['y'] - 50) and abs(playerx - nearest_lower_pipe['x']) < GAME_SPRITES['pipe'][0].get_width() + 50:
        fitness_lower = (-1.0/fitness_lower) * 999999
    else:
        fitness_lower = fitness_lower

    fitness = (fitness_ground + fitness_upper + fitness_lower)/3
    return fitness

# Global Variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'

def welcomeScreen():
    """
    Shows welcome images on the screen
    """

    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))    
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))    
                SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))    
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))    
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame():
    global playerx, playery, upperPipes, lowerPipes
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH/2), 'y': newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200+ (SCREENWIDTH/2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -20

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
        if crashTest:
            return   

        #check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos <= playerMidPos < pipeMidPos + abs(pipeVelX):
                score += 1
                print(f"Your score is {score}") 
                GAME_SOUNDS['point'].play()

        # move pipes to the left
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0 < upperPipes[0]['x'] < abs(pipeVelX) + 1:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    pygad_thread = PygadThread()
    pygad_thread.run()

    # print(playery, fitness_func(None, playery, 0))
    if playery > GROUNDY - 25  or playery < 0:
        print("Ground", playery, fitness_func(None, playery, 0))
        # If the player hit the upper part of the screen.
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            print("Upper", playery, fitness_func(None, playery, 0))
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            print("Lower", playery, fitness_func(None, playery, 0))
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
    global pipeHeight
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, # upper Pipe
        {'x': pipeX, 'y': y2} # lower Pipe
    ]
    return pipe

if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init() # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Unbeaten PyGAD Plays Flappy Bird')
    GAME_SPRITES['numbers'] = ( 
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] =pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] =pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180), 
    pygame.image.load(PIPE).convert_alpha()
    )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
    
    while True:
        welcomeScreen() # Shows welcome screen to the user until he presses a button
        mainGame() # This is the main game function 

