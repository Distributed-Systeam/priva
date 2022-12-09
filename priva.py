from colorama import Fore, Style

# print the banner
print("""
            _            
           (_)           
 _ __  _ __ ___   ____ _ 
| '_ \| '__| \ \ / / _` |
| |_) | |  | |\ V / (_| |
| .__/|_|  |_| \_/ \__,_|
| |                      
|_|                      

– Decentralised P2P chat
""")

# username selection
while True:
    username = input('Select a username:\n')
    if not username:
        print(f'{Fore.RED}\nUsername cannot be empty.{Style.RESET_ALL}\n')
    elif len(username) > 25:
        print(f'{Fore.RED}\nUsername cannot be more than 25 characters long.{Style.RESET_ALL}\n')
    elif '#' in username:
        print(f'{Fore.RED}\nThe character # cannot be used.{Style.RESET_ALL}\n')
    elif ' ' in username:
        print(f'{Fore.RED}\nUsername must be one word.{Style.RESET_ALL}\n')
    else:
        break

# todo: call user_id generation
tag = f'{username}#1234'
print(f'\nYour tag is {Fore.GREEN}{tag}{Style.RESET_ALL}.')
print(f'Start messaging with a peer by using their tag: {Fore.BLUE}connect {Fore.GREEN}username#1234{Style.RESET_ALL}.')

print(f'\nType {Fore.BLUE}help{Style.RESET_ALL} to see available commands.\n')

# todo: add all available commands
help_prompt = f"""
Usage: [command] [args]
=======================
Available commands:

{Fore.BLUE}connect username#1234{Style.RESET_ALL} || Start messaging with the peer username#1234.

{Fore.BLUE}list{Style.RESET_ALL} || List your active sessions with peers.

{Fore.BLUE}exit{Style.RESET_ALL} || Close the application and remove your identity from the network.

=======================
"""

# command prompt
while True:
    command = input('priva> ')
    if command == 'help' or not command:
        print(help_prompt)
    if command == 'list' or not command:
        print('Active sessions:')
        # todo: list inbound and outbound nodes
    # handle command args
    elif len(command.split(' ')) > 1:
        # handle malformed commands
        try:
            body = command.split(' ')[0]
            args = command.split(' ')[1]
            if body == 'connect' and '#' in args:
                print(f'\nConnecting to {args}...')
                # todo: establish a connection with the peer
                # todo: handle conection not successful
            else:
                print(help_prompt)
        except:
            print(help_prompt)
    elif command == 'exit':
        print('\nExiting gracefully...')
        # todo: inform the network about leaving
        break
    else:
        print(help_prompt)
