import gspread
from google.oauth2.service_account import Credentials
from time import sleep

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


def set_grid_size():
    while True:
        print('Please select the size of the grid that you would like to play on.')
        print(f'(Enter 10 for 10x10, 12 for 12x12, or 14 for 14x14)\n')

        grid = int(input('Enter your selection here: '))

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


def select_player_ships(grid, grid_dict):
    player_ships = {}

    while True:
        print('You will now be asked to place each one of your ships.')
        print('For the first two ships, you must enter two numbers, separated by a space, to serve as x and y coordinates, e.g. 2 10')
        print('For the remaining five ships, you must also enter either H or V, for horizontal or vertical, e.g. 2 10 V')
        print(f'(Keep in mind that you have selected a {grid}x{grid} grid, which means that numbers greater than {grid} will not be accepted)\n')

        player_ships['first submarine'] = input('Please position your first Submarine (occupies 1 square): ').split(' ')
        player_ships['second submarine'] = input('Please position your second Submarine (occupies 1 square): ').split(' ')
        player_ships['first destroyer'] = input('Please position your first Destroyer (occupies 2 squares): ').upper().split(' ')
        player_ships['second destroyer'] = input('Please position your second Destroyer (occupies 2 squares): ').upper().split(' ')
        player_ships['cruiser'] = input('Please position your Cruiser (occupies 3 squares): ').upper().split(' ')
        player_ships['battleship'] = input('Please position your Battleship (occupies 4 squares): ').upper().split(' ')
        player_ships['aircraft carrier'] = input('Please position your Aircraft Carrier (occupies 5 squares): ').upper().split(' ')

        if validate_ships(grid, grid_dict, player_ships):
            print(f'\nShips selected.\n')
            break

    return player_ships
    

def validate_ships(grid, grid_dict, player_ships):
    coordinates = list(player_ships.values())
    # print(f'coordinates variable: {coordinates}')

    try:
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
                if player_ships[player_ship][2] != 'H' and player_ships[player_ship][2] != 'V':
                    raise ValueError(f'\nYou did not provide a valid horizontal or vertical value (H or V) for the {player_ship} that you placed.')
                elif len(player_ships[player_ship]) <= 2:
                    raise IndexError(f'\nYou did not provide a horizontal or vertical value (H or V) for {player_ship} that you placed.')

        for x, player_ship in enumerate(player_ships, start=0):
            if x >= 2:
                if int(player_ships[player_ship][0]) + SHIP_SIZES[x] - 1 > grid and player_ships[player_ship][2] == 'H' or int(player_ships[player_ship][1]) + SHIP_SIZES[x] - 1 > grid and player_ships[player_ship][2] == 'V':
                    raise ValueError(f'\nThe {player_ship} that you placed is partially outside of the {grid}x{grid} grid.')

        for grid_coordinates in grid_dict:  # Each iteration passes a key name from grid_dict to grid_coordinates. Each key name is a string, e.g. '1 1'
            
            coordinates_comp = grid_coordinates.split(' ')  # creates list from current key name, e.g. ['1', '1'] (removes white space)  

            for x, coordinate in enumerate(coordinates, start=0):  # coordinates is a list of lists, so coordinate will be passed a list on each iteration.
                if len(coordinate) == 3:  # if coordinate contains a H or V it will be a list of length 3.
                    if coordinates_comp == coordinate[0:2] and grid_dict[grid_coordinates] != 'occupied':  # compares key from grid_dict with slice of length 3 list, i.e. the slice omits the H or V.
                        grid_dict[grid_coordinates] = 'occupied'  # sets the current key of grid_dict to 'occupied' from None.
                        
                        if coordinate[2] == 'H':  # If the third index of coordinate contains 'H'. 
                            for y in range(0, SHIP_SIZES[x] - 1):
                                coordinates_comp[0] = int(coordinates_comp[0]) + 1
                                coordinates_comp[0] = str(coordinates_comp[0])
                                coord_str = str(coordinates_comp[0] + ' ' + coordinates_comp[1])  # creates a string that is identical to a key in grid_dict. str cast necessary?
                                if grid_dict[coord_str] != 'occupied':
                                    grid_dict[coord_str] = 'occupied'  # uses created string in coord_str to access a key of grid_dict, and then change its value.
                                else:
                                    raise ValueError(f'\nA ship you placed overlapped with another.')         
                        elif coordinate[2] == 'V':  # If the third index of coordinate contains 'V'.
                            for y in range(0, SHIP_SIZES[x] - 1):
                                coordinates_comp[1] = int(coordinates_comp[1]) + 1
                                coordinates_comp[1] = str(coordinates_comp[1])
                                coord_str = str(coordinates_comp[0] + ' ' + coordinates_comp[1])  # creates a string that is identical to a key in grid_dict.
                                if grid_dict[coord_str] != 'occupied':
                                    grid_dict[coord_str] = 'occupied'  # uses created string in coord_str to access a key of grid_dict, and then change its value.
                                else:
                                    raise ValueError(f'\nA ship you placed overlapped with another.')                           
                elif coordinates_comp == coordinate and grid_dict[grid_coordinates] != 'occupied':  # runs if coordinate does not have a length of 3, which means it should have a length of 2 after previous validation.
                        grid_dict[grid_coordinates] = 'occupied'  # sets the current key of grid_dict to 'occupied' from None. Only one coordinate necessary, because this ship has to be a submarine.
                else:
                    continue
    except (ValueError, IndexError) as e:
        print(f'{e} Please place your ships again.\n')
        print(grid_dict)
        grid_dict = {f'{x} {y}': None for x in range(1, grid + 1) for y in range(1, grid + 1)}
        return False

    return True    


def place_player_ships(grid, player_ships, grid_dict):
    player_grid = SHEET.worksheet('player')

    occupied_squares = list(grid_dict.values())

    for x, player_ship in enumerate(player_ships, start=0):  # 7 loops - 1 for each ship.

        for ind, y in enumerate(range(1, grid + 1), start=0):  # As many loops as there are squares in a single row or column of the grid, i.e. 10, 12, or 14. ind = 0-9 / 0-11 / 0-13, and y = 1-10 / 1-12 / 1-14.
            row_list = []

            for z in range(grid):  # 0-9, 0-11, or 0-13
                
                if z > grid - 1:  # only iterates 10/12/14 times because of this break statement. 10/12/14 of these loops for every 1 loop of the 'ind, y' loop
                    break

                if ind == 0:
                    if occupied_squares[z] == 'occupied':  # checks first ten keys of grid_dict to see if any of them are set to 
                        row_list.append(SHIP_INITIALS[x])
                    else:
                        row_list.append('')
                elif y >= 10:
                    combined_str = str(y) + str(z)
                    if occupied_squares[int(combined_str)] == 'occupied':
                        row_list.append(SHIP_INITIALS[x])
                    else:
                        row_list.append('')
                elif ind > 0:
                    combined_str = str(ind) + str(z)
                    if occupied_squares[int(combined_str)] == 'occupied':
                        row_list.append(SHIP_INITIALS[x])
                    else:
                        row_list.append('')
                
            player_grid.append_row(row_list)

        print(f'Adding your {player_ship} to the grid...')
        sleep(3)

    print('Spreadsheet populated with player ships.')
    

def main():
    grid = set_grid_size()
    grid_dict = {f'{x} {y}': None for x in range(1, grid + 1) for y in range(1, grid + 1)}
    player_ships = select_player_ships(grid, grid_dict) 
    print(grid_dict)
    place_player_ships(grid, player_ships, grid_dict)


print(f'Welcome to Battleships!\n')
main()