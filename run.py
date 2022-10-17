import gspread
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
        player_ships['aircraft_carrier'] = input('Please position your Aircraft Carrier (occupies 5 squares): ').upper().split(' ')

        if validate_ships(grid, grid_dict, player_ships):
            print(f'\nShips selected.\n')
            break

    return player_ships
    
def validate_ships(grid, grid_dict, player_ships):
    coordinates = list(player_ships.values())

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

        for grid_coordinates in grid_dict:
            coordinates = grid_coordinates.split(' ')
            for player_ship in player_ships:
                
            
    except (ValueError, IndexError) as e:
        print(f'{e} Please place your ships again.\n')
        return False

    return True    

def place_player_ships(grid, player_ships):
    player_grid = SHEET.worksheet('player')

def main():
    grid = set_grid_size()
    grid_dict = {f'{x} {y}': None for x in range(1, grid + 1) for y in range(1, grid + 1)}
    player_ships = select_player_ships(grid, grid_dict)  
    place_player_ships(grid, player_ships)

print(f'Welcome to Battleships!\n')

print(grid_dict)

# for grid_coordinate in grid_dict:
#     print(grid_coordinate) PRINTS 11
#     for x in grid_coordinate:
#         print(x) PRINTS 1
#         break
#     break

main()