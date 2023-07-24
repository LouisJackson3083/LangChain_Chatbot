import os, sys
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from utils import clear_terminal, get_user_input, display_conversation
from termcolor import colored

class Chatbot():
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.verbose = False
        self.temperature = 0.0
        self.memory_name = "ConversationalBufferMemory"
        self.memory_options = {
            "ConversationalBufferMemory": ConversationBufferMemory(),
            "ConversationBufferWindowMemory": ConversationBufferWindowMemory()
        }

        self.llm = ChatOpenAI(openai_api_key=api_key, temperature=0.0)
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm = self.llm,
            memory = self.memory,
            verbose = self.verbose
        )

    def change_verbose(self):
        self.verbose = not self.verbose
        self.conversation.verbose = self.verbose

    def change_temperature(self):
        new_temperature = -1
        while (new_temperature < 0 or new_temperature > 1):
            new_temperature = float(input(colored(f"Old temperature: {self.temperature} , Enter new temperature: ","green")))
        self.temperature = new_temperature
        self.llm.temperature = self.temperature
        self.conversation.llm = self.llm

    def change_memory(self):
        print(colored(f"The memory method the chatbot is currently using is: {self.memory_name}\nYour options are:", "green"))
        for index, memory_method in enumerate(self.memory_options):
            print(colored(str(index+1) + ". " + str(memory_method), "yellow"))
        memory_choice = -1
        while (memory_choice < 0 or memory_choice > 2):
            memory_choice = int(input(colored(f"Enter the number of the new memory: ","green")))

        self.memory = self.memory_options.get(memory_choice-1)
        print(self.memory_options.get(memory_choice-1))
        if memory_choice == 2:
            k_choice = -1
            while (k_choice < 0):
                k_choice = int(input(colored(f"Enter the k number for the window buffer: ","green")))
            self.memory.k = k_choice

        self.conversation.memory = self.memory


def main_chat_loop(chatbot):
    clear_terminal()

    chatbot.change_memory()
    user_input = get_user_input()
    while user_input != "exit":
        clear_terminal()
        print(colored("AI is thinking...", "green"))
        chatbot.conversation.predict(input=user_input)
        display_conversation(memory_buffer=chatbot.memory.buffer)
        user_input = get_user_input()
        # if (user_input == "settings"):
        #     change_

if __name__ == "__main__":
    api_key = str(sys.argv[1])
    chatbot = Chatbot(api_key=api_key)
    main_chat_loop(chatbot=chatbot)
