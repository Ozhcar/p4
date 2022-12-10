from colorama import Back, Fore, Style
from typing import List


import re


class FullColumnError(Exception):
    pass


class UnwinnableGameError(Exception):
    pass


class Player:
    def __init__(self, nickname: str):
        self.nickname = nickname
        self.games = 0
        self.wins = 0

    def __repr__(self):
        return f'Player {self.nickname}'


class Grid:
    def __init__(self, lines: int = 6, columns: int = 7):
        self.lines = lines
        self.columns = columns
        self.grid = []
        self.winning_tiles = []
        # self.default_filler = ' '
        self.default_filler = f'{Fore.BLACK}⬤{Style.RESET_ALL}'
        # self.a = '⬤⬤⬤⬤⬤⬤⬤⬤'  # 5 almost, 8 perfect
        # self.b = '-----------'  # 11 normal chars for 8 circles

    def __repr__(self):
        def get_aligned_columns_numbers(force: str = '0') -> str:
            if force == '0':
                return ' '.join((' ' if (i % 5) % 2 == 1 and (i % 5) % 3 != 0 or (i % 5) % 4 == 0 and (i % 5) >= 4 else
                                 '') + (str(i + 1)[-1]) for i in range(self.columns)) + '\n'
            else:
                return ' '.join((' ' if ((i + 4) % 5) % 2 == 1 and ((i + 4) % 5) % 3 != 0 or ((i + 4) % 5) % 4 == 0
                                 and ((i + 4) % 5) >= 4 else '') +
                                force for i in range(min(self.columns - int(force + '0') + 1, 10)))

        line_count = 0
        # text = ' ' * 22 + (get_aligned_columns_numbers('1') + ' ' + get_aligned_columns_numbers('2') + '\n') if \
        #     self.columns > 9 else ''
        text = ' ' * 22 + get_aligned_columns_numbers('1') + '\n' if self.columns > 9 else ''
        text += ' ' + get_aligned_columns_numbers()
        # Rewrite how the numbers text should display when using regular characters

        for line in self.grid:
            line_count += 1
            text += f'|{"|".join(line)}|' + ('\n' if line_count < self.lines else '')

        return text

    def create_grid(self):
        if not self.grid:
            # self.grid = [[' '] * self.columns] * self.lines  # Deep copies the columns, not what we want
            for i in range(self.lines):
                self.grid.extend([[self.default_filler] * self.columns])

    def display_grid(self) -> list:
        return self.grid

    def check_column_validity(self, column: int) -> bool:
        return self.grid[0][column] == self.default_filler

    def check_winner(self, align_count: int, player_symbol: str, skip_diags: bool) -> bool:
        # Columns check
        for i in range(self.columns):
            count = 0
            self.winning_tiles = []

            for j in range(self.lines - 1, -1, -1):  # self.grid[::-1]:
                if player_symbol == self.grid[j][i]:
                    count += 1
                    self.winning_tiles.append({'line': j, 'column': i})

                    if count == align_count:
                        return True
                else:
                    count = 0
                    self.winning_tiles = []

        # Lines check
        for j in range(self.lines - 1, -1, -1):
            count = 0
            self.winning_tiles = []

            for i in range(self.columns):
                if player_symbol == self.grid[j][i]:
                    count += 1
                    self.winning_tiles.append({'line': j, 'column': i})

                    if count == align_count:
                        return True
                else:
                    count = 0
                    self.winning_tiles = []

        if skip_diags:
            return False

        # Left diagonals check
        for i in range(align_count - self.lines, self.columns - align_count + 1):
            count = 0
            self.winning_tiles = []

            for j in range(self.lines):
                try:
                    if player_symbol == self.grid[j][j + i]:
                        count += 1
                        self.winning_tiles.append({'line': j, 'column': j + i})

                        if count == align_count:
                            return True
                    else:
                        count = 0
                        self.winning_tiles = []
                except IndexError:
                    pass

        # Right diagonals check
        for i in range(self.columns + self.lines - align_count - 1, align_count - 2, -1):
            count = 0
            self.winning_tiles = []

            for j in range(self.lines):
                try:
                    if player_symbol == self.grid[j][i - j]:
                        count += 1
                        self.winning_tiles.append({'line': j, 'column': i - j})

                        if count == align_count:
                            return True
                    else:
                        count = 0
                        self.winning_tiles = []
                except IndexError:
                    pass

        return False

    def set_token(self, player_symbol: str, column: int):
        for line in self.grid[::-1]:
            if line[column] == self.default_filler:
                line[column] = player_symbol
                break

    def set_winning_tiles_background(self):
        for winning_tile in self.winning_tiles:
            tile_content = self.grid[winning_tile['line']][winning_tile['column']]
            self.grid[winning_tile['line']][winning_tile['column']] = Back.GREEN + tile_content


class AlignGame:
    def __init__(self, grid: Grid, players: List[Player], align_count: int = 4, skip_diags: bool = False):
        self.grid = grid
        self.game_name = '4 in a Row'
        self.players = players
        self.align_count = align_count
        self.skip_diags = skip_diags
        self.turns = 0
        self.winner = None
        # self.token_colors = '🔴🟡🟠🔵🟢🟣🟤-⬤'

    def __repr__(self):
        return '\n'.join([f'Player {self.players.index(player) + 1} : {player.nickname}' for player in self.players])

    def get_current_player_data(self) -> dict:
        return {'number': (symbol := (self.turns - 1) % 2),
                'symbol': f'\033[91m⬤{Style.RESET_ALL}' if symbol == 0 else f'\033[93m⬤{Style.RESET_ALL}'}

    def play_game(self):
        self.grid.create_grid()

        while not self.winner and self.turns < self.grid.lines * self.grid.columns:
            self.turns += 1
            player_data = self.get_current_player_data()
            true_player_input = ''

            print(f'\n----- TURN {self.turns} : {self.players[player_data["number"]]} ({player_data["symbol"]}) -----')
            print(self.grid)

            while True:
                try:
                    # Undo and restart functionalities
                    true_player_input = input('Which column you wanna play in ? ')
                    player_input = int(true_player_input) - 1

                    if not self.grid.check_column_validity(player_input):
                        raise FullColumnError

                    break
                except ValueError:
                    print(f'"{true_player_input}" is not a valid column to play in, try again')
                except IndexError:
                    print(f'Column {true_player_input} is unexistant, choose a valid one')
                except FullColumnError:
                    print(f'Column {true_player_input} is full, choose another one')

            self.grid.set_token(player_data['symbol'], player_input)

            if self.turns >= 2 * self.align_count - 1 and \
                    self.grid.check_winner(self.align_count, player_data['symbol'], self.skip_diags):
                self.grid.set_winning_tiles_background()
                self.winner = self.players[player_data['number']]

        if self.winner:
            print(f'\n----- WINNER : {self.winner.nickname} -----')
            print(self.grid)

            if self.winner.nickname == 'Ozhcar':
                print('GG EZ')
            else:
                print('bro ur so lucky')
        else:
            print(f'\n----- TIE -----')
            print(self.grid)
            print('One of you two is MAD lucky')

        print()


def plural_adjuster(count: int, singular: str = '', plural: str = 's') -> str:
    return plural if count >= 2 else singular


def player_login(count: int = 2) -> List[Player]:
    players = []

    for i in range(count):
        while True:
            choice = input('Register or Login (r/l) ? ')

            if choice.lower() in ['register', 'reg', 'r']:
                nick = input(f'Player {i + 1} nickname ? ')
                players.append(Player(nick))

                break
            elif choice.lower() in ['login', 'log', 'l']:
                print('Soon')
            else:
                print('The action could not be recognized, try again')

    return players


def game_setup() -> dict:
    while True:
        lines = input('Number of lines and columns of the grid ? ')

        match = re.compile(r'(\d+).+?(\d+)').search(lines)

        if match:
            grid_lines = int(match.groups()[0])
            grid_columns = int(match.groups()[1])
            break
        else:
            match = re.compile(r'(\d+)').search(lines)

            if match:
                if len(match.group()) == 1:
                    grid_lines = int(match.group())
                    grid_columns = int(match.group())
                else:
                    grid_lines = int(match.group()[:len(match.group()) // 2])
                    grid_columns = int(match.group()[len(match.group()) // 2:])

                break
            else:
                print('You must pass at least two integers to create a grid, try again')

    while True:
        skip_diags = False
        align_count = 0
        true_lines = ''

        try:
            true_lines = input('Number of tokens to align on the grid ? ')
            align_count = int(true_lines)

            if align_count <= 0:
                raise ValueError
            if align_count > grid_columns and align_count > grid_lines:
                raise UnwinnableGameError
            elif align_count > grid_columns or align_count > grid_lines:
                while True:
                    choice = input(f'You won\'t be able to align {align_count} token{plural_adjuster(align_count)} '
                                   f'in the diagonals, do you still want to proceed (y/n) ? ')

                    if choice.lower() in ['yes', 'y']:
                        skip_diags = True

                        break
                    elif choice.lower() in ['no', 'n']:
                        break
                    else:
                        print('The action could not be recognized, try again')
            else:
                break

            if skip_diags:
                break
        except ValueError:
            print(f'You must pass a strictly positive integer which "{true_lines}" is not, try again')
        except UnwinnableGameError:
            print(f'The number of tokens to align ({align_count}) exceeds the number of lines ({grid_lines}) '
                  f'and columns ({grid_columns}) of the game grid, try again')

    return {'lines': grid_lines, 'columns': grid_columns, 'align_count': align_count, 'skip_diags': skip_diags}


def setup_menu() -> dict:
    while True:
        choice = input('New Game or Resume Game (n/r) ? ')

        if choice.lower() in ['new', 'n']:
            return game_setup()
        elif choice.lower() in ['resume', 'res', 'r']:
            print('Soon')
        else:
            print('The action could not be recognized, try again')


def main(align_game=None, players=None, data=None):
    while True:
        if not align_game:
            players = player_login()

        # if data ask if they wanna reshape the game
        if not data:
            data = setup_menu()  # Back functionnality

        print(data['skip_diags'])

        align_game = AlignGame(Grid(data['lines'], data['columns']), players, data['align_count'], data['skip_diags'])
        align_game.play_game()

        while True:
            choice = input('Do you want to play again (y/n) ? ')

            if choice.lower() in ['yes', 'y']:
                break
            elif choice.lower() in ['no', 'n']:
                return
            else:
                print('The action could not be recognized, try again')


main()


# 1 - Choosable token color https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
# 2 - Choosable default filler token color (like Fore.BLACK or Fore.WHITE)
# 3 - Restart the game option
# 4 - Undo turn if both players agree
# 5 - Maybe save game option (resumable later)
# 6 - Create, save and login to profiles
# 7 - Update stats in json file
# 8 - Use pygame for a better rendering
# 9 - Optimize winner check : if on the kind of check you check there is still enough space for a potential alignment
