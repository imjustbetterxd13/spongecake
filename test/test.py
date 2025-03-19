# test_script.py
from time import sleep
from dotenv import load_dotenv
from spongecake import Desktop
load_dotenv()

def main():
    # Start up an isolated desktop. Edit desktop name, and docker_image if needed
    desktop = Desktop(name="newdesktop")
    container = desktop.start()
    print("🍰 spongecake container started:", container)

    # Example usage
    print('What would you like your agent to do? Below are some examples or write your own:')
    print('> Find me flights from San Francisco to Tokyo')
    print('> Fill out the form at https://bit.ly/3RiWH76, CBP\'s website')
    print('> Go to Youtube.com and search for a video titled "Python Tutorial"')
    user_prompt = input("").strip()
    try:
        result = desktop.handle_action(user_prompt) # handle_action() is a wrapper function that calls action() and handles user input and safety checks
        if result:
            print("Result:", result)
    except Exception as e:
        print(f"An error occured: {e}")
        print("\nExiting gracefully...")

    # Clean up the container. Optionally, leave the container running and connect to it again when needed. 
    print("Stopping and removing container...")
    desktop.stop()


if __name__ == "__main__":
    main()
