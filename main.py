import pygame
import sys
import time
import random
import json
import os

class Tinta:
    def __init__(self, valoare_baza, durata, panel_width, panel_height, level):
        self.valoare_baza = valoare_baza
        self.valoare = valoare_baza * level
        self.durata = durata
        self.aparitie = time.time()
        self.radius = 30 if valoare_baza == 1 else 40

        img_path = "Tinta_1.png" if valoare_baza == 1 else "Tinta_5.png"
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.radius * 2, self.radius * 2))

        self.panel_width = panel_width
        self.panel_height = panel_height
        self.panel2_height = int(panel_height * 0.2)

        edge = random.choice(["top", "bottom", "left", "right"])
        margin = 10

        if edge == "top":
            self.x = random.randint(margin, panel_width - margin)
            self.y = -self.radius * 2
        elif edge == "bottom":
            self.x = random.randint(margin, panel_width - margin)
            self.y = panel_height + self.radius * 2
        elif edge == "left":
            self.x = -self.radius * 2
            self.y = random.randint(margin, panel_height - self.panel2_height - margin)
        else:
            self.x = panel_width + self.radius * 2
            self.y = random.randint(margin, panel_height - self.panel2_height - margin)

        target_x = random.randint(self.radius, panel_width - self.radius)
        target_y = random.randint(self.radius, panel_height - self.panel2_height - self.radius)
        dx = target_x - self.x
        dy = target_y - self.y

        self.dx, self.dy = self.normalize(dx, dy)

        base_speed = 2 + (0.3 if valoare_baza == 1 else 0.5)
        self.speed = base_speed * (1 + (level - 1) * 0.3)
        self.dx *= self.speed
        self.dy *= self.speed

    def normalize(self, dx, dy):
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            return 0, 0
        return dx / length, dy / length

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def is_out_of_bounds(self):
        return (
        self.x < -self.radius * 2 or
        self.x > self.panel_width + self.radius * 2 or
        self.y < -self.radius * 2 or
        self.y > self.panel_height + self.radius * 2
        )

    def draw(self, screen):
        screen.blit(self.image, (self.x - self.radius, self.y - self.radius))

    def is_hit(self, pos):
        mx, my = pos
        dist = ((self.x - mx) ** 2 + (self.y - my) ** 2) ** 0.5
        return dist <= self.radius

pygame.init()
hit_sound = pygame.mixer.Sound("hit.wav")
clock = pygame.time.Clock()
custom_font_big = pygame.font.Font("font.ttf", 80)
custom_font_small = pygame.font.Font("font.ttf", 48)

T = 2
score = 0
tinte = []
last_spawn1 = time.time()
last_spawn5 = time.time()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rapid Fire - Joc")

tinta1_img = pygame.image.load("Tinta_1.png").convert_alpha()
tinta1_img = pygame.transform.scale(tinta1_img, (30, 30))

tinta5_img = pygame.image.load("Tinta_5.png").convert_alpha()
tinta5_img = pygame.transform.scale(tinta5_img, (40, 40))

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
AQUA = (0, 200, 255)

panel1_height = int(HEIGHT * 0.8)
panel2_height = HEIGHT - panel1_height
GAME_HEIGHT = panel1_height

font = pygame.font.SysFont(None, 36)
start_time = time.time()
total_time = 15


LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return {}

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_leaderboard(player_name, score):
    leaderboard = load_leaderboard()
    if player_name in leaderboard:
        if score > leaderboard[player_name]:
            leaderboard[player_name] = score
    else:
        leaderboard[player_name] = score
    save_leaderboard(leaderboard)

def show_leaderboard():
    leaderboard = load_leaderboard()
    top_players = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:10]

    background = pygame.image.load("fundal_meniu.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    font_title = pygame.font.Font("font.ttf", 60)
    font_entry = pygame.font.Font("font.ttf", 32)

    back_arrow = pygame.Rect(20, 20, 40, 40)

    running = True
    while running:
        screen.blit(background, (0, 0))
        pygame.draw.polygon(screen, WHITE, [(30, 40), (50, 20), (50, 60)])

        title = font_title.render("Leaderboard", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        for i, (name, scor) in enumerate(top_players):
            text = font_entry.render(f"{i+1}. {name} - {scor} puncte", True, WHITE)
            screen.blit(text, (100, 160 + i * 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_arrow.collidepoint(event.pos):
                    return

        pygame.display.flip()
        clock.tick(60)

def show_help():
    background = pygame.image.load("fundal_meniu.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    font_title = pygame.font.Font("font.ttf", 60)
    font_text = pygame.font.Font("font.ttf", 20)

    back_arrow = pygame.Rect(20, 20, 40, 40)

    instructions = [
        "Rapid Fire - Instructiuni:",
        "- Tinteste si doboara tintele care apar.",
        "- Valoarea tintei se mareste la fiecare runda",
        "- Atinge targetul pentru a promova in runda urmatoare",
        "- Scorul tau este afisat jos.",
        "- Loveste cat mai multe tinte!",
    ]

    running = True
    while running:
        screen.blit(background, (0, 0))

        pygame.draw.polygon(screen, WHITE, [(30, 40), (50, 20), (50, 60)])

        title = font_title.render("Help", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        for i, line in enumerate(instructions):
            text = font_text.render(line, True, (255, 255, 255))
            screen.blit(text, (60, 160 + i * 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_arrow.collidepoint(event.pos):
                    return

        pygame.display.flip()
        clock.tick(60)

def show_game_over(name, final_score):
    pygame.mouse.set_visible(True)
    font_big = pygame.font.Font("font.ttf", 60)
    font_small = pygame.font.Font("font.ttf", 36)

    button_font = pygame.font.Font("font.ttf", 30)
    button_text = button_font.render("Back to Menu", True, WHITE)
    button_rect = button_text.get_rect(center=(WIDTH // 2, HEIGHT - 80))

    running = True
    while running:
        screen.fill((120, 20, 20))

        msg = font_big.render("Game Over!", True, WHITE)
        score_display = font_small.render(f"{name}, scorul tau: {final_score}", True, WHITE)

        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(score_display, (WIDTH // 2 - score_display.get_width() // 2, HEIGHT // 2 + 20))

        
        mouse_pos = pygame.mouse.get_pos()
        color = (255, 255, 255) if button_rect.collidepoint(mouse_pos) else (180, 180, 180)
        button_text = button_font.render("Back to Menu", True, color)
        screen.blit(button_text, button_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    running = False

        pygame.display.flip()
        clock.tick(60)

def show_level_up(level):
    pygame.mouse.set_visible(True)
    font_big = pygame.font.Font("font.ttf", 40)
    font_small = pygame.font.Font("font.ttf", 25)

    screen.fill((50, 100, 50))
    msg = font_big.render("Felicitari ! Nivelul urmator", True, WHITE)
    info = font_small.render("Apasa click pentru a continua...", True, WHITE)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def main_menu():
    background = pygame.image.load("fundal_meniu.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    try:
        custom_font_title = pygame.font.Font("font.ttf", 80)
        custom_font_button = pygame.font.Font("font.ttf", 48)
    except Exception as e:
        print("Font font nu a putut fi încărcat:", e)
        custom_font_title = pygame.font.SysFont("arial", 80)
        custom_font_button = pygame.font.SysFont("arial", 48)

    start_text = custom_font_button.render("Start Game", True, (255, 255, 255))
    start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))

    help_text = custom_font_button.render("Help", True, (255, 255, 255))
    help_rect = help_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

    leaderboard_text = custom_font_button.render("Leaderboard", True, (255, 255, 255))
    leaderboard_rect = leaderboard_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background, (0, 0))

        title_text = custom_font_title.render("Rapid Fire", True, (255, 70, 70))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_text, title_rect)


        start_color = (255, 255, 255) if start_rect.collidepoint(mouse_pos) else (180, 180, 180)
        help_color = (255, 255, 255) if help_rect.collidepoint(mouse_pos) else (180, 180, 180)
        leaderboard_color = (255, 255, 255) if leaderboard_rect.collidepoint(mouse_pos) else (180, 180, 180)


        start_text = custom_font_button.render("Start Game", True, start_color)
        help_text = custom_font_button.render("Help", True, help_color)
        leaderboard_text = custom_font_button.render("Leaderboard", True, leaderboard_color)


        screen.blit(start_text, start_rect)
        screen.blit(help_text, help_rect)
        screen.blit(leaderboard_text, leaderboard_rect)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(mouse_pos):
                    name = get_player_name()
                    if name:
                        run_game(name)
                        return  
                elif help_rect.collidepoint(mouse_pos):
                    show_help()
                elif leaderboard_rect.collidepoint(mouse_pos):
                    show_leaderboard()

        pygame.display.flip()
        clock.tick(60)

def get_player_name():
    name = ""
    input_active = True
    font_input = pygame.font.Font("font.ttf", 36)

    while input_active:
        screen.fill((50, 100, 150))
        text_surface = font_input.render("Insert Player Name:", True, WHITE)
        name_surface = font_input.render(name, True, WHITE)
        screen.blit(text_surface, (WIDTH//2 - 250, HEIGHT//2 - 60))
        screen.blit(name_surface, (WIDTH//2 - 250, HEIGHT//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15 and event.unicode.isprintable():
                        name += event.unicode

        pygame.display.flip()
        clock.tick(60)

level = 1
target_score = 15

def run_game(player_name):
    global score, tinte, last_spawn1, last_spawn5, start_time, level, target_score

    cursor_img = pygame.image.load("cursor_tinta.png").convert_alpha()
    cursor_img = pygame.transform.scale(cursor_img, (40, 40))
    pygame.mouse.set_visible(False)

    T = 2
    tinte = []
    running = True

    while running:
        start_time = time.time()
        last_spawn1 = time.time()
        last_spawn5 = time.time()
        time_left = total_time
        level_score = 0

        while time_left > 0:
            current_time = time.time()
            time_left = max(0, int(total_time - (current_time - start_time)))

            screen.fill(WHITE)

            
            if current_time - last_spawn1 > T / 2:
                tinte.append(Tinta(1, T, WIDTH, GAME_HEIGHT, level))
                last_spawn1 = current_time

            if current_time - last_spawn5 > T:
                tinte.append(Tinta(5, T, WIDTH, GAME_HEIGHT, level))
                last_spawn5 = current_time

            pygame.draw.rect(screen, AQUA, (0, 0, WIDTH, panel1_height))
            for tinta in tinte[:]:
                tinta.update()
                if tinta.is_out_of_bounds():
                    tinte.remove(tinta)
            for tinta in tinte:
                tinta.draw(screen)

            pygame.draw.rect(screen, BLACK, (0, panel1_height, WIDTH, panel2_height))

            legend_x = WIDTH - 180
            legend_y = panel1_height + panel2_height - 80
            screen.blit(tinta1_img, (legend_x, legend_y))
            text1 = font.render(f"= {1 * level} punct", True, WHITE)
            screen.blit(text1, (legend_x + 40, legend_y + 5))
            screen.blit(tinta5_img, (legend_x, legend_y + 35))
            text5 = font.render(f"= {5 * level} puncte", True, WHITE)
            screen.blit(text5, (legend_x + 40, legend_y + 40))

            
            score_text = font.render(f"{player_name} | Scor total: {score}", True, WHITE)
            time_text = font.render(f"Timp rămas: {time_left}", True, WHITE)
            next_level_text = font.render(f"Nivel {level} | Scor necesar: {target_score}", True, WHITE)
            screen.blit(score_text, (20, panel1_height + 10))
            screen.blit(time_text, (350, panel1_height + 10))
            screen.blit(next_level_text, (20, panel1_height + 50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for tinta in tinte[:]:
                        if tinta.is_hit(event.pos):
                            if hit_sound:
                                hit_sound.play()
                            score += tinta.valoare
                            level_score += tinta.valoare
                            tinte.remove(tinta)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(cursor_img, (mouse_x - 20, mouse_y - 20))

            pygame.display.flip()
            clock.tick(60)

        if score >= target_score:
            level += 1
            target_score = int(target_score * 2)
            show_level_up(level)
        else:
            show_game_over(player_name, score)
            update_leaderboard(player_name, score)
            running = False
            main_menu()
main_menu()

pygame.quit()
sys.exit()