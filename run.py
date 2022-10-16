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

def select_player_ships(grid):
    player_ships = {}

    while True:
        print('You will now be asked to place each one of your ships.')
        print('For the first two ships, you must enter two numbers, separated by a space, to serve as coordinates, e.g. 2 10')
        print('For the remaining five ships, you must also enter either H or V, for horizontal or vertical, e.g. 2 10 V')
        print(f'(Keep in mind that you have selected a {grid}x{grid} grid, which means that numbers greater than {grid} will not be accepted)\n')

        player_ships['submarine_1'] = input('Please position your first Submarine (occupies 1 square): ').split(' ')
        player_ships['submarine_2'] = input('Please position your second Submarine (occupies 1 square): ').split(' ')
        player_ships['destroyer_1'] = input('Please position your first Destroyer (occupies 2 squares): ').split(' ')
        player_ships['destroyer_2'] = input('Please position your second Destroyer (occupies 2 squares): ').split(' ')
        player_ships['cruiser'] = input('Please position your Cruiser (occupies 3 squares): ').split(' ')
        player_ships['battleship'] = input('Please position your Battleship (occupies 4 squares): ').split(' ')
        player_ships['aircraft_carrier'] = input('Please position your Aircraft Carrier (occupies 5 squares): ').split(' ')

        if validate_ships(grid, player_ships):
            print(f'\nShips selected.\n')
            break

    return player_ships
    
def validate_ships(grid, player_ships):
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
                if int(x) > grid:
                    raise ValueError(f'\nA coordinate you entered lies outside of the {grid}x{grid} grid.')
        
    except ValueError as e:
        print(f'{e} Please place your ships again.\n')
        return False

    return True    

def place_player_ships(grid, player_ships):
    player_grid = SHEET.worksheet('player')

def main():
    grid = set_grid_size()
    player_ships = select_player_ships(grid)
    place_player_ships(grid, player_ships)

print(f'Welcome to Battleships!\n')
main()