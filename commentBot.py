import threading
import time
import src.utils as utils
from src.generateAccounts import *
from src.helpers.logger import get_custom_logger
import os
from colorama import Fore, Style, init
import sys

# Initialize colorama (for Windows)
init(autoreset=True)
logger = get_custom_logger()

# Define a global token list to be used across functions
token_list = []

def comment_task(monitor_func, proxy_list, comments, bearers, pics=None):
    global token_list
    token_list = []
    index = 0
    pic = None
    
    while True:
        try:
            current_token = monitor_func()
            if current_token not in token_list:
                logger.debug(f"{current_token} | NEW TOKEN!")
                proxy = proxy_list[index % len(proxy_list)]
                bearer = bearers[index % len(bearers)]
                text = comments[index % len(comments)]
                kwargs = {'proxy': proxy}
        
                if pics:
                    pic = pics[index % len(pics)]
                    kwargs['picture_uri'] = pic

                token_list.append(current_token)
                thread = threading.Thread(target=utils.post_comment, args=(bearer, current_token, text), kwargs=kwargs)
                thread.start()
                index += 1
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            break

def comment_new(proxy_list, comments, bearers, pics=None):
    monitor_thread = threading.Thread(target=comment_task, args=(utils.monitor, proxy_list, comments, bearers, pics))
    monitor_thread.start()
    monitor_thread.join()

def comment_koh(proxy_list, comments, bearers, pics=None):
    monitor_thread = threading.Thread(target=comment_task, args=(utils.get_koh, proxy_list, comments, bearers, pics))
    monitor_thread.start()
    monitor_thread.join()

def comment_launch(proxy_list, comments, bearers, pics=None):
    pic = None
    mint_address = input("Enter mint address: ")
    index = 0
    
    for token in bearers:
        proxy = proxy_list[index % len(proxy_list)]
        bearer = bearers[index % len(bearers)]
        text = comments[index % len(comments)]
        kwargs = {'proxy': proxy}

        if pics:
            pic = pics[index % len(pics)]
            kwargs['picture_uri'] = pic

        utils.post_comment(bearer, mint_address, text, **kwargs)
        index += 1

def put_like_on_comment(bearers):
    counter = 0
    logger.warning("To run this module ALL liking accounts must have nicknames/pfp set! Otherwise likes won't be shown")
    comment_id = int(input('Input comment ID: '))
    for token in bearers:
        response = utils.put_like(comment_id, token)
        if response == 201:
            counter += 1
            logger.info(f"Successfully liked comment: {counter}")

def follow_address(bearers):
    counter = 0
    wallet_address = input("Enter wallet address to follow: ")
    for token in bearers:
        follow_response = utils.follow(wallet_address, token)
        if follow_response == 201:
            counter+=1
            logger.info(f"Successfully followed! | {counter}")
        else:
            logger.error(f"Error: {follow_response}")

def set_nicks_and_pfp():
    use_random = input("Use random nicknames? (y/n): ")
    tokens = utils.parse_generated()
    pics = utils.parse_pfp()
    nicknames = utils.parse_nicks()
    index = 0
    for _ in tokens:
        token = tokens[index % len(tokens)]
        pic = pics[index % len(pics)]
        nick = utils.get_random_username() if use_random == 'y' else nicknames[index % len(nicknames)]
        nick = nick[:10] if len(nick) > 10 else nick
        update_response = utils.update_profile(token, nick, pic)
        if update_response == True:
            logger.info(f"{index + 1} | Account updated!")
        else:
            logger.error(f"Error: {update_response}")
        index += 1

def main():
    while True:
        time.sleep(2)
        os.system('clear')
        proxy_list = utils.parse_proxies()
        comments = utils.parse_texts()
        bearers = utils.parse_bearer()
        print(Fore.RED+"""

 /$$$$$$$  /$$$$$$$$         /$$                         /$$          
| $$__  $$| $$_____/        | $$                        | $$          
| $$  \ $$| $$             /$$$$$$    /$$$$$$   /$$$$$$ | $$  /$$$$$$$
| $$$$$$$/| $$$$$         |_  $$_/   /$$__  $$ /$$__  $$| $$ /$$_____/
| $$____/ | $$__/           | $$    | $$  \ $$| $$  \ $$| $$|  $$$$$$ 
| $$      | $$              | $$ /$$| $$  | $$| $$  | $$| $$ \____  $$
| $$      | $$              |  $$$$/|  $$$$$$/|  $$$$$$/| $$ /$$$$$$$/
|__/      |__/               \___/   \______/  \______/ |__/|_______/ 
                                                        By: TG @SolScriptsDev 
        """)

        print("""                                              
Choose module:
1) Comment every new token
2) Comment every new KOH
3) Comment exact token
4) Generate accounts
5) Set nicknames and PFP
6) Put like on comment
7) Parse comment from token
8) Exit
        """)
        
        try:
            module = int(input("Choice: "))
        except ValueError:
            logger.error("Invalid input! Please enter a number.")
            continue
        
        pics = None
        if module in {1, 2, 3}:
            choice = input("Use pics from pics.txt? (y/n): ")
            if choice == 'y':
                pics = utils.parse_pics()

        if module == 1:
            comment_new(proxy_list, comments, bearers, pics)
        elif module == 2:
            comment_koh(proxy_list, comments, bearers, pics)
        elif module == 3:
            comment_launch(proxy_list, comments, bearers, pics)
        elif module == 4:
            gen_amount = int(input("How many accounts generate: "))
            call_main_with_delay(gen_amount)
            logger.info(f"Successfully generated {gen_amount} accounts!")
        elif module == 5:
            set_nicks_and_pfp()
        elif module == 6:
            put_like_on_comment(bearers)
        elif module == 7:
            logger.debug("COMMENT PARSER")
            token_address = input("Input token address to parse: ")
            utils.parse_replies(token_address)
            logger.info(f"Comments saved to parsed_comments/comments_{token_address}")
        elif module == 8:
            logger.info("Exiting the program.")
            break
        else:
            logger.critical("Invalid option!")

if __name__ == "__main__":
    main()
