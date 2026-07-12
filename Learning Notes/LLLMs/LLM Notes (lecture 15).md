- To keep our project a longtime used (DURABLE) we use the "interface concept in the oop" as if we used diffrent llms compnies(openai,ollama,...) the all will use the same functions.

- the only differince is the setup we will use a design pattern called "Factory"
its a normal class contains all the logic of the logic so that we can use it when using any llm company/provider (openai,ollama,...)

![alt text](image.png) 

- in the function called 
```
 def generate_text

```
each provider may has its own arguments in the generation (some model needs prompt , some of them we want to put on it max tokes . so we put all the args we think of and when we are using each provider we choose what args to give a value and what args will stay as default value .)

- for the function:
'''
 def construct_prompt(self, prompt: str, role: str = None): 
'''
 we reformate the prompt to be compatible with the model we choose 

- we can use OPENAI provider to use another providers .
```
from openai import OpenAI

```
we can use it for ollama as well , but when passing the key we pass also another arg called "url"

- we use loggers to easily identify any fault / faliuer in our system

- smell code : the code that is not used in the program and may make an error in the future 

-         ''' raise NotImplementedError ''' Acts as a  break as well but with a message to the user that this method is not implemented yet.

- '''text[:self.default_input_max_characters].strip()''' . strip is to remove the trailing spaces or /n

- LLMFactoryProvider.py is a file that contain a pattern disgen allowing us to easily create  (choose) a provider from the given provider classes(OpenAIProvider.py,CohereProvider.py,...)

- 