import pygame
import sys

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 5
CELL_SIZE = 80
PADDING = 50
COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
]
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 24


# --- Helper Classes ---
class Cell:
    """Represents a single cell in the grid."""

    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.color_index = -1  # -1 means no color yet

    def set_color(self, color_index):
        """Set the color of the cell."""
        self.color_index = color_index

    def draw(self, screen):
        """Draw the cell on the screen."""
        if self.color_index >= 0:
            pygame.draw.rect(screen, COLORS[self.color_index], self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)  # Border


class Grid:
    """Manages the grid of cells."""

    def __init__(self, grid_size, cell_size, padding):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.padding = padding
        self.cells = self._initialize_cells()

    def _initialize_cells(self):
        """Create a grid of cells."""
        cells = []
        start_x = self.padding
        start_y = self.padding
        for row in range(self.grid_size):
            row_cells = []
            for col in range(self.grid_size):
                x = start_x + col * self.cell_size
                y = start_y + row * self.cell_size
                row_cells.append(Cell(x, y, self.cell_size))
            cells.append(row_cells)
        return cells

    def draw(self, screen):
        """Draw the grid on the screen."""
        for row in self.cells:
            for cell in row:
                cell.draw(screen)

    def get_cell_at(self, pos):
        """Return the cell at a given mouse position."""
        for row in self.cells:
            for cell in row:
                if cell.rect.collidepoint(pos):
                    return cell
        return None

    def is_valid_color(self, cell, color_index):
        """Check if the color can be applied to the cell."""
        neighbors = self.get_neighbors(cell)
        for neighbor in neighbors:
            if neighbor.color_index == color_index:
                return False
        return True

    def get_neighbors(self, cell):
        """Get neighboring cells of a given cell."""
        neighbors = []
        for row in self.cells:
            for c in row:
                if (
                    abs(c.rect.x - cell.rect.x) == self.cell_size
                    and c.rect.y == cell.rect.y
                ) or (
                    abs(c.rect.y - cell.rect.y) == self.cell_size
                    and c.rect.x == cell.rect.x
                ):
                    neighbors.append(c)
        return neighbors

    def get_valid_colors(self, cell):
        """Return a list of valid colors for the given cell."""
        valid_colors = []
        for i in range(len(COLORS)):
            if self.is_valid_color(cell, i):
                valid_colors.append(i)
        return valid_colors

    def is_complete(self):
        """Check if all cells have been filled."""
        for row in self.cells:
            for cell in row:
                if cell.color_index == -1:
                    return False
        return True


class ColorFillGame:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Color Fill Puzzle - 211080")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.grid = Grid(GRID_SIZE, CELL_SIZE, PADDING)
        self.hovered_cell = None
        self.game_won = False

        self.selected_color_index = 0

    def draw_text(self, text, x, y, center=False):
        """Render text on the screen."""
        render = self.font.render(text, True, TEXT_COLOR)
        if center:
            rect = render.get_rect(center=(x, y))
            self.screen.blit(render, rect)
        else:
            self.screen.blit(render, (x, y))

    def draw_selected_color(self):
        """Draw the currently selected color and text in the bottom-right corner."""
        x = SCREEN_WIDTH - PADDING - 50
        y = SCREEN_HEIGHT - PADDING - 60

        self.draw_text("Current Color:", x - 50, y - 30)
        self.draw_text("Right-click to change", x - 90, y + 60)

        rect = pygame.Rect(x, y, 50, 50)
        pygame.draw.rect(self.screen, COLORS[self.selected_color_index], rect)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)  # Border

    def draw_hover_preview(self, cell):
        """Draw a hover preview of valid colors for the cell."""

        if not cell or cell.color_index != -1:
            return

        valid_colors = self.grid.get_valid_colors(cell)
        preview_size = self.grid.cell_size // 2
        for i, color_index in enumerate(valid_colors):
            col = i % 2
            row = i // 2
            x = cell.rect.x + col * preview_size
            y = cell.rect.y + row * preview_size
            preview_rect = pygame.Rect(x, y, preview_size, preview_size)
            pygame.draw.rect(self.screen, (COLORS[color_index]), preview_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), preview_rect, 1)  # Border

    def check_win_condition(self):
        """Check if the player has won."""
        if self.grid.is_complete():
            self.game_won = True

    def draw_win_screen(self):
        """Draw the win screen with a play again button."""
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_text("You Win!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)
        play_again_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50
        )
        pygame.draw.rect(self.screen, (100, 200, 100), play_again_rect)
        self.draw_text(
            "Play Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25, center=True
        )
        return play_again_rect

    def reset_game(self):
        """Reset the game state for a new round."""
        self.grid = Grid(GRID_SIZE, CELL_SIZE, PADDING)
        self.selected_color_index = 0
        self.game_won = False

    def run(self):
        """Main game loop."""
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.hovered_cell = self.grid.get_cell_at(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_won:
                        play_again_rect = self.draw_win_screen()
                        if play_again_rect.collidepoint(event.pos):
                            self.reset_game()
                    elif event.button == 1:  # Left click
                        self.handle_mouse_click(event.pos)
                    elif event.button == 3:  # Right click
                        self.cycle_selected_color()

            if not self.game_won:
                self.screen.fill(BACKGROUND_COLOR)
                self.draw_text("Teodor Angeleski - Click to color the cells.", 10, 10)
                self.grid.draw(self.screen)
                if self.hovered_cell:
                    self.draw_hover_preview(self.hovered_cell)
                self.draw_selected_color()
                self.check_win_condition()
            else:
                self.draw_win_screen()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_mouse_click(self, pos):
        """Handle mouse click events."""
        cell = self.grid.get_cell_at(pos)
        if cell:
            if self.grid.is_valid_color(cell, self.selected_color_index):
                cell.set_color(self.selected_color_index)

    def cycle_selected_color(self):
        """Cycle to the next color."""
        self.selected_color_index = (self.selected_color_index + 1) % len(COLORS)


if __name__ == "__main__":
    game = ColorFillGame()
    game.run()
