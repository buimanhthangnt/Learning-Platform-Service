from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain


class BaseLLM:
    def __init__(self):
        pass
        

    def setup_memory(self, llm):
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=llm,
            memory=self.memory,
            verbose=True
        )


    def invoke(self, messages):
        return self.llm.invoke(messages)
