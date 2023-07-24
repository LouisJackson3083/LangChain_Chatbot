import os, sys
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationTokenBufferMemory
from utils import clear_terminal, get_user_input, display_conversation
from termcolor import colored

class Chatbot():
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.verbose = False
        self.temperature = 0.0
        self.memory_options = ["ConversationalBufferMemory", "ConversationBufferWindowMemory", "ConversationTokenBufferMemory"]
        self.memory_current = self.memory_options[0]

        self.llm = ChatOpenAI(openai_api_key=api_key, temperature=0.0)
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm = self.llm,
            memory = self.memory,
            verbose = self.verbose
        )

    def change_settings(self):
        print(colored(f"What setting would you like to change?", "green") + colored(f"\n1. Verbosity: {self.verbose}\n2. Temperature: {self.temperature}\n3. Memory: {self.memory_current}", "yellow"))
        setting_choice = -1
        while (setting_choice < 0 or setting_choice > 3):
            try:
                setting_choice = int(input(colored(f"Enter the number of the setting: ","green")))
            except ValueError:
                print(colored(f"Invalid input", "red"))

        if (setting_choice == 1):
            self.change_verbose()
        elif (setting_choice == 2):
            self.change_temperature()
        elif (setting_choice == 3):
            self.change_memory()

    def change_verbose(self):
        self.verbose = not self.verbose
        self.conversation.verbose = self.verbose
        print(colored(f"Verbosity has been changed!", "yellow"))

    def change_temperature(self):
        new_temperature = -1
        while (new_temperature < 0 or new_temperature > 1):
            try:
                new_temperature = float(input(colored(f"Old temperature: {self.temperature} , Enter new temperature: ","green")))
            except ValueError:
                print(colored(f"Invalid input", "red"))
        self.temperature = new_temperature
        self.llm.temperature = self.temperature
        self.conversation.llm = self.llm
        print(colored(f"Temperature has been changed!", "yellow"))

    def change_memory(self):
        print(colored(f"The memory method the chatbot is currently using is: {self.memory_current}\nYour options are:", "green"))
        for index, memory_method in enumerate(self.memory_options):
            print(colored(str(index+1) + ". " + str(memory_method), "yellow"))
        memory_choice = -1
        while (memory_choice < 0 or memory_choice > 2):
            try:
                memory_choice = int(input(colored(f"Enter the number of the new memory: ","green")))
            except ValueError:
                print(colored(f"Invalid input", "red"))

        
        self.memory_current = self.memory_options[memory_choice-1]
        if memory_choice == 1:
            self.memory = ConversationBufferMemory()
        elif memory_choice == 2:
            k_choice = -1
            while (k_choice < 0):
                try:
                    k_choice = int(input(colored(f"Enter the k number for the window buffer (default is 5): ","green")))
                except ValueError:
                    print(colored(f"Invalid input", "red"))
            self.memory = ConversationBufferWindowMemory(k=k_choice)
        # elif memory_choice == 3:
        #     token_choice = -1
        #     while (token_choice < 0):
        #         try:
        #             token_choice = int(input(colored(f"Enter the max token limit for the memory (default is 30): ","green")))
        #         except ValueError:
        #             print(colored(f"Invalid input", "red"))
        #     self.memory = ConversationTokenBufferMemory(llm=self.llm, max_token_limit=token_choice)

        self.conversation = ConversationChain(
            llm = self.llm,
            memory = self.memory,
            verbose = self.verbose
        )


def main_chat_loop(chatbot):
    clear_terminal()

    user_input = get_user_input()
    while (user_input == "settings"):
        chatbot.change_settings()
        user_input = get_user_input()
        clear_terminal()

    while user_input != "exit":
        clear_terminal()
        print(colored("AI is thinking...", "green"))
        chatbot.conversation.predict(input=user_input)
        display_conversation(memory_buffer=chatbot.memory.buffer)
        user_input = get_user_input()
        while (user_input == "settings"):
            chatbot.change_settings()
            user_input = get_user_input()
            clear_terminal()

if __name__ == "__main__":
    api_key = str(sys.argv[1])
    chatbot = Chatbot(api_key=api_key)
    main_chat_loop(chatbot=chatbot)
