# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using
# sprite-sheets-and-drawing-the-background
# I've added some code to fail if the file wasn't found..
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)

import pygame

class SpriteSheet(object):
    def __init__(self, filename, dimensions, colorkey=None, scale=None):
        try:
            sheet = pygame.image.load(filename).convert()
            if colorkey:
                sheet.set_colorkey(colorkey)
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message

        width, height = dimensions
        size_x, size_y = sheet.get_size()
        self.images = []
        
        for y in xrange(0, size_y, height):
            strip = []
            for x in xrange(0, size_x, width):
                image = pygame.Surface((width, height))
                image.set_colorkey((0, 0, 0))
                image.blit(sheet, (0, 0), (x, y, x+width, y+width))


                if scale:
                    image = pygame.transform.scale(image, scale)
                strip.append(image)
            self.images.append(strip)
        # print self.images
    # Load a specific image from a specific rectangle
    def image(self, position):
        "Loads image from x,y,x+offset,y+offset"
        x, y = position
        return self.images[y][x]

class Animation(object):
    def __init__(self, filename, dimensions, colorkey=None, scale=None, frame_rate=10):
        self.sprite_sheet = SpriteSheet(filename, dimensions, colorkey, scale)
        self.fps = frame_rate
        self.last_time = pygame.time.get_ticks()
        self.cols, self.rows = len(self.sprite_sheet.images), len(self.sprite_sheet.images[0])
        self.row = 0
        self.col = 0

    def animate(self, row):
        assert row < self.rows
        self.row = row
    def next(self):
        if (pygame.time.get_ticks()-self.last_time) >= 1000./self.fps:
            self.col = (self.col+1)%self.cols
            self.last_time = pygame.time.get_ticks()
        return self.sprite_sheet.image((self.col, self.row))

    def default(self):
        return self.sprite_sheet.image((0, self.row))


# pygame.init()

# screen = pygame.display.set_mode((300, 300))
# ss = Animation('images/goomba_sheet-1.png', (32, 32), (255, 0, 255))
# ss.animate(3)
# running = True
# while running:
#     screen.blit(ss.next(), (0, 0))
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#     pygame.display.flip()

# pygame.display.quit()


