# Simple pygame program

# https://realpython.com/pygame-a-primer/

import pygame
import random
import time
import requests
import sys
import requests
from datetime import date

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_KP_ENTER,
    K_RETURN,
    K_SPACE,
    K_0,
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_6,
    K_7,
    K_8,
    K_9,
    K_d
)

pygame.mixer.init()
pygame.init()
clock = pygame.time.Clock()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
DICE_SIZE = 180
DICE_HALF_SIZE = DICE_SIZE/2
FONT_SIZE_TITLE = 50
FONT_SIZE_CAPTION = 22

# Set up the drawing window
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption('Dice Royal')


running = True

bet = 0
balance = 1000
dice_black = 6
dice_white = 6
dice_white_color = (185,235,235)
dice_black_color = (20,0,40)
slug = 'Good Luck!'

# Read user data
with open("diceroyal.txt", "r") as file:
    lines = file.readlines()

# Initialize variables
username = None
password = None
balance = None

url_connect='http://localhost:5000/login/games'

for line in lines:
    if line.startswith("username:"):
        username = line.split(":", 1)[1].strip()
    elif line.startswith("password:"):
        password = line.split(":", 1)[1].strip()

# # get_balance()

font1 = pygame.font.SysFont('freesanbold.ttf', FONT_SIZE_TITLE)
font2 = pygame.font.SysFont('freesanbold.ttf', FONT_SIZE_CAPTION)

textCaption = font2.render('[1-9] Bet [0] Cancel Bet [SPACE] Double Bet [ARROWS] Increase/Decrease Bet [ENTER] Play [D] Deposit 1000', True, dice_black_color)
textRect_caption = textCaption.get_rect()
textRect_caption.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-10)

textPlayer = font1.render(username, True, dice_white_color)
textRect_player = textPlayer.get_rect()
textRect_player.center = (DICE_SIZE+FONT_SIZE_TITLE, FONT_SIZE_TITLE)

def connect():
    payload = {
        "username": username,
        "password": password
        }

    # Optionally, define headers (if needed)
    headers = {
         "Content-Type": "application/x-www-form-urlencoded",  # For form data
         "User-Agent": "Python-requests/2.x"
         }
    # Send the POST request
    response = requests.post(url_connect, data=payload)
    print(response.status_code, response.text)
    # Check the response
    return response.text

def get_balance():
    global balance
    
    # Send a request to the server
    response = requests.post('http://localhost:5000/game/balance', data={"username": username})
    
    if response.status_code == 200:
        try:
            # Parse the JSON response
            data = response.json()
            # Update the balance variable if the answer contains the value
            balance = data.get("balance", 0)
            print("Balance actualizat:", balance)
        except ValueError:
            print("Eroare la parsarea raspunsului JSON:", response.text)
    else:
        print("Eroare la cererea GET balance:", response.status_code, response.text)

    return balance

def update_balance(new_balance):
    global balance
    
    # Payload-ul cererii
    payload = {
        "username": username,
        "balance": new_balance
    }

    headers = {
         "Content-Type": "application/json",
         "User-Agent": "Python-requests/2.x"
    }

    # Send a request to the server
    response = requests.post('http://localhost:5000/game/updatebalance', json=payload, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            balance = data.get("balance", balance)
            print("Balance actualizat cu succes:", balance)
        except ValueError:
            print("Eroare la parsarea răspunsului JSON:", response.text)
    else:
        print(f"Eroare la actualizarea balance-ului: {response.status_code}, {response.text}")

def bet_transaction(amount, merchant, transaction_type):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Python-requests/2.x"
    }
    
    # Datele tranzacției
    transaction_data = {
        "transaction_type": transaction_type,
        "date": str(date.today()),
        "amount": amount,
        "merchant": merchant
    }

    # Trimiterea cererii POST
    response = requests.post("http://localhost:5000/newdeposit", json=transaction_data, headers=headers)

    if response.status_code == 200:
        print("Deposit successful!")
    else:
        print(f"Error during deposit: {response.status_code}, {response.text}")



def show_dice(dice,color):
    if color == 'black':
        rect = dice.get_rect()
        screen.blit(dice, (SCREEN_WIDTH - DICE_SIZE - DICE_HALF_SIZE, SCREEN_HEIGHT/2- DICE_HALF_SIZE))
    if color == 'white':
        rect = dice.get_rect()
        screen.blit(dice, (DICE_HALF_SIZE, SCREEN_HEIGHT/2- DICE_HALF_SIZE))
    return

def draw_dice(n,color):
    dice_surface = pygame.Surface((160, 160))
    if color == 'white':
        dice_color = dice_white_color
        circle_color = dice_black_color
    if color == 'black':
        dice_color = dice_black_color
        circle_color = dice_white_color
    dice_surface.fill(dice_color)
    if n in (1,3,5):
       pygame.draw.circle(dice_surface, circle_color, (80, 80), 10)
       if n == 1:
           show_dice(dice_surface,color)
           return
    if n in (1,3,5):
       pygame.draw.circle(dice_surface, circle_color, (30, 30), 10)
       pygame.draw.circle(dice_surface, circle_color, (130, 130), 10)
       if n == 3:
           show_dice(dice_surface,color)
           return
    if n in (1,3,5):
       pygame.draw.circle(dice_surface, circle_color, (130, 30), 10)
       pygame.draw.circle(dice_surface, circle_color, (30, 130), 10)
       show_dice(dice_surface,color)
       return
    if n in (2,4,6):
       pygame.draw.circle(dice_surface, circle_color, (30, 30), 10)
       pygame.draw.circle(dice_surface, circle_color, (130, 130), 10)
       if n == 2:
           show_dice(dice_surface,color)
           return
    if n in (2,4,6):
       pygame.draw.circle(dice_surface, circle_color, (130, 30), 10)
       pygame.draw.circle(dice_surface, circle_color, (30, 130), 10)
       if n == 4:
           show_dice(dice_surface,color)
           return
    if n in (2,4,6):
       pygame.draw.circle(dice_surface, circle_color, (130, 80), 10)
       pygame.draw.circle(dice_surface, circle_color, (30, 80), 10)
       show_dice(dice_surface,color)
       return   
    return

if connect() == '-1':
    pygame.quit()
    sys.exit("Failed to connect to the server.")

# Run until the user asks to quit

balance = get_balance()
print("Balance este acum:", balance)

while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == KEYDOWN:
                        
            if event.key == K_ESCAPE:
                running = False
            # Deposit 1000 into your account   
            if event.key == K_d:
                balance = balance + 1000
                bet_transaction(1000, "Game deposit", "Income")
            # Play
            if event.key == K_RETURN:
                if bet == 0:
                    slug = 'Place your bet!'
                    if balance == 0:
                        slug = 'Game Over!'
                else:
                    pygame.mixer.music.load("diceroyal.mp3")
                    pygame.mixer.music.play(loops=1)
                    dice_black = random.randint(1, 6)
                    dice_white = random.randint(1, 6)
                    #while pygame.mixer.music.get_busy():
                       #time.sleep(0.1)
                    while pygame.mixer.music.get_busy():
                       time.sleep(0.2)
                       draw_dice(random.randint(1, 6),'black')
                       draw_dice(random.randint(1, 6),'white')                   
                       pygame.display.flip()
                    if dice_black > 6:
                       dice_black = 1
                    if dice_white > 6:
                       dice_white = 1
                    if dice_white == dice_black:
                       slug = 'DRAW'
                       bet = 0
                    if dice_white < dice_black:
                       pygame.mixer.music.load("diceroyallose.mp3")
                       pygame.mixer.music.play(loops=1)	
                       slug = 'LOSER'
                       balance = balance - bet
                       bet_transaction(bet, "Lost bet", "Expense")
                       bet = 0
                       if balance <= 0:
                           bet = 0
                           balance = 0
                           slug = 'Game Over!'
                    if dice_white > dice_black:
                       pygame.mixer.music.load("diceroyalwin.mp3")
                       pygame.mixer.music.play(loops=1)
                       slug = 'WINNER'
                       balance = balance + bet
                       bet_transaction(bet, "Bet won", "Income")
                       bet = 0
                    update_balance(balance)
            if event.key == K_UP:
                bet = bet + 1
                if bet > balance:
                    bet = balance
            if event.key == K_DOWN:
                bet = bet - 1
                if bet < 0:
                    bet = 0
            if event.key == K_RIGHT:
                bet = bet + 5
                if bet > balance:
                    bet = balance  
            if event.key == K_LEFT:
                bet = bet - 5
                if bet < 0:
                    bet = 0
            # Double your bet
            if event.key == K_SPACE:
                bet = bet * 2
                if bet > balance:
                    bet = balance  
            if event.type == pygame.QUIT:
                running = False
            # Place a bet
            if event.key == K_0:
                bet = 0
            if event.key == K_1:
                if balance > 0:
                   bet = 1
            if event.key == K_2:
                if balance > 1:
                   bet = 2
            if event.key == K_3:
                if balance > 2:
                   bet = 3
            if event.key == K_4:
                if balance > 3:
                   bet = 4
            if event.key == K_5:
                if balance > 4:
                   bet = 5
            if event.key == K_6:
                if balance > 9:
                   bet = 10
            if event.key == K_7:
                if balance > 19:
                   bet = 20
            if event.key == K_8:
                if balance > 49:
                   bet = 50
            if event.key == K_9:
                if balance > 99:
                   bet = 100
        
    # Fill the background with white
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, dice_white_color, (0,SCREEN_HEIGHT-FONT_SIZE_CAPTION,SCREEN_WIDTH,SCREEN_HEIGHT))
    surf = pygame.Surface((DICE_SIZE, DICE_SIZE))
    surf = pygame.image.load("diceroyal.jpeg").convert()
    rect = surf.get_rect()
    screen.blit(surf, (0, 0))
    
    screen.blit(textCaption, textRect_caption)
    screen.blit(textPlayer, textRect_player)
    

    #pygame.draw.circle(screen, (255, 255, 255), (SCREEN_WIDTH/2, SCREEN_HEIGHT/2), CIRCLE1_RADIUS-2)
    
    textBet = font1.render(str(bet), True, dice_white_color)
    textRect_bet = textBet.get_rect()
    textRect_bet.center = (SCREEN_WIDTH/2, DICE_SIZE)
    screen.blit(textBet, textRect_bet)
    
    textBalance = font1.render(str(balance), True, dice_white_color)
    textRect_balance = textBalance.get_rect()
    textRect_balance.center = (SCREEN_WIDTH - DICE_HALF_SIZE, FONT_SIZE_TITLE)
    screen.blit(textBalance, textRect_balance)

    draw_dice(dice_black,'black')
    draw_dice(dice_white,'white')
    
    textSlug = font1.render(slug, True, dice_black_color)
    textRect_slug = textSlug.get_rect()
    textRect_slug.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2+DICE_HALF_SIZE)
    screen.blit(textSlug, textRect_slug)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
