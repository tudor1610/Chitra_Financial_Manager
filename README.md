<small>Copyright Ariciu Toma, Brandibur Tudor, Iliescu Miruna-Elena, Stanciulescu Ana 322CA, 2024-2025</small>
<br>
<small>Github link: https://github.com/tudor1610/Chitra_Financial_Manager </small>

# Chitra Financial Manager

## Introduction
Chitra is a comprehensive financial management application designed to help users track their income, expenses, and investments. It combines a user friendly financial tracking system which lets users track their income and expenses, having detailed charts and easy to use features. Moreover, it provides users possibilities to invest, ensuring fun and totally legal ways to manage and grow their funds.

### Features
___
#### 1. Core Financial Management
Transaction Management:
  - Log income and expenses with details like date, amount, and merchant.
  - Since it's not a banking application, Chitra relies on the user to properly log in the transactions. 
  - Even so, there are multiple fields available for completion, which offer the user a detailed overview of their activity.

Balance Tracking:
- Real-time updates of user balance, integrated with a backend server.
- All budget modifications are made on-the-spot in the databases, including in the user.balance, selected account.balance and transaction.amount.
- Depending on the transaction type, some changes are more precise.
- The home page even gives the user a more detailed insight into their spending habits, by showcasing the amount of money spent in the last month.

Analytics:
- Graphical representation of income and expenses for better financial insights.
- Going through the transactions' database, the graphs are made so that no variation in the budget is missed. 
- There are also multiple time-period options the user can choose from, so that the graphs can be as detailed as desired.
___
#### 2. Investing Made Fun with Chitra
Here at Chitra, we believe in empowering our customers with full control over their wealth while ensuring they have fun along the way. That's why we've provided the most exhilarating way to grow your savings: *GAMBLING!*

Who needs a traditional college savings account when you can experience the thrill of turning your fortunes around? Let's have fun and explore the infinite possibilities of making more money than you could ever imagine. With our two wonderfully designed games—Dice Royale and the timeless classic, Blackjack—the journey to financial growth has never been more entertaining. Rest assured, these games are definitely not adjusted in favor of the house. 😉

**Our Games**
##### 1.*Dice Royale*
Take your chance in this fast-paced and exciting dice game! Dice Royale is all about quick decisions and big payouts:

- **How it Works**: Place your bets and roll the dice. Your winnings are determined by the dice combinations.
- **Why You’ll Love It**: The thrill of rolling doubles, triples, or hitting the jackpot keeps every moment unpredictable and rewarding.
- **A Word of Advice**: Double down, triple up, or risk it all—the choice is yours. But remember, **fortune favors the bold!**

##### 2.*Blackjack*
The classic card game you know and love, Blackjack is your ticket to endless excitement:

- **How it Works**: Bet against the dealer, draw cards ("Hit"), or hold your total ("Stand") to see if you can get closer to 21 than the dealer without going over.
- **Why You’ll Love It**: With dynamic gameplay and strategic decisions, every round is a battle of wits and luck.
- **A Word of Advice**: Aim for 21, but don’t bust! And if the dealer’s on a hot streak, maybe try Dice Royale instead. 😉

_____________________
#### 3.Secure Backend Server
The Flask-written server handles all operations, from the moment you log in or create your first account.

User Authentication:
- Secure login and session management, using a SQLAlchemy database
- Account creation possibility
- Keeps the transactions and balance between sessions

API integration
- (Almost) Seamless communication between the frontend (Pygame) and the backend (Flask).

Transaction Logging:
- All game transactions (wins/losses) are logged as part of the user’s financial data.

___
#### 4. Design
Main Features:
- Root page:
  - the entry point in our website;
  - new users can create an account, while loyal users can choose between logging into their existing one or simply creating another;
- Login page
- Create account page
- Home page:
  - first official page;
  - it has two sections:
    1. the latest spending habits are showed and broke down into important categories: Living and Food expenses;
    2. short peek into the budget evolution of the first three accounts the user has;
- Portfolio page:
  - for all curious users who want to have a clear evidence of all their transactions;
  - it has two sections:
    1. a log of all the transactions with comprehensive details;
    2. a customizable graph that shows the budget evolution over time;
- Transaction page:
  - the place where new transactions are made 😉;
  - indulge in a light reading on the latest top 5 articles on the topic of "bussiness". Who wouldn't want to know all about the money flow?
  - it has three useful sections:
    1. short overview on the general budget;
    2. the form for logging a new transaction;
    3. the reading corner with a list of 5 articles;
- Invest page:
  - games, it's all about games... and maybe a little luck;
  - there are also some great investing tips that our customers can access;
- User page:
  - the place where all account and card information is stored;
  - create accounts, add cards, even delete information... everything is made possible for our lovely users;

___
### Technologies used
- Frontend:
  - <strong>HTML, CSS</strong> for styling;
  - <strong>Font Awesome icons</strong> for visual elements like the piggy bank and food utensils;
- Backend:
  - <strong>Flask</strong> for handling routing and server-side logic;
  - <strong>SQLAlchemy</strong> for managing the database and fetching financial data;
  - <strong>Matplotlib</strong> for chart generation;
  - <strong>Pygame</strong> as main game development library;
  - <strong>HTTP/REST</strong> for server communication through the *requets* library;
  - <strong>News API</strong> integration for financial and business recommendations;
 
___
### Instructions
- First time, try running the code by writing: ```python3 server.py``` in the Chitra_Financial_Manager/ directory;
- If that way fails, write:
```
  sudo apt install python3-virtualenv

  virtualenv -p python3 venv_name

  source venv_name/bin/activate

  python3 server.py
```
- If there are still errors, install the suggested dependencies;
- If you want to easily play the games available in the Invest page, make sure the server is running and then:
  - for Diceroyal: write ```python3 diceroyal.py``` in the Chitra_financial_Manager/ directory;
  - for Blackjack: write ```python3 main.py``` in the Chitra_Financial_Manager/blackjack/ directory;
 
___
### Workload
- Ariciu Toma: developed the entire logic of making and tracking transactions, which also required making the Portfolio and Transaction pages;
- Brandibur Tudor: devised the initial logic of the server, the first rough design of the website and made the Blackjack game;
- Iliescu Miruna: made the Diceroyal game and was the first to figure out how to create a connection between the server and the games and how to add downloadable execs in the Invest Page;
- Stanciulescu Ana: designed the website so that the user could benefit from a consistent page aspect, which also implied coding the logic of the Home and User pages;

___
### Dificulties
- This project was challenging from start to finish:
  1. It was the first project where we had to also make the frontend. Only Ana Stanciulescu and Tudor Brandibur had some small knowledge on designing websites with HTML from past optional courses. They managed in the end to make the website look pretty through a lot of trial-and-error.
  2. Nobody knew anything about making games. But Miruna Iliescu and Tudor Brandibur took on the challenge. The game logic wasn't as hard to write as making the games communicate with the server. After trying multiple methods of getting the user's balance from the database, the problem was resolved through sending requests to the server by referencing some methods inside it.
  3. Since there were a lot of things to be done in order to finish the project, we ended up simultaneously modifying the server.py, each person on their own branch. This led to multiple conflicts when trying to open a pull request. Some were fixed and merged, others not.
  4. There were also some issues with the databases, but Toma Ariciu fixed them by creating multiple database models with enough fields inside to gain a comprehensive profile on each user.
___
### Conclusion
Chitra Financial Manager is more than just an app—it’s a fun and engaging way to take control of your finances. Whether you’re logging your daily expenses or trying your luck with Dice Royale and Blackjack, Chitra ensures every user has an enjoyable and empowering experience. 

With secure transaction handling, real-time balance tracking, and exciting investment opportunities, Chitra provides everything you need to manage and grow your wealth.

So why wait? Start your journey to financial mastery and endless entertainment with Chitra today. Who knows—your next big win could be just around the corner!
