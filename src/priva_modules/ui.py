from ensurepip import bootstrap
from colorama import Fore, Style
from priva_modules.chord_node import ChordNode

class UI():
    def init_ui(priva_node: ChordNode):
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
        priva_node.set_node_name(username)
        if username != 'boot0':
            print('\nJoining the network...')
            result = priva_node.join()
            if result == 'Failed to join the network':
                print(f'\n{Fore.RED}Failed to join the network. Please try again later.{Style.RESET_ALL}\n')
                return 'exited'
            else:
                print(f'\n{result}\n')
        tag = f'{priva_node.user_id}'
        print(f'\nYour tag is {Fore.GREEN}{tag}{Style.RESET_ALL}.')
        print(f'Start messaging with a peer by using their tag: {Fore.BLUE}connect {Fore.GREEN}username#1234{Style.RESET_ALL}.')

        print(f'\nType {Fore.BLUE}help{Style.RESET_ALL} to see available commands.\n')

        # todo: add all available commands
        help_prompt = f"""
        Usage: [command] [args]
        =======================
        Available commands:

        {Fore.BLUE}connect username#1234{Style.RESET_ALL} - Start messaging with the peer username#1234.

        {Fore.BLUE}list{Style.RESET_ALL} - Show your contacts list.

        {Fore.BLUE}tag{Style.RESET_ALL} - Show your own tag.

        {Fore.BLUE}exit{Style.RESET_ALL} - Reset the tor configuration & close the application.

        =======================
        """

        # command prompt
        while True:
            command = input('priva> ')
            if command == 'help' or not command:
                print(help_prompt)
            if command == 'list':
                print('\nContacts list:')
                print('===============\n')
                f = open('.contacts_list.txt', 'r')
                contacts = f.readlines()
                for c in contacts:
                    print(f'{Fore.GREEN}{c}{Style.RESET_ALL}')
                print('===============')
                continue
            if command == 'tag':
                print(f'\n{Fore.GREEN}{tag}{Style.RESET_ALL}\n')
            # handle command args
            elif command == 'node_info':
                priva_node.node_info()
            elif command == 'node_test':
                priva_node.node_test()
            elif len(command.split(' ')) > 1:
                # handle malformed commands
                try:
                    body = command.split(' ')[0]
                    args = command.split(' ')[1]
                    if body == 'connect' and '#' in args:
                        print(f'\nConnecting...')
                        # todo: establish a connection with the peer
                        print(f'{Fore.GREEN}Connected to {args}.{Style.RESET_ALL}\n')
                        print(f'Type {Fore.BLUE}back{Style.RESET_ALL} to exit the chat.\n')
                        # todo: logic for connection successful or not 
                        connection_successful = True
                        if (connection_successful):
                            # save the contact
                            f = open('.contacts_list.txt', 'a')
                            f.write(f'{args}\n')
                            f.close()
                            while True:
                                # show user_id of the peer so that the user knows who they are messaging with atm
                                msg = input(f'priva({Fore.GREEN}{args}{Style.RESET_ALL})> ')
                                if msg == 'back':
                                    break
                        else:
                            # todo: handle conection not successful
                            print(f'{Fore.Red}Connection failed.{Style.RESET_ALL}\n')
                            print(f'{Fore.GREEN}{args}{Style.RESET_ALL} might not be online.\n')
                    else:
                        print(help_prompt)
                        continue
                except:
                    print(help_prompt)
                    continue
            elif command == 'exit':
                print('Exiting gracefully...')
                # todo: inform the network about leaving
                break
            else:
                print(help_prompt)
        return 'exited'
