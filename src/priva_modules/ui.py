from colorama import Fore, Style
from priva_modules.chord_node import ChordNode
from priva_modules import services
from os.path import exists

# tor proxies
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

class UI():
    def __init__(self, priva_node: ChordNode):
        self.priva_node = priva_node

    def init_ui(self):
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
        self.priva_node.set_node_name(username)
        if 'boot0#' not in self.priva_node.user_id:
            print('\nJoining the network...')
        result = self.priva_node.join()
        if result == 'Failed to join the network.':
            print(f'\n{Fore.RED}Failed to join the network. Please try again later.{Style.RESET_ALL}\n')
            return 'exited'
        # join successful
        else:
            print(f'{Fore.GREEN}{result}{Style.RESET_ALL}')
        tag = f'{self.priva_node.user_id}'
        print(f'\nYour tag is {Fore.GREEN}{tag}{Style.RESET_ALL}.')
        print(f'Start messaging with a peer by using their tag: {Fore.BLUE}connect {Fore.GREEN}username#1234{Style.RESET_ALL}.')

        print(f'\nType {Fore.BLUE}help{Style.RESET_ALL} to see available commands.\n')
        self.priva_node.start_stabilize_timer()
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
                self.priva_node.node_info()
            elif len(command.split(' ')) > 1:
                # handle malformed commands
                try:
                    body = command.split(' ')[0]
                    args = command.split(' ')[1]
                    if body == 'connect' and '#' in args:
                        print(f'\nConnecting...')
                        # todo: establish a connection with the peer
                        # todo: logic for connection successful or not
                        connection_successful = self.priva_node.send_connect(args)
                        if (connection_successful):
                            # save the contact
                            print(f'{Fore.GREEN}Connected to {args}{Style.RESET_ALL}\n')
                            print(f'\nType {Fore.BLUE}back{Style.RESET_ALL} to exit the chat.\n')
                            file_exists = exists('.contacts_list.txt')
                            if file_exists:
                                cl = open('.contacts_list.txt', 'r')
                                contacts = cl.readlines()
                                if args not in contacts:
                                    f = open('.contacts_list.txt', 'a')
                                    f.write(f'{args}\n')
                                    f.close()
                            else:
                                f = open('.contacts_list.txt', 'a')
                                f.write(f'{args}\n')
                                f.close()
                            # print message history with the peer
                            msg_history = self.priva_node.get_msg_history()
                            if msg_history != None:
                                for m in msg_history:
                                    print(m)
                            while self.priva_node.current_msg_peer:
                                # show user_id of the peer so that the user knows who they are messaging with atm
                                msg = input('')
                                if msg == 'back':
                                    self.priva_node.current_msg_peer = None
                                    break
                                # onion_addr = priva_node.msg_conn(args)
                                res = services.send_message(self.priva_node.current_msg_peer.onion_addr, tag, msg)
                                # save sent message to msg_history
                                if res == 'message received':
                                    self.priva_node.receive_msg(tag, msg)
                                    msg_history = self.priva_node.get_msg_history()
                        else:
                            # todo: handle conection not successful
                            print(f'{Fore.RED}Connection failed.{Style.RESET_ALL}\n')
                            print(f'{Fore.GREEN}{args}{Style.RESET_ALL} might not be online.\n')
                    else:
                        print(help_prompt)
                        continue
                except Exception as e:
                    print(f'{Fore.RED}Error: {e}{Style.RESET_ALL}\n')
                    continue
            elif command == 'exit':
                print('Exiting gracefully...')
                # todo: inform the network about leaving
                break
            else:
                print(help_prompt)
        return 'exited'
