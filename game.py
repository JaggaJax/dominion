import itertools
from random import shuffle

all_cards = []

class Card:
    def __init__(self, name, cardType, cost):
        self.name = name
        self.cardType = cardType
        self.cost = cost

    def performAction(self, state):
        pass

    def __repr__(self):
        return self.name

class Card_Copper(Card):
    def __init__(self):
        super(Card_Copper, self).__init__('Copper', 'Money', 0)

    def get_value(self):
        return 1

class Card_Silver(Card):
    def __init__(self):
        super(Card_Silver, self).__init__('Silver', 'Money', 3)

    def get_value(self):
        return 2

class Card_Gold(Card):
    def __init__(self):
        super(Card_Gold, self).__init__('Gold', 'Money', 6)

    def get_value(self):
        return 3


class Card_Estate(Card):
    def __init__(self):
        super(Card_Estate, self).__init__('Estate', 'Point', 2)

    def get_points(self):
        return 1

class Card_Duchy(Card):
    def __init__(self):
        super(Card_Duchy, self).__init__('Duchy', 'Point', 5)

    def get_points(self):
        return 3

class Card_Province(Card):
    def __init__(self):
        super(Card_Province, self).__init__('Province', 'Point', 8)

    def get_points(self):
        return 6


class Card_Village(Card):
    def __init__(self):
        super(Card_Village, self).__init__('Village', 'Action', 3)

    def perform_action(self, state):
        state.num_actions += 2
        state.draw_card()

class Card_Lumberjack(Card):
    def __init__(self):
        super(Card_Lumberjack, self).__init__('Lumberjack', 'Action', 3)

    def perform_action(self, state):
        state.num_buys += 1
        state.num_money += 2

class Card_Forge(Card):
    def __init__(self):
        Card.__init__(self, 'Forge', 'Action', 4)

    def perform_action(self, state):
        for _ in range(3):
            state.draw_card()

class Card_Mine(Card):
    def __init__(self):
        Card.__init__(self, 'Mine', 'Action', 5)

    def perform_action(self, state):
        cards_in_hand = [card.name for card in state.hand_cards]
        all_money_cards = [card for card in all_cards if card.cardType == 'Money']
        discard_options = [card for card in all_money_cards if card.name in cards_in_hand]
        print('Select money card to discard...')
        print(', '.join(["{}: {}".format(val+1, i) for val, i in enumerate(discard_options)]) + ', 0: None')
        input_number = int(input())
        if input_number not in range(1, len(discard_options)+1):
            return
        buy_options = [card for card in all_money_cards if discard_options[input_number-1].cost + 3 == card.cost]
        print(buy_options)
        if len(buy_options) != 1:
            assert(False)
        else:
            print('Discarded card {} for {}.'.format(discard_options[input_number-1], buy_options[0]))
            state.get_card(buy_options[0])

class Card_Market(Card):
    def __init__(self):
        Card.__init__(self, 'Market', 'Action', 5)

    def perform_action(self, state):
        state.draw_card()
        state.num_actions += 1
        state.num_buys += 1
        state.num_money += 1

class Card_Fair(Card):
    def __init__(self):
        Card.__init__(self, 'Fair', 'Action', 5)

    def perform_action(self, state):

all_cards = [Card_Copper(), Card_Silver(), Card_Gold(), \
    Card_Estate(), Card_Duchy(), Card_Province(), \
    Card_Village(), Card_Lumberjack(), Card_Forge(), Card_Mine(), Card_Market()]

class Card():
    def __init__(self, types, cost, perform_action = None, count_points = None, perform_reaction = None, count_money = None):
        self.types = types
        self.cost = cost
        self.perform_action = perform_action
        assert((not 'Action' in types) or (perform_action != None))
        self.count_points = count_points
        assert((not 'Point' in types) or (count_points != None))
        self.perform_reaction = perform_reaction
        assert((not 'Reaction' in types) or (perform_reaction != None))
        self.count_money = count_money
        assert((not 'Money' in types) or (count_money != None))


def action_fair(state):
    state.num_actions += 2
    state.num_buys += 1
    state.num_money += 2


card_dict = {
    'Copper' : Card(['Money'], 6, count_money = lambda state: 3)
    'Silver' : Card(['Money'], 6, count_money = lambda state: 3)
    'Gold' : Card(['Money'], 6, count_money = lambda state: 3)

    'Fair' : Card(['Action'], 5, perform_action = action_fair)
}

class PlayerState:
    def __init__(self, hand_cards, draw_stack, played_stack):
        self.num_buys = 1
        self.num_money = 0
        self.num_actions = 1

        self.hand_cards = hand_cards
        self.draw_stack = draw_stack
        self.played_stack = played_stack
        self.active_cards = []

    def play_card(self, card):
        self.num_actions -= 1
        card.perform_action(self)
        self.hand_cards.remove(card)
        self.active_cards.append(card)

    def end_turn(self):
        self.played_stack += self.hand_cards + self.active_cards
        self.hand_cards.clear()
        self.active_cards.clear()

    def draw_card(self):
        if len(self.draw_stack) == 0:
            self.draw_stack = self.played_stack[:]
            self.played_stack.clear()
            shuffle(self.draw_stack)

        self.hand_cards.append(self.draw_stack[0])
        print('Drew {} from stack.'.format(self.draw_stack[0]))
        del(self.draw_stack[0])

    def availible_actions(self):
        if self.num_actions > 0:
            return [ card for card in self.hand_cards if card.cardType == 'Action']
        return []

    def end_play_phase(self):
        self.num_money += sum(card.get_value() for card in self.hand_cards if card.cardType == 'Money')
        

    def availible_buys(self):
        if self.num_buys > 0:
            return [card for card in all_cards if card.cost <= self.num_money]
        return []
        #combinations = []
        #for i in range(1, self.num_buys+1):
        #    combinations += list(itertools.combinations_with_replacement(all_cards, i))
        #return list(filter(lambda comb: sum(c.cost for c in comb) <= self.num_money, combinations))

    def get_card(self, card):
        self.played_stack.append(card)

    def buy_card(self, card):
        self.num_buys -= 1
        self.num_money -= card.cost
        self.get_card(card)


    def count_points(self):
        whole_deck = self.active_cards + self.hand_cards + self.played_stack + self.draw_stack
        return sum(card.get_points() for card in whole_deck if card.cardType == 'Point')

    def print_state(self):
        print('Draw stack cards (secret): {}'.format(self.draw_stack))
        print('Hand cards: {}'.format(self.hand_cards))
        print('Active cards (on the table): {}'.format(self.active_cards))
        print('Played stack: {}'.format(self.played_stack))
        print('{} actions left. {} gold availible. {} buys availible. {} total points.'.format(self.num_actions, self.num_money, self.num_buys, self.count_points()))

    def start_turn(self):
        assert(len(self.hand_cards) == 0)
        assert(len(self.active_cards) == 0)
        self.num_buys = 1
        self.num_actions = 1
        self.num_money = 0
        for _ in range(5):
            self.draw_card()

    def main_loop(self):
        while True:
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

#hand_cards = [Card_Village(), Card_Lumberjack(), Card_Copper(), Card_Copper(), Card_Duchy()]
#draw_stack = [Card_Copper(), Card_Copper(), Card_Duchy(), Card_Duchy(), Card_Copper()]
draw_stack = [Card_Copper() for _ in range(7)] + [Card_Estate() for _ in range(3)] + [Card_Mine() for _ in range(6)]
shuffle(draw_stack)
hand_cards = []
played_stack = []

ps = PlayerState(hand_cards, draw_stack, played_stack)
ps.main_loop()

