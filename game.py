import itertools
from random import shuffle

all_cards = {}
player_states = {}

class Card():
    def __init__(self, types, cost, perform_action = None, count_points = None, perform_reaction = None, count_money = None, perform_attack = None, count = 10):
        self.types = types
        self.cost = cost
        self.perform_action = perform_action
        self.count = count
        assert((not 'Action' in types) or (perform_action != None))
        self.count_points = count_points
        assert((not 'Point' in types) or (count_points != None))
        self.perform_reaction = perform_reaction
        assert((not 'Reaction' in types) or (perform_reaction != None))
        self.count_money = count_money
        assert((not 'Money' in types) or (count_money != None))
        self.perform_attack = perform_attack
        assert((not 'Attack' in types) or (perform_attack != None))

def action_village(state):
    state.num_actions += 2
    state.draw_cards()

def action_lumberjack(state):
    state.num_buys += 1
    state.num_money += 2

def action_forge(state):
    for _ in range(3):
        state.draw_cards()

def action_mine(state):
    all_money_cards = [card_name for card_name, card in all_cards.items() if 'Money' in card.types]
    discard_options = [card_name for card_name in all_money_cards if card_name in state.hand_cards]
    print('Select money card to discard...')
    print(', '.join(["{}: {}".format(val+1, i) for val, i in enumerate(discard_options)]) + ', 0: None')
    input_number = int(input())
    if input_number not in range(1, len(discard_options)+1):
        return

    discarded_card = discard_options[input_number - 1]
    buy_options = [card_name for card_name in all_money_cards if all_cards[discarded_card].cost + 3 == all_cards[card_name].cost]
    print(buy_options)
    if len(buy_options) != 1:
        assert(False)
    else:
        print('Discarded card {} for {}.'.format(discard_options[input_number-1], buy_options[0]))
        state.get_card(buy_options[0])

def action_market(state):
    state.draw_cards()
    state.num_actions += 1
    state.num_buys += 1
    state.num_money += 1

def action_fair(state):
    state.num_actions += 2
    state.num_buys += 1
    state.num_money += 2



class PlayerState:
    def __init__(self, hand_cards, draw_stack, played_stack):
        self.num_buys = 1
        self.num_money = 0
        self.num_actions = 1

        self.hand_cards = hand_cards
        self.draw_stack = draw_stack
        self.played_stack = played_stack
        self.active_cards = []

    def process_attack(self, attack):
        #TODO: make all of this optional
        can_block = 'Moat' in self.hand_cards
        reaction_cards_in_hand = [card_name for card_name in self.hand_cards if 'Reaction' in all_cards[card_name].types]
        for card_name in reaction_cards_in_hand:
            all_cards[card_name].perform_reaction(self)
        #this will automatically block attacks if possible
        if not can_block:
            attack(self)
        

    def play_card(self, card_name):
        self.num_actions -= 1
        self.hand_cards.remove(card_name)
        self.active_cards.append(card_name)
        all_cards[card_name].perform_action(self)
        if 'Attack' in all_cards[card_name].types:
            for player in player_states.values():
                if player != self and all_cards['Curse'].count > 0:
                    player.process_attack(all_cards[card_name].perform_attack)

    def end_turn(self):
        self.played_stack += self.hand_cards + self.active_cards
        self.hand_cards.clear()
        self.active_cards.clear()
        self.draw_cards(5)

    def draw_cards(self, num = 1):
        for _ in range(num):
            self.hand_cards.append(self.draw_stack[0])
            #print('Drew {} from stack.'.format(self.draw_stack[0]))
            del(self.draw_stack[0])
            if len(self.draw_stack) == 0:
                self.draw_stack = self.played_stack[:]
                self.played_stack.clear()
                shuffle(self.draw_stack)

    def availible_actions(self):
        if self.num_actions > 0:
            return [ card_name for card_name in self.hand_cards if ('Action' in all_cards[card_name].types)]
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
            self.print_state()
            print('Perform action...')
            print(', '.join(["{}: {}".format(val+1, i) for val, i in enumerate(actions)]) + ', 0: None')
            input_number = int(input())
            if input_number not in range(1, len(actions)+1):
                break
            print('Chose option {}: {}'.format(input_number, actions[input_number-1]))
            self.play_card(actions[input_number-1])
            actions = self.availible_actions()

        self.end_play_phase()

        buys = self.availible_buys()
        while len(buys) > 0:
            self.print_state()
            print('Select buy option...')
            buys = self.availible_buys()
            print(', '.join(["{}: {}".format(val+1, i) for val, i in enumerate(buys)]) + ', 0: None')
            input_number = int(input())
            if input_number not in range(1, len(buys)+1):
                break
            print('Chose buy {}: {}'.format(input_number, buys[input_number - 1]))
            self.buy_card(buys[input_number - 1])
            buys = self.availible_buys()

        self.end_turn()
        self.print_state()

def action_council(state):
    state.draw_cards(4)
    state.num_buys += 1
    for player in player_states.values():
        if player != state:
            player.draw_cards()

def count_points_garden(state):
    return 

def action_laboratory(state):
    state.draw_cards(2)
    state.num_actions += 1

def action_chappel(state):
    for _ in range(4):
        print('Chose card to discard...')
        print(', '.join(["{}: {}".format(val+1, i) for val, i in enumerate(state.hand_cards)]) + ', 0: None')
        input_number = int(input())
        if input_number not in range(1, len(state.hand_cards)+1):
            return 
        state.hand_cards.remove(state.hand_cards[input_number-1])

def action_cellar(state):
    state.num_actions += 1
    count = 0
    for _ in range(len(state.hand_cards))
        print('Chose card to lay aside...')
        print(', '.join(["{}: {}".format(val+1, i) for val, i in enumerate(state.hand_cards)]) + ', 0: None')
        input_number = int(input())
        if input_number not in range(1, len(state.hand_cards)+1):
            return 
        state.played_stack.append(state.hand_cards[input_number-1])
        state.hand_cards.remove(state.hand_cards[input_number-1])
        count += 1
    state.draw_cards(count)

def action_chancellor(state):
    state.num_money += 2
    print('1: Lay aside entire draw pile, 0: Leave draw pile.')    
    input_number = int(input())
    if input_number == 1:
        state.played_stack += state.draw_stack
        state.draw_stack.clear()

def action_workshop(state):
    availible_buys_unsorted =  [(card_name, card) for card_name, card in all_cards.items() if card.cost <= 4 and card.count > 0]
    availible_buys_sorted = [card_name for card_name, card in sorted(availible_buys_unsorted, key = lambda card: card[1].cost, reverse=True)]
    print('Select card to pick...')
    print(', '.join(["{}: {}".format(val+1, i) for val, i in enumerate(availible_buys_sorted)]) + ', 0: None')
    input_number = int(input())
    if input_number not in range(1, len(availible_buys_sorted)+1):
        break
    print('Chose buy {}: {}'.format(input_number, availible_buys_sorted[input_number - 1]))
    self.get_card(buys[input_number - 1])

def action_burocrat(state):
    if all_cards['Silver'].count > 0:
        state.draw_stack.insert(0, 'Silver')
        all_cards['Silver'].count -= 1
        #TODO: finish burocrat

all_cards = {
    'Copper' : Card(['Money'], 0, count_money = lambda state: 1, count = 50),
    'Silver' : Card(['Money'], 3, count_money = lambda state: 2, count = 40),
    'Gold' : Card(['Money'], 6, count_money = lambda state: 3, count = 30),

    'Estate' : Card(['Point'], 2, count_points = lambda state: 1, count = 12),
    'Duchy' : Card(['Point'], 5, count_points = lambda state: 3, count = 12),
    'Province' : Card(['Point'], 8, count_points = lambda state: 6, count = 12),
    'Curse' : Card(['Point'], 0, count_points = lambda state: -1, count = 20),
    'Garden' : Card(['Point'], 4, count_points = lambda state : len(state.get_entire_deck()) // 10, count = 12),

    'Moat' : Card(['Action', 'Reaction'], 2, perform_action = lambda state: state.draw_cards(2), perform_reaction = lambda state: print('Invalidating attack!')),
    'Chappel' : Card(['Action'], 2, perform_action = action_chappel),
    'Cellar' : Card(['Action'], 2, perform_action = action_cellar), 
    'Chancelor' : Card(['Action'], 3, perform_action = action_chancellor), 
    'Village' : Card(['Action'], 3, perform_action = action_village),
    'Lumberjack' : Card(['Action'], 3, perform_action = action_lumberjack),
    'Workshop' : Card(['Action'], perform_action = action_workshop),
    'Forge' : Card(['Action'], 4, perform_action = action_forge),
    'Fair' : Card(['Action'], 5, perform_action = action_fair),
    'Market' : Card(['Action'], 5, perform_action = action_market),
    'Mine' : Card(['Action'], 5, perform_action = action_mine),
    'Council' : Card(['Action'], 5, perform_action = action_council),
    'Witch' : Card(['Action', 'Attack'], 5, perform_action = lambda state: state.draw_cards(2), perform_attack = lambda state: state.get_card('Curse')),
    'Laboratory' : Card(['Action'], 5, perform_action = action_laboratory)
}

turn_counter = 0

def init_game(player_names):
    global player_states
    
    if len(player_names) <= 2:
        for card_name in ('Estate', 'Duchy', 'Province'):
            all_cards[card_name].count = 8
    shuffle(player_names)
    draw_stack = ['Copper'] * 7 + ['Estate'] * 3
    for player in player_names:
        shuffle(draw_stack)
        player_states[player] = PlayerState(['Chappel'], draw_stack[:], [])
        player_states[player].draw_cards(5)

def check_for_end_condition():
    if all_cards['Province'].count == 0 or len([None for card in all_cards.values() if card.count == 3]) == 3:
        winning_player = max(player_states.items(), key = lambda player: player[1].count_points())
        print('\n-----Player {} won the game!-----'.format(winning_player[0]))
        print(', '.join(['{}: {} points'.format(name, player.count_points()) for name, player in player_states.items()]))
        return True
    return False

def print_all_cards():
    print(', '.join(['{} ({})'.format(card_name, card.count) for card_name, card in all_cards.items()]))

def do_single_turn():
    for player_name, player in player_states.items():
        print("\n---Player {}'s turn---".format(player_name))
        player.do_single_turn()
        if check_for_end_condition():
            return True
    return False

def main_loop():
    global turn_counter
    game_over = False
    while not game_over:
        print('\n-----Turn {}-----'.format(turn_counter))
        print_all_cards()
        game_over = do_single_turn()
        turn_counter += 1

init_game(['p1', 'p2'])
main_loop()
