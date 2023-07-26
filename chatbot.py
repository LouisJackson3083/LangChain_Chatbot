import os, openai, sys
import panel as pn
import param
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain, ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.prompts import ChatPromptTemplate


def load_db(file, chain_type, k):
    # load documents
    loader = PyPDFLoader(file)
    documents = loader.load()
    # split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    # define embedding
    embeddings = OpenAIEmbeddings()
    # create vector database from data
    db = DocArrayInMemorySearch.from_documents(docs, embeddings)
    # define retriever
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": k})
    # create a ChatBot chain. Memory is managed externally.
    qa = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0), 
        chain_type=chain_type, 
        retriever=retriever, 
        return_source_documents=True,
        return_generated_question=True,
    )
    return qa 


class ChatBot():
    def __init__(self):
        self.loaded_file = None
        self.qa = None
        self.panels = []
        self.chat_history = []
        self.llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.memory = ConversationBufferMemory()
        self.conversation_chain = ConversationChain(
            llm = self.llm,
            memory = self.memory,
            verbose = False
        )
        self.translator_segmenter = LLMChain(llm=self.llm, prompt=prompt_segment)
        self.translator_translate = LLMChain(llm=self.llm, prompt=prompt_translate)

    def call_load_db(self, count):
        if count == 0 or file_input.value is None:  # init or no file specified :
            return pn.pane.Markdown(f"Loaded File: {self.loaded_file}")
        else:
            file_input.save("temp.pdf")  # local copy
            self.loaded_file = file_input.filename
            button_load.button_style="outline"
            self.qa = load_db("temp.pdf", "stuff", 4)
            button_load.button_style="solid"
        self.clr_history()
        return pn.pane.Markdown(f"Loaded File: {self.loaded_file}")

    def conversation(self, query):
        if not query: # if there are no queries
            return pn.WidgetBox(pn.Row('User:', pn.pane.Markdown("", width=600)), scroll=True)
        result = self.conversation_chain.predict(input=query) # if we have a query get a response from the ChatBot
        self.chat_history.append([(query, result)]) # add it to the chat_history
        self.panels.extend([ # display it
            pn.Row('User:', pn.pane.Markdown(query, width=600, styles={'background-color': '#FFFFDD'})),
            pn.Row('ChatBot:', pn.pane.Markdown(result, width=600, styles={'background-color': '#DDFFDD'}))
        ])
        panel_conversation_input.value = ''  # clears loading indicator when cleared
        return pn.WidgetBox(*self.panels, scroll=True)
    
    def data_conversation(self, query):
        if not query:
            return pn.WidgetBox(pn.Row('User:', pn.pane.Markdown("", width=600)), scroll=True)
        # Call our qa on the loaded document
        result = self.qa({"question": query, "chat_history": self.chat_history})
        # append the results to the chat history
        self.chat_history.append([(query, result["answer"])])
        self.db_query = result["generated_question"]
        self.db_response = result["source_documents"]
        self.answer = result['answer'] 
        self.panels.extend([ # display it
            pn.Row('User:', pn.pane.Markdown(query, width=600, styles={'background-color': '#FFFFDD'})),
            pn.Row('ChatBot:', pn.pane.Markdown(result, width=600, styles={'background-color': '#DDFFDD'}))
        ])
        panel_data_conversation_input.value = ''  #clears loading indicator when cleared
        return pn.WidgetBox(*self.panels,scroll=True)
    
    def translator(self, query):
        if not query: # if there are no queries
            return pn.WidgetBox(pn.Row('User:', pn.pane.Markdown("", width=600)), scroll=True)
        result_segment = self.translator_segmenter({'text':query})['text']
        result_translate = self.translator_translate({'text':query})['text']
        self.panels.extend([ # display it
            pn.Row('User:', pn.pane.Markdown(query, width=600, styles={'background-color': '#FFFFDD'})),
            pn.Row('AI Translation:', pn.pane.Markdown(result_translate, width=600, styles={'background-color': '#DDFFDD'})),
            pn.Row('AI Segmentation:', pn.pane.Markdown(result_segment, width=600, styles={'background-color': '#DDFFDD'}))
        ])
        panel_translator_input.value = ''  # clears loading indicator when cleared
        return pn.WidgetBox(*self.panels, scroll=True)

    def clr_history(self,count=0):
        self.chat_history = []
        return 

# Load in the open api key as an environment variable
os.environ['OPENAI_API_KEY'] = str(sys.argv[1])
openai.api_key = os.environ['OPENAI_API_KEY']

# prompt_segment = ChatPromptTemplate.from_template(
#     """
#     For each identified languages in this text: {text}
#     please return the segmented texts that are of that language in this format:
#     '<language_1>: <text_1> \n
#     <language_1>: <text_2> \n
#     <language_n>: <text_n> \n'
#     """
# )

prompt_segment = ChatPromptTemplate.from_template(
    """
    ## Instruction ##
    Identify each language in the text below, and segment the text by language:
    {text}
    """
)

prompt_translate = ChatPromptTemplate.from_template(
    """
    ## Instruction ##
    Translate the text below to English:
    {text}
    """
)

cb = ChatBot()

# Conversation panels
panel_conversation_input = pn.widgets.TextInput(placeholder='Enter text here...')
panel_conversation = pn.bind(cb.conversation, panel_conversation_input) # this binds the input box to the ChatBot's conversation function (where the llm is called)

# Translator panels
panel_translator_input = pn.widgets.TextInput(placeholder='Enter text to be translated here...')
panel_translator = pn.bind(cb.translator, panel_translator_input) # this binds the input box to the ChatBot's conversation function (where the llm is called)

# Data conversation panels
file_input = pn.widgets.FileInput(accept='.pdf')
button_load = pn.widgets.Button(name="Load DB", button_type='primary')
bound_button_load = pn.bind(cb.call_load_db, button_load.param.clicks)
panel_data_conversation_input = pn.widgets.TextInput(placeholder='Enter text here...')
panel_data_conversation = pn.bind(cb.data_conversation, panel_data_conversation_input) # this binds the input box to the ChatBot's conversation function (where the llm is called)
         
tab_conversation = pn.Column( # this tab is the ChatBot tab
    pn.Row(panel_conversation_input), # create the input box
    pn.layout.Divider(),
    pn.panel(panel_conversation, loading_indicator=True, height=300), # display the conversation
    pn.layout.Divider(),
)
tab_data_conversation = pn.Column( # this tab is the ChatBot tab
    pn.Row(file_input, button_load, bound_button_load),
    pn.Row(panel_data_conversation_input), # create the input box
    pn.layout.Divider(),
    pn.panel(panel_data_conversation, loading_indicator=True, height=300), # display the conversation
    pn.layout.Divider(),
)
tab_translator = pn.Column( # this tab is the ChatBot tab
    pn.Row(panel_translator_input), # create the input box
    pn.layout.Divider(),
    pn.panel(panel_translator, loading_indicator=True, height=300), # display the conversation
    pn.layout.Divider(),
)
panel_master = pn.Column( # this panel creates the title, "logo", and is the parent of all the individual tab panels
    pn.Row(pn.pane.PNG('./img/langchain.png', width=400)),
    pn.Row(pn.pane.Markdown('# ChatBot Implementation')),
    pn.Tabs(('Chat',tab_conversation), ('Chat with Data',tab_data_conversation), ('Translate',tab_translator), )
)

panel_master.servable()