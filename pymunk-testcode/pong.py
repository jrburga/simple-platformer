import sys, random
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util

class Ball(pymunk.Body):
    def __init__(self, mass, radius, position):
        '''
        mass = value [float]
        '''
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        pymunk.Body.__init__(self, mass, inertia)
        self.elasticity = 1
        self.position = position
        self.shape = pymunk.Circle(self, radius, (0, 0))

class Paddle(pymunk.Body):
    def __init__(self, mass, size, position):
        '''
        mass = value [float]
        with = value ]int]
        position = (x, y) [ints]    (defines center)
        '''
        inertia = pymunk.moment_for_box(mass, size)
        pymunk.Body.__init__(self, mass, inertia)
        a = (position[0], position[1]+size[1]/2)
        b = (position[0], position[1]-size[1]/2)
        self.shape = pymunk.Segment(self, a, b, size[0])

    def move_paddle(self):
        print '----------'
        print self.position
        print 300-pygame.mouse.get_pos()[1]
        print '-----------'
        dm = (300-pygame.mouse.get_pos()[1])-self.position[1]
        # self.position
        # print dm
        self.apply_force_at_local_point((0, dm*100), (0, 0))



class World(pymunk.Space):
    def __init__(self):
        pymunk.Space.__init__(self)
        self.gravity = (0, 0)
    def add_body(self, body):
        self.add(body, body.shape)


# def add_paddle(space):
# 	paddle = pymunk.

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()
    step = 50

    space = World()
    ball = Ball(.001, 5, (300, 300))
    left_paddle = Paddle(100, [5, 60], [10, 300])
    space.add_body(ball)
    space.add_body(left_paddle)
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    ticks_to_next_ball = 10
    ball.apply_force_at_local_point((-10, 0), (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        left_paddle.move_paddle()
        # print left_paddle.force


        screen.fill((255,255,255))
        space.debug_draw(draw_options)
        space.step(1./step)
        pygame.display.flip()
        clock.tick(step)

if __name__ == '__main__':
    main()