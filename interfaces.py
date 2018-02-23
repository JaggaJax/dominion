#from game import PlayerState

class GeneralInterface:
    def __init__(self, name):
        self.player_name = name
        self.player_state = None
        
    def set_player_state(self, player_state):
        self.player_state = player_state


class HumanInterface(GeneralInterface):
    def __init__(self, name):
        super().__init__(name)

    def decide(self, message, options, tag = 'DEFAULT'):
        print(self.player_name, ', ', message)
        options_string = ', '.join('{}: {}'.format(val + 1 if i != 'None' else 0, i) for val, i in enumerate(options))
        print(options_string)
        input_number = int(input())
        if input_number not in range(1, len(options)+1) and 'None' in options:
            return 'None'
        return options[input_number-1]

class SimpleBot(GeneralInterface):
    def __init__(self, name):
        super().__init__(name)

    def decide(self, message, options, tag = 'DEFAULT'):
        print(self.player_name, ', ', message)
        options_string = ', '.join('{}: {}'.format(val + 1 if i != 'None' else 0, i) for val, i in enumerate(options))
        print(options_string)
        print('{} chooses {}'.format(self.player_name, options[0]))
        input('Press return...')
        return options[0]

class MoneyGrabber(GeneralInterface):
    def __init__(self, name):
        super().__init__(name)

    def decide(self, message, options, tag = 'DEFAULT'):
        print(self.player_name, ', ', message)
        options_string = ', '.join('{}: {}'.format(val + 1 if i != 'None' else 0, i) for val, i in enumerate(options))
        print(options_string)

        choice_priority = ['Province', 'Gold', 'Silver', 'None', options[0]]
        for choice in choice_priority:
            if choice in options:
                print('{} chooses {}'.format(self.player_name, choice))
                input('Press return...')
                return choice



