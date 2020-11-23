# finance
A website via which users can “buy” and “sell” stocks by querying [IEX](https://iexcloud.io/) for stocks’ prices. (For this solution I used python Flask for the backend and Jinja as well as HTML, CSS and Bootstrap for frontend)
Anyone wishing to test out the solution can register or login with a test user: <br/>
- _username_: test_user<br/>
- _password_: testingfinance <br/>


### Main page
After registering and/or logging in the user enters the main page. There the user can see a summary of all the transactions he has done<br/>
![alt text](https://github.com/agnija-bako/finance/blob/main/docs/index.png?raw=true)

### Buy shares
The user can buy shares by entering a symbol - such as NFLX for netflix shares - find all shares [here](https://iextrading.com/trading/eligible-symbols/) - and the number of shares they wish to purchase (every user by default gets $10 000 to spend)
![alt text](https://github.com/agnija-bako/finance/blob/main/docs/buy.png?raw=true)

### Sell shares
The user can also sell their existing shares, by choosing a symbol and entering the number of shares they want to sell
![alt text](https://github.com/agnija-bako/finance/blob/main/docs/sell.png?raw=true)

### History
The user can also see a history of every transaction they have done
![alt text](https://github.com/agnija-bako/finance/blob/main/docs/history.png?raw=true)

### Other features
- The user can add money to their account
- The user  is also able to look up a stock’s current price
