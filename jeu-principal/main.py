import pygame 

pygame.init()
win = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("jeu nsiissininisissini")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.group()

running = True 
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #all_sprites.update()

    screen.fill(BLACK)

    #all_sprites.draw(win)

    pygame.display.flip()

pygame.quit()
