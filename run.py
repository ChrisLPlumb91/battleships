import gspread
from google.oauth2.service_account import Credentials
import random

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


def set_grid_size():
    """
    Prompts the user to enter one of three 2-digit integers, and validates this input.
    This input is cast to an int, and the try / except catches any input that cannot
    be cast in this way.

    If the user enters 0, the exit_game() function is called.

    Because any number can be entered, a function that further validates the input
    to ensure that it is one of the three options is called. If it returns false,
    the user is prompted again. If it returns True, the number representing the
    grid is returned by this function.
    """    
    while True:
        grid = 0
        while grid == 0:
            print(f'\nPlease select the size of the grid that you would like to play on.')
            print(f'(Enter 10 for 10x10, 12 for 12x12, 14 for 14x14, or 0 to exit the game)\n')

            try:
                grid = int(input(f'Enter your selection here:\n'))
            except ValueError:
                print(f'Please enter either 10, 12, or 14 (or 0 if you wish to quit).\n')
                continue

            if grid == 0:
                exit_game()

        if validate_grid(grid):
            print(f'{grid}x{grid} grid selected.\n')
            break

    return grid


def exit_game():
    """
    If the user enters 0 during the grid size function, they are taken to this
    function. If they enter N, the game will return to the grid selection function.

    The while loop here ensures that the game can only proceed (exit or continue),
    if the user enters the correct value.
    """
    choice = input(f'Do you really want to quit the game? (enter Y or N)\n').upper()

    while True:
        if choice == 'N':
            return True
        elif choice == 'Y':
            print(f'\nThanks for playing!\n')
            exit()
        else:
            print('Please enter either Y or N.')
            continue


def validate_grid(grid):
    """
    This is the function that further validates the user's input for their choice of grid.
    If their choice is not one of the three, a ValueError is raised and caught. They are then
    carried back to the grid selection function.
    """
    try:
        if grid != 10 and grid != 12 and grid != 14:
            raise ValueError(f'{grid} is not a valid option.')
    except ValueError as e:
        print(f'{e} Please try again.\n')
        return False
    
    return True


def select_player_ships(grid, grid_dict_player):
    """
    This function prompts the user to enter coordinates for each of their ships.
    Each request for input is wrapped in a while loop and is followed by a call
    to a validating function, and the input itself becomes the value of a key
    in a dictionary. Each key bears the name of a ship.

    After each ship is successfully validated individually, a function is called
    that ensures that none of the ships' coordinates are identical or overlapping.

    This function ultimately returns the dictionary of ships and their coordinates.
    """
    player_ships = {}

    while True:
        print(f'\nYou will now be asked to place each one of your ships.\n\n')
        print('For the first two ships, you must enter two numbers, separated by a space, to serve as x and y coordinates, e.g. 2 10')
        print('For the remaining five ships, you must also enter either H or V, for horizontal or vertical, e.g. 2 10 V')
        print(f'(Keep in mind that you have selected a {grid}1 x{grid} grid, which means that numbers greater than {grid} will not be accepted)\n')

        while True:
            x = 2
            player_ships['first Submarine'] = input(f'Please position your first Submarine (occupies 1 square):\n').split(' ')
            
            if validate_ship(grid, x, player_ships['first Submarine'], 'first Submarine'):
                break
        
        while True:
            x = 2
            player_ships['second Submarine'] = input(f'Please position your second Submarine (occupies 1 square):\n').split(' ')

            if validate_ship(grid, x, player_ships['second Submarine'], 'second Submarine'):
                break

        while True:
            x = 3
            player_ships['first Destroyer'] = input(f'Please position your first Destroyer (occupies 2 squares):\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['first Destroyer'], 'first Destroyer'):
                break

        while True:
            x = 3
            player_ships['second Destroyer'] = input(f'Please position your second Destroyer (occupies 2 squares):\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['second Destroyer'], 'second Destroyer'):
                break

        while True:
            x = 3
            player_ships['Cruiser'] = input(f'Please position your Cruiser (occupies 3 squares):\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['Cruiser'], 'Cruiser'):
                break
        
        while True:
            x = 3
            player_ships['Battleship'] = input(f'Please position your Battleship (occupies 4 squares):\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['Battleship'], 'Battleship'):
                break
        
        while True:
            x = 3
            player_ships['Aircraft Carrier'] = input(f'Please position your Aircraft Carrier (occupies 5 squares):\n').upper().split(' ')

            if validate_ship(grid, x, player_ships['Aircraft Carrier'], 'Aircraft Carrier'):
                break

        if validate_player_ships(grid, grid_dict_player, player_ships):
            print(f'\nPositioning your ships. Please wait...')
            break

    return player_ships
    

def validate_ship(grid, sub_or_ship, coordinate_list, ship_name):
    """
    This is the function that is called for each pair of coordinates that the user enters.
    It checks to makes sure that the user has not: entered a single number, entered more
    numbers than required, entered fewer numbers than required, neglected to provide a H
    or V value for the orientation of the ships that take up 2 squares or more,
    or entered a letter where a number was expected.

    If an exception is raised, the user will be taken back to the ship select function
    and asked to enter proper coordinates for the ship that caused the error.
    """
    try:
        coordinate_dict = dict(enumerate(coordinate_list))
        if not coordinate_dict.get(1):
            raise ValueError(f'\nEither you entered only a single character, or you did not put a space between the characters.')

        if sub_or_ship == 2 and len(coordinate_list) > 2:
            raise ValueError(f'\nYou entered {len(coordinate_list)} numbers / characters where only 2 were required.')
        elif sub_or_ship == 3 and len(coordinate_list) > 3:
            raise ValueError(f'\nYou entered {len(coordinate_list)} numbers / characters where only 3 were required.')

        if sub_or_ship == 3 and len(coordinate_list) < 3:
            raise ValueError(f'\nYou entered {len(coordinate_list)} numbers / characters where 3 were required.')

        if sub_or_ship == 3 and coordinate_list[2] != 'H' and coordinate_list[2] != 'V':
            raise ValueError(f'\nYou did not provide a valid horizontal or vertical value (H or V) for the {ship_name} that you placed.')

        if not coordinate_list[0].isnumeric() or not coordinate_list[1].isnumeric():
            raise ValueError(f'\nYou entered a letter where a number was expected.')

        if int(coordinate_list[0]) <= 0 or int(coordinate_list[1]) <= 0:
            raise ValueError(f"\nYou entered a coordinate that doesn't exist on the grid.")

        for y in coordinate_list:    
            if y.isalpha():
                continue
            if int(y) > grid:
                raise ValueError(f'\nThese coordinates would place this ship outside of the {grid}x{grid} grid.')

    except ValueError as e:
        print(f'{e} Try again.\n')
        return False

    return True


def validate_player_ships(grid, grid_dict_player, player_ships):
    """
    This is the function that checks to make sure that the coordinates of each of the ships
    do not clash with one another. It also checks to make sure that a given ship does not 
    extend beyond the boundaries of the grid, e.g placing an Aircraft Carrier horizontally 
    at 10, 1 on a 10x10 grid.

    Another important thing that it does is "occupy" keys in a dictionary. Each key is
    a coordinate (from 1, 1 to 10, 10, in the case of a 10x10 grid), and this function
    assigns values to the coordinates that are occupied by ships. It figures this out
    by referring to each ship's length, as well as its starting coordinate (i.e. the coordinate
    provided by the user).
    """
    coordinates = list(player_ships.values())
        
    try:
        for x, coordinate in enumerate(coordinates, start=0):
            for y, coordinate_comp in enumerate(coordinates, start=0):
                if x == y:
                    continue
                elif coordinate == coordinate_comp:
                    raise ValueError(f'\nYou chose identical coordinates for two different ships.') 

        for x, player_ship in enumerate(player_ships, start=0):
            if x >= 2:
                if int(player_ships[player_ship][0]) + SHIP_SIZES[x] - 1 > grid and player_ships[player_ship][2] == 'H' or int(player_ships[player_ship][1]) + SHIP_SIZES[x] - 1 > grid and player_ships[player_ship][2] == 'V':
                    raise ValueError(f'\nThe {player_ship} that you placed is partially outside of the {grid}x{grid} grid.')

        for player_ship in player_ships:
            for grid_coordinates in grid_dict_player:
                    
                coordinates_comp = grid_coordinates.split(' ')

                for x, coordinate in enumerate(coordinates, start=0):
                    if len(coordinate) == 3:
                        if coordinates_comp == coordinate[0:2] and 'occupied' not in grid_dict_player[grid_coordinates] and player_ships[player_ship] == coordinate:
                            grid_dict_player[grid_coordinates] = f'occupied by {player_ship}'
                                
                            if coordinate[2] == 'H':
                                for y in range(0, SHIP_SIZES[x] - 1):
                                    coordinates_comp[0] = int(coordinates_comp[0]) + 1
                                    coordinates_comp[0] = str(coordinates_comp[0])
                                    coord_str = str(coordinates_comp[0] + ' ' + coordinates_comp[1])
                                    if 'occupied' not in grid_dict_player[coord_str]:
                                        grid_dict_player[coord_str] = f'occupied by {player_ship}'
                                    else:
                                        raise ValueError(f'\nThe horizontal {player_ship} that you placed overlapped with another ship.')         
                            elif coordinate[2] == 'V':
                                for y in range(0, SHIP_SIZES[x] - 1):
                                    coordinates_comp[1] = int(coordinates_comp[1]) + 1
                                    coordinates_comp[1] = str(coordinates_comp[1])
                                    coord_str = str(coordinates_comp[0] + ' ' + coordinates_comp[1])
                                    if 'occupied' not in grid_dict_player[coord_str]:
                                        grid_dict_player[coord_str] = f'occupied by {player_ship}'
                                    else:
                                        raise ValueError(f'\nThe vertical {player_ship} that you placed overlapped with another ship.')                           
                    elif coordinates_comp == coordinate and player_ships[player_ship] == coordinate and 'occupied' not in grid_dict_player[grid_coordinates]:
                        grid_dict_player[grid_coordinates] = f'occupied by {player_ship}'
                    else:
                        continue
    except (ValueError, IndexError) as e:
        print(f'{e} Please place your ships again.\n')
        grid_dict_player = {f'{x} {y}': 'empty' for x in range(1, grid + 1) for y in range(1, grid + 1)}
        return False

    return True    


def place_player_ships(grid, player_ships, grid_dict_player):
    """
    This function is responsible for actually inserting the user's ships into the spreadsheet.
    Depending on the ship, a different initial is inserted into the correct cells of the
    spreadsheet - the spreadsheet itself representing the grid.

    Throughout its execution, this function creates lists that are either 10, 12, or 14 in length
    (depending on the grid size), and then appends them to the 'player' spreadsheet. Where in each
    row a ship should be, and which ship that ship should be, is determined from the dictionary
    of coordinates and ships created previously.
    """
    player_grid = SHEET.worksheet('player')
    row_values = list(grid_dict_player.values())
    row_list = []
    overflow = 0

    if grid == 12:
        overflow = 3
    elif grid == 14:
        overflow = 6
    
    for x in range(grid + overflow):
        if grid == 10 and len(row_list) == 10 or grid == 12 and len(row_list) == 12 or grid == 14 and len(row_list) == 14:
            row_list = []

        for y in range(grid):          
            if x == 0:
                if row_values[y] == 'occupied by first Submarine' or row_values[y] == 'occupied by second Submarine':
                    row_list.append(SHIP_INITIALS[0])
                elif row_values[y] == 'occupied by first Destroyer' or row_values[y] == 'occupied by second Destroyer':
                    row_list.append(SHIP_INITIALS[2])
                elif row_values[y] == 'occupied by Cruiser':
                    row_list.append(SHIP_INITIALS[4])
                elif row_values[y] == 'occupied by Battleship':
                    row_list.append(SHIP_INITIALS[5])
                elif row_values[y] == 'occupied by Aircraft Carrier':
                    row_list.append(SHIP_INITIALS[6])
                else:
                    row_list.append('')
            elif x > 0:
                str_x = str(x)
                str_y = str(y)
                int_xy = int(str_x + str_y)

                if grid == 12 and int_xy <= 11 or grid == 12 and int_xy > 143:
                    continue
                elif grid == 14 and int_xy <= 13 or grid == 14 and int_xy > 195:
                    continue
                else:
                    if row_values[int_xy] == 'occupied by first Submarine' or row_values[int_xy] == 'occupied by second Submarine':
                        row_list.append(SHIP_INITIALS[0])
                    elif row_values[int_xy] == 'occupied by first Destroyer' or row_values[int_xy] == 'occupied by second Destroyer':
                        row_list.append(SHIP_INITIALS[2])
                    elif row_values[int_xy] == 'occupied by Cruiser':
                        row_list.append(SHIP_INITIALS[4])
                    elif row_values[int_xy] == 'occupied by Battleship':
                        row_list.append(SHIP_INITIALS[5])
                    elif row_values[int_xy] == 'occupied by Aircraft Carrier':
                        row_list.append(SHIP_INITIALS[6])
                    else:
                        row_list.append('')

    
            if x >= 1 and grid == 12 and len(row_list) == 12 and y % 2 != 0 or x >= 1 and grid == 14 and len(row_list) == 14 and y % 2 != 0:
                player_grid.append_row(row_list)
                row_list = []
            
            if grid == 12 and x >= 1 and y == 9 or grid == 14 and x >= 1 and y == 9:
                break

        if grid == 10 and len(row_list) == 10:
            player_grid.append_row(row_list)
        elif grid == 12 and x == 0 or grid == 14 and x == 0:
            player_grid.append_row(row_list)  
    
    print(f'Your spreadsheet has been populated with your ships! Take a look!.\n')


def select_cpu_ships(grid, player_ships):
    """
    This function assigns coordinates to the CPU's ships. It makes use of the random library
    to generate those coordinates. For the ships that take up more than 1 square, either
    H or V is selected randomly to provide their orientation on the grid.

    Then, a function is called on the resulting dictionary to validate its contents.
    If the validation function returns True, this function returns a dictionary of
    the CPU's ships and their starting coordinates.
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
                random_coordinate_1 = random.randrange(grid)
                random_coordinate_2 = random.randrange(grid)

            if x <= 1:
                sub_coordinates_string.append(str(random_coordinate_1)) 
                sub_coordinates_string.append(str(random_coordinate_2))
                sub_coordinates_string.append('')
                cpu_ships[cpu_ship] = sub_coordinates_string           
            else:
                other_coordinates_string.append(str(random_coordinate_1)) 
                other_coordinates_string.append(str(random_coordinate_2))
                other_coordinates_string.append(random.choice(['H', 'V']))
                cpu_ships[cpu_ship] = other_coordinates_string

        if validate_cpu_ships(grid, cpu_ships):
            print(f"You sense that the CPU's ships have taken up position behind the colossal wall before you...\n")
            break

    return cpu_ships
    

def validate_cpu_ships(grid, cpu_ships):
    """
    This is the function that validates the coordinates randomly generated for the CPU's ships.
    It does not use exception handling, as the CPU ship selection process is more controlled than
    the user's, i.e. the CPU can only "input" from a very small pool of possible values.

    Like with the function that validates all of the user's ships together, this function
    generates a dictionary of coordinates, and "occupies" the relevant coordinates with values.

    Over the course of this function, several flags are set if conflicts are detected, and the validation
    can only be successful if all of these flags are False by the end. If they are True,
    a different set of coordinates are randomly generated for the CPU.
    """
        
    global grid_dict_cpu
    cpu_ships_coordinates = list(cpu_ships.values())

    while True:
        same_square = False

        for y, cpu_ship_coordinates in enumerate(cpu_ships_coordinates, start=0):
            for z in range(7):
                if z != y:
                    if cpu_ship_coordinates[0:2] == cpu_ships_coordinates[z][0:2]:
                        same_square = True
                    else:
                        continue
                else:
                    continue
        
        grid_dict_cpu = {f'{x} {y}': 'empty' for y in range(1, grid + 1) for x in range(1, grid + 1)}
        grid_keys = list(grid_dict_cpu.keys())
        keys_dict = dict(enumerate(grid_keys))

        overlap = False
        out_of_bounds = False

        for x, cpu_ship in enumerate(cpu_ships, start=0):
            for ind, coordinates in enumerate(grid_dict_cpu, start=0):
                if coordinates.split(' ') == cpu_ships[cpu_ship][0:2] and cpu_ships[cpu_ship][2] == 'H':
                    if 'occupied' not in grid_dict_cpu[coordinates]:
                        grid_dict_cpu[coordinates] = f'occupied by {cpu_ship}'
                    else:
                        overlap = True
                    for z in range(1, SHIP_SIZES[x]):
                        if grid_keys[ind + z].split(' ')[1] == coordinates.split(' ')[1]:
                            if 'occupied' not in grid_dict_cpu[grid_keys[ind + z]]:
                                grid_dict_cpu[grid_keys[ind + z]] = f'occupied by {cpu_ship}'
                            else:
                                overlap = True
                        else:
                            out_of_bounds = True
                elif coordinates.split(' ') == cpu_ships[cpu_ship][0:2] and cpu_ships[cpu_ship][2] == 'V':
                    if 'occupied' not in grid_dict_cpu[coordinates]:
                        grid_dict_cpu[coordinates] = f'occupied by {cpu_ship}'
                    else:
                        overlap = True
                    for z in range(1, SHIP_SIZES[x]):
                        if keys_dict.get(ind + grid * z):
                            if 'occupied' not in grid_dict_cpu[grid_keys[ind + grid * z]]:
                                grid_dict_cpu[grid_keys[ind + grid * z]] = f'occupied by {cpu_ship}'
                            else:
                                overlap = True
                        else:
                            out_of_bounds = True
                elif coordinates.split(' ') == cpu_ships[cpu_ship][0:2]:
                    if 'occupied' not in grid_dict_cpu[coordinates]:
                        grid_dict_cpu[coordinates] = f'occupied by {cpu_ship}'
                    else:
                        overlap = True

        if same_square == False and overlap == False and out_of_bounds == False:
            break
        else:
            return False
    return True


def start_game(grid, player_ships, cpu_ships, grid_dict_player):
    """
    This function contains code for the playable part of the program. It prompts the user
    to input numbers as coordinates, just like when they had to position their ships.
    These coordinates are checked against the CPU's dictionary of coordinates,
    and if occupied coordinates are found, the number of hits against the CPU
    ticks up, and the initial of ship that was hit is inserted in the 'cpu' spreadsheet,
    at the coordinates where that ship was found.

    The CPU does the same, but its guess is randomly generated, and if it lands a hit,
    the respective initial on the 'player' spreadsheet becomes an 'X'. Also, a
    validation function is not called to validate the CPU guess.

    When a ship is sunk, the user is notified (whether it belongs to them or to the CPU).
    There is a dictionary containing lists of Os that serve as the hit points for each ship.
    When a ship is hit, an O is popped off the relevant list, and when the list's length
    becomes zero, the ship is sunk.

    As there are 18 possible targets for both the user and the CPU, once one of the hit counters
    ticks up to 18, a winner is declared, and both spreadsheets are cleared of their contents.
    """
    print(f'\nMan the poop deck! War has returned to the high seas!\n')

    player_grid = SHEET.worksheet('player')
    cpu_grid = SHEET.worksheet('cpu')
    global grid_dict_cpu

    hit_dict_player = {}
    hit_dict_cpu = {}
    
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
            print(f'Try to guess where your opponent has placed their ships! (any hits will appear on the CPU spreadsheet!)')
            player_guess = input(f'Enter two numbers separated by a space and then press enter (neither number should be greater than {grid}):\n').split(' ')

            if validate_guess(player_guess, grid):
                break
        
        player_guess_str = player_guess[0] + ' ' + player_guess[1]
        
        if 'occupied' in grid_dict_cpu[player_guess_str]:
            hit_ship_str = grid_dict_cpu[player_guess_str][12:len(grid_dict_cpu[player_guess_str]) + 1]
            
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

            cpu_grid.update_cell(player_guess[1], player_guess[0], ship_initial)          

            grid_dict_cpu[player_guess_str] = 'Hit!'
            cpu_hits += 1
        elif grid_dict_cpu[player_guess_str] == 'Hit!':
            print(f'Nothing but wreckage, there!\n')
        else:
            print(f'\nMiss!\n')

        if cpu_hits >= 18:
            break
        
        print(f"CPU's turn!\n")
        
        random_coordinate_1 = 0
        random_coordinate_2 = 0

        while True:
            while random_coordinate_1 == 0 or random_coordinate_2 == 0:
                random_coordinate_1 = random.randrange(grid + 1)
                random_coordinate_2 = random.randrange(grid + 1)
            
            cpu_guess_str = str(random_coordinate_1) + ' ' + str( random_coordinate_2)
            cpu_guess_list = [random_coordinate_1, random_coordinate_2]

            if 'occupied' in grid_dict_player[cpu_guess_str]:
                hit_ship_str = grid_dict_player[cpu_guess_str][12:len(grid_dict_player[cpu_guess_str]) + 1]

                if len(hit_dict_player[hit_ship_str]) >= 2:
                    hit_dict_player[hit_ship_str].pop()
                    print(f'The CPU guessed {cpu_guess_str} and hit your {hit_ship_str}!\n')
                elif len(hit_dict_player[hit_ship_str]) == 1:
                    hit_dict_player[hit_ship_str].pop()
                    print(f'The CPU guessed {cpu_guess_str} and sunk your {hit_ship_str}!\n')
                    
                grid_dict_player[cpu_guess_str] = 'Hit!'
                player_hits += 1

                player_grid.update_cell(random_coordinate_2, random_coordinate_1, 'X')
                break              
            elif grid_dict_player[cpu_guess_str] == 'Hit!':
                print(f'The CPU guessed {cpu_guess_str} and blasted the wreckage of one of your ships!\n')
                break
            else:
                print(f'The CPU guessed {cpu_guess_str}, but missed!\n')
                break
    
    if cpu_hits >= 18:
        print(f'YOU ARE VICTORIOUS!\n')
        if player_hits == 0:
            print(f'FLAWLESS VICTORY!!\n')
        elif player_hits > 0:
            print(f'...however, The CPU landed {player_hits} hits on your fleet...\n')
    elif player_hits >=18:
        print('The CPU has scuppered your entire fleet! You lose!')

    player_grid.clear()
    cpu_grid.clear()
            

def validate_guess(player_guess, grid):
    """
    This function validates each guess the user makes during the playable phase of the program.
    It is similar to the function that validates each coordinate provided by the user at the game's outset,
    but it is subtly different, and so had to be its own function. Specifically, some of the messages in the former 
    one would not make sense in the context of the playable phase. Moreover, letters denoting H and V
    are not requested during said phase.
    """
    player_guess_dict = dict(enumerate(player_guess))
    
    try:
        if not player_guess_dict.get(1):
            raise ValueError('Either you entered only a single character, or you did not put a space between the characters.')
        elif len(player_guess) > 2:
            raise ValueError(f'You entered {len(player_guess)} numbers / characters. Only 2 are required.')
        elif not player_guess[0].isnumeric() or not player_guess[1].isnumeric():
            raise ValueError('The coordinates you provided contained an alphabetic character where a number was expected.')
        elif player_guess[0].isalpha() or player_guess[1].isalpha():
            raise ValueError('The coordinates you provided contained an alphabetic character where a number was expected.')
        elif int(player_guess[0]) > grid or int(player_guess[1]) > grid:
            raise ValueError(f'The coordinates you provided lie outside of the {grid}x{grid} grid.')       
        elif int(player_guess[0]) <= 0 or int(player_guess[1]) <= 0:
            raise ValueError(f'There is no 0 coordinate on the grid.')

        else:
            return True
    except ValueError as e:
        print(f'{e} Please guess again.\n')
        return False


def main():
    """
    This is the main function for the game. Excluding the validation functions, all of the
    major functions of the program are called from inside this one. Return values from functions
    are passed to other functions. Once all of these functions have successfully executed, 
    the user is asked if they would like to play again. If they do, the game restarts 
    from the beginning, and if they do not, execution stops.
    """
    continue_game = 'Y'
    
    while continue_game == 'Y':
        global grid_dict_cpu
    
        grid = set_grid_size()

        grid_dict_player = {f'{x} {y}': 'empty' for y in range(1, grid + 1) for x in range(1, grid + 1)}
        player_ships = select_player_ships(grid, grid_dict_player)
        place_player_ships(grid, player_ships, grid_dict_player)

        grid_dict_cpu = {f'{x} {y}': 'empty' for y in range(1, grid + 1) for x in range(1, grid + 1)}
        cpu_ships = select_cpu_ships(grid, player_ships)

        start_game(grid, player_ships, cpu_ships, grid_dict_player)

        while True:
            continue_game = input(f'Would you like to play again? (enter Y or N):\n').upper()

            if continue_game == 'Y':
                print('')
                break
            elif continue_game == 'N':
                print(f'\nThanks for playing!\n')
                break
            else:
                print(f'Please enter either Y or N.\n')

    exit()


print(f'\nWelcome to Battleships!')
main()