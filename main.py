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
    global level
    objs = []
    obj_changes = []
    locations = [] + [loc]
    new_locations = []
    while locations:
        for location in locations:
            check = check_obj((location[0] + v[0], location[1] + v[1]))
            if check is not None and check not in objs:
                objs += [check]
                remove = []
                for part in check[2]:
                    new_location = (part[0] + check[1][0], part[1] + check[1][1])
                    if [new_location[0] + v[0], new_location[1] + v[1]] in level["doors"]:
                        remove += [part]
                    else:
                        new_locations += [new_location]
                if remove:
                    if check[5]:
                        obj_changes += [(check, remove)]
                    else:
                        return False
            if not (location[0] + v[0] >= level["size"][0] or location[1] + v[1] >= level["size"][1] or
                    location[0] + v[0] < 0 or location[1] + v[1] < 0):
                if level["wall"][location[1] + v[1]][location[0] + v[0]] != 0:
                    return False
            else:
                return False
        locations = new_locations[:]
        new_locations = []
    return objs, obj_changes


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


def move(v, p):
    global position, player_loc, moving, level, level_start, level_reset, history
    position = p
    check = check_push((player_loc[0] - 1, player_loc[1] - 1), v)
    if check is not False:
        moving = (BLOCK_SIZE * v[0], BLOCK_SIZE * v[1])
        player_loc = (player_loc[0] + v[0], player_loc[1] + v[1])
        for obj in level["objs"]:
            if obj in check[0]:
                index = level["objs"].index(obj)
                for remove in check[1]:
                    if remove[0] == obj:
                        for r in remove[1]:
                            level["objs"][index][2].remove(r)
                level["objs"][index][1] = (level["objs"][index][1][0] + v[0], level["objs"][index][1][1] + v[1])
                level["objs"][index][4] = True
            else:
                obj[4] = False
        finished = True
        for obj in level["objs"]:
            if obj[5] and obj[2]:
                finished = False
        if finished:
            level_start += 1
            level = levels[level_start]
            player_loc = level["start"]
            level_reset = copy.deepcopy(level["objs"])
            position = 0
            history = [(copy.deepcopy(level["objs"]), player_loc, moving, position)]
            draw_level_tiles()
            moving = (0, 0)
            objs_screen.fill((0, 0, 0, 0))
            draw_level_objs()
            position = 0
    else:
        moving = (MOVEMENT_SPEED * WALL_BUMP * -1 * v[0], MOVEMENT_SPEED * WALL_BUMP * -1 * v[1])


BLOCK_SIZE = 16
MOVEMENT_SPEED = 4
ANIMATION_STEPS = 4
step_speed = 2
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
objs_screen.fill((0, 0, 0, 0))
draw_level_objs()
player_loc = level["start"]
pygame.display.set_caption("Mouse Movers")
level_reset = copy.deepcopy(level["objs"])
position = 0
history = [(copy.deepcopy(level["objs"]), player_loc, moving, position)]

draw_level_tiles()
backwards = False

player_images = []
for i in range((ANIMATION_STEPS+1)*4):
    player_images.append(pygame.image.load(f"images/player/{i}.png"))


async def main():
    global done, moving, player_loc, position, game_screen, level_screen, size, history, level, backwards, step_speed
    while not done:
        game_screen.fill((69, 43, 63, 255))
        draw = False
        if moving[0] + moving[1] != 0:
            for obj in level["objs"]:
                if obj[4]:
                    draw = True
        if draw:
            objs_screen.fill((0, 0, 0, 0))
            draw_level_objs()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    level["objs"] = copy.deepcopy(level_reset)
                    draw_level_objs()
                    player_loc = level["start"]
                    position = 0
                    objs_screen.fill((0, 0, 0, 0))
                    draw_level_objs()
                elif event.key == pygame.K_l:
                    step_speed *= 2
                    if step_speed == 32:
                        step_speed = 1
                keys.append(event.key)
            elif event.type == pygame.KEYUP:
                keys.remove(event.key)
            elif event.type == pygame.WINDOWRESIZED:
                size = (pygame.display.get_window_size()[0] // scale, pygame.display.get_window_size()[1] // scale)
                game_screen = pygame.Surface(size)
        for key in keys:
            if moving == (0, 0):
                if key == pygame.K_z or key == pygame.K_u:
                    if len(history) > 1:
                        level["objs"] = copy.deepcopy(history[-2][0])
                        for index, obj in enumerate(level["objs"]):
                            obj[4] = history[-1][0][index][4]
                        moving = (history[-1][2][0] * -1, history[-1][2][1] * -1)
                        draw_level_objs()
                        player_loc = history[-2][1]
                        position = history[-1][3]
                        history.pop(-1)
                        backwards = True
                else:
                    backwards = False
                if key == pygame.K_RIGHT or key == pygame.K_d:
                    move((1, 0), 1)
                elif key == pygame.K_LEFT or key == pygame.K_a:
                    move((-1, 0), 2)
                elif key == pygame.K_DOWN or key == pygame.K_s:
                    move((0, 1), 0)
                elif key == pygame.K_UP or key == pygame.K_w:
                    move((0, -1), 3)
                if player_loc != history[-1][1]:
                    history = history + [(copy.deepcopy(level["objs"]), player_loc, moving, position)]
        game_screen.blit(level_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                        size[1] // 2 - (player_loc[1] - 0.5) * BLOCK_SIZE + moving[1]))
        image = round((((abs(moving[0] + moving[1]) // MOVEMENT_SPEED) % ANIMATION_STEPS) * (
                backwards * 2 - 1)) + ANIMATION_STEPS * (-backwards + 1))
        if moving == (0, 0):
            image = 0
        image += position * ANIMATION_STEPS + position
        game_screen.blit(player_images[image],
                         (size[0] // 2 - 0.5 * BLOCK_SIZE, size[1] // 2 - 0.5 * BLOCK_SIZE))
        game_screen.blit(objs_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                       size[1] // 2 - (player_loc[1]) * BLOCK_SIZE + moving[1]))
        display_screen.blit(pygame.transform.scale(game_screen, (size[0] * scale, size[1] * scale)), (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60 / step_speed)
        if moving[0] != 0:
            moving = (moving[0] - step_speed * moving[0] / abs(moving[0]), moving[1])
            if moving[0] == 0:
                for obj in level["objs"]:
                    obj[4] = False
                    objs_screen.fill((0, 0, 0, 0))
                    draw_level_objs()
        if moving[1] != 0:
            moving = (moving[0], moving[1] - step_speed * moving[1] / abs(moving[1]))
            if moving[1] == 0:
                for obj in level["objs"]:
                    obj[4] = False
                    objs_screen.fill((0, 0, 0, 0))
                    draw_level_objs()


if __name__ == "__main__":
    asyncio.run(main())
