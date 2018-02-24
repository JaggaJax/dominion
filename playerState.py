from random import shuffle

class PlayerState:
    def __init__(self, game_state, hand_cards, draw_stack, played_stack, name, interface):
        self.num_buys = 1
        self.num_money = 0
        self.num_actions = 1
        self.g = game_state

        self.hand_cards = hand_cards
        self.draw_stack = draw_stack
        self.played_stack = played_stack
        self.active_cards = []
        self.name = name
        self.interface = interface

    def perform_decision(self, message, options, allow_none = True):
        if self.g.verbose:
            self.g.print_state()
            print('{}, {}'.format(self.name, message))
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
        self.g.all_cards[card_name].perform_action(self, self.g)
        if 'Attack' in self.g.all_cards[card_name].types:
            for opponent in self.g.player_states.values():
                can_block = 'Moat' in opponent.hand_cards
                reaction_cards_in_hand = [card_name for card_name in opponent.hand_cards if 'Reaction' in self.g.all_cards[card_name].types]
                for reaction_card in reaction_cards_in_hand:
                    self.g.all_cards[reaction_card].perform_reaction(opponent, self.g)
                if not can_block:
                    self.g.all_cards[card_name].perform_attack(self, opponent, self.g)

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
            return [ card_name for card_name in self.hand_cards if 'Action' in self.g.all_cards[card_name].types]
        return []

    def end_play_phase(self):
        self.num_money += sum(self.g.all_cards[card_name].count_money(self, self.g) \
            for card_name in self.hand_cards if ('Money' in self.g.all_cards[card_name].types))

    def availible_buys(self):
        if self.num_buys > 0:
            availible_buys_unsorted =  [(card_name, card) for card_name, card in self.g.all_cards.items() if card.cost <= self.num_money and card.count > 0]
            return [card_name for card_name, card in sorted(availible_buys_unsorted, key = lambda card: card[1].cost, reverse=True)]
        return []

    def get_card(self, card_name):
        if self.g.all_cards[card_name].count > 0:
            self.g.all_cards[card_name].count -= 1
            self.played_stack.append(card_name)
        else:
            print('Card "{}" not availible!'.format(card_name))

    def buy_card(self, card_name):
        self.num_buys -= 1
        self.num_money -= self.g.all_cards[card_name].cost
        self.get_card(card_name)


    def count_points(self):
        whole_deck = self.active_cards + self.hand_cards + self.played_stack + self.draw_stack
        return sum(self.g.all_cards[card_name].count_points(self, self.g) \
            for card_name in whole_deck if ('Point' in self.g.all_cards[card_name].types))

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
