from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self,prompt:str,num_responses:int=1) -> list:
        """
        Generate responses from the LLM based on the provided prompt.
        
        :param prompt: The input prompt to send to the LLM.
        :param num_responses: The number of responses to generate.
        :return: A list of generated responses.
        """
        pass