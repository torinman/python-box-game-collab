import pygame

pygame.init()

images = []
for i in range(26):
    images.append(pygame.image.load(f"images/font/{i}.png"))

def write(text="HELLO abcdefghijklmnopqrstuvwxyz"):
    spacer = 0
    text_surface = pygame.Surface((len(text)*6, 5)).convert_alpha()
    text_surface.fill((0, 0, 0, 0))
    for letter in text:
        if letter != " ":
            letternum = ord(letter)
            if 65 <= letternum <= 90:
                letternum -= 65
            elif 97 <= letternum <= 122:
                letternum -= 97
            text_surface.blit(images[letternum], (spacer, 0))
        spacer += 6
    return text_surface


def main():
    screen = pygame.display.set_mode((700, 700))
    writing = write()
    done = False
    while not done:
        screen.fill((125, 128, 130))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        screen.blit(writing, (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    main()