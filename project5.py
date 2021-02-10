# Justin Quach
# 47143732


import pygame
import random
import project4_logic as logic


FRAME_RATE = 1
INITIAL_WIDTH = 600
INITIAL_HEIGHT = 600
BACKGROUND_COLOR = pygame.Color(200, 200, 200)
FIELD_LINES = pygame.Color(0, 0, 0)
RED, ORANGE, YELLOW, GREEN, LIGHTBLUE, DARKBLUE, PURPLE = \
    (245, 66, 66), (245, 144, 66), (245, 239, 66), (69, 245, 66), \
    (66, 245, 218), (66, 69, 245), (236, 66, 245)
JEWEL_COLORS = [RED, ORANGE, YELLOW, GREEN, LIGHTBLUE, DARKBLUE, PURPLE]


class ColumnsGame:
    def __init__(self):
        self.state = logic.GameState(13, 6, None)
        self.running = True
        self.surface = None


    def run(self) -> None:
        """Runs the game."""
        pygame.init()

        try:
            clock = pygame.time.Clock()

            self._create_window((INITIAL_WIDTH, INITIAL_HEIGHT))
            
            self.state.new_game()

            while self.running:
                clock.tick(FRAME_RATE)
                
                self._add_faller()
                self._lower_faller()
                self._handle_events()
                self._draw_frame()

        finally:
            pygame.quit()


    def _handle_events(self) -> None:
        """Handles events."""
        for event in pygame.event.get():
            self._handle_event(event)


    def _handle_event(self, event) -> None:
        """Given one event, it handles the event."""
        if event.type == pygame.QUIT:
            self._end_game()
        elif event.type == pygame.VIDEORESIZE:
            self._create_window(event.size)
        elif event.type == pygame.KEYDOWN:
            self._handle_moves(event)
    

    def _handle_moves(self, event) -> None:
        """Given key pressed down event, handles the move."""
        if event.key == pygame.K_LEFT:
            self.state.move_faller(-1)
        if event.key == pygame.K_RIGHT:
            self.state.move_faller(1)
        if event.key == pygame.K_SPACE:
            self.state.rotate_faller()


    def _add_faller(self) -> None:
        """Adds faller if there is none."""
        if self.state.fallerFrozen:
            emptyCols = []
            for col, topCell in enumerate(self.state.field[0]):
                if topCell.status == logic.EMPTY:
                    emptyCols.append(col)
            randCol = emptyCols[random.randint(0, len(emptyCols)-1)]
            fallerContent = []
            for i in range(3):
                fallerContent.append(random.randint(0, 6))
            self.state.create_faller(randCol+1, fallerContent)


    def _lower_faller(self) -> None:
        """Lowers faller one cell if there is a faller."""
        if not self.state.fallerFrozen:
            self.state.drop_faller()


    def _draw_frame(self) -> None:
        """Draws the frame of the game."""
        self.surface.fill(BACKGROUND_COLOR)
        self._draw_field()
        pygame.display.flip()


    def _draw_field(self) -> None:
        """Draws the field with cells."""
        cell_width_frac = 0.06
        cell_height_frac = 0.06
        cell_width_pixel = self._frac_x_to_pixel_x(cell_width_frac)
        cell_height_pixel = self._frac_y_to_pixel_y(cell_height_frac)
        top_left_frac_x = 0.1
        top_left_frac_y = 0.1
        for row in range(self.state.rows):
            for col in range(self.state.columns):
                top_left_pixel_x = self._frac_x_to_pixel_x(top_left_frac_x)
                top_left_pixel_y = self._frac_y_to_pixel_y(top_left_frac_y)
                top_left_frac_x += cell_width_frac

                cellRect = pygame.Rect(
                    top_left_pixel_x, top_left_pixel_y,
                    cell_width_pixel, cell_height_pixel)
                pygame.draw.rect(self.surface, FIELD_LINES, cellRect, 2)

                self._draw_cell(row, col, cellRect)

            top_left_frac_x = 0.1
            top_left_frac_y += cell_height_frac


    def _draw_cell(self, row: int, col: int, cellRect: pygame.Rect) -> None:
        """Draws the cell color given field row and column."""
        cellColor = self.state.field[row][col].color
        cellStatus = self.state.field[row][col].status
        if cellColor != None:
            jewelColor = pygame.Color(
                JEWEL_COLORS[cellColor][0],
                JEWEL_COLORS[cellColor][1],
                JEWEL_COLORS[cellColor][2])
            if cellStatus == logic.LANDED:
                jewelColor = pygame.Color(
                JEWEL_COLORS[cellColor][0]-50,
                JEWEL_COLORS[cellColor][1]-50,
                JEWEL_COLORS[cellColor][2]-50)
            pygame.draw.rect(self.surface, jewelColor, cellRect)


    def _frac_x_to_pixel_x(self, frac_x: float) -> int:
        """Turns fractional to pixel for x coordinate."""
        return self._frac_to_pixel(frac_x, self.surface.get_width())


    def _frac_y_to_pixel_y(self, frac_y: float) -> int:
        """Turns fractional to pixel for y coordinate."""
        return self._frac_to_pixel(frac_y, self.surface.get_height())


    def _frac_to_pixel(self, frac: float, max_pixel: int) -> int:
        """Turns fractional into pixel coordinates."""
        return int(frac * max_pixel)


    def _create_window(self, size: (int, int)) -> None:
        """Creates window size."""
        self.surface = pygame.display.set_mode(size, pygame.RESIZABLE)


    def _end_game(self) -> None:
        """Stops running the game."""
        self.running = False


if __name__ == "__main__":
    ColumnsGame().run()