import pygame

import sqlite3
import random


pygame.init()

# константы
WIDTH, HEIGHT = 800, 400
WHITE, BLACK, RED, BLUE, GREEN = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255), (0, 255, 0)
GRAVITY = 0.5
JUMP_STRENGTH = -10

SPEEDS = {'easy': 4, 'medium': 6, 'hard': 8}

# создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash")

# подключение к базе данных
conn = sqlite3.connect("scores.db")
cursor = conn.cursor()

# проверяем существование таблицы
cursor.execute("PRAGMA table_info(scores)")
columns = [column[1] for column in cursor.fetchall()]


# удаляем старую таблицу
if "level" not in columns:
    cursor.execute("DROP TABLE IF EXISTS scores")
    cursor.execute("CREATE TABLE scores (score INTEGER, level TEXT)")


conn.commit()


# класс игры
class Player:
    # инициализацич
    def __init__(self):
        self.rect = pygame.Rect(100, HEIGHT - 50, 30, 30)
        self.vel_y = 0
        self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


# игровой процесс
def game_loop(difficulty):
    player = Player()
    obstacles = [Obstacle(WIDTH + i * 300, SPEEDS[difficulty]) for i in range(3)]
    clock = pygame.time.Clock()
    score = 0
    running = True

    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.jump()

        player.update()
        player.draw()

        for obstacle in obstacles:
            obstacle.update()
            obstacle.draw()

            if obstacle.rect.right < 0:
                obstacle.rect.x = WIDTH + random.randint(100, 300)
                score += 1

            if player.rect.colliderect(obstacle.rect):
                cursor.execute("INSERT INTO scores (score, level) VALUES (?, ?)", (score, difficulty))
                conn.commit()
                game_over(score, difficulty)
                return  # Выход из игры при столкновении

        pygame.display.flip()
        clock.tick(30)


# препятствия
class Obstacle:
    def __init__(self, x, speed):
        self.rect = pygame.Rect(x, HEIGHT - 50, 30, 30)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self):
        pygame.draw.rect(screen, BLACK, self.rect)


# окно окончания игры
def game_over(score, difficulty):
    while True:
        screen.fill(WHITE)
        font = pygame.font.Font(None, 50)
        text_game_over = font.render("Game Over", True, BLACK)
        text_score = font.render(f"Score: {score}", True, BLACK)
        text_restart = font.render("Press R to Restart", True, BLACK)
        text_menu = font.render("Press M for Menu", True, BLACK)

        screen.blit(text_game_over, (WIDTH // 3, HEIGHT // 4))
        screen.blit(text_score, (WIDTH // 3, HEIGHT // 4 + 50))
        screen.blit(text_restart, (WIDTH // 3, HEIGHT // 4 + 100))
        screen.blit(text_menu, (WIDTH // 3, HEIGHT // 4 + 150))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop(difficulty)
                    return
                elif event.key == pygame.K_m:
                    main_menu()
                    return


# показ рекордов
def show_records():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 40)
    cursor.execute("SELECT * FROM scores ORDER BY score DESC LIMIT 10")
    records = cursor.fetchall()
    y_offset = 50

    for record in records:
        text = font.render(f"Score: {record[0]} - Level: {record[1]}", True, BLACK)
        screen.blit(text, (50, y_offset))
        y_offset += 40

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    main_menu()

                    return


# главное меню
def main_menu():
    button_start = pygame.Rect(WIDTH // 3, HEIGHT // 3, 200, 50)

    button_records = pygame.Rect(WIDTH // 3, HEIGHT // 3 + 70, 200, 50)

    while True:
        screen.fill(WHITE)
        font = pygame.font.Font(None, 50)
        text_start = font.render("Start", True, BLACK)
        text_records = font.render("Records", True, BLACK)

        pygame.draw.rect(screen, GREEN, button_start)
        pygame.draw.rect(screen, BLUE, button_records)

        screen.blit(text_start, (button_start.x + 50, button_start.y + 10))
        screen.blit(text_records, (button_records.x + 30, button_records.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()

                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_start.collidepoint(event.pos):
                    choose_difficulty()

                    return
                elif button_records.collidepoint(event.pos):
                    show_records()

                    return


# Выбор уровня сложности
def choose_difficulty():
    button_easy = pygame.Rect(WIDTH // 3, HEIGHT // 3, 200, 50)
    button_medium = pygame.Rect(WIDTH // 3, HEIGHT // 3 + 60, 200, 50)
    button_hard = pygame.Rect(WIDTH // 3, HEIGHT // 3 + 120, 200, 50)

    while True:
        screen.fill(WHITE)
        font = pygame.font.Font(None, 40)

        pygame.draw.rect(screen, GREEN, button_easy)
        pygame.draw.rect(screen, BLUE, button_medium)
        pygame.draw.rect(screen, RED, button_hard)

        # проверка уровня

        text_easy = font.render("Easy", True, BLACK)
        text_medium = font.render("Medium", True, BLACK)
        text_hard = font.render("Hard", True, BLACK)

        screen.blit(text_easy, (button_easy.x + 70, button_easy.y + 10))
        screen.blit(text_medium, (button_medium.x + 50, button_medium.y + 10))
        screen.blit(text_hard, (button_hard.x + 70, button_hard.y + 10))

        pygame.display.flip()

        # обработка нажатия

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_easy.collidepoint(event.pos):
                    game_loop('easy')
                    return
                elif button_medium.collidepoint(event.pos):
                    game_loop('medium')
                    return
                elif button_hard.collidepoint(event.pos):
                    game_loop('hard')
                    return


# запуск главного меню
main_menu()
