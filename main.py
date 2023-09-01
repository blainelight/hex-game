import pygame
import math
import random
import logging


log_file = open("click_log.txt", "w") #Creates a log file when clicks are made to troubleshoot clicking issue
logging.basicConfig(filename='game_log.txt', level=logging.DEBUG)

# Initialize Pygame
pygame.init()

# Set window dimensions
width, height = 800, 600

# Create the window
screen = pygame.display.set_mode((width, height))

# Set window title
pygame.display.set_caption("My Hex Game Catan")

# Font settings
big_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Define colors for players
colors = [(255, 0, 0), (0, 0, 255)]

# Initialize scores and current player
scores = [0, 0]
current_player = 0

# Create a dictionary to store hex states
hex_states = {}

# Draw hex function
def draw_hex(x, y, size, color=(255, 255, 255)):
    points = []
    for angle in [30, 90, 150, 210, 270, 330]:
        x_point = x + size * math.cos(math.radians(angle))
        y_point = y + size * math.sin(math.radians(angle))
        points.append((x_point, y_point))
    pygame.draw.polygon(screen, color, points)

# Catan board rows
rows = [3, 4, 5, 4, 3]

# Create a dictionary to store cells owned by players
owned_cells = {0: [], 1: []}

# Create a variable to store orange cell
orange_cell = None

def is_adjacent(cell1, cell2):
    x1, y1 = cell1
    x2, y2 = cell2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) < 2 * horiz_dist

# Create a variable to store error message in game
error_message = None


# Main loop
running = True
while running:
    # Fill screen with black
    screen.fill((0, 0, 0))

    # Initialize drawing coords
    start_x, start_y = 350, 300  # Moved it to the left for better centering

    # Variable to store hex centers
    hex_centers = []

    # Draw Catan board
    hex_radius = 30
    hex_height = math.sqrt(3) * hex_radius
    vert_dist = hex_height  # Add 5 for vertical spacing
    horiz_dist = 1.8 * hex_radius  # Add 5 for horizontal spacing

    y = start_y
    for row in rows:
        x = start_x - (row - 1) * horiz_dist * 0.5  # Centering each row
        for col in range(row):
            color = hex_states.get((x, y), (255, 255, 255))
            draw_hex(x, y, hex_radius, color=color)
            hex_centers.append((x, y))
            x += horiz_dist
        y -= vert_dist

    # Random Orange Cell after both players have a cell
    if len(owned_cells[0]) > 0 and len(owned_cells[1]) > 0 and orange_cell is None:
        orange_cell = random.choice(hex_centers)
        hex_states[orange_cell] = (255, 165, 0)  # Orange

    # Mouse handling
    mouse_x, mouse_y = pygame.mouse.get_pos()
    cursor_set = False

    for center_x, center_y in hex_centers:
        points = []
        for angle in [30, 90, 150, 210, 270, 330]:
            x_point = center_x + hex_radius * math.cos(math.radians(angle))
            y_point = center_y + hex_radius * math.sin(math.radians(angle))
            points.append((x_point, y_point))
        temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(temp_surface, (0, 0, 0, 1), points)

        if temp_surface.get_rect().collidepoint(mouse_x, mouse_y):
            px_alpha = temp_surface.get_at((mouse_x, mouse_y))[3]
            if px_alpha > 0:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                cursor_set = True
                break  # Stop checking further hexes

    if not cursor_set:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Reset to arrow if not over hex

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            log_file.write(f"Mouse clicked at: ({mouse_x}, {mouse_y})\n")

            # Reset error message
            error_message = None

            # Check if the click is within a hex
            for center_x, center_y in hex_centers:
                distance = math.sqrt((center_x - mouse_x) ** 2 + (center_y - mouse_y) ** 2)
                log_file.write(f"Hex center at: ({center_x}, {center_y})\n")
                log_file.write(f"Distance to hex center: {distance}\n")
                if distance < hex_radius:
                    if orange_cell is not None and math.sqrt(
                            (center_x - orange_cell[0]) ** 2 + (center_y - orange_cell[1]) ** 2) < 1e-6:
                        if any(is_adjacent((center_x, center_y), owned_cell) for owned_cell in
                               owned_cells[current_player]):
                            scores[current_player] += 3
                            hex_states[(center_x, center_y)] = colors[current_player]
                            owned_cells[current_player].append((center_x, center_y))
                            orange_cell = None
                            current_player = 1 - current_player  # Switch player
                        else:
                            error_message = "That is an illegal move. You can only click on an Orange hex if you are adjacent to that hex already. Please click on a blank cell to continue."
                    elif (center_x, center_y) not in hex_states:
                        hex_states[(center_x, center_y)] = colors[current_player]
                        logging.debug(f"Cell ({center_x}, {center_y}) set to color {colors[current_player]}")
                        scores[current_player] += 1
                        owned_cells[current_player].append((center_x, center_y))
                        current_player = 1 - current_player  # Switch player

                    # Generate a new orange cell
                    if current_player == 0:
                        available_cells = [cell for cell in hex_centers if cell not in hex_states]
                        if available_cells:
                            orange_cell = random.choice(available_cells)
                            hex_states[orange_cell] = (255, 165, 0)

                    break  # Stop checking further

    # Display the error message if it exists
    if error_message:
        error_text = small_font.render(error_message, True, (255, 0, 0))
        screen.blit(error_text, (580, 110))

    # Draw UI for scores
    header = big_font.render("Player 1, Player 2", True, (255, 255, 255))
    colors_row = small_font.render("Red, Blue", True, (255, 255, 255))
    scores_row = small_font.render(f"{scores[0]}, {scores[1]}", True, (255, 255, 255))

    screen.blit(header, (580, 10))  # Moved UI to the left
    screen.blit(colors_row, (605, 50))  # Moved UI to the left
    screen.blit(scores_row, (615, 80))  # Moved UI to the left

    # Update display
    pygame.display.update()

log_file.close()
# Quit Pygame
pygame.quit()
