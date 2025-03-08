# test_script.py
import base64
from time import sleep
from dotenv import load_dotenv
from spongecake import Desktop
load_dotenv()

def main():
    # Start up an isolated desktop. Edit desktop name, and docker_image if needed
    desktop = Desktop(name="newdesktop")
    container = desktop.start()
    print("🍰 spongecake container started:", container)
    
    # To handle responses and feedback for the agent
    def handle_action(action_input, stored_response=None, user_input=None):
        print('Performing desktop action... see output_image.png to see screenshot captures OR connect to the VNC server to view actions in real time')
        result = desktop.action(action_input, user_input) if not stored_response else desktop.action(stored_response, user_input)
        
        while 'needs_input' in result:
            # Display messages and get user input
            for msg in result['needs_input']:
                text_parts = [part.text for part in msg.content if hasattr(part, 'text')]
                print(f"Agent asks: {' '.join(text_parts)}")
            
            user_input = input("Enter your response (or type 'exit' to quit): ").strip()
            if user_input.lower() == 'exit':
                print("Exiting as per user request")
                return result
            
            # Continue with user input
            result = desktop.action(result['result'], user_input)
        
        return result

    # Example usage
    print('What would you like your agent to do? Below are some examples or write your own:')
    print('> Go to Linkedin.com')
    print('> Go to Reddit.com')
    print('> Go to facebook.com')
    user_prompt = input("").strip()
    result = handle_action(user_prompt)
    if result:
        print("Result:", result)

    # Clean up the container. Optionally, leave the container running and connect to it again when needed. 
    print("Stopping and removing container...")
    desktop.stop()


if __name__ == "__main__":
    main()
