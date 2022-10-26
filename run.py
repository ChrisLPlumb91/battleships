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
    while True:
        print('Please select the size of the grid that you would like to play on.')
        print(f'(Enter 10 for 10x10, 12 for 12x12, or 14 for 14x14)\n')

        try:
            grid = int(input('Enter your selection here: '))
        except ValueError:
            print(f'Please enter either 10, 12, or 14.\n')
            continue

        if validate_grid(grid):
            print(f'{grid}x{grid} grid selected.\n')
            break

    return grid


def validate_grid(grid):
    try:
        if grid != 10 and grid != 12 and grid != 14:
            raise ValueError(f'{grid} is not a valid option.')
    except ValueError as e:
        print(f'{e} Please try again.\n')
        return False
    
    return True


def select_player_ships(grid, grid_dict_player):
    player_ships = {}

    while True:
        print(f'\nYou will now be asked to place each one of your ships.\n')
        print('For the first two ships, you must enter two numbers, separated by a space, to serve as x and y coordinates, e.g. 2 10')
        print('For the remaining five ships, you must also enter either H or V, for horizontal or vertical, e.g. 2 10 V')
        print(f'(Keep in mind that you have selected a {grid}x{grid} grid, which means that numbers greater than {grid} will not be accepted)\n')

        player_ships['first Submarine'] = input(f'Please position your first Submarine (occupies 1 square):\n').split(' ')
        player_ships['second Submarine'] = input(f'Please position your second Submarine (occupies 1 square):\n').split(' ')
        player_ships['first Destroyer'] = input(f'Please position your first Destroyer (occupies 2 squares):\n').upper().split(' ')
        player_ships['second Destroyer'] = input(f'Please position your second Destroyer (occupies 2 squares):\n').upper().split(' ')
        player_ships['Cruiser'] = input(f'Please position your Cruiser (occupies 3 squares):\n').upper().split(' ')
        player_ships['Battleship'] = input(f'Please position your Battleship (occupies 4 squares):\n').upper().split(' ')
        player_ships['Aircraft Carrier'] = input(f'Please position your Aircraft Carrier (occupies 5 squares):\n').upper().split(' ')

        if validate_player_ships(grid, grid_dict_player, player_ships):
            print(f'\nPositioning your ships. Please wait...')
            break

    return player_ships
    

def validate_player_ships(grid, grid_dict_player, player_ships):
    coordinates = list(player_ships.values())

    try:
        for coordinate in coordinates:
            coordinate_dict = dict(enumerate(coordinate))
            if not coordinate_dict.get(1):
                raise ValueError(f'\nEither you entered only a single character, or you did not put a space between the characters ({coordinate}).')
            else:
                continue
    
        for x, coordinate in enumerate(coordinates, start=0):
            if x <= 1 and len(coordinate) > 2:
                raise ValueError(f'\nYou entered {len(coordinate)} numbers / characters ({coordinate}) where only 2 were required.')
            elif x > 1 and len(coordinate) > 3:
                raise ValueError(f'\nYou entered {len(coordinate)} numbers / characters ({coordinate}) where only 3 were required.')
            else:
                continue

        for x, player_ship in enumerate(player_ships, start=0):
            if x >= 2:
                if player_ships[player_ship][2] != 'H' and player_ships[player_ship][2] != 'V':
                    raise ValueError(f'\nYou did not provide a valid horizontal or vertical value (H or V) for the {player_ship} that you placed.')
                elif len(player_ships[player_ship]) <= 2:
                    raise IndexError(f'\nYou did not provide a horizontal or vertical value (H or V) for {player_ship} that you placed.')
            else: 
                continue
        
        for x, coordinate in enumerate(coordinates, start=0):
            if x > 1 and len(coordinate) < 3:
                raise ValueError(f'\nYou entered {len(coordinate)} numbers / characters ({coordinate}) where 3 were required.')
            else:
                continue

        for x, coordinate in enumerate(coordinates, start=0):
            if x <= 1 and not coordinate[0].isnumeric() or x <= 1 and not coordinate[1].isnumeric():
                raise ValueError(f'\nYou entered a letter where a number was expected ({coordinate}).')
            else:
                continue
        
        for coordinate in coordinates:
            if coordinate[0].isalpha() or coordinate[1].isalpha():
                raise ValueError(f'\nThe coordinates you provided contained an alphabetic character where a number was expected.')
            else:
                continue
        
        for x, coordinate in enumerate(coordinates, start=0):
            for y, coordinate_comp in enumerate(coordinates, start=0):
                if x == y:
                    continue
                elif coordinate == coordinate_comp:
                    raise ValueError(f'\nYou chose identical coordinates for two different ships.')
        
        for coordinate in coordinates:
            for x in coordinate:    
                if x.isalpha():
                    continue
                if int(x) > grid:
                    raise ValueError(f'\nA coordinate you entered lies outside of the {grid}x{grid} grid.')

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

    print(hit_dict_player)
    print(hit_dict_cpu)

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
            print(f'...but at what cost? The CPU landed {player_hits} on your fleet...\n')
    elif player_hits >=18:
        print('The CPU has scuppered your entire fleet! You lose!')

    player_grid.clear()
    cpu_grid.clear()
            

def validate_guess(player_guess, grid):
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


print(f'\nWelcome to Battleships!\n')
main()