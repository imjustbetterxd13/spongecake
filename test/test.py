# test_script.py
import base64
from time import sleep
from dotenv import load_dotenv
from spongecake import Desktop
load_dotenv()

def main():
    # Start up an isolated desktop. Edit desktop name, and docker_image if needed
    desktop = Desktop(name="newdesktop", docker_image="local-full-vm")
    container = desktop.start()
    print("🍰 spongecake container started:", container)
    
    def extract_and_print_safety_checks(result):
        checks = result.get("safety_checks") or []
        for check in checks:
            # If each check has a 'message' attribute with sub-parts
            if hasattr(check, "message"):
                # Gather text for printing
                print(f"Pending Safety Check: {check.message}")
        return checks

    def handle_action(action_input, stored_response=None, user_input=None):
        """
        1) Call the desktop.action method to handle commands or continue interactions
        2) Print out agent prompts and safety checks
        3) If there's user input needed, prompt
        4) If there's a pending computer call with safety checks, ask user for ack, then continue
        5) Repeat until no further action is required
        """
        print(
            "Performing desktop action... see output_image.png to see screenshots "
            "OR connect to the VNC server to view actions in real time"
        )

        # Start the chain
        initial_input = stored_response if stored_response else action_input
        result = desktop.action(input=initial_input, user_input=user_input)

        while True:
            # Check if the agent is asking for user text input
            needs_input = result.get("needs_input")
            # Check for any pending computer_call we must run after acknowledging checks
            pending_call = result.get("pending_call")

            # Print any safety checks
            safety_checks = extract_and_print_safety_checks(result)

            # If the agent is asking for text input, handle that
            if needs_input:
                for msg in needs_input:
                    if hasattr(msg, "content"):
                        text_parts = [part.text for part in msg.content if hasattr(part, "text")]
                        print(f"Agent asks: {' '.join(text_parts)}")

                user_says = input("Enter your response (or 'exit'/'quit'): ").strip().lower()
                if user_says in ("exit", "quit"):
                    print("Exiting as per user request.")
                    return result

                # Call .action again with the user text, plus the previously extracted checks
                # They may or may not matter if there are no pending calls
                result = desktop.action(input=result["result"], user_input=user_says, safety_checks=safety_checks)
                continue

            # If there's a pending call with checks, the user must acknowledge them
            if pending_call and safety_checks:
                print(
                    "Please acknowledge the safety check(s) in order to proceed with the computer call."
                )
                ack = input("Type 'ack' to confirm, or 'exit'/'quit': ").strip().lower()
                if ack in ("exit", "quit"):
                    print("Exiting as per user request.")
                    return result
                if ack == "ack":
                    print("Acknowledged. Proceeding with the computer call...")
                    # We call 'action' again with the pending_call
                    # and pass along the same safety_checks to mark them as acknowledged
                    result = desktop.action(input=result["result"], pending_call=pending_call, safety_checks=safety_checks)
                    continue

            # If we reach here, no user input is needed & no pending call with checks
            # so presumably we are done
            return result


    # Example usage
    print('What would you like your agent to do? Below are some examples or write your own:')
    print('> Go to Linkedin.com')
    print('> Go to Reddit.com')
    print('> Go to facebook.com')
    user_prompt = input("").strip()
    try:
        result = handle_action(user_prompt)
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
