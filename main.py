import pygame
import json
import asyncio
import random

editor = False
levels = []
with open("levels.json", "r") as f:
    for line in f.readlines():
        levels.append(json.loads(line))
print(levels)

pygame.init()

done = False
clock = pygame.time.Clock()
size = (80, 60)
display_screen = pygame.display.set_mode((size[0]*10, size[1]*10))
game_screen = pygame.Surface(size)
level_screen = pygame.Surface(size)
objects_screen = pygame.Surface(size)
with open("colour_palette.txt", "r") as c:
    colours = c.readlines()

async def main():
    global done
    while not done:
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        for i in range(size[0]):
            for j in range(size[1]):
                game_screen.set_at((i,j), tuple(int(random.choice(colours)[i:i+2], 16) for i in (0, 2, 4)))
        display_screen.blit(pygame.transform.scale(game_screen, (size[0]*10, size[1]*10)), (0, 0))
        pygame.display.flip()
        clock.tick(20)

if __name__ == "__main__":
    asyncio.run(main())
