import pygame
import json
import asyncio
import copy
import font

levels = []
num_levels = 0
with open("levels.json", "r") as f:
    for line in f.readlines():
        levels.append(json.loads(line))
        num_levels += 1
level_start = 1
editor = False

with open("images/objects.json", "r") as f:
    objs_info = json.loads(f.read())

for level_edit in levels:
    for obj_edit in level_edit["objs"]:
        if obj_edit[2] == "default":
            obj_edit[2] = objs_info[obj_edit[0]]["parts"]


def draw_level_tiles(level):
    global level_screen
    level_screen = level_screen.convert_alpha()
    level_screen.fill((0, 0, 0, 0))
    for y in range(level["size"][1]):
        for x in range(level["size"][0]):
            level_screen.blit(pygame.image.load(f"images/tiles/{level['tile'][y][x]}.png"),
                              (x * BLOCK_SIZE, y * BLOCK_SIZE))

def draw_level_overlay(level):
    global overlay_screen
    overlay_screen = overlay_screen.convert_alpha()
    overlay_screen.fill((0, 0, 0, 0))
    for y in range(level["size"][1]):
        for x in range(level["size"][0]):
            if [x + 1, y] in level["doors"]:
                objs_screen.blit(pygame.image.load("images/door/0.png"), (x * BLOCK_SIZE, y * BLOCK_SIZE))
            if [x - 1, y] in level["doors"]:
                objs_screen.blit(pygame.image.load("images/door/2.png"), (x * BLOCK_SIZE, y * BLOCK_SIZE))
            if [x, y + 1] in level["doors"]:
                objs_screen.blit(pygame.image.load("images/door/3.png"), (x * BLOCK_SIZE, y * BLOCK_SIZE))
            if [x, y - 1] in level["doors"]:
                objs_screen.blit(pygame.image.load("images/door/1.png"), (x * BLOCK_SIZE, y * BLOCK_SIZE))


def check_obj(loc, level):
    for obj in level["objs"]:
        for part in obj[2]:
            if part[1] + obj[1][1] == loc[1] and part[0] + obj[1][0] == loc[0]:
                return obj


def check_push(loc, v, level) -> tuple[list, list] | bool:
    objs = []
    obj_changes = []
    locations = [] + [loc]
    new_locations = []
    while locations:
        for location in locations:
            check = check_obj((location[0] + v[0], location[1] + v[1]), level)
            if check is not None and check not in objs:
                if check[7]:
                    return False
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


def get_wall_tile(location, kind, level):
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


def draw_level_objs(level):
    global objs_screen
    for y in range(-1, level["size"][1] + 2):
        if player_loc[1] == y:
            objs_screen.blit(player_images[image], ((player_loc[0]-1)*BLOCK_SIZE-moving[0], ((player_loc[1]-0.5)*BLOCK_SIZE)-4-moving[1]))
        for obj in level["objs"]:
            for part in obj[2]:
                if part[1] + obj[1][1] == y:
                    if objs_info[obj[0]]["parts"] == "generic":
                        objs_screen.blit(
                            pygame.image.load(f"images/objects/{obj[0]}/{obj[3]}/0v{obj[6]}.png"),
                            ((part[0] + obj[1][0]) * BLOCK_SIZE + obj[4] * moving[0] * -1,
                             (part[1] + obj[1][1]) * BLOCK_SIZE + obj[4] * moving[1] * -1))
                    else:
                        objs_screen.blit(
                            pygame.image.load(f"images/objects/{obj[0]}/{obj[3]}/{obj[2].index(part)}v{obj[6]}.png"),
                            ((part[0] + obj[1][0]) * BLOCK_SIZE + obj[4] * moving[0] * -1,
                             (part[1] + obj[1][1]) * BLOCK_SIZE + obj[4] * moving[1] * -1))
        for x in range(level["size"][0]):
            if 0 <= y < level["size"][1]:
                if level["wall"][y][x] != 0:
                    objs_screen.blit(pygame.image.load(
                        f"images/wall/{level['wall'][y][x] - 1}/"
                        f"{get_wall_tile((x, y), level['wall'][y][x], level)}.png"),
                        (x * BLOCK_SIZE, y * BLOCK_SIZE))

def move(v, p, level):
    global position, player_loc, moving, level_start, level_reset, history, finishing, finished
    position = p
    check = check_push((player_loc[0] - 1, player_loc[1] - 1), v, level)
    if finishing:
        if [player_loc[0] + v[0] - 1, player_loc[1] + v[1] - 1] in level["doors"]:
            finished = True
            moving = (BLOCK_SIZE * v[0], BLOCK_SIZE * v[1])
            player_loc = (player_loc[0] + v[0], player_loc[1] + v[1])
    if check is not False:
        moving = (BLOCK_SIZE * v[0], BLOCK_SIZE * v[1])
        player_loc = (player_loc[0] + v[0], player_loc[1] + v[1])
        for obj in level["objs"]:
            if obj in check[0]:
                index = level["objs"].index(obj)
                for remove in check[1]:
                    if remove[0] == obj:
                        for r in remove[1]:
                            level["objs"][index][2][level["objs"][index][2].index(r)][2] = True
                level["objs"][index][1] = (level["objs"][index][1][0] + v[0], level["objs"][index][1][1] + v[1])
                level["objs"][index][4] = True
            else:
                obj[4] = False
    else:
        if moving == (0, 0):
            moving = (MOVEMENT_SPEED * WALL_BUMP * -1 * v[0], MOVEMENT_SPEED * WALL_BUMP * -1 * v[1])


BLOCK_SIZE = 16
MOVEMENT_SPEED = 4
ANIMATION_STEPS = 4
step_speed = 2
WALL_BUMP = 0
fps = 3
position = 0

pygame.init()

done = False
clock = pygame.time.Clock()
scale = 48 // BLOCK_SIZE
moving = (0, 0)
keys = []
display_screen = pygame.display.set_mode((800, 600), flags=pygame.RESIZABLE)
size = (pygame.display.get_window_size()[0] // scale, pygame.display.get_window_size()[1] // scale)
game_screen = pygame.Surface(size).convert_alpha()
pygame.display.set_caption("Mouse Movers")
finishing = False
player_loc = (0, 0)
level_reset = []
history = []
finished = False
level_screen = pygame.Surface((0, 0))
objs_screen = pygame.Surface((0, 0))
overlay_screen = pygame.Surface((0, 0))
image = 0

player_images = []
for i in range((ANIMATION_STEPS + 1) * 4):
    player_images.append(pygame.image.load(f"images/player/{i}.png"))


def edit(level):
    global done, moving, size, fps, step_speed, finishing, \
        game_screen, player_loc, level_reset, level_screen, objs_screen


async def play_level(level):
    global done, moving, size, fps, step_speed, finishing, \
        game_screen, position, player_loc, history, finished, level_reset, level_screen, objs_screen, image, overlay_screen
    level_screen = pygame.Surface((level["size"][0] * BLOCK_SIZE, level["size"][1] * BLOCK_SIZE))
    objs_screen = pygame.Surface((level["size"][0] * BLOCK_SIZE, (level["size"][1] + 0.5) * BLOCK_SIZE))
    objs_screen = objs_screen.convert_alpha()
    objs_screen.fill((0, 0, 0, 0))
    overlay_screen = pygame.Surface((level["size"][0] * BLOCK_SIZE, (level["size"][1] + 0.5) * BLOCK_SIZE))
    overlay_screen = overlay_screen.convert_alpha()
    overlay_screen.fill((0, 0, 0, 0))
    fade_screen = pygame.Surface(size)
    fade_screen = fade_screen.convert_alpha()
    fade_screen.fill((0, 0, 0, 0))
    draw_level_objs(level)
    player_loc = level["start"]
    level_reset = copy.deepcopy(level["objs"])
    position = 0
    history = [(copy.deepcopy(level["objs"]), player_loc, moving, position)]
    finished = False
    finishing = False
    draw_level_overlay(level)

    draw_level_tiles(level)
    backwards = False
    fade_in = BLOCK_SIZE
    while not done:
        game_screen.fill((69, 43, 63, 255))
        draw = False
        if moving[0] + moving[1] != 0:
            for obj in level["objs"]:
                if obj[4]:
                    draw = True
        #if draw:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    level["objs"] = copy.deepcopy(level_reset)
                    draw_level_objs(level)
                    player_loc = level["start"]
                    position = 0
                    objs_screen.fill((0, 0, 0, 0))
                    draw_level_objs(level)
                elif event.key == pygame.K_l:
                    step_speed *= 2
                    if step_speed == 32:
                        step_speed = 1
                elif event.key == pygame.K_p:
                    fps += 1
                    if fps == 6:
                        fps = 2
                keys.insert(0, event.key)
            elif event.type == pygame.KEYUP:
                keys.remove(event.key)
            elif event.type == pygame.WINDOWRESIZED:
                size = (pygame.display.get_window_size()[0] // scale, pygame.display.get_window_size()[1] // scale)
                game_screen = pygame.Surface(size).convert_alpha()
                fade_screen = pygame.Surface(size).convert_alpha()
        for key in keys:
            if moving == (0, 0):
                if key == pygame.K_z or key == pygame.K_u:
                    if len(history) > 1:
                        level["objs"] = copy.deepcopy(history[-2][0])
                        for index, obj in enumerate(level["objs"]):
                            obj[4] = history[-1][0][index][4]
                        moving = (history[-1][2][0] * -1, history[-1][2][1] * -1)
                        draw_level_objs(level)
                        player_loc = history[-2][1]
                        position = history[-1][3]
                        history.pop(-1)
                        backwards = True
                else:
                    backwards = False
                if key == pygame.K_RIGHT or key == pygame.K_d:
                    move((1, 0), 1, level)
                elif key == pygame.K_LEFT or key == pygame.K_a:
                    move((-1, 0), 2, level)
                elif key == pygame.K_DOWN or key == pygame.K_s:
                    move((0, 1), 0, level)
                elif key == pygame.K_UP or key == pygame.K_w:
                    move((0, -1), 3, level)
                if player_loc != history[-1][1]:
                    history = history + [(copy.deepcopy(level["objs"]), player_loc, moving, position)]
        game_screen.blit(level_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                        size[1] // 2 - (player_loc[1] - 0.5) * BLOCK_SIZE + moving[1]))
        image = round((((abs(moving[0] + moving[1]) // MOVEMENT_SPEED) % ANIMATION_STEPS) * (
                backwards * 2 - 1)) + ANIMATION_STEPS * (-backwards + 1))
        if moving == (0, 0):
            image = 0
        image += position * ANIMATION_STEPS + position
        objs_screen.fill((0, 0, 0, 0))
        draw_level_objs(level)
        draw_level_overlay(level)
        # game_screen.blit(player_images[image],
        #                  (size[0] // 2 - 0.5 * BLOCK_SIZE, size[1] // 2 - 0.5 * BLOCK_SIZE), )
        game_screen.blit(objs_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                       size[1] // 2 - (player_loc[1]) * BLOCK_SIZE + moving[1]))
        game_screen.blit(overlay_screen, (size[0] // 2 - (player_loc[0] - 0.5) * BLOCK_SIZE + moving[0],
                                       size[1] // 2 - (player_loc[1]) * BLOCK_SIZE + moving[1]))
        game_screen.blit(font.write("Moving Mouses"), (1, 1))
        if moving[0] != 0:
            moving = (moving[0] - step_speed * moving[0] / abs(moving[0]), moving[1])
            if moving[0] == 0:
                finishing = True
                for obj in level["objs"]:
                    obj[4] = False
                    objs_screen.fill((0, 0, 0, 0))
                    new_obj = obj[2][:]
                    for part in obj[2]:
                        if part[2]:
                            new_obj.remove(part)
                    obj[2] = new_obj[:]
                    if obj[5] and obj[2]:
                        finishing = False
                draw_level_objs(level)
        if moving[1] != 0:
            moving = (moving[0], moving[1] - step_speed * moving[1] / abs(moving[1]))
            if moving[1] == 0:
                finishing = True
                for obj in level["objs"]:
                    obj[4] = False
                    objs_screen.fill((0, 0, 0, 0))
                    new_obj = obj[2][:]
                    for part in obj[2]:
                        if part[2]:
                            new_obj.remove(part)
                    obj[2] = new_obj[:]
                    if obj[5] and obj[2]:
                        finishing = False
                draw_level_objs(level)
        if finished:
            if moving == (0, 0):
                return 1
            else:
                fade_screen.fill((69, 43, 63, 255 * (1 - abs(moving[0] + moving[1]) / BLOCK_SIZE)))
                game_screen.blit(fade_screen, (0, 0))
        if fade_in:
            fade_screen.fill((69, 43, 63, 255 * (fade_in / BLOCK_SIZE)))
            game_screen.blit(fade_screen, (0, 0))
            fade_in -= MOVEMENT_SPEED
        display_screen.blit(pygame.transform.scale(game_screen, (size[0] * scale, size[1] * scale)), (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(fps * BLOCK_SIZE / step_speed)


async def main():
    global level_start
    while not done:
        level = copy.deepcopy(levels[level_start])
        await play_level(level)
        if level_start < num_levels - 1:
            level_start += 1
        else:
            level_start = 0


if __name__ == "__main__":
    asyncio.run(main())
