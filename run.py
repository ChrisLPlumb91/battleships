import random
import time
import uuid
import gspread
from gspread_formatting import CellFormat
from gspread_formatting import format_cell_range
from gspread_formatting import Color
from gspread_formatting import set_column_width
from gspread_formatting import set_row_height
from gspread_formatting import Border
from gspread_formatting import Borders
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)

SHEET = GSPREAD_CLIENT.open('Battleships')

SHIP_SIZES = [1, 1, 2, 2, 3, 4, 5]
SHIP_INITIALS = ['S', 'S', 'D', 'D', 'C', 'B', 'A']

grid_dict_cpu = {}
grid_dict_player = {}


def set_grid_size():
    """
    Prompts the user to enter one of three 2-digit integers,
    and validates this input. This input is cast to an int,
    and the try / except catches any input that cannot
    be cast in this way.

    Because any number can be entered, a function
    that further validates the input to ensure
    that it is one of the three options is called.
    """
    while True:
        grid = 0

        while grid == 0:
            print('\nPlease select the size of the grid that you would like' +
                  ' to play on.')
            print('(Enter 10 for 10x10, 12 for 12x12, 14 for 14x14, or 0' +
                  ' to exit the game)\n')

            try:
                grid = int(input('Enter your selection here:\n'))
            except ValueError:
                print('Please enter either 10, 12, or 14' +
                      ' (or 0 if you wish to quit).\n')
                continue

            if grid == 0:
                exit_game()

        if validate_grid(grid):
            print(f'\n{grid}x{grid} grid selected.\n')
            break

    return grid


def exit_game():
    """
    If the user enters 0 during the grid size function, they are taken to this
    function. If they enter N, the game will return to the grid selection
    function.

    The while loop here ensures that the game can only proceed
    (exit or continue), if the user enters the correct value.
    """
    while True:
        choice = input('Do you really want to quit the game?' +
                       ' (enter Y or N)\n').upper()

        if choice == 'N':
            return True
        elif choice == 'Y':
            print('\nThanks for playing!\n')
            exit()
        else:
            print('Please enter either Y or N.\n')
            continue


def validate_grid(grid):
    """
    This is the function that further validates the user's input for their
    choice of grid. If their choice is not one of the three, a ValueError
    is raised and caught. They are then carried back to the grid selection
    function.
    """
    try:
        if grid != 10 and grid != 12 and grid != 14:
            raise ValueError(f'{grid} is not a valid option.')
    except ValueError as error:
        print(f'{error} Please try again.\n')
        return False

    return True


def generate_sheet(grid, sheet_id):
    """
    This function is used to create and format both the player
    and CPU spreadsheets. To ensure that players aren't working
    from the same sheet, a UUID is used to create a unique
    one for each of them.
    """
    sheet = SHEET.add_worksheet(sheet_id, grid, grid)

    formatting_all = CellFormat(
                backgroundColor=Color(0.78, 0.85, 0.97),
                horizontalAlignment='CENTER',
                verticalAlignment='MIDDLE',
                borders=Borders(bottom=Border('SOLID'),
                                top=Border('SOLID'),
                                left=Border('SOLID'),
                                right=Border('SOLID')))

    formatting_top = (CellFormat(borders=Borders
                      (top=Border('SOLID_MEDIUM'))))
    formatting_bottom = (CellFormat(borders=Borders
                         (bottom=Border('SOLID_MEDIUM'))))
    formatting_left = (CellFormat(borders=Borders
                       (left=Border('SOLID_MEDIUM'))))
    formatting_right = (CellFormat(borders=Borders
                        (right=Border('SOLID_MEDIUM'))))

    column_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G',
                      'H', 'I', 'J', 'K', 'L', 'M', 'N']

    for row in range(grid):
        row = row + 1
        format_cell_range(sheet, f'{row}', formatting_all)
        set_row_height(sheet, str(row), 42)
        set_column_width(sheet, column_letters[row - 1], 42)

        if row == 1:
            format_cell_range(sheet, f'{row}', formatting_top)
            format_cell_range(sheet, column_letters[row - 1],
                              formatting_left)
        elif row == grid:
            format_cell_range(sheet, f'{row}', formatting_bottom)
            format_cell_range(sheet, column_letters[grid - 1],
                              formatting_right)

    return sheet


def select_player_ships(grid):
    """
    This function prompts the user to enter coordinates for each of their
    ships. Each request is followed by a call to a validating function,
    and the input itself becomes the value of a key in a dictionary.
    Each key bears the name of a ship.

    A function is then called that ensures that none of the ships'
    coordinates are identical or overlapping.

    This function ultimately returns the dictionary of ships
    and their coordinates.
    """
    player_ships = {}

    while True:
        print('\nYou will now be asked to place each one of your ships.\n')
        print('For the first two ships, you must enter two numbers,' +
              ' separated by a space, to serve as x and y coordinates,' +
              ' e.g. 2 10\n')
        print('For the remaining five ships, you must also enter either' +
              ' H, V, DR, or DL, for Horizontal, Vertical, Diagonal Right,' +
              ' and Diagonal Left, respectively, e.g. 2 10 V\n')
        print('Two things to keep in mind:')
        print(f'1. You have selected a {grid}x{grid} grid, which means' +
              f' that numbers greater than {grid} will not be accepted.')
        print("2. The letters you must provide for the last 5 ships'" +
              " orientations are not case-sensitive.\n\n")

        while True:
            x = 2
            player_ships['first Submarine'] = input('Please position your' +
                                                    ' first Submarine' +
                                                    ' (occupies 1 square)' +
                                                    ':\n').split(' ')
            if validate_ship(grid, x, player_ships['first Submarine'], 'first'
                             + ' Submarine'):
                break
        while True:
            x = 2
            player_ships['second Submarine'] = input('Please position your' +
                                                     ' second Submarine' +
                                                     ' (occupies 1 square)' +
                                                     ':\n').split(' ')

            if validate_ship(grid, x, player_ships['second Submarine'],
                             'second Submarine'):
                break
        while True:
            x = 3
            player_ships['first Destroyer'] = input('Please position your' +
                                                    ' first Destroyer' +
                                                    ' (occupies 2 squares)' +
                                                    ':\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['first Destroyer'],
                             'first Destroyer'):
                break

        while True:
            x = 3
            player_ships['second Destroyer'] = input('Please position your' +
                                                     ' second Destroyer' +
                                                     ' (occupies 2 squares)' +
                                                     ':\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['second Destroyer'],
                             'second Destroyer'):
                break

        while True:
            x = 3
            player_ships['Cruiser'] = input('Please position your' +
                                            ' Cruiser' +
                                            ' (occupies 3 squares)' +
                                            ':\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['Cruiser'], 'Cruiser'):
                break
        while True:
            x = 3
            player_ships['Battleship'] = input('Please position your' +
                                               ' Battleship' +
                                               ' (occupies 4 squares)' +
                                               ':\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['Battleship'],
                             'Battleship'):
                break
        while True:
            x = 3
            player_ships['Aircraft Carrier'] = input('Please position your' +
                                                     ' Aircraft Carrier' +
                                                     ' (occupies 5 squares)' +
                                                     ':\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['Aircraft Carrier'],
                             'Aircraft Carrier'):
                break

        if validate_all_ships(grid, player_ships):
            print('\nPositioning your ships. Please wait...')
            break
    return player_ships


def validate_ship(grid, sub_or_ship, coordinate_list, ship_name):
    """
    This is the function that is called for each pair of coordinates
    that the user enters. It checks to makes sure that the user
    has not: entered a single number, entered more numbers than required,
    entered fewer numbers than required, neglected to provide a value
    for the orientation of the ships that take up 2 squares or more,
    or entered a letter where a number was expected.
    """
    try:
        coordinate_dict = dict(enumerate(coordinate_list))

        if not coordinate_dict.get(1):
            raise ValueError('\nEither you entered only a single character,' +
                             ' or you did not put a space between the' +
                             ' characters, or you pressed enter before' +
                             'typing anything.')

        if (not coordinate_list[0].isnumeric() or
                not coordinate_list[1].isnumeric()):
            raise ValueError('\nYou entered a letter, a punctuation mark, ' +
                             'or a space, where a number was expected.')

        if sub_or_ship == 2 and len(coordinate_list) > 2:
            raise ValueError(f'\nYou entered {len(coordinate_list)} ' +
                             'numbers / characters where only 2 ' +
                             'were required (if you cannot see ' +
                             'the problem, make sure you did not enter ' +
                             'any spaces before the first number).')
        elif sub_or_ship == 3 and len(coordinate_list) > 3:
            raise ValueError(f'\nYou entered {len(coordinate_list)} ' +
                             'numbers / characters where only 3 ' +
                             'were required (if you cannot see ' +
                             'the problem, make sure you did not enter ' +
                             'any spaces before the first number).')

        if sub_or_ship == 3 and len(coordinate_list) < 3:
            raise ValueError(f'\nYou entered {len(coordinate_list)} ' +
                             'numbers / characters where 3 were required.')

        if (sub_or_ship == 3 and coordinate_list[2] != 'H' and
                coordinate_list[2] != 'V' and
                coordinate_list[2] != 'DL' and
                coordinate_list[2] != 'DR'):
            raise ValueError('\nYou did not provide a valid ' +
                             'orientation value (H, V, DR, or DL) ' +
                             f'for the {ship_name} that you placed.')

        if int(coordinate_list[0]) <= 0 or int(coordinate_list[1]) <= 0:
            raise ValueError("\nYou entered a coordinate that doesn't exist " +
                             "on the grid.")

        for y in coordinate_list:
            if y.isalpha():
                continue
            if int(y) > grid:
                raise ValueError('\nThese coordinates would place ' +
                                 'this ship outside ' +
                                 f'of the {grid}x{grid} grid.')

    except ValueError as error:
        print(f'{error} Try again.\n')
        return False

    return True


def validate_all_ships(grid, player_ships):
    """
    This is the function that checks to make sure that the coordinates
    of each of the ships do not clash with one another. It also checks
    to make sure that a given ship does not extend beyond the boundaries
    of the grid.

    Another important thing that it does is "occupy" keys in a dictionary.
    Each key is a coordinate, and this function assigns values to the
    coordinates that are occupied by ships. It figures this out by referring
    to each ship's length, as well as its starting coordinate.
    """
    global grid_dict_player

    coordinates = list(player_ships.values())

    try:
        for x, coordinate in enumerate(coordinates, start=0):
            for y, coordinate_comp in enumerate(coordinates, start=0):
                if x == y:
                    continue
                elif coordinate == coordinate_comp:
                    raise ValueError('\nYou chose identical coordinates ' +
                                     'for two different ships.')

        for x, player_ship in enumerate(player_ships, start=0):
            if x >= 2:
                if (int(player_ships[player_ship][0]) +
                        SHIP_SIZES[x] - 1 > grid
                        and player_ships[player_ship][2] == 'H'
                        or int(player_ships[player_ship][1])
                        + SHIP_SIZES[x] - 1 > grid
                        and player_ships[player_ship][2] == 'V'
                        or int(player_ships[player_ship][0])
                        + SHIP_SIZES[x] - 1 > grid
                        and player_ships[player_ship][2] == 'DR'
                        or int(player_ships[player_ship][1])
                        + SHIP_SIZES[x] - 1 > grid
                        and player_ships[player_ship][2] == 'DR'
                        or int(player_ships[player_ship][0])
                        + SHIP_SIZES[x] - 1 > grid
                        and player_ships[player_ship][2] == 'DL'
                        or int(player_ships[player_ship][1])
                        + SHIP_SIZES[x] - 1 > grid
                        and player_ships[player_ship][2] == 'DL'
                        or int(player_ships[player_ship][0])
                        - SHIP_SIZES[x] + 1 < 1
                        and player_ships[player_ship][2] == 'DL'):

                    raise ValueError(f'\nThe {player_ship} that you placed ' +
                                     'is partially outside ' +
                                     f'of the {grid}x{grid} grid.')

        for player_ship in player_ships:
            for grid_coordinates in grid_dict_player:

                coordinates_comp = grid_coordinates.split(' ')

                for x, coordinate in enumerate(coordinates, start=0):
                    if len(coordinate) == 3:
                        if (coordinates_comp == coordinate[0:2]
                                and 'occupied'
                                not in grid_dict_player[grid_coordinates]
                                and player_ships[player_ship] == coordinate):

                            grid_dict_player[grid_coordinates] = (
                                f'occupied by {player_ship}')

                            if coordinate[2] == 'H':
                                for y in range(0, SHIP_SIZES[x] - 1):

                                    coordinates_comp[0] = (
                                        int(coordinates_comp[0]) + 1)
                                    coordinates_comp[0] = (
                                        str(coordinates_comp[0]))

                                    coord_str = (str(coordinates_comp[0] +
                                                 ' ' + coordinates_comp[1]))

                                    if ('occupied'
                                            not in
                                            grid_dict_player[coord_str]):
                                        grid_dict_player[coord_str] = (
                                            f'occupied by {player_ship}')
                                    else:
                                        raise ValueError('\nThe horizontal ' +
                                                         f'{player_ship} ' +
                                                         'that you placed ' +
                                                         'overlapped with ' +
                                                         'another ship.')
                            elif coordinate[2] == 'V':
                                for y in range(0, SHIP_SIZES[x] - 1):

                                    coordinates_comp[1] = (
                                        int(coordinates_comp[1]) + 1)
                                    coordinates_comp[1] = (
                                        str(coordinates_comp[1]))

                                    coord_str = (str(coordinates_comp[0]
                                                 + ' ' + coordinates_comp[1]))
                                    if ('occupied'
                                            not in
                                            grid_dict_player[coord_str]):

                                        grid_dict_player[coord_str] = (
                                            f'occupied by {player_ship}')
                                    else:
                                        raise ValueError('\nThe vertical ' +
                                                         f'{player_ship} ' +
                                                         'that you placed ' +
                                                         'overlapped with ' +
                                                         'another ship.')
                            elif coordinate[2] == 'DR':
                                for y in range(0, SHIP_SIZES[x] - 1):

                                    coordinates_comp[0] = (
                                        int(coordinates_comp[0]) + 1)
                                    coordinates_comp[0] = (
                                        str(coordinates_comp[0]))
                                    coordinates_comp[1] = (
                                        int(coordinates_comp[1]) + 1)
                                    coordinates_comp[1] = (
                                        str(coordinates_comp[1]))

                                    coord_str = (str(coordinates_comp[0] +
                                                 ' ' + coordinates_comp[1]))
                                    if ('occupied'
                                            not in
                                            grid_dict_player[coord_str]):

                                        grid_dict_player[coord_str] = (
                                            f'occupied by {player_ship}')
                                    else:
                                        raise ValueError('\nThe right ' +
                                                         'diagonal ' +
                                                         f'{player_ship} ' +
                                                         'that you placed ' +
                                                         'overlapped with ' +
                                                         'another ship.')
                            elif coordinate[2] == 'DL':
                                for y in range(0, SHIP_SIZES[x] - 1):
                                    coordinates_comp[0] = (
                                        int(coordinates_comp[0]) - 1)
                                    coordinates_comp[0] = (
                                        str(coordinates_comp[0]))
                                    coordinates_comp[1] = (
                                        int(coordinates_comp[1]) + 1)
                                    coordinates_comp[1] = (
                                        str(coordinates_comp[1]))

                                    coord_str = (str(coordinates_comp[0] +
                                                 ' ' + coordinates_comp[1]))
                                    if ('occupied'
                                            not in
                                            grid_dict_player[coord_str]):

                                        grid_dict_player[coord_str] = (
                                            f'occupied by {player_ship}')
                                    else:
                                        raise ValueError('\nThe left ' +
                                                         'diagonal ' +
                                                         f'{player_ship} ' +
                                                         'that you placed ' +
                                                         'overlapped ' +
                                                         'with another ship.')

                    elif (coordinates_comp == coordinate
                          and player_ships[player_ship] == coordinate
                          and 'occupied'
                          not in grid_dict_player[grid_coordinates]):

                        grid_dict_player[grid_coordinates] = (
                            f'occupied by {player_ship}')
                    else:
                        continue
    except (ValueError, IndexError) as error:
        print(f'{error} Please place your ships again.\n')
        grid_dict_player = ({f'{x} {y}': 'empty'
                            for y in range(1, grid + 1)
                            for x in range(1, grid + 1)})
        return False

    return True


def place_player_ships(grid, player_id):
    """
    This function is responsible for actually inserting the user's ships
    into the spreadsheet. Depending on the ship, a different initial
    is inserted into the correct cells of the spreadsheet.

    Throughout its execution, this function creates lists that are either
    10, 12, or 14 in length (depending on the grid size), and then appends
    them to the 'player' spreadsheet. Where in each row a ship should be,
    and which ship that ship should be, is determined from the dictionary
    of coordinates and ships created previously.
    """
    player_grid = SHEET.worksheet(player_id)
    # player_grid.clear()

    global grid_dict_player

    row_values = list(grid_dict_player.values())
    row_list = []
    overflow = 0

    if grid == 12:
        overflow = 3
    elif grid == 14:
        overflow = 6

    for x in range(grid + overflow):
        if (grid == 10
                and len(row_list) == 10
                or grid == 12
                and len(row_list) == 12
                or grid == 14
                and len(row_list) == 14):

            row_list = []

        for y in range(grid):
            if x == 0:
                if (row_values[y] == 'occupied by first Submarine'
                        or row_values[y] == 'occupied by second Submarine'):
                    row_list.append(SHIP_INITIALS[0])
                elif (row_values[y] == 'occupied by first Destroyer'
                        or row_values[y] == 'occupied by second Destroyer'):
                    row_list.append(SHIP_INITIALS[2])
                elif row_values[y] == 'occupied by Cruiser':
                    row_list.append(SHIP_INITIALS[4])
                elif row_values[y] == 'occupied by Battleship':
                    row_list.append(SHIP_INITIALS[5])
                elif row_values[y] == 'occupied by Aircraft Carrier':
                    row_list.append(SHIP_INITIALS[6])
                else:
                    row_list.append('~')
            elif x > 0:
                str_x = str(x)
                str_y = str(y)
                int_xy = int(str_x + str_y)

                if grid == 12 and int_xy <= 11 or grid == 12 and int_xy > 143:
                    continue
                elif (grid == 14 and int_xy <= 13
                      or grid == 14 and int_xy > 195):
                    continue
                else:
                    if (row_values[int_xy] == 'occupied by first Submarine'
                            or row_values[int_xy] == 'occupied by second ' +
                            'Submarine'):
                        row_list.append(SHIP_INITIALS[0])
                    elif (row_values[int_xy] == 'occupied by first Destroyer'
                            or row_values[int_xy] == 'occupied by second ' +
                            'Destroyer'):
                        row_list.append(SHIP_INITIALS[2])
                    elif row_values[int_xy] == 'occupied by Cruiser':
                        row_list.append(SHIP_INITIALS[4])
                    elif row_values[int_xy] == 'occupied by Battleship':
                        row_list.append(SHIP_INITIALS[5])
                    elif row_values[int_xy] == 'occupied by Aircraft Carrier':
                        row_list.append(SHIP_INITIALS[6])
                    else:
                        row_list.append('~')

            if (x >= 1 and grid == 12 and len(row_list) == 12
                    and y % 2 != 0 or x >= 1 and grid == 14
                    and len(row_list) == 14 and y % 2 != 0):

                player_grid.append_row(row_list)
                row_list = []

            if (grid == 12 and x >= 1 and y == 9
                    or grid == 14 and x >= 1 and y == 9):
                break

        if grid == 10 and len(row_list) == 10:
            player_grid.append_row(row_list)
        elif grid == 12 and x == 0 or grid == 14 and x == 0:
            player_grid.append_row(row_list)

    print('\nYour spreadsheet has been populated ' +
          'with your ships! Take a look!.\n')


def select_cpu_ships(grid, player_ships):
    """
    This function assigns coordinates to the CPU's ships. It makes use of
    the random library to generate those coordinates. For the ships
    that take up more than 1 square, either H or V is selected
    randomly to provide their orientation on the grid.

    Then, a function is called on the resulting dictionary
    to validate its contents. If the validation function
    returns True, this function returns a dictionary of the CPU's ships
    and their starting coordinates.
    """
    cpu_ships = {}
    cpu_ship_names = list(player_ships.keys())

    global grid_dict_cpu

    while True:
        for x, cpu_ship in enumerate(cpu_ship_names, start=0):

            random_coordinate_1 = 0
            random_coordinate_2 = 0
            sub_coordinates_string = []
            other_coordinates_string = []

            while random_coordinate_1 == 0 or random_coordinate_2 == 0:
                random_coordinate_1 = random.randrange(grid + 1)
                random_coordinate_2 = random.randrange(grid + 1)

            if x <= 1:
                sub_coordinates_string.append(str(random_coordinate_1))
                sub_coordinates_string.append(str(random_coordinate_2))
                sub_coordinates_string.append('')
                cpu_ships[cpu_ship] = sub_coordinates_string
            else:
                other_coordinates_string.append(str(random_coordinate_1))
                other_coordinates_string.append(str(random_coordinate_2))
                (other_coordinates_string.append
                    (random.choice(['H', 'V', 'DR', 'DL'])))
                cpu_ships[cpu_ship] = other_coordinates_string

        if validate_cpu_ships(grid, cpu_ships):
            print("You sense that the CPU's ships have taken up position " +
                  "behind the colossal wall before you...\n")
            break

    return cpu_ships


def validate_cpu_ships(grid, cpu_ships):
    """
    This is the function that validates the coordinates randomly generated
    for the CPU's ships. This function generates a dictionary of coordinates,
    and "occupies" the relevant coordinates with values.

    Several flags are set if conflicts are detected, and the validation
    can only be successful if all of these flags are False by the end.
    If they are True, a different set of coordinates are randomly generated
    for the CPU.
    """
    global grid_dict_cpu

    cpu_ships_coordinates = list(cpu_ships.values())

    while True:
        same_square = False

        for y, cpu_ship_coordinates in enumerate(cpu_ships_coordinates,
                                                 start=0):
            for z in range(7):
                if z != y:
                    if (cpu_ship_coordinates[0:2]
                            == cpu_ships_coordinates[z][0:2]):
                        same_square = True
                    else:
                        continue
                else:
                    continue

        grid_dict_cpu = ({f'{x} {y}': 'empty'
                         for y in range(1, grid + 1)
                         for x in range(1, grid + 1)})
        grid_keys = list(grid_dict_cpu.keys())
        keys_dict = dict(enumerate(grid_keys))

        overlap = False
        out_of_bounds = False

        for x, cpu_ship in enumerate(cpu_ships, start=0):
            for ind, coordinates in enumerate(grid_dict_cpu, start=0):
                if (coordinates.split(' ') == cpu_ships[cpu_ship][0:2]
                        and cpu_ships[cpu_ship][2] == 'H'):

                    if 'occupied' not in grid_dict_cpu[coordinates]:
                        grid_dict_cpu[coordinates] = f'occupied by {cpu_ship}'
                    else:
                        overlap = True

                    for z in range(1, SHIP_SIZES[x]):
                        if keys_dict.get(ind + z):
                            if (grid_keys[ind + z].split(' ')[1] ==
                                    coordinates.split(' ')[1]):

                                if ('occupied'
                                        not in
                                        grid_dict_cpu[grid_keys[ind + z]]):

                                    grid_dict_cpu[grid_keys[ind + z]] = (
                                        f'occupied by {cpu_ship}')
                                else:
                                    overlap = True
                            else:
                                out_of_bounds = True
                elif (coordinates.split(' ') == cpu_ships[cpu_ship][0:2]
                      and cpu_ships[cpu_ship][2] == 'V'):

                    if 'occupied' not in grid_dict_cpu[coordinates]:
                        grid_dict_cpu[coordinates] = f'occupied by {cpu_ship}'
                    else:
                        overlap = True
                    for z in range(1, SHIP_SIZES[x]):
                        if keys_dict.get(ind + grid * z):
                            if ('occupied' not in
                                    grid_dict_cpu[grid_keys[ind + grid * z]]):

                                grid_dict_cpu[grid_keys[ind + grid * z]] = (
                                    f'occupied by {cpu_ship}')
                            else:
                                overlap = True
                        else:
                            out_of_bounds = True
                elif (coordinates.split(' ') == cpu_ships[cpu_ship][0:2]
                        and cpu_ships[cpu_ship][2] == 'DR'):

                    if 'occupied' not in grid_dict_cpu[coordinates]:
                        grid_dict_cpu[coordinates] = f'occupied by {cpu_ship}'
                    else:
                        overlap = True

                    for z in range(1, SHIP_SIZES[x]):
                        if keys_dict.get(ind + grid * z + z):
                            keys_dict_coord_list = (
                                keys_dict[ind + grid * z + z].split(' '))

                            if (int(keys_dict_coord_list[1])
                                    == int(cpu_ships[cpu_ship][1]) + (z + 1)
                                    or int(keys_dict_coord_list[1]) + 1
                                    > grid
                                    or int(keys_dict_coord_list[0]) + 1
                                    > grid):

                                out_of_bounds = True
                            if ('occupied' not in
                                    grid_dict_cpu
                                    [grid_keys[ind + grid * z + z]]):

                                grid_dict_cpu[grid_keys[ind+grid*z+z]] = (
                                    f'occupied by {cpu_ship}')
                            else:
                                overlap = True
                        else:
                            out_of_bounds = True
                elif (coordinates.split(' ') == cpu_ships[cpu_ship][0:2]
                        and cpu_ships[cpu_ship][2] == 'DL'):

                    if 'occupied' not in grid_dict_cpu[coordinates]:
                        grid_dict_cpu[coordinates] = f'occupied by {cpu_ship}'
                    else:
                        overlap = True
                    for z in range(1, SHIP_SIZES[x]):

                        if keys_dict.get(ind + grid * z - z):
                            keys_dict_coord_list = (
                                keys_dict[ind + grid * z - z].split(' '))

                            if (int(keys_dict_coord_list[1])
                                    == int(cpu_ships[cpu_ship][1]) + (z - 1)
                                    or int(keys_dict_coord_list[1]) + 1
                                    > grid):

                                out_of_bounds = True
                            elif ('occupied'
                                  not in grid_dict_cpu
                                  [grid_keys[ind + grid * z - z]]):

                                grid_dict_cpu[grid_keys[ind+grid*z-z]] = (
                                    f'occupied by {cpu_ship}')
                            else:
                                overlap = True
                        else:
                            out_of_bounds = True
                elif coordinates.split(' ') == cpu_ships[cpu_ship][0:2]:
                    if 'occupied' not in grid_dict_cpu[coordinates]:
                        grid_dict_cpu[coordinates] = f'occupied by {cpu_ship}'
                    else:
                        overlap = True

        if not same_square and not overlap and not out_of_bounds:
            break
        else:
            return False
    return True


def start_game(grid, player_ships, cpu_ships, player_id, cpu_id):
    """
    This function contains code for the playable part of the program.
    It prompts the user to input numbers as coordinates,
    just like when they had to position their ships.

    These coordinates are checked against the CPU's dictionary of coordinates,
    and if occupied coordinates are found, the number of hits against the CPU
    ticks up, and the initial of ship that was hit is inserted in the 'cpu'
    spreadsheet, at the coordinates where that ship was found.

    The CPU does the same, but its guess is randomly generated,
    and if it lands a hit, the respective initial on the 'player'
    spreadsheet becomes an 'X'. Also, a validation function
    is not called to validate the CPU guess.
    """
    print('\nMan the poop deck! War has returned to the high seas!\n')

    player_grid = SHEET.worksheet(player_id)
    cpu_grid = SHEET.worksheet(cpu_id)

    global grid_dict_player
    global grid_dict_cpu

    hit_dict_player = {}
    hit_dict_cpu = {}

    for x in range(grid):
        cpu_grid_sea = []
        for y in range(grid):
            cpu_grid_sea.append('~')
        cpu_grid.append_row(cpu_grid_sea)

    for x, player_ship in enumerate(player_ships, start=0):
        hit_dict_player[player_ship] = []
        for y in range(SHIP_SIZES[x]):
            hit_dict_player[player_ship].append('O')

    for x, cpu_ship in enumerate(cpu_ships, start=0):
        hit_dict_cpu[cpu_ship] = []
        for y in range(SHIP_SIZES[x]):
            hit_dict_cpu[cpu_ship].append('O')

    player_hits = 0
    cpu_hits = 0

    while player_hits < 18 or cpu_hits < 18:
        while True:
            print('Try to guess where your opponent has placed ' +
                  'their ships! (any hits will appear on the ' +
                  'CPU spreadsheet!)')
            player_guess = input('Enter two numbers separated by a space ' +
                                 'and then press enter (neither number ' +
                                 'should be greater ' +
                                 f'than {grid}):\n').split(' ')

            if validate_guess(player_guess, grid):
                break

        player_guess_str = player_guess[0] + ' ' + player_guess[1]

        if 'occupied' in grid_dict_cpu[player_guess_str]:
            hit_ship_str = (grid_dict_cpu[player_guess_str]
                            [12:len(grid_dict_cpu[player_guess_str]) + 1])

            if len(hit_dict_cpu[hit_ship_str]) >= 2:
                hit_dict_cpu[hit_ship_str].pop()
                print(f"\nYou hit the CPU's {hit_ship_str}!\n")
            elif len(hit_dict_cpu[hit_ship_str]) == 1:
                hit_dict_cpu[hit_ship_str].pop()
                print(f"\nYou sunk the CPU's {hit_ship_str}!\n")

            if 'first' in hit_ship_str:
                ship_initial = hit_ship_str[6:7].upper()
            elif 'second' in hit_ship_str:
                ship_initial = hit_ship_str[7:8].upper()
            else:
                ship_initial = hit_ship_str[0].upper()

            cpu_grid.update_cell(player_guess[1], player_guess[0],
                                 ship_initial)

            grid_dict_cpu[player_guess_str] = 'Hit!'
            cpu_hits += 1
        elif grid_dict_cpu[player_guess_str] == 'Hit!':
            print('Nothing but wreckage, there!\n')
        else:
            print('\nMiss!\n')

        if cpu_hits >= 18:
            break

        print("CPU's turn!\n")

        random_coordinate_1 = 0
        random_coordinate_2 = 0

        while True:
            while random_coordinate_1 == 0 or random_coordinate_2 == 0:
                random_coordinate_1 = random.randrange(grid + 1)
                random_coordinate_2 = random.randrange(grid + 1)

            cpu_guess_str = (str(random_coordinate_1) +
                             ' ' + str(random_coordinate_2))

            if 'occupied' in grid_dict_player[cpu_guess_str]:
                hit_ship_str = (grid_dict_player[cpu_guess_str]
                                [12:len(grid_dict_player[cpu_guess_str])
                                + 1])

                if len(hit_dict_player[hit_ship_str]) >= 2:
                    hit_dict_player[hit_ship_str].pop()
                    print(f'The CPU guessed {cpu_guess_str} ' +
                          f'and hit your {hit_ship_str}!\n')
                elif len(hit_dict_player[hit_ship_str]) == 1:
                    hit_dict_player[hit_ship_str].pop()
                    print(f'The CPU guessed {cpu_guess_str} ' +
                          f'and sunk your {hit_ship_str}!\n')

                grid_dict_player[cpu_guess_str] = 'Hit!'
                player_hits += 1

                player_grid.update_cell(random_coordinate_2,
                                        random_coordinate_1, 'X')
                break
            elif grid_dict_player[cpu_guess_str] == 'Hit!':
                print(f'The CPU guessed {cpu_guess_str} ' +
                      'and blasted the wreckage of one of your ships!\n')
                break
            else:
                print(f'The CPU guessed {cpu_guess_str}, but missed!\n')
                break

    if cpu_hits >= 18:
        print('YOU ARE VICTORIOUS!\n')
        if player_hits == 0:
            print('FLAWLESS VICTORY!!\n')
        elif player_hits > 0:
            print(f'...however, The CPU landed {player_hits} ' +
                  'hit(s) on your fleet...\n')
    elif player_hits >= 18:
        print('The CPU has scuppered your entire fleet! You lose!')


def validate_guess(player_guess, grid):
    """
    This function validates each guess the user makes during the playable
    phase of the program.
    """
    player_guess_dict = dict(enumerate(player_guess))

    try:
        if not player_guess_dict.get(1):
            raise ValueError('Either you entered nothing, or only a ' +
                             'single character, or you did not put ' +
                             'a space between the characters.')
        elif (not player_guess[0].isnumeric()
              or not player_guess[1].isnumeric()):
            raise ValueError('The coordinates you provided contained ' +
                             'an alphabetic character, a punctuation ' +
                             'mark, or a space, where a number was expected.')
        elif player_guess[0].isalpha() or player_guess[1].isalpha():
            raise ValueError('The coordinates you provided contained ' +
                             'an alphabetic character, a punctuation ' +
                             'mark, or a space, where a number was expected.')
        elif len(player_guess) > 2:
            raise ValueError(f'You entered {len(player_guess)} ' +
                             'numbers / characters. Only 2 are required.')
        elif int(player_guess[0]) > grid or int(player_guess[1]) > grid:
            raise ValueError('The coordinates you provided lie outside ' +
                             f'of the {grid}x{grid} grid.')
        elif int(player_guess[0]) <= 0 or int(player_guess[1]) <= 0:
            raise ValueError('There is no 0 coordinate on the grid.')

        else:
            return True
    except ValueError as error:
        print(f'{error} Please guess again.\n')
        return False


def main():
    """
    This is the main function for the game. Excluding the validation
    functions, all of the major functions of the program are called
    from inside this one. At the end, the user is asked if they would
    like to play again. If they do, the game restarts from the beginning,
    and if they do not, execution stops.
    """
    continue_game = 'Y'

    while continue_game == 'Y':
        global grid_dict_player
        global grid_dict_cpu

        grid = set_grid_size()
        print('Please wait while your grid is generated...\n')

        player_grid_id = 'player-' + str(uuid.uuid4())
        player_sheet = generate_sheet(grid, player_grid_id)

        print('Your grid has been generated! Have a look ' +
              'at the spreadsheet!\n')

        grid_dict_player = ({f'{x} {y}': 'empty'
                            for y in range(1, grid + 1)
                            for x in range(1, grid + 1)})
        player_ships = select_player_ships(grid)
        place_player_ships(grid, player_grid_id)

        print('\nAnnoyingly, there is a limit to the number ' +
              'of write operations that can be made to a Google ' +
              'Sheet in a minute...\n')
        print('Therefore, before it can generate the CPU grid, ' +
              'this program must pause for 60 seconds.\n')
        print("Use this time to plan your strategy!\n")
        time.sleep(60)

        print('Thanks for waiting! Now generating CPU grid...\n\n')

        cpu_grid_id = 'cpu-' + str(uuid.uuid4())
        cpu_sheet = generate_sheet(grid, cpu_grid_id)

        grid_dict_cpu = ({f'{x} {y}': 'empty'
                         for y in range(1, grid + 1)
                         for x in range(1, grid + 1)})
        cpu_ships = select_cpu_ships(grid, player_ships)

        start_game(grid, player_ships, cpu_ships, player_grid_id, cpu_grid_id)

        while True:
            continue_game = input('Would you like to play again? ' +
                                  '(enter Y or N):\n').upper()

            if continue_game == 'Y':
                SHEET.del_worksheet(player_sheet)
                SHEET.del_worksheet(cpu_sheet)
                print('')
                break
            elif continue_game == 'N':
                SHEET.del_worksheet(player_sheet)
                SHEET.del_worksheet(cpu_sheet)
                print('\nThanks for playing!\n')
                break
            else:
                print('Please enter either Y or N.\n')

    exit()


print('\nWelcome to Battleships!')
main()
