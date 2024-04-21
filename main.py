import pygame
import json
import asyncio


def draw_level_tiles():
    global level, level_screen
    for y in range(level["size"][1]):
        for x in range(level["size"][0]):
            level_screen.blit(pygame.image.load(f"images/tiles/{level['tile'][y][x]}.png"),
                              (x*BLOCK_SIZE, y*BLOCK_SIZE))

def check_obj(loc):
    for object in level["objs"]:
        for part in object[2]:
            if part[1] + object[1][1] == loc[1] and part[0] + object[1][0] == loc[0]:
                return object

def check_push(loc, v):
    objects = []
    locations = [] + [loc]
    new_locations = []
    while locations != []:
        for location in locations:
            check = check_obj((location[0]+v[0], location[1]+v[1]))
            if check is not None and not check in objects:
                objects += [check]
                for part in check[2]:
                    new_locations += [(part[0] + check[1][0], part[1] + check[1][1])]
            if level["wall"][location[1]+v[1]][location[0]+v[0]] != 0:
                return False
        locations = new_locations[:]
        new_locations = []
    return objects

def get_wall_tile(location, kind):
    tile = 0
    if location[1] != 0:
        if level["wall"][location[1]-1][location[0]] == kind:
            tile += 1
    if location[1] != level["size"][1]-1:
        if level["wall"][location[1]+1][location[0]] == kind:
            tile += 2
    if location[0] != 0:
        if level["wall"][location[1]][location[0]-1] == kind:
            tile += 4
    if location[0] != level["size"][0]-1:
        if level["wall"][location[1]][location[0]+1] == kind:
            tile += 8
    return tile

def draw_level_objects():
    global level, objects_screen
    for y in range(level["size"][1]):
        for object in level["objs"]:
            for part in object[2]:
                if part[1] + object[1][1] == y:
                    objects_screen.blit(pygame.image.load(f"images/{object[0]}/{object[3]}/{object[2].index(part)}.png"),
                                        ((part[0] + object[1][0]) * BLOCK_SIZE + object[4]*moving[0]*-1, (part[1] + object[1][1]) * BLOCK_SIZE + object[4]*moving[1]*-1))
        for x in range(level["size"][0]):
            if level["wall"][y][x] != 0:
                objects_screen.blit(pygame.image.load(f"images/wall/{level['wall'][y][x]-1}/{get_wall_tile((x, y), level['wall'][y][x])}.png"),
                                    (x*BLOCK_SIZE, y*BLOCK_SIZE))


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
level_start = 0
if levels == [{}]:
    editor = True
    level = {"size": (7, 7),
             "start": (4, 4),
             "wall": [[1, 1, 1, 0, 1, 1, 1],
                      [1, 0, 0, 0, 0, 0, 1],
                      [1, 0, 0, 0, 0, 0, 0],
                      [1, 0, 0, 0, 0, 0, 0],
                      [1, 0, 0, 0, 0, 0, 0],
                      [1, 0, 0, 0, 0, 0, 1],
                      [1, 1, 1, 0, 1, 1, 1]],
             "tile": [[0, 0, 0, 1, 0, 0, 0],
                      [0, 1, 1, 1, 1, 1, 0],
                      [0, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 1, 1, 0],
                      [0, 0, 0, 1, 0, 0, 0]],
             "objs": [["box", (2, 2), [(0, 0), (0, 1), (-1, 1), (-1, 2)], 0, False], ["box", (3, 4), [(0, 0)], 0, False], ["box", (4, 3), [(0, 0), (1, 0)], 0, False]]}
else:
    level = levels[level_start]
level_reset = level

pygame.init()

done = False
clock = pygame.time.Clock()
scale = 48//BLOCK_SIZE
moving = (0, 0)
keys = []
display_screen = pygame.display.set_mode((800, 600), flags=pygame.RESIZABLE)
size = (pygame.display.get_window_size()[0]//scale, pygame.display.get_window_size()[1]//scale)
game_screen = pygame.Surface(size)
level_screen = pygame.Surface((level["size"][1]*BLOCK_SIZE, level["size"][0]*BLOCK_SIZE))
objects_screen = pygame.Surface((level["size"][0]*BLOCK_SIZE, (level["size"][1] + 0.5)*BLOCK_SIZE))
objects_screen = objects_screen.convert_alpha()
player_loc = level["start"]
pygame.display.set_caption("Mouse Movers")

draw_level_tiles()
position = 0


async def main():
    global done, moving, player_loc, position, game_screen, level_screen, size
    while not done:
        game_screen.fill((0, 0, 0))
        objects_screen.fill((0, 0, 0, 0))
        draw_level_objects()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keys.append(event.key)
            elif event.type == pygame.KEYUP:
                keys.remove(event.key)
            elif event.type == pygame.WINDOWRESIZED:
                size = (pygame.display.get_window_size()[0]//scale, pygame.display.get_window_size()[1]//scale)
                game_screen = pygame.Surface(size)
        for key in keys:
            if moving == (0, 0):
                if key == pygame.K_RIGHT:
                    if player_loc[0] < level["size"][0]:
                        position = 1
                        check = check_push((player_loc[0]-1, player_loc[1]-1), (1, 0))
                        if check is not False:
                            moving = (BLOCK_SIZE, moving[1])
                            player_loc = (player_loc[0] + 1, player_loc[1])
                            for object in level["objs"]:
                                if object in check:
                                    index = level["objs"].index(object)
                                    level["objs"][index][1] = (level["objs"][index][1][0]+1, level["objs"][index][1][1])
                                    level["objs"][index][4] = True
                                else:
                                    object[4] = False
                        else:
                            moving = (-MOVEMENT_SPEED*WALL_BUMP, moving[1])
                elif key == pygame.K_LEFT:
                    if player_loc[0] > 1:
                        position = 2
                        check = check_push((player_loc[0] - 1, player_loc[1] - 1), (-1, 0))
                        if check is not False:
                            moving = (-BLOCK_SIZE, moving[1])
                            player_loc = (player_loc[0] - 1, player_loc[1])
                            for object in level["objs"]:
                                if object in check:
                                    index = level["objs"].index(object)
                                    level["objs"][index][1] = (level["objs"][index][1][0] - 1, level["objs"][index][1][1])
                                    level["objs"][index][4] = True
                                else:
                                    object[4] = False
                        else:
                            moving = (MOVEMENT_SPEED*WALL_BUMP, moving[1])
                elif key == pygame.K_DOWN:
                    if player_loc[1] < level["size"][1]:
                        position = 0
                        check = check_push((player_loc[0] - 1, player_loc[1] - 1), (0, 1))
                        if check is not False:
                            moving = (moving[0], BLOCK_SIZE)
                            player_loc = (player_loc[0], player_loc[1] + 1)
                            for object in level["objs"]:
                                if object in check:
                                    index = level["objs"].index(object)
                                    level["objs"][index][1] = (level["objs"][index][1][0], level["objs"][index][1][1] + 1)
                                    level["objs"][index][4] = True
                                else:
                                    object[4] = False
                        else:
                            moving = (moving[0], -MOVEMENT_SPEED*WALL_BUMP)
                elif key == pygame.K_UP:
                    if player_loc[1] > 1:
                        position = 3
                        check = check_push((player_loc[0] - 1, player_loc[1] - 1), (0, -1))
                        if check is not False:
                            moving = (moving[0], -BLOCK_SIZE)
                            player_loc = (player_loc[0], player_loc[1] - 1)
                            for object in level["objs"]:
                                if object in check:
                                    index = level["objs"].index(object)
                                    level["objs"][index][1] = (level["objs"][index][1][0], level["objs"][index][1][1] - 1)
                                    level["objs"][index][4] = True
                                else:
                                    object[4] = False
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
        await asyncio.sleep(0)
        clock.tick(60/MOVEMENT_SPEED)
        if moving[0] != 0:
            moving = (moving[0] - MOVEMENT_SPEED * moving[0] / abs(moving[0]), moving[1])
        if moving[1] != 0:
            moving = (moving[0], moving[1] - MOVEMENT_SPEED * moving[1] / abs(moving[1]))

if __name__ == "__main__":
    asyncio.run(main())
