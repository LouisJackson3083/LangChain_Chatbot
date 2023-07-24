from os import system, name
from termcolor import colored

def clear_terminal():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def get_user_input():
    print(colored("Type 'exit' to quit or 'settings' to change the parameters of the chatbot...", "green"))
    while True:
        try:
            user_input = str(input(colored("Enter query: ","green")))
            return user_input
        except ValueError:
            print(colored("Sorry, something went wrong with your input","red"))
            continue

def display_conversation(memory_buffer):
    final_memory_buffer = ""
    for index, line in enumerate(memory_buffer.split('\n')):
        if (index % 2 == 0):
            final_memory_buffer += colored("You: ","light_yellow") + colored(line[7:],"yellow") + "\n"
        else:
            final_memory_buffer += colored(line[:3],"light_cyan") + colored(line[3:],"cyan") + "\n"
    print(final_memory_buffer)
