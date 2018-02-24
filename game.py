import itertools
import random
from random import shuffle
from termcolor import colored
import copy

import os
clear = lambda: os.system('cls' if os.name=='nt' else 'clear')

import cards
import interfaces
from playerState import PlayerState


class GameState:
    def __init__(self, players, verbose = True, requested_cards = []):
        self.verbose = verbose
        self.turn_counter = 0
        self.winning_player = ''
        self.all_cards = copy.deepcopy(cards.base_cards)
        self.active_player = ''

        assert(len(requested_cards) <= 10)
        random_cards = []
        if len(requested_cards) < 10:
            random_cards = random.sample(list(cards.optional_cards.keys()), 10 - len(requested_cards)) 
        for card_name in random_cards + requested_cards:
            self.all_cards[card_name] = copy.deepcopy(cards.optional_cards[card_name])

        if len(players) <= 2:
            for card_name in ('Estate', 'Duchy', 'Province'):
                self.all_cards[card_name].count = 8

        shuffle(players)
        draw_stack = ['Copper'] * 7 + ['Estate'] * 3

        self.player_states = {}
        for player in players:
            player_name, Interface = player
            shuffle(draw_stack)
            h = Interface(player_name, self)
            self.player_states[player_name] = PlayerState(self, [], draw_stack[:], [], player_name, h)
            h.set_player_state = self.player_states[player_name]
            self.player_states[player_name].draw_cards(5)

    def get_opponents(self, player):
        return [opponent for opponent in self.player_states if opponent != player]
    
    def check_for_end_condition(self):
        if self.all_cards['Province'].count == 0 or len([None for card in self.all_cards.values() if card.count == 3]) == 3:
            self.winning_player = max(self.player_states.items(), key = lambda player: player[1].count_points())
            print('\n-----Player {} won the game!-----'.format(self.winning_player[0]))
            print(', '.join(['{}: {} points'.format(name, player.count_points()) for name, player in self.player_states.items()]))
            return True
        return False



    def coloredCardsString(self, card_names, atribs = None, print_card_count = False):
        string_list = []
        for card_name in card_names:
            text = card_name
            if print_card_count:
                text += ' ({})'.format(self.all_cards[card_name].count)

            card_types = self.all_cards[card_name].types
            if 'Money' in card_types:
                string_list.append(colored(text, 'yellow', attrs = atribs))
            elif 'Point' in card_types:
                string_list.append(colored(text, 'green', attrs = atribs))
            elif 'Attack' in card_types:
                string_list.append(colored(text, 'red', attrs = atribs))
            else:
                string_list.append(colored(text, 'magenta', attrs = atribs))
        return '[{}]'.format(' '.join(string_list))

    def print_all_cards(self):
        base_point_cards = ['Estate', 'Duchy', 'Province']
        base_money_cards = ['Copper', 'Silver', 'Gold']
        optional_cards_in_game = set(self.all_cards.keys()) & set(cards.optional_cards.keys())
        all_cards_sorted = sorted(optional_cards_in_game, key = lambda card: self.all_cards[card].cost)
        print(self.coloredCardsString(base_point_cards + base_money_cards, print_card_count = True))
        print(self.coloredCardsString(all_cards_sorted, print_card_count = True))

    def print_state(self):
        clear()
        print(colored('\t\t-------------Turn {}-------------'.format(self.turn_counter), 'red', attrs = ['bold']))
        print(self.print_all_cards())
        for player in self.player_states.values():
            is_active = player.name == self.active_player 
            print(colored(player.name, 'red' if is_active else 'white'), '\tDraw:', self.coloredCardsString(player.draw_stack), \
            ' Played:', self.coloredCardsString(player.played_stack))
            print('{} actions left. {} gold availible. {} buys availible. {} total points.'.format(player.num_actions, \
                player.num_money, player.num_buys, player.count_points()), self.coloredCardsString(player.hand_cards, ['bold']), \
                self.coloredCardsString(player.active_cards))
            print()


    def do_single_turn(self):
        for player_name, player in self.player_states.items():
            #print("\n---Player {}'s turn---".format(player_name))
            self.active_player = player_name
            player.do_single_turn()
            if self.check_for_end_condition():
                return True
        return False

    def main_loop(self):
        game_over = False
        while not game_over:
            if self.verbose:
                print('\n-----Turn {}-----'.format(self.turn_counter))
                self.print_all_cards()
            game_over = self.do_single_turn()
            self.turn_counter += 1

    def play_multiple_games(self, number_of_games = 500):
        score = {}
        for player_name in self.player_states.keys():
            score[player_name] = 0
        optional_cards_in_game = list(set(self.all_cards.keys()) & set(cards.optional_cards.keys()))
        print(optional_cards_in_game)
        players = [(player.name, type(player.interface)) for player in self.player_states.values()]
        print(players)
        for _ in range(number_of_games):
            self.__init__(players, verbose = True, requested_cards = optional_cards_in_game)
            self.main_loop()
            score[self.winning_player[0]] += 1
        print(score)


#gs = GameState([('Human', interfaces.HumanInterface), ('DumbBot', interfaces.SimpleBot), ('MoneyGrabber', interfaces.MoneyGrabber)], \
#    requested_cards = ['Village', 'Library', 'Chappel'])

gs = GameState([('DumbBot', interfaces.SimpleBot), ('MoneyGrabber', interfaces.MoneyGrabber)], \
    requested_cards = [], verbose = False)
gs.play_multiple_games(1000)