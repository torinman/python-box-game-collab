import pygame
import json
import asyncio


def draw_level_tiles():
    global level, level_screen
    for y in range(level["size"][1]):
        for x in range(level["size"][0]):
            level_screen.blit(pygame.image.load(f"images/tiles/{level['tile'][y][x]}.png"),
                              (x*BLOCK_SIZE, y*BLOCK_SIZE))


def draw_level_objects():
    global level, objects_screen
    for y in range(level["size"][1]):
        for x in range(level["size"][0]):
            if level["wall"][y][x] != 0:
                objects_screen.blit(pygame.image.load(f"images/wall/{level['wall'][y][x]-1}.png"), (x*BLOCK_SIZE, y*BLOCK_SIZE))


BLOCK_SIZE = 16
MOVEMENT_SPEED = 2
ANIMATION_STEPS = 4
WALL_BUMP = 0
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
             "wall": [[1, 1, 0, 1, 1],
                      [1, 0, 0, 0, 1],
                      [0, 0, 0, 0, 0],
                      [1, 0, 0, 0, 1],
                      [1, 1, 0, 1, 1]],
             "tile": [[0, 0, 1, 0, 0],
                      [0, 1, 1, 1, 0],
                      [1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 0],
                      [0, 0, 1, 0, 0]],
             "objs": []}
else:
    level = levels[0]
level_reset = level

pygame.init()

done = False
clock = pygame.time.Clock()
size = (10*BLOCK_SIZE, 6*BLOCK_SIZE)
scale = 80//BLOCK_SIZE
moving = (0, 0)
keys = []
display_screen = pygame.display.set_mode((size[0]*scale, size[1]*scale))
game_screen = pygame.Surface(size)
level_screen = pygame.Surface((level["size"][1]*BLOCK_SIZE, level["size"][0]*BLOCK_SIZE))
objects_screen = pygame.Surface((level["size"][0]*BLOCK_SIZE, (level["size"][1] + 0.5)*BLOCK_SIZE))
objects_screen = objects_screen.convert_alpha()
player_loc = level["start"]

draw_level_tiles()
position = 0


async def main():
    global done, moving, player_loc, position
    while not done:
        game_screen.fill((0, 0, 0))
        objects_screen.fill((0, 0, 0, 0))
        draw_level_objects()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keys.append(event.key)
            elif event.type == pygame.KEYUP:
                keys.remove(event.key)
        for key in keys:
            if moving == (0, 0):
                if key == pygame.K_RIGHT:
                    if player_loc[0] < level["size"][0]:
                        position = 1
                        if level["wall"][player_loc[1]-1][player_loc[0]] == 0:
                            moving = (BLOCK_SIZE, moving[1])
                            player_loc = (player_loc[0] + 1, player_loc[1])
                        else:
                            moving = (-MOVEMENT_SPEED*WALL_BUMP, moving[1])
                elif key == pygame.K_LEFT:
                    if player_loc[0] > 1:
                        position = 2
                        if level["wall"][player_loc[1] - 1][player_loc[0] - 2] == 0:
                            moving = (-BLOCK_SIZE, moving[1])
                            player_loc = (player_loc[0] - 1, player_loc[1])
                        else:
                            moving = (MOVEMENT_SPEED*WALL_BUMP, moving[1])
                elif key == pygame.K_DOWN:
                    if player_loc[1] < level["size"][1]:
                        position = 0
                        if level["wall"][player_loc[1]][player_loc[0] - 1] == 0:
                            moving = (moving[0], BLOCK_SIZE)
                            player_loc = (player_loc[0], player_loc[1] + 1)
                        else:
                            moving = (moving[0], -MOVEMENT_SPEED*WALL_BUMP)
                elif key == pygame.K_UP:
                    if player_loc[1] > 1:
                        position = 3
                        if level["wall"][player_loc[1]-2][player_loc[0] - 1] == 0:
                            moving = (moving[0], -BLOCK_SIZE)
                            player_loc = (player_loc[0], player_loc[1] - 1)
                        else:
                            moving = (moving[0], MOVEMENT_SPEED*WALL_BUMP)
        game_screen.blit(level_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                        size[1] // 2 - (player_loc[1] - 0.5) * BLOCK_SIZE + moving[1]))
        image = round((((abs(moving[0]+moving[1])//MOVEMENT_SPEED) % ANIMATION_STEPS) * -1) + ANIMATION_STEPS)
        if moving == (0, 0):
            image = 0
        image += position * ANIMATION_STEPS + position
        game_screen.blit(pygame.image.load(f"images/player/{image}.png"),
                         (size[0]//2-0.5*BLOCK_SIZE, size[1]//2-0.5*BLOCK_SIZE))
        game_screen.blit(objects_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                         size[1] // 2 - (player_loc[1]) * BLOCK_SIZE + moving[1]))
        display_screen.blit(pygame.transform.scale(game_screen, (size[0]*scale, size[1]*scale)), (0, 0))
        pygame.display.flip()
        clock.tick(60/MOVEMENT_SPEED)
        if moving[0] != 0:
            moving = (moving[0] - MOVEMENT_SPEED * moving[0] / abs(moving[0]), moving[1])
        if moving[1] != 0:
            moving = (moving[0], moving[1] - MOVEMENT_SPEED * moving[1] / abs(moving[1]))

if __name__ == "__main__":
    asyncio.run(main())
