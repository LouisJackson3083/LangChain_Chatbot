# LangChain_Chatbot
## Environment setup
First create a virtual python environment using your preferred method, and execute:
`
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
`
## Running the Chatbot
To run the chatbot, please run the following command in a terminal (vs-code terminal does not work)
`panel serve chatbot_v2.py --autoreload --show --args <API_KEY>`
You must have an OpenAI api key which you can get here: https://platform.openai.com/account/api-keys

## Potential Errors
I you get an error like this:
`Retrying langchain.chat_models.openai.ChatOpenAI.completion_with_retry.<locals>._completion_with_retry in 1.0 seconds as it raised RateLimitError: You exceeded your current quota, please check your plan and billing details..`
You will have to upgrade your free account to a paid account to gain more credits - or update your billing at https://platform.openai.com/account/billing/overview
