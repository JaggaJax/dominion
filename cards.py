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

def action_village(player, game):
    player.num_actions += 2
    player.draw_cards()

def action_lumberjack(player, game):
    player.num_buys += 1
    player.num_money += 2

def action_forge(player, game):
    for _ in range(3):
        player.draw_cards()

def action_mine(player, game):
    all_money_cards = [card_name for card_name, card in game.all_cards.items() if 'Money' in card.types]
    discard_options = [card_name for card_name in all_money_cards if card_name in player.hand_cards]
    if len(discard_options) == 0:
        return
    discarded_card = player.perform_decision('Select money card to discard...', discard_options, True)
    buy_options = [card_name for card_name in all_money_cards if game.all_cards[discarded_card].cost + 3 == game.all_cards[card_name].cost]
    if len(buy_options) != 1:
        return
    else:
        print('Discarded card {} for {}.'.format(discarded_card, buy_options[0]))
        player.get_card(buy_options[0])

def action_market(player, game):
    player.draw_cards()
    player.num_actions += 1
    player.num_buys += 1
    player.num_money += 1

def action_fair(player, game):
    player.num_actions += 2
    player.num_buys += 1
    player.num_money += 2

def action_council(player, game):
    player.draw_cards(4)
    player.num_buys += 1
    for opponent in game.get_opponents(player):
        opponent.draw_cards(1)

def action_laboratory(player, game):
    player.draw_cards(2)
    player.num_actions += 1

def action_chappel(player, game):
    for _ in range(4):
        card_to_discard = player.perform_decision('Chose card to discard...', player.hand_cards[:], True)
        if card_to_discard == 'None':
            return
        player.hand_cards.remove(card_to_discard)

def action_cellar(player, game):
    player.num_actions += 1
    count = 0
    for _ in range(len(player.hand_cards)):
        desicion = player.perform_decision('Chose card to lay aside...', player.hand_cards[:], True)
        if desicion == 'None':
            return
        player.played_stack.append(desicion)
        player.hand_cards.remove(desicion)
        count += 1
    player.draw_cards(count)

def action_chancellor(player, game):
    player.num_money += 2
    choice = player.perform_decision('Lay aside entire draw pile?', ['Yes', 'No'], False)
    if choice == 'Yes':
        player.played_stack += player.draw_stack
        player.draw_stack.clear()

def action_workshop(player, game):
    availible_buys_unsorted =  [(card_name, card) for card_name, card in game.all_cards.items() if card.cost <= 4 and card.count > 0]
    availible_buys_sorted = [card_name for card_name, card in sorted(availible_buys_unsorted, key = lambda card: card[1].cost, reverse=True)]
    decision = player.perform_decision('Select card to pick...', availible_buys_sorted, True)
    if decision == 'None':
        return
    print('Chose buy {}'.format(decision))
    player.get_card(decision)

def action_bureaucrat(player, game):
    if game.all_cards['Silver'].count > 0:
        player.draw_stack.insert(0, 'Silver')
        game.all_cards['Silver'].count -= 1

def attack_bureaucrat(player, opponent, game):
    if player == opponent:
        return
    point_cards_in_hand = [card_name for card_name in opponent.hand_cards if 'Point' in game.all_cards[card_name].types]
    if len(point_cards_in_hand) == 0:
        #print('No point card on hand')
        return
    decision = opponent.perform_decision('Select point card to put on draw pile...', point_cards_in_hand, False)
    #print('Chose to put {} on draw pile'.format(decision))
    opponent.draw_stack.insert(0, decision)
    opponent.hand_cards.remove(decision)

def action_rebuilding(player, game):
    card_to_discard = player.perform_decision('Pick a card to discard...', player.hand_cards[:])
    if card_to_discard == 'None':
        return
    player.hand_cards.remove(card_to_discard)
    availible_buys_unsorted = [card_name for card_name, card in game.all_cards.items() if card.cost <= game.all_cards[card_to_discard].cost + 2]
    if len(availible_buys_unsorted) == 0:
        return
    buy = player.perform_decision('Pick a card to buy...', sorted(availible_buys_unsorted, key = lambda c: game.all_cards[c].cost, reverse=True), False)
    player.get_card(buy)

def action_throneroom(player, game):
    actions_on_hand = [card_name for card_name in player.hand_cards if 'Action' in game.all_cards[card_name].types]
    action_card = player.perform_decision('Chose action to perform twice...', actions_on_hand)
    if action_card == 'None':
        return
    player.num_actions += 2
    print('Playing card {} 1/2'.format(action_card))
    player.play_card(action_card)
    player.active_cards.remove(action_card)
    player.hand_cards.append(action_card)
    print('Playing card {} 2/2'.format(action_card))
    player.play_card(action_card)

def action_spy(player, game):
    player.num_buys += 1
    player.draw_cards(1)

def attack_spy(player, opponent, game):
    options = ['Discard', 'Keep']
    if len(opponent.draw_stack) == 0:
        print('Player {} has empty draw stack.'.format(opponent.name))
        return
    top_card = opponent.draw_stack[0]
    choice = player.perform_decision('Let player {} discard or keep card {}'.format(opponent.name, top_card), \
        options, False)
    if choice == 'Discard':
        opponent.played_stack.append(top_card)
        opponent.draw_stack.remove(top_card)

def action_militia(player, game):
    player.num_money += 2

def attack_militia(player, opponent, game):
    if player == opponent:
        return
    for _ in range(3, len(opponent.hand_cards)):
        card_to_discard = opponent.perform_decision('Choose card to discard...', opponent.hand_cards[:], False)
        opponent.hand_cards.remove(card_to_discard)
        opponent.played_stack.append(card_to_discard)

def action_moneylender(player, game):
    if not 'Copper' in player.hand_cards:
        return
    if player.perform_decision('Discard Copper for +3?', ['Yes', 'No'], False) == 'Yes':
        player.hand_cards.remove('Copper')
        player.num_money += 3
    
def action_feast(player, game):
    player.active_cards.remove('Feast')
    buy_options = [card_name for card_name, card in game.all_cards.items() if card.cost <= 5 and card.count > 0]
    buy_options.sort(key = lambda card_name: game.all_cards[card_name].cost, reverse=True)
    choice = player.perform_decision('Pick card to buy...', buy_options, True)
    if choice == 'None':
        return
    player.get_card(choice)

def action_thief(player, game):
    pass

def attack_thief(player, opponent, game):
    if player == opponent or len(opponent.draw_stack) == 0: 
        return
    if len(opponent.draw_stack) == 1:
        card = opponent.draw_stack[0]
    else:
        card = player.perform_decision('Pick money card...', opponent.draw_stack[:2], False)
        opponent.draw_stack.remove(card)
        steal = player.perform_decision('Steal or leave card?', ['Steal', 'Leave'], False)
        if steal == 'Steal':
            player.played_stack.append(card)

def action_adventurer(player, game):
    count = 0
    while count < 2:
        player.restockDrawIfNeeded()
        card_name = player.draw_stack[0]
        player.draw_stack.remove(card_name)
        if 'Money' in game.all_cards[card_name].types:
            count += 1
            player.hand_cards.append(card_name)
        else:
            player.played_stack.append(card_name)

def action_library(player, game):
    while len(player.hand_cards) < 7:
        player.restockDrawIfNeeded()
        if len(player.draw_stack) == 0:
            return
        card_name = player.draw_stack[0]
        player.draw_stack.remove(card_name)
        if 'Action' in game.all_cards[card_name].types:
            choice = player.perform_decision('Take or discard card {}?'.format(card_name), ['Take', 'Discard'], False)
            if choice == 'Discard':
                player.played_stack.append(card_name)
                continue
        player.hand_cards.append(card_name)
            
base_cards = {
    'Copper' : Card(['Money'], 0, count_money = lambda player, _: 1, count = 50),
    'Silver' : Card(['Money'], 3, count_money = lambda player, _: 2, count = 40),
    'Gold' : Card(['Money'], 6, count_money = lambda player, _: 3, count = 30),

    'Curse' : Card(['Point'], 0, count_points = lambda player, _: -1, count = 20),
    'Estate' : Card(['Point'], 2, count_points = lambda player, _: 1, count = 12),
    'Duchy' : Card(['Point'], 5, count_points = lambda player, _: 3, count = 12),
    'Province' : Card(['Point'], 8, count_points = lambda player, _: 6, count = 12)
}

optional_cards = {
    'Garden' : Card(['Point'], 4, count_points = lambda player, _ : len(player.get_entire_deck()) // 10, count = 12),
    'Moat' : Card(['Action', 'Reaction'], 2, perform_action = lambda player, _: player.draw_cards(2), \
        perform_reaction = lambda player, _ : print('Invalidating attack!')),
    'Chappel' : Card(['Action'], 2, perform_action = action_chappel),
    'Cellar' : Card(['Action'], 2, perform_action = action_cellar), 
    'Village' : Card(['Action'], 3, perform_action = action_village),
    'Lumberjack' : Card(['Action'], 3, perform_action = action_lumberjack),
    'Chancelor' : Card(['Action'], 3, perform_action = action_chancellor), 
    'Workshop' : Card(['Action'], 3, perform_action = action_workshop),
    'Bureaucrat': Card(['Action', 'Attack'], 4, perform_action = action_bureaucrat, perform_attack = attack_bureaucrat),
    'Thief' : Card(['Action', 'Attack'], 4, perform_action = action_thief, perform_attack = attack_thief),
    'Feast' : Card(['Action'], 4, perform_action = action_feast),
    'Moneylender' : Card(['Action'], 4, perform_action = action_moneylender),
    'Militia' : Card(['Action', 'Attack'], 4, perform_action = lambda player, _: action_militia, perform_attack = attack_militia),
    'Forge' : Card(['Action'], 4, perform_action = action_forge),
    'Spy' : Card(['Action', 'Attack'], 4, perform_action = action_spy, perform_attack = attack_spy),
    'Thoneroom': Card(['Action'], 4, perform_action = action_throneroom),
    'Rebuilding': Card(['Action'], 4, perform_action = action_rebuilding),
    'Library' : Card(['Action'], 5, perform_action = action_library),
    'Witch' : Card(['Action', 'Attack'], 5, perform_action = lambda player, _: player.draw_cards(2), \
        perform_attack = lambda player, opponent, _: opponent.get_card('Curse') if player != opponent else None),
    'Fair' : Card(['Action'], 5, perform_action = action_fair),
    'Laboratory' : Card(['Action'], 5, perform_action = action_laboratory),
    'Market' : Card(['Action'], 5, perform_action = action_market),
    'Mine' : Card(['Action'], 5, perform_action = action_mine),
    'Council' : Card(['Action'], 5, perform_action = action_council),
    'Adventurer' : Card(['Action'], 6, perform_action = action_adventurer)
}