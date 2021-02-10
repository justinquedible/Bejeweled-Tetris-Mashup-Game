# Justin Quach
# 47143732


EMPTY = 0
FROZEN = 1
FALLING = 2
LANDED = 3
MATCH = 4


class InvalidMoveError(Exception):
    """Raised whenever an invalid move is made."""
    pass


class GameOverError(Exception):
    """Raised when action is taken but game is over."""
    pass


class Cell():
    def __init__(self, color: int or None, status: int):
        self.color = color
        self.status = status


class GameState():
    def __init__(self, rows: int, columns: int, contents: [[]] or None):
        self.rows = rows
        self.columns = columns
        self.contents = contents
        self.hiddenField = []
        self.hiddenFieldAttached = False
        self.field = []
        self.faller = []
        self.fallerRow = 0  # row of bottom cell of faller when hidden field is attached
        self.fallerCol = 0
        self.hasMatch = False
        self.matchedCells = set()
        self.matchesRemoved = True
        self.fallerFrozen = True

    
    def new_game(self) -> None:
        """Sets up the field attribute."""
        if self.contents == None:
            self._create_empty_field()
        else:
            self._create_content_field()
            self._all_fall_down()


    def create_faller(self, col: int, colors: [int]) -> None:
        """
        Creates faller given the colors and creates hidden field.
        First color in colors will be the bottom of the faller.
        """
        if self._game_is_over():
            raise GameOverError("Game is over. Cannot create faller.")
        self.fallerFrozen = False
        self.fallerRow = 2
        self.fallerCol = col - 1
        self.faller = []
        for color in colors:
            if self._faller_landed():
                self.faller.append(Cell(color, LANDED))
            else:
                self.faller.append(Cell(color, FALLING))
        self._create_hidden_field()


    def drop_faller(self) -> None:
        """Drops faller down one row in the field and/or hidden field."""
        if self._game_is_over():
            raise GameOverError("Game is over. Cannot drop faller.")
        self._remove_faller_from_field()
        self._attach_hidden_field()
        if self.faller[0].status == LANDED and self._faller_landed():
            self._set_faller_status(FROZEN)
            self.fallerFrozen = True
        else:
            self.fallerRow += 1
            if self._faller_landed():
                self._set_faller_status(LANDED)
            else:
                self._set_faller_status(FALLING)
        self._detach_hidden_field()
        self._add_faller_to_field()


    def rotate_faller(self) -> None:
        """Rotates faller. Colors shift downward."""
        if self._game_is_over():
            raise GameOverError("Game is over. Cannot rotate faller.")
        self._remove_faller_from_field()
        self.faller[0], self.faller[1], self.faller[2] = \
        self.faller[1], self.faller[2], self.faller[0]
        self._add_faller_to_field()


    def move_faller(self, colDelta: int) -> None:
        """Moves faller left or right colDelta columns unless it is blocked by a wall or non-empty cell."""
        if self._game_is_over():
            raise GameOverError("Game is over. Cannot move faller.")
        self._remove_faller_from_field()
        self._attach_hidden_field()
        if (0 <= self.fallerCol+colDelta < self.columns) and (self.field[self.fallerRow][self.fallerCol+colDelta].status == EMPTY):
            self.fallerCol += colDelta
        self._detach_hidden_field()
        self._add_faller_to_field()


    def find_matches(self) -> None:
        """Find cells that match at least 3 in a row and change their status to MATCH."""
        if self._game_is_over():
            raise GameOverError("Game is over. Cannot find matches.")
        self._attach_hidden_field()
        self.hasMatch = False
        self.matchedCells = set()
        for row in range(len(self.field)):
            for col in range(self.columns):
                self._add_all_match(row, col)
        if len(self.matchedCells) >= 3:
            self.hasMatch = True
            for cell in self.matchedCells:
                cell.status = MATCH
        if len(self.field) != self.rows:
            self._detach_hidden_field()


    def remove_matches(self) -> None:
        """Removes all cells with MATCH status, replaces them with empty cell, and drops all cells down."""
        if self._game_is_over():
            raise GameOverError("Game is over. Cannot remove matches.")
        self._attach_hidden_field()
        for row in range(len(self.field)):
            for col in range(self.columns):
                if self.field[row][col].status == MATCH:
                    self.field[row][col] = Cell(None, EMPTY)
        self._all_fall_down()
        if len(self.field) != self.rows:
            self._detach_hidden_field()
        self.matchesRemoved = True


    def game_over(self) -> bool:
        """
        Returns True if faller could not be fully displayed on field.
        Returns False otherwise. NOTE: Only works when hidden field is not attached to field.
        """
        if len(self.field) != self.rows:
            self._detach_hidden_field()
        if (self._all_frozen() and not self._hidden_field_is_empty()) or self._top_row_is_full():
            return True
        return False


    # Private Functions Below


    def _create_empty_field(self) -> None:
        """Fills the field with empty Cells."""
        for row in range(self.rows):
            self.field.append([])
            for col in range(self.columns):
                self.field[-1].append(Cell(None, EMPTY))


    def _create_content_field(self) -> None:
        """Fills the field with the given contents, which should be a list of lists of Cells."""
        for row in range(self.rows):
            self.field.append([])
            for col in range(self.columns):
                self.field[-1].append(self.contents[row][col])


    def _add_faller_to_field(self) -> None:
        """Adds faller to hidden field and/or field."""
        self._attach_hidden_field()
        if self.faller[0].status != FROZEN:
            if self._faller_landed():
                self._set_faller_status(LANDED)
            else:
                self._set_faller_status(FALLING)
        for i in range(3):
            self.field[self.fallerRow-i][self.fallerCol] = self.faller[i]
        self._detach_hidden_field()


    def _remove_faller_from_field(self) -> None:
        """Removes faller from field and/or field."""
        self._attach_hidden_field()
        for i in range(3):
            self.field[self.fallerRow-i][self.fallerCol] = Cell(None, EMPTY)
        self._detach_hidden_field()


    def _set_faller_status(self, status: int) -> None:
        """Sets the status in every Cell of the faller to given status."""
        for i in range(3):
            self.faller[i].status = status


    def _attach_hidden_field(self) -> None:
        """Attaches hidden field to top of field."""
        self.field = self.hiddenField + self.field
        self.hiddenFieldAttached = True


    def _detach_hidden_field(self) -> None:
        """Detaches hidden field from top of field."""
        for i in range(3):
            self.field.pop(0)
        self.hiddenFieldAttached = False


    def _create_hidden_field(self) -> None:
        """Creates hidden field attribute for the faller."""
        self.hiddenField = []
        for i in range(3):
            row = []
            for col in range(self.columns):
                if self.fallerCol == col:
                    row.append(self.faller[i])
                else:
                    row.append(Cell(None, EMPTY))
            self.hiddenField.append(row)


    def _faller_landed(self) -> None:
        """
        Returns True if faller has reached bottom row or Cell below it is not empty. Returns False otherwise.
        NOTE: Only works when hidden field is attached to field.
        """
        return (self.fallerRow == len(self.field)-1) or (self.field[self.fallerRow+1][self.fallerCol].status != EMPTY)


    def _add_all_match(self, row: int, col: int) -> None:
        """
        Adds all matching sequences of 3 cells appears beginning in the given row and column and
        extending in any of the 8 possible directions to matchedCells set.
        """
        self._add_match(row, col, 0, 1)
        self._add_match(row, col, 1, 1)
        self._add_match(row, col, 1, 0)
        self._add_match(row, col, 1, -1)
        self._add_match(row, col, 0, -1)
        self._add_match(row, col, -1, -1)
        self._add_match(row, col, -1, 0)
        self._add_match(row, col, -1, 1)


    def _add_match(self, row: int, col: int, rowDelta: int, colDelta: int) -> None:
        """
        Adds a matching sequence of 3 cells that appear beginning in the given row and column and
        extending in a direction specified by rowDelta and colDelta to matchedCells set.
        """
        if self.field[row][col].status != EMPTY:
            for i in range(1, 3):
                if not self._is_valid_row_num(row + rowDelta * i) \
                        or not self._is_valid_col_num(col + colDelta * i) \
                        or self.field[row + rowDelta * i][col + colDelta * i].color != self.field[row][col].color:
                    return
            for i in range(3):
                self.matchedCells.add(self.field[row + rowDelta * i][col + colDelta * i])


    def _game_is_over(self) -> bool:
        """
        Returns True if faller could not be fully displayed on field even after matching.
        Returns False otherwise. NOTE: Only works when hidden field is not attached to field.
        """
        if len(self.field) != self.rows:
            self._detach_hidden_field()
        if self.matchesRemoved and ((self._all_frozen() and not self._hidden_field_is_empty()) or self._top_row_is_full()):
            self.matchesRemoved = False
            return True
        else:
            self.matchesRemoved = False
            return False


    def _all_frozen(self) -> bool:
        """Returns True if all cells in field are frozen or empty. Returns False otherwise."""
        for row in self.field:
            for cell in row:
                if cell.status != FROZEN and cell.status != EMPTY:
                    return False
        return True


    def _hidden_field_is_empty(self) -> bool:
        """Returns True if all cells in hidden field are empty. Returns False otherwise."""
        for row in self.hiddenField:
            for cell in row:
                if cell.status != EMPTY:
                    return False
        return True


    def _top_row_is_full(self) -> bool:
        """Returns True if top row of field is full. Returns False otherwise."""
        for cell in self.field[0]:
            if cell.status == EMPTY:
                return False
        return True


    def _all_fall_down(self) -> None:
        """All Cells fall down to the bottom."""
        for i in range(len(self.field)*2):
            self._all_fall_once()


    def _all_fall_once(self) -> None:
        """All Cells fall down one cell if there's an empty cell below."""
        for row in range(len(self.field)-2, -1, -1):
            for col in range(self.columns):
                self._fall_once(row, col)


    def _fall_once(self, row: int, col: int) -> None:
        """If given Cell has an empty Cell below, they switch positions."""
        self._require_valid_row_num(row)
        self._require_valid_col_num(col)
        if self._is_empty_below(row, col):
            self.field[row][col], self.field[row+1][col] = self.field[row+1][col], self.field[row][col]


    def _is_empty_below(self, row: int, col: int) -> bool:
        """Returns True if there is an empty Cell below given Cell. Returns False otherwise."""
        self._require_valid_row_num(row)
        self._require_valid_col_num(col)
        try:
            if (self.field[row][col].status != EMPTY) and (self.field[row+1][col].status == EMPTY):
                return True
            else:
                return False
        except IndexError:
            raise IndexError("Can't check cell below the bottom most cell.")


    def _require_valid_row_num(self, rowNum: int) -> None:
        """Raises a ValueError if its parameter is not a valid row number."""
        if type(rowNum) != int or not self._is_valid_row_num(rowNum):
            raise ValueError(f"Row number must be int between 0 and {len(self.field)-1}")


    def _require_valid_col_num(self, colNum: int) -> None:
        """Raises a ValueError if its parameter is not a valid column number."""
        if type(colNum) != int or not self._is_valid_col_num(colNum):
            raise ValueError(f"Column number must be int between 0 and {self.columns-1}")


    def _is_valid_row_num(self, rowNum: int) -> bool:
        """Returns True if the given row number is valid; returns False otherwise."""
        return 0 <= rowNum < len(self.field)


    def _is_valid_col_num(self, colNum: int) -> bool:
        """Returns True if the given column number is valid; returns False otherwise."""
        return 0 <= colNum < self.columns