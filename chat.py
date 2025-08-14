import asyncio
from colorama import Fore
from userProfile import User
from ollamaHelperMain import Agent

def checkForChatExit(userInput):
    if userInput.lower() in ['exit', 'quit', 'q']:
        return True
    return False

async def main():
    model_name = "granite3-dense:8b"
    instructions_filepath = "systemInstructions.txt"
    user = User("UserProfiles/Zachary_Gray_Profile.json")
    agent = Agent(modelName=model_name, instructionsFilepath=instructions_filepath, user=user)
    chatIsActive = True
    while chatIsActive:
        userInput = input(f"{Fore.LIGHTGREEN_EX}You: {Fore.RESET}")

        if checkForChatExit(userInput): # Check if user wants to exit chat
            chatIsActive = False
            print(f"{Fore.YELLOW}Exiting chat...{Fore.RESET}")
            continue
        elif userInput.lower() == 'history':
            agent.printMemory()
            continue
        elif userInput.lower() == 'clear':
            agent.memory = [agent.memory[0]]
        else:
            await agent.generateResponse(inputTextRole='user', inputText=userInput)
            print(f"{Fore.LIGHTCYAN_EX}Assistant: {Fore.RESET}{agent.memory[-1].content.strip()}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}Exiting gracefully...{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Fore.RESET}")