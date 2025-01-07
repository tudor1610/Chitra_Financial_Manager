import pygame
import random
import asyncio
import time

pygame.init()

BALANCE = 100
IS_DECK_SHUFFLED = 52

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chitra Games")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (147, 204, 250)
RED = (255, 0, 0)

FONT = pygame.font.Font(None, 36)

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k", "a"]
SUITS = ["h", "c", "s", "d"]
#construct the CARDS array 
CARDS = [suit + rank for suit in SUITS for rank in RANKS]

CARD_VALUES = {rank: int(rank) if rank.isdigit() else 10 for rank in RANKS}
CARD_VALUES["a"] = 11

CARD_IMAGES = {card: pygame.image.load(f"cards/{card}.png") for card in CARDS}
CARD_BACK = pygame.image.load("cards/back.png")

BUTTON_COLOR = (192, 192, 192)
BUTTON_TEXT_COLOR = BLACK
BUTTON_HOVER_COLOR = (160, 160, 160)

HIT_BUTTON_RECT = pygame.Rect(75, 200, 100, 50)
STAND_BUTTON_RECT = pygame.Rect( 75, 300, 100, 50)

BACKGROUND = pygame.image.load("buttons/background.png").convert_alpha()
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))


def draw_button(text, x, y, width, height, is_hovered):
    color = BUTTON_HOVER_COLOR if is_hovered else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
    display_text(text, x + 20, y + 10, BUTTON_TEXT_COLOR)

def shuffle_deck():
    deck = CARDS[:]
    random.shuffle(deck)
    return deck

def calculate_hand_value(hand):
    value = sum(CARD_VALUES[card[1:]] for card in hand)
    aces = sum(1 for card in hand if card[1:] == "a")
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


# Display text on the screen
def display_text(text, x, y, color=WHITE):
    rendered_text = FONT.render(text, True, color)
    screen.blit(rendered_text, (x, y))

def display_hand(hand, x, y, show_all=True):
    for index, card in enumerate(hand):
        if show_all or index == 0:
            card_image = CARD_IMAGES[card]
        else:
            card_image = CARD_BACK
        screen.blit(card_image, (x + index * 80, y))


def out_of_balance():
    while True:
        screen.blit(BACKGROUND, (0, 0))
        display_text("Blackjack", WIDTH // 2 - 60, 20, WHITE)
        display_text("You are out of funds... :(((", WIDTH // 2 - 140, 300, WHITE)
        display_text("Thank you for playing", WIDTH // 2 - 120, 200, WHITE)
        display_text("Press Q to exit.", WIDTH // 2 - 80 , 450, WHITE)
        display_text("GOODBYE!", WIDTH // 2 - 60, 500, WHITE)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return


def init_deck():
    deck = shuffle_deck()
    return deck


# Main game loop
async def main():
    global BALANCE
    global IS_DECK_SHUFFLED
    global deck
    running = True
    clock = pygame.time.Clock()

    if IS_DECK_SHUFFLED == 52:
        deck = init_deck()
        IS_DECK_SHUFFLED = True
    
    IS_DECK_SHUFFLED -= 4
    if IS_DECK_SHUFFLED < 4:
        deck = shuffle_deck()
        IS_DECK_SHUFFLED = 52
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    player_turn = True
    game_over = False
    winner = None
    bet = 0
    cards_on_table = 6

    while running:
        screen.blit(BACKGROUND, (0, 0))

        display_text("Blackjack", WIDTH // 2 - 60, 20, WHITE)
        display_text(f"Balance: ${BALANCE}", 600, 75, WHITE)
        display_text(f"Bet: ${bet}", 640, 550, WHITE)

        display_hand(dealer_hand, WIDTH // 2 - 100, 100, show_all=game_over)
        display_hand(player_hand, WIDTH // 2 - 100, 400)
        display_text(f"Player Total: {calculate_hand_value(player_hand)}", WIDTH // 2 - 100, 520)
        display_text(f"Dealer Total: ", WIDTH // 2 - 100, 220)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered_hit = HIT_BUTTON_RECT.collidepoint(mouse_x, mouse_y)
        is_hovered_stand = STAND_BUTTON_RECT.collidepoint(mouse_x, mouse_y)
        draw_button("Hit", 75, 200, 100, 50, is_hovered_hit)
        draw_button("Stand",  75, 300, 100, 50, is_hovered_stand)

        screen.blit(CARD_BACK, (325, 260))
        for i in range(cards_on_table):
            screen.blit(CARD_BACK, (325 + 7 * i, 260))
        pygame.display.flip()

        input_active = True
        bet_text = ""
        #Place the bet
        if bet == 0:
            while input_active:
                screen.blit(BACKGROUND, (0, 0))
                display_text("Blackjack", WIDTH // 2 - 60, 20, WHITE)
                display_text(f"Balance: ${BALANCE}", 600, 75, WHITE)
                display_text("Please, place your bet!", 270, 250, WHITE)
                display_text(f"Amount to Bet: ${bet_text}", 300, 300, WHITE)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if bet_text.isdigit() and 0 < int(bet_text) <= BALANCE:
                                bet = int(bet_text)
                                BALANCE -= bet
                                input_active = False
                            else:
                                bet_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            bet_text = bet_text[:-1]
                        else:
                            bet_text += event.unicode

            display_text("Bet confirmed!", 310, 400, WHITE)
            pygame.display.flip()
            time.sleep(1)

        if game_over:
            display_text(f"Dealer Total: {calculate_hand_value(dealer_hand)}", WIDTH // 2 - 100, 220)
            display_text(winner, 500, HEIGHT // 2, WHITE)
            if BALANCE > 1:
                display_text("Press R to Restart or Q to Quit", 430, HEIGHT // 2 + 70)
            else:
                time.sleep(2)
                out_of_balance()
                

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and BALANCE:
                        return "restart"
                    elif event.key == pygame.K_q:
                        running = False
            elif player_turn:
                  if player_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    # Hit button
                    if HIT_BUTTON_RECT.collidepoint(event.pos):
                        if IS_DECK_SHUFFLED == 0:
                            deck = shuffle_deck()
                            IS_DECK_SHUFFLED = 52
                        player_hand.append(deck.pop())
                        IS_DECK_SHUFFLED -= 1
                        if calculate_hand_value(player_hand) > 21:
                            game_over = True
                            winner = "You Busted! Dealer Wins!"
                    # Stand button
                    elif STAND_BUTTON_RECT.collidepoint(event.pos):
                        player_turn = False
                        time.sleep(2)


        if not player_turn and not game_over:
            pygame.display.flip()
            while True:
                screen.blit(BACKGROUND, (0, 0))
                display_text("Blackjack", WIDTH // 2 - 60, 20, WHITE)
                display_text(f"Balance: ${BALANCE}", 600, 75, WHITE)
                display_text(f"Bet: ${bet}", 640, 550, WHITE)

                display_hand(dealer_hand, WIDTH // 2 - 100, 100, show_all=True)
                display_hand(player_hand, WIDTH // 2 - 100, 400)
                display_text(f"Your Total: {calculate_hand_value(player_hand)}", WIDTH // 2 - 100, 520)
                display_text(f"Dealer Total: {calculate_hand_value(dealer_hand)}", WIDTH // 2 - 100, 220)
                
                mouse_x, mouse_y = pygame.mouse.get_pos()
                is_hovered_hit = HIT_BUTTON_RECT.collidepoint(mouse_x, mouse_y)
                is_hovered_stand = STAND_BUTTON_RECT.collidepoint(mouse_x, mouse_y)
                draw_button("Hit", 75, 200, 100, 50, is_hovered_hit)
                draw_button("Stand", 75, 300, 100, 50, is_hovered_stand)

                screen.blit(CARD_BACK, (3250, 260))
                for i in range(cards_on_table):
                    screen.blit(CARD_BACK, (325 + 7 * i, 260))
                pygame.display.flip()

                if calculate_hand_value(dealer_hand) < 17:
                    if IS_DECK_SHUFFLED == 0:
                        deck = shuffle_deck()
                        IS_DECK_SHUFFLED = 52
                    dealer_hand.append(deck.pop())
                    IS_DECK_SHUFFLED -= 1
                    cards_on_table -= 1
                    time.sleep(2)

                player_total = calculate_hand_value(player_hand)
                dealer_total = calculate_hand_value(dealer_hand)
                if calculate_hand_value(dealer_hand) >= 17:
                    game_over = True
                    if dealer_total > 21 or player_total > dealer_total:
                        winner = "You Win!"
                        if player_total == 21:
                            BALANCE += bet * 2.5
                        else:
                            BALANCE += bet * 2
                        break
                    elif dealer_total == player_total:
                        winner = "It's a Tie!"
                        BALANCE += bet
                        break
                    else:
                        winner = "Dealer Wins!"
                        break

        clock.tick(40)
        await asyncio.sleep(0)

    pygame.quit()


async def game_loop():
    while True:
        result = await main()
        if result != "restart":
            break

if __name__ == "__main__":
    asyncio.run(game_loop())
