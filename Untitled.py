import pygame
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MCQ Quiz")

# Fonts
font = pygame.font.SysFont(None, 36)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Load questions from txt file
def load_questions(filename):
    questions = []
    with open(filename, "r") as f:
        content = f.read().strip().split("\n\n")  # Questions separated by blank line
        for block in content:
            lines = block.split("\n")
            q = lines[0]
            options = lines[1:5]
            answer = int(lines[5])  # correct answer index (1–4)
            questions.append((q, options, answer))
    return questions

questions = load_questions("questions.txt")

# Pick a random question
question, options, correct_answer = random.choice(questions)
selected_answer = None
feedback = ""

running = True
while running:
    screen.fill(WHITE)

    # Display question
    question_surface = font.render(question, True, BLACK)
    screen.blit(question_surface, (50, 50))

    # Display options
    for i, option in enumerate(options):
        option_surface = font.render(f"{i+1}. {option}", True, BLACK)
        screen.blit(option_surface, (100, 150 + i*50))

    # Display feedback
    if feedback:
        feedback_surface = font.render(feedback, True, GREEN if "Correct" in feedback else RED)
        screen.blit(feedback_surface, (50, 400))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_KP1]:
                selected_answer = 1
            elif event.key in [pygame.K_2, pygame.K_KP2]:
                selected_answer = 2
            elif event.key in [pygame.K_3, pygame.K_KP3]:
                selected_answer = 3
            elif event.key in [pygame.K_4, pygame.K_KP4]:
                selected_answer = 4

            if selected_answer:
                if selected_answer == correct_answer:
                    feedback = "Correct!"
                else:
                    feedback = f"Wrong! Correct answer: {correct_answer}. {options[correct_answer-1]}"
                question, options, correct_answer = random.choice(questions)

pygame.quit()
