import itertools
import random
from random import shuffle

import os
clear = lambda: os.system('cls' if os.name=='nt' else 'clear')

all_cards = {}
player_states = {}
base_cards = {}
optional_cards = {}

exec(open("cards.py").read())
#from cards import base_cards, optional_cards
exec(open("interfaces.py").read())
#from interfaces import HumanInterface 
#from interfaces import SimpleBot 

class PlayerState:
    def __init__(self, hand_cards, draw_stack, played_stack, name, interface):
        self.num_buys = 1
        self.num_money = 0
        self.num_actions = 1

        self.hand_cards = hand_cards
        self.draw_stack = draw_stack
        self.played_stack = played_stack
        self.active_cards = []
        self.name = name
        self.interface = interface

    def perform_decision(self, message, options, allow_none = True):
        #print_state()
        #print('{}, {}'.format(self.name, message))
        if allow_none:
            options.append('None')
        if len(options) == 0:
            return 'None'
        if len(options) == 1:
            choice = options[0]
        else:
            choice = self.interface.decide(message, options, 'DEFAULT')
        return choice
        
    def play_card(self, card_name):
        self.num_actions -= 1
        self.hand_cards.remove(card_name)
        self.active_cards.append(card_name)
        all_cards[card_name].perform_action(self)
        if 'Attack' in all_cards[card_name].types:
            for player in player_states.values():
                can_block = 'Moat' in player.hand_cards
                reaction_cards_in_hand = [card_name for card_name in self.hand_cards if 'Reaction' in all_cards[card_name].types]
                for card_name in reaction_cards_in_hand:
                    all_cards[card_name].perform_reaction(player)
                if not can_block:
                    all_cards[card_name].perform_attack(self, player)

    def end_turn(self):
        self.played_stack += self.hand_cards + self.active_cards
        self.hand_cards.clear()
        self.active_cards.clear()
        self.draw_cards(5)

    def restockDrawIfNeeded(self):
        if len(self.draw_stack) == 0:
            if len(self.played_stack) == 0:
                return False
            self.draw_stack = self.played_stack[:]
            self.played_stack.clear()
            shuffle(self.draw_stack)
        return True

    def draw_cards(self, num = 1):
        for _ in range(num):
            if not self.restockDrawIfNeeded():
                return
            self.hand_cards.append(self.draw_stack[0])
            #print('Drew {} from stack.'.format(self.draw_stack[0]))
            del(self.draw_stack[0])

    def availible_actions(self):
        if self.num_actions > 0:
            return [ card_name for card_name in self.hand_cards if 'Action' in all_cards[card_name].types]
        return []

    def end_play_phase(self):
        self.num_money += sum(all_cards[card_name].count_money(self) for card_name in self.hand_cards if ('Money' in all_cards[card_name].types))

    def availible_buys(self):
        if self.num_buys > 0:
            availible_buys_unsorted =  [(card_name, card) for card_name, card in all_cards.items() if card.cost <= self.num_money and card.count > 0]
            return [card_name for card_name, card in sorted(availible_buys_unsorted, key = lambda card: card[1].cost, reverse=True)]
        return []

    def get_card(self, card_name):
        if all_cards[card_name].count > 0:
            all_cards[card_name].count -= 1
            self.played_stack.append(card_name)
        else:
            print('Card "{}" not availible!'.format(card_name))

    def buy_card(self, card_name):
        self.num_buys -= 1
        self.num_money -= all_cards[card_name].cost
        self.get_card(card_name)


    def count_points(self):
        whole_deck = self.active_cards + self.hand_cards + self.played_stack + self.draw_stack
        return sum(all_cards[card_name].count_points(self) for card_name in whole_deck if ('Point' in all_cards[card_name].types))

    def print_state(self):
        print('{} actions left. {} gold availible. {} buys availible. {} total points.'.format(self.num_actions, self.num_money, self.num_buys, self.count_points()))
        print('Draw stack: {}, Played stack: {}'.format(self.draw_stack, self.played_stack))
        print('Hand: {}, Active: {}'.format(self.hand_cards, self.active_cards))

    def start_turn(self):
        assert(len(self.active_cards) == 0)
        self.num_buys = 1
        self.num_actions = 1
        self.num_money = 0
    
    def get_entire_deck(self):
        return self.hand_cards + self.active_cards + self.played_stack + self.draw_stack

    def do_single_turn(self):
        self.start_turn()
        actions = self.availible_actions()
        while len(actions) > 0:
            #self.print_state()
            choice = self.perform_decision('Perform action...', actions, True)
            if choice == 'None':
                break
            self.play_card(choice)
            actions = self.availible_actions()

        self.end_play_phase()

        buys = self.availible_buys()
        while len(buys) > 0:
            #self.print_state()
            choice = self.perform_decision('Select buy option...', buys, True)
            if choice == 'None':
                break
            self.buy_card(choice)
            buys = self.availible_buys()

        self.end_turn()
        #self.print_state()

turn_counter = 0

def init_game(players):
    global player_states
    global all_cards
    
    #pick random 10 cards + base cards
    all_cards = dict(base_cards)
    random_cards = random.sample(list(optional_cards.keys()), 10)
    for card in random_cards:
        all_cards[card] = optional_cards[card]

    if len(players) <= 2:
        for card_name in ('Estate', 'Duchy', 'Province'):
            all_cards[card_name].count = 8
    shuffle(players)
    draw_stack = ['Copper'] * 7 + ['Estate'] * 3

    for player in players:
        player_name, Interface = player
        shuffle(draw_stack)
        h = Interface(player_name)
        player_states[player_name] = PlayerState([], draw_stack[:], [], player_name, h)
        h.set_player_state = player_states[player_name]
        player_states[player_name].draw_cards(5)

def check_for_end_condition():
    if all_cards['Province'].count == 0 or len([None for card in all_cards.values() if card.count == 3]) == 3:
        winning_player = max(player_states.items(), key = lambda player: player[1].count_points())
        print('\n-----Player {} won the game!-----'.format(winning_player[0]))
        print(', '.join(['{}: {} points'.format(name, player.count_points()) for name, player in player_states.items()]))
        return True
    return False


from termcolor import colored
def coloredCardsString(card_names, atribs = None, print_card_count = False):
    string_list = []
    for card_name in card_names:
        text = card_name
        if print_card_count:
            text += ' ({})'.format(all_cards[card_name].count)

        card_types = all_cards[card_name].types
        if 'Money' in card_types:
            string_list.append(colored(text, 'yellow', attrs = atribs))
        elif 'Point' in card_types:
            string_list.append(colored(text, 'green', attrs = atribs))
        elif 'Attack' in card_types:
            string_list.append(colored(text, 'red', attrs = atribs))
        else:
            string_list.append(colored(text, 'magenta', attrs = atribs))
    return '[{}]'.format(' '.join(string_list))

def print_all_cards():
    base_point_cards = ['Estate', 'Duchy', 'Province']
    base_money_cards = ['Copper', 'Silver', 'Gold']
    optional_cards_in_game = set(all_cards.keys()) & set(optional_cards.keys())
    all_cards_sorted = sorted(optional_cards_in_game, key = lambda card: all_cards[card].cost)
    print(coloredCardsString(base_point_cards + base_money_cards, print_card_count = True))
    print(coloredCardsString(all_cards_sorted, print_card_count = True))

active_player = ''
def print_state():
    #clear()
    print(colored('\t\t-------------Turn {}-------------'.format(turn_counter), 'red', attrs = ['bold']))
    print(print_all_cards())
    for player in player_states.values():
        is_active = player.name == active_player 
        print(colored(player.name, 'red' if is_active else 'white'), '\tDraw:', coloredCardsString(player.draw_stack), ' Played:', coloredCardsString(player.played_stack))
        print('{} actions left. {} gold availible. {} buys availible. {} total points.'.format(player.num_actions, \
            player.num_money, player.num_buys, player.count_points()), coloredCardsString(player.hand_cards, ['bold']), \
            coloredCardsString(player.active_cards))
        print()


def do_single_turn():
    global active_player
    for player_name, player in player_states.items():
        print("\n---Player {}'s turn---".format(player_name))
        active_player = player_name
        player.do_single_turn()
        if check_for_end_condition():
            return True
    return False

def main_loop():
    global turn_counter
    game_over = False
    while not game_over:
        print('\n-----Turn {}-----'.format(turn_counter))
        #print_all_cards()
        game_over = do_single_turn()
        turn_counter += 1

#init_game([('Simon', HumanInterface), ('Simpleton', SimpleBot), ('Moneyman', MoneyGrabber), ('Moneyman2', MoneyGrabber)] )
init_game([('Simpleton', SimpleBot), ('Moneyman', MoneyGrabber), ('Moneyman2', MoneyGrabber)] )
main_loop()
