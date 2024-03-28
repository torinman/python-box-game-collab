import pygame
import pygame
import json
import asyncio


def draw_level_tiles():
    global level, level_screen
    for y in range(level["size"][1]):
        for x in range(level["size"][0]):
            level_screen.blit(pygame.image.load(f"images/tiles/{level['tile'][y][x]}.png"),
                              (x*BLOCK_SIZE, y*BLOCK_SIZE))


def draw_level_objects(ignore):
    global level, objects_screen
    for y in range(level["size"][1]):
        for x in range(level["size"][0]):
            if level["wall"][y][x] != 0:
                objects_screen.blit(pygame.image.load(f"images/wall/{level['wall'][y][x]-1}.png"), (x*BLOCK_SIZE, y*BLOCK_SIZE))


BLOCK_SIZE = 8
editor = False
levels = []
with open("levels.json", "r") as f:
    for line in f.readlines():
        levels.append(json.loads(line))
print(levels)
if levels == [{}]:
    editor = True
    level = {"size": (5, 5),
             "start": (3, 3),
             "wall": [[1, 1, 1, 1, 1],
                      [1, 0, 0, 0, 1],
                      [1, 0, 0, 0, 1],
                      [1, 0, 0, 0, 1],
                      [1, 1, 1, 1, 1]],
             "tile": [[0, 0, 0, 0, 0],
                      [0, 1, 1, 1, 0],
                      [0, 1, 1, 1, 0],
                      [0, 1, 1, 1, 0],
                      [0, 0, 0, 0, 0]],
             "objs": []}
else:
    level = levels[0]
level_reset = level

pygame.init()

done = False
clock = pygame.time.Clock()
size = (80, 60)
scale = 10
moving = ((0, 0), None)
keys = []
display_screen = pygame.display.set_mode((size[0]*scale, size[1]*scale))
game_screen = pygame.Surface(size)
level_screen = pygame.Surface((level["size"][1]*BLOCK_SIZE, level["size"][0]*BLOCK_SIZE))
objects_screen = pygame.Surface((level["size"][0]*BLOCK_SIZE, (level["size"][1] + 0.5)*BLOCK_SIZE))
objects_screen = objects_screen.convert_alpha()
player_loc = level["start"]
with open("colour_palette.txt", "r") as c:
    colours = c.readlines()

draw_level_tiles()


async def main():
    global done, moving, player_loc
    while not done:
        game_screen.fill((0, 0, 0))
        objects_screen.fill((0, 0, 0, 0))
        draw_level_objects(None)
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keys.append(event.key)
            elif event.type == pygame.KEYUP:
                keys.remove(event.key)
        for key in keys:
            if moving[0] == (0, 0):
                if key == pygame.K_RIGHT:
                    moving = ((8, moving[0][1]), None)
                    player_loc = (player_loc[0]+1, player_loc[1])
                elif key == pygame.K_LEFT:
                    moving = ((-8, moving[0][1]), None)
                    player_loc = (player_loc[0]-1, player_loc[1])
                elif key == pygame.K_DOWN:
                    moving = ((moving[0][0], 8), None)
                    player_loc = (player_loc[0], player_loc[1]+1)
                elif key == pygame.K_UP:
                    moving = ((moving[0][0], -8), None)
                    player_loc = (player_loc[0], player_loc[1]-1)
        game_screen.blit(level_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0][0],
                                        size[1] // 2 - (player_loc[1] - 0.5) * BLOCK_SIZE + moving[0][1]))
        image = round(((moving[0][0]+moving[0][1]) % 8)//4)
        if moving[0] != (0, 0):
            image += 1
            if moving[0][0] != 0:
                if moving[0][0] > 0:
                    image += 6
                else:
                    image += 4
            else:
                if moving[0][1] < 0:
                    image += 2
        game_screen.blit(pygame.image.load(f"images/player/{image}.png"),
                         (size[0]//2-0.5*BLOCK_SIZE, size[1]//2-0.5*BLOCK_SIZE))
        game_screen.blit(objects_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0][0],
                                          size[1] // 2 - (player_loc[1]) * BLOCK_SIZE + moving[0][1]))
        display_screen.blit(pygame.transform.scale(game_screen, (size[0]*scale, size[1]*scale)), (0, 0))
        pygame.display.flip()
        clock.tick(40)
        if moving[0][0] != 0:
            moving = ((moving[0][0]-1*moving[0][0]/abs(moving[0][0]), moving[0][1]), moving[1])
        if moving[0][1] != 0:
            moving = ((moving[0][0], moving[0][1] - 1 * moving[0][1] / abs(moving[0][1])), moving[1])

if __name__ == "__main__":
    asyncio.run(main())
