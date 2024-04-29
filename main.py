import pygame
import json
import asyncio
import copy

levels = []
with open("levels.json", "r") as f:
    for line in f.readlines():
        levels.append(json.loads(line))
level_start = 0
editor = False
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
             "objs": [["box", (2, 2), [(0, 0), (0, 1), (-1, 1), (-1, 2)], 0, False],
                      ["box", (3, 4), [(0, 0)], 0, False], 
                      ["box", (4, 3), [(0, 0), (1, 0)], 0, False]]}
else:
    level = levels[level_start]

def draw_level_tiles():
    global level, level_screen
    level_screen = level_screen.convert_alpha()
    level_screen.fill((0, 0, 0, 0))
    for y in range(level["size"][1]):
        for x in range(level["size"][0]):
            level_screen.blit(pygame.image.load(f"images/tiles/{level['tile'][y][x]}.png"),
                              (x * BLOCK_SIZE, y * BLOCK_SIZE))


def check_obj(loc):
    for obj in level["objs"]:
        for part in obj[2]:
            if part[1] + obj[1][1] == loc[1] and part[0] + obj[1][0] == loc[0]:
                return obj


def check_push(loc, v):
    objs = []
    locations = [] + [loc]
    new_locations = []
    while locations:
        for location in locations:
            check = check_obj((location[0] + v[0], location[1] + v[1]))
            if check is not None and check not in objs:
                objs += [check]
                for part in check[2]:
                    new_locations += [(part[0] + check[1][0], part[1] + check[1][1])]
            if level["wall"][location[1] + v[1]][location[0] + v[0]] != 0:
                return False
        locations = new_locations[:]
        new_locations = []
    return objs


def get_wall_tile(location, kind):
    tile = 0
    if location[1] != 0:
        if level["wall"][location[1] - 1][location[0]] == kind:
            tile += 1
    if location[1] != level["size"][1] - 1:
        if level["wall"][location[1] + 1][location[0]] == kind:
            tile += 2
    if location[0] != 0:
        if level["wall"][location[1]][location[0] - 1] == kind:
            tile += 4
    if location[0] != level["size"][0] - 1:
        if level["wall"][location[1]][location[0] + 1] == kind:
            tile += 8
    return tile


def draw_level_objs():
    global level, objs_screen
    for y in range(level["size"][1]):
        for obj in level["objs"]:
            for part in obj[2]:
                if part[1] + obj[1][1] == y:
                    objs_screen.blit(
                        pygame.image.load(f"images/{obj[0]}/{obj[3]}/{obj[2].index(part)}.png"),
                        ((part[0] + obj[1][0]) * BLOCK_SIZE + obj[4] * moving[0] * -1,
                         (part[1] + obj[1][1]) * BLOCK_SIZE + obj[4] * moving[1] * -1))
        for x in range(level["size"][0]):
            if level["wall"][y][x] != 0:
                objs_screen.blit(pygame.image.load(
                    f"images/wall/{level['wall'][y][x] - 1}/{get_wall_tile((x, y), level['wall'][y][x])}.png"),
                    (x * BLOCK_SIZE, y * BLOCK_SIZE))


BLOCK_SIZE = 16
MOVEMENT_SPEED = 2
ANIMATION_STEPS = 4
WALL_BUMP = 0

pygame.init()

done = False
clock = pygame.time.Clock()
scale = 48 // BLOCK_SIZE
moving = (0, 0)
keys = []
display_screen = pygame.display.set_mode((800, 600), flags=pygame.RESIZABLE)
size = (pygame.display.get_window_size()[0] // scale, pygame.display.get_window_size()[1] // scale)
game_screen = pygame.Surface(size).convert_alpha()
level_screen = pygame.Surface((level["size"][1] * BLOCK_SIZE, level["size"][0] * BLOCK_SIZE))
objs_screen = pygame.Surface((level["size"][0] * BLOCK_SIZE, (level["size"][1] + 0.5) * BLOCK_SIZE))
objs_screen = objs_screen.convert_alpha()
player_loc = level["start"]
pygame.display.set_caption("Mouse Movers")
level_reset = copy.deepcopy(level["objs"])
position = 0
history = [(copy.deepcopy(level["objs"]), player_loc, moving, position)]

draw_level_tiles()
backwards = False


async def main():
    global done, moving, player_loc, position, game_screen, level_screen, size, history, level, backwards
    while not done:
        game_screen.fill((69,43,63,255))
        objs_screen.fill((0, 0, 0, 0))
        draw_level_objs()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keys.append(event.key)
                if event.key == pygame.K_r:
                    level["objs"] = level_reset
                    draw_level_objs()
                    player_loc = level["start"]
            elif event.type == pygame.KEYUP:
                keys.remove(event.key)
            elif event.type == pygame.WINDOWRESIZED:
                size = (pygame.display.get_window_size()[0] // scale, pygame.display.get_window_size()[1] // scale)
                game_screen = pygame.Surface(size)
        for key in keys:
            if moving == (0, 0):
                if key == pygame.K_u:
                    if len(history) > 1:
                        level["objs"] = copy.deepcopy(history[-2][0])
                        for index, obj in enumerate(level["objs"]):
                            obj[4] = history[-1][0][index][4]
                        moving = (history[-1][2][0]*-1, history[-1][2][1]*-1)
                        draw_level_objs()
                        player_loc = history[-2][1]
                        position = history[-1][3]
                        history.pop(-1)
                        backwards = True
                else:
                    backwards = False
                if key == pygame.K_RIGHT:
                    if player_loc[0] < level["size"][0]:
                        position = 1
                        check = check_push((player_loc[0] - 1, player_loc[1] - 1), (1, 0))
                        if check is not False:
                            moving = (BLOCK_SIZE, moving[1])
                            player_loc = (player_loc[0] + 1, player_loc[1])
                            for obj in level["objs"]:
                                if obj in check:
                                    index = level["objs"].index(obj)
                                    level["objs"][index][1] = (
                                        level["objs"][index][1][0] + 1, level["objs"][index][1][1])
                                    level["objs"][index][4] = True
                                else:
                                    obj[4] = False
                        else:
                            moving = (-MOVEMENT_SPEED * WALL_BUMP, moving[1])
                elif key == pygame.K_LEFT:
                    if player_loc[0] > 1:
                        position = 2
                        check = check_push((player_loc[0] - 1, player_loc[1] - 1), (-1, 0))
                        if check is not False:
                            moving = (-BLOCK_SIZE, moving[1])
                            player_loc = (player_loc[0] - 1, player_loc[1])
                            for obj in level["objs"]:
                                if obj in check:
                                    index = level["objs"].index(obj)
                                    level["objs"][index][1] = (
                                        level["objs"][index][1][0] - 1, level["objs"][index][1][1])
                                    level["objs"][index][4] = True
                                else:
                                    obj[4] = False
                        else:
                            moving = (MOVEMENT_SPEED * WALL_BUMP, moving[1])
                elif key == pygame.K_DOWN:
                    if player_loc[1] < level["size"][1]:
                        position = 0
                        check = check_push((player_loc[0] - 1, player_loc[1] - 1), (0, 1))
                        if check is not False:
                            moving = (moving[0], BLOCK_SIZE)
                            player_loc = (player_loc[0], player_loc[1] + 1)
                            for obj in level["objs"]:
                                if obj in check:
                                    index = level["objs"].index(obj)
                                    level["objs"][index][1] = (
                                        level["objs"][index][1][0], level["objs"][index][1][1] + 1)
                                    level["objs"][index][4] = True
                                else:
                                    obj[4] = False
                        else:
                            moving = (moving[0], -MOVEMENT_SPEED * WALL_BUMP)
                elif key == pygame.K_UP:
                    if player_loc[1] > 1:
                        position = 3
                        check = check_push((player_loc[0] - 1, player_loc[1] - 1), (0, -1))
                        if check is not False:
                            moving = (moving[0], -BLOCK_SIZE)
                            player_loc = (player_loc[0], player_loc[1] - 1)
                            for obj in level["objs"]:
                                if obj in check:
                                    index = level["objs"].index(obj)
                                    level["objs"][index][1] = (
                                        level["objs"][index][1][0], level["objs"][index][1][1] - 1)
                                    level["objs"][index][4] = True
                                else:
                                    obj[4] = False
                        else:
                            moving = (moving[0], MOVEMENT_SPEED * WALL_BUMP)
                if player_loc != history[-1][1]:
                    history = history + [(copy.deepcopy(level["objs"]), player_loc, moving, position)]
        game_screen.blit(level_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                        size[1] // 2 - (player_loc[1] - 0.5) * BLOCK_SIZE + moving[1]))
        image = round((((abs(moving[0] + moving[1]) // MOVEMENT_SPEED) % ANIMATION_STEPS) * (backwards * 2 - 1)) + ANIMATION_STEPS * (-backwards+1))
        if moving == (0, 0):
            image = 0
        image += position * ANIMATION_STEPS + position
        game_screen.blit(pygame.image.load(f"images/player/{image}.png"),
                         (size[0] // 2 - 0.5 * BLOCK_SIZE, size[1] // 2 - 0.5 * BLOCK_SIZE))
        game_screen.blit(objs_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                      size[1] // 2 - (player_loc[1]) * BLOCK_SIZE + moving[1]))
        display_screen.blit(pygame.transform.scale(game_screen, (size[0] * scale, size[1] * scale)), (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(10 / MOVEMENT_SPEED)
        if moving[0] != 0:
            moving = (moving[0] - MOVEMENT_SPEED * moving[0] / abs(moving[0]), moving[1])
            if moving[0] == 0:
                for object in level["objs"]:
                    object[4] = False
        if moving[1] != 0:
            moving = (moving[0], moving[1] - MOVEMENT_SPEED * moving[1] / abs(moving[1]))
            if moving[1] == 0:
                for object in level["objs"]:
                    object[4] = False


if __name__ == "__main__":
    asyncio.run(main())
