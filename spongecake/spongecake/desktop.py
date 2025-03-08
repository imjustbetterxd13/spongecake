import docker
from docker.errors import NotFound, ImageNotFound, APIError
import requests
import time
import base64
from openai import OpenAI

import os
import requests
import subprocess  # Import subprocess module


from . import _exceptions

# -------------------------
# Container Management Functions
# -------------------------
class Desktop:

    def __init__(self, name: str = "newdesktop", docker_image: str = "spongebox/spongecake:latest", vnc_port: int = 5900, api_port: int = 8000, openai_api_key: str = None):
        # Set container info
        self.container_name = name  # Set container name for use in methods
        self.docker_image = docker_image # Set image name to start container
        self.display = ":99"

        # Set up access ports
        self.vnc_port = vnc_port
        self.api_port = api_port

        # Create a Docker client from environment
        self.docker_client = docker.from_env()

        # Ensure OpenAI API key is available to use
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key is None:
            raise _exceptions.SpongecakeException("The openai_api_key client option must be set either by passing openai_api_key to the client or by setting the OPENAI_API_KEY environment variable")
        self.openai_api_key = openai_api_key

        # Set up OpenAI API key
        self.openai_client = OpenAI(api_key=openai_api_key)

    def start(self):
        """
        Starts the container if it's not already running.
        Maps the VNC port and API port.
        """
        try:
            # Check to see if the container already exists
            container = self.docker_client.containers.get(self.container_name)
            print(f"⏰ Container '{self.container_name}' found with status '{container.status}'.")

            # If it's not running, start it
            if container.status != "running":
                print(f"Container '{self.container_name}' is not running. Starting...")
                container.start()
            else:
                print(f"Container '{self.container_name}' is already running.")

        except NotFound:
            # The container does not exist yet. Create it and pull the image first.
            print(f"Container '{self.container_name}' not found. Creating and starting a new container...")

            # Always attempt to pull the latest version of the image
            try:
                self.docker_client.images.pull(self.docker_image)
            except APIError as e:
                print("Failed to pull image. Attempting to start container...")

            # Try running a new container from the (hopefully just-pulled) image
            try:
                container = self.docker_client.containers.run(
                    self.docker_image,
                    detach=True,
                    name=self.container_name,
                    ports={
                        f"{self.vnc_port}/tcp": self.vnc_port,
                        f"{self.api_port}/tcp": self.api_port,
                    }
                )
            except ImageNotFound:
                # If for some reason the image is still not found locally,
                # try pulling again explicitly and run once more.
                print(f"Image '{self.docker_image}' not found locally. Pulling now...")
                try:
                    self.docker_client.images.pull(self.docker_image)
                except APIError as e:
                    raise RuntimeError(
                        f"Failed to find or pull image '{self.docker_image}'. Unable to start container."
                        f"Docker reported: {str(e)}"
                    ) from e

                container = self.docker_client.containers.run(
                    self.docker_image,
                    detach=True,
                    name=self.container_name,
                    ports={
                        f"{self.vnc_port}/tcp": self.vnc_port,
                        f"{self.api_port}/tcp": self.api_port,
                    }
                )

        # Give the container a brief moment to initialize its services
        time.sleep(2)
        return container

    def stop(self):
        """
        Stops and removes the container.
        """
        try:
            container = self.docker_client.containers.get(self.container_name)
            container.stop()
            container.remove()
            print(f"Container '{self.container_name}' stopped and removed.")
        except docker.errors.NotFound:
            print(f"Container '{self.container_name}' not found.")

    # -------------------------
    # DESKTOP ACTIONS
    # -------------------------

    # ----------------------------------------------------------------
    # RUN COMMANDS IN DESKTOP
    # ----------------------------------------------------------------
    def exec(self, command):
        # Wrap docker exec
        container = self.docker_client.containers.get(self.container_name)
        # Use /bin/sh -c to execute shell commands
        result = container.exec_run(["/bin/sh", "-c", command], stdout=True, stderr=True)
        if result.output:
            print("Command Output:", result.output.decode())

        return {
            "result": result.output.decode() if result.output else "",
            "returncode": result.exit_code
        }

    # ----------------------------------------------------------------
    # CLICK
    # ----------------------------------------------------------------
    def click(self, x: int, y: int, click_type: str = "left"):
        """
        Move the mouse to (x, y) and click the specified button.
        click_type can be 'left', 'middle', or 'right'.
        """
        click_type_map = {"left": 1, "middle": 2, "right": 3}
        t = click_type_map.get(click_type.lower(), 1)

        print(f"Action: click at ({x}, {y}) with button '{click_type}' -> mapped to {t}")
        cmd = f"export DISPLAY={self.display} && xdotool mousemove {x} {y} click {t}"
        self.exec(cmd)

    # ----------------------------------------------------------------
    # SCROLL
    # ----------------------------------------------------------------
    def scroll(self, x: int, y: int, scroll_x: int = 0, scroll_y: int = 0):
        """
        Move to (x, y) and scroll horizontally (scroll_x) or vertically (scroll_y).
        Negative scroll_y -> scroll up, positive -> scroll down.
        Negative scroll_x -> scroll left, positive -> scroll right (button 6 or 7).
        """
        print(f"Action: scroll at ({x}, {y}) with offsets (scroll_x={scroll_x}, scroll_y={scroll_y})")
        # Move mouse to position
        move_cmd = f"export DISPLAY={self.display} && xdotool mousemove {x} {y}"
        self.exec(move_cmd)

        # Vertical scroll (button 4 = up, button 5 = down)
        if scroll_y != 0:
            button = 4 if scroll_y < 0 else 5
            clicks = abs(scroll_y)
            for _ in range(clicks):
                scroll_cmd = f"export DISPLAY={self.display} && xdotool click {button}"
                self.exec(scroll_cmd)

        # Horizontal scroll (button 6 = left, button 7 = right)
        if scroll_x != 0:
            button = 6 if scroll_x < 0 else 7
            clicks = abs(scroll_x)
            for _ in range(clicks):
                scroll_cmd = f"export DISPLAY={self.display} && xdotool click {button}"
                self.exec(scroll_cmd)

    # ----------------------------------------------------------------
    # KEYPRESS
    # ----------------------------------------------------------------
    def keypress(self, keys: list[str]):
        """
        Press (and possibly hold) keys in sequence. Allows pressing
        Ctrl/Shift down, pressing other keys, then releasing them.
        Example: keys=["CTRL","F"] -> Ctrl+F
        """
        print(f"Action: keypress with keys: {keys}")

        ctrl_pressed = False
        shift_pressed = False

        for k in keys:
            print(f"  - key '{k}'")

            # Check modifiers
            if k.upper() == 'CTRL':
                print("    => holding down CTRL")
                self.exec(f"export DISPLAY={self.display} && xdotool keydown ctrl")
                ctrl_pressed = True
            elif k.upper() == 'SHIFT':
                print("    => holding down SHIFT")
                self.exec(f"export DISPLAY={self.display} && xdotool keydown shift")
                shift_pressed = True
            # Check special keys
            elif k.lower() == "enter":
                self.exec(f"export DISPLAY={self.display} && xdotool key Return")
            elif k.lower() == "space":
                self.exec(f"export DISPLAY={self.display} && xdotool key space")
            else:
                # For normal alphabetic or punctuation
                lower_k = k.lower()  # xdotool keys are typically lowercase
                self.exec(f"export DISPLAY={self.display} && xdotool key '{lower_k}'")

        # Release modifiers
        if ctrl_pressed:
            print("    => releasing CTRL")
            self.exec(f"export DISPLAY={self.display} && xdotool keyup ctrl")
        if shift_pressed:
            print("    => releasing SHIFT")
            self.exec(f"export DISPLAY={self.display} && xdotool keyup shift")

    # ----------------------------------------------------------------
    # TYPE
    # ----------------------------------------------------------------
    def type_text(self, text: str):
        """
        Type a string of text (like using a keyboard) at the current cursor location.
        """
        print(f"Action: type text: {text}")
        cmd = f"export DISPLAY={self.display} && xdotool type '{text}'"
        self.exec(cmd)
    
    # ----------------------------------------------------------------
    # TAKE SCREENSHOT
    # ----------------------------------------------------------------
    def get_screenshot(self):
        """
        Takes a screenshot of the current desktop.
        Returns the base64-encoded PNG screenshot as a string.
        """
        # The command:
        # 1) Sets DISPLAY to :99 (as Xvfb is running on :99 in your Dockerfile)
        # 2) Runs 'import -window root png:- | base64'
        # 3) The -w 0 option on base64 ensures no line wrapping (optional)
        
        command = (
            "export DISPLAY=:99 && "
            "import -window root png:- | base64 -w 0"
        )

        # We run docker exec, passing the above shell command
        # Note: we add 'bash -c' so we can use shell pipes
        proc = subprocess.run(
            ["docker", "exec", self.container_name, "bash", "-c", command],
            capture_output=True,
            text=True
        )

        if proc.returncode != 0:
            raise RuntimeError(
                f"Screenshot command failed:\nSTDERR: {proc.stderr}\n"
            )

        # proc.stdout is now our base64-encoded screenshot
        return proc.stdout.strip()

    # -------------------------
    # OpenAI Agent Integration
    # -------------------------

    def handle_model_action(self, action):
        """
        Given a computer action (e.g., click, double_click, scroll, etc.),
        execute the corresponding operation on the Docker environment.
        """
        action_type = action.type

        try:
            match action_type:
            
                case "click":
                    x, y = int(action.x), int(action.y)
                    button_map = {"left": 1, "middle": 2, "right": 3}
                    b = button_map.get(action.button, 1)
                    print(f"Action: click at ({x}, {y}) with button '{action.button}'")
                    self.exec(f"export DISPLAY={self.display} && xdotool mousemove {x} {y} click {b}")

                case "scroll":
                    x, y = int(action.x), int(action.y)
                    scroll_x, scroll_y = int(action.scroll_x), int(action.scroll_y)
                    print(f"Action: scroll at ({x}, {y}) with offsets (scroll_x={scroll_x}, scroll_y={scroll_y})")
                    self.exec(f"export DISPLAY={self.display} && xdotool mousemove {x} {y}")
                    
                    # For vertical scrolling, use button 4 (scroll up) or button 5 (scroll down)
                    if scroll_y != 0:
                        button = 4 if scroll_y < 0 else 5
                        clicks = abs(scroll_y)
                        for _ in range(clicks):
                            self.exec(f"export DISPLAY={self.display} && xdotool click {button}")
                
                case "keypress":
                    keys = action.keys
                    ctrl_pressed = False
                    shift_pressed = False
                    for k in keys:
                        print(f"Action: keypress '{k}'")
                        if k == 'CTRL':
                            print(f"  - holding down 'CTRL'")
                            self.exec(f"export DISPLAY={self.display} && xdotool keydown 'ctrl'")
                            ctrl_pressed = True
                        elif k == 'SHIFT':
                            print(f"  - holding down 'SHIFT'")
                            self.exec(f"export DISPLAY={self.display} && xdotool keydown 'shift'")
                            shift_pressed = True
                        elif k.lower() == "enter":
                            self.exec(f"export DISPLAY={self.display} && xdotool key 'Return'")
                        elif k.lower() == "space":
                            self.exec(f"export DISPLAY={self.display} && xdotool key 'space'")
                        else:
                            self.exec(f"export DISPLAY={self.display} && xdotool key '{k.lower()}'")
                    if ctrl_pressed:
                        print(f"  - releasing 'CTRL'")
                        self.exec(f"export DISPLAY={self.display} && xdotool keyup 'ctrl'")
                        ctrl_pressed = False
                    if shift_pressed:
                        print(f"  - releasing 'SHIFT'")
                        self.exec(f"export DISPLAY={self.display} && xdotool keyup 'shift'")
                        shift_pressed = False
                
                case "type":
                    text = action.text
                    print(f"Action: type text: {text}")
                    self.exec(f"export DISPLAY={self.display} && xdotool type '{text}'")
                
                case "wait":
                    print(f"Action: wait")
                    time.sleep(2)

                case "screenshot":
                    # Nothing to do as screenshot is taken at each turn
                    screenshot_bytes = self.get_screenshot()
                    return screenshot_bytes
                
                # Handle other actions here

                case _:
                    print(f"Unrecognized action: {action}")

        except Exception as e:
            print(f"Error handling action {action}: {e}")

    def computer_use_loop(self, response):
        """
        Run the loop that executes computer actions until no 'computer_call' is found.
        If the agent asks for input, return the messages to get user input from the caller.
        
        Args:
            response: The OpenAI API response
            
        Returns:
            tuple: (response, messages) where messages is None if no input needed,
                  or a list of messages if user input is required
        """
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        if not computer_calls:
            # No actionable computer_call found.
            # Check if there are interactive messages asking for input.
            messages = [item for item in response.output if item.type == "message"]
            if messages:
                # Return messages to caller for user input handling
                return response, messages
            else:
                print("No actionable computer_call or interactive prompt found. Finishing loop.")
                return response, None

        # We expect at most one computer_call per response.
        computer_call = computer_calls[0]
        last_call_id = computer_call.call_id
        action = computer_call.action

        # Execute the action.
        self.handle_model_action(action)
        time.sleep(1)  # Allow time for changes to take effect.

        # Take a screenshot after the action.
        screenshot_base64 = self.get_screenshot()
        image_data = base64.b64decode(screenshot_base64)

        with open("output_image.png", "wb") as f:
            f.write(image_data)
        print("* Saved image data.")

        # Send the screenshot back as a computer_call_output.
        response = self.openai_client.responses.create(
            model="computer-use-preview",
            previous_response_id=response.id,
            tools=[
                {
                    "type": "computer_use_preview",
                    "display_width": 1024,
                    "display_height": 768,
                    "environment": "linux"
                }
            ],
            input=[
                {
                    "call_id": last_call_id,
                    "type": "computer_call_output",
                    "output": {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{screenshot_base64}"
                    }
                }
            ],
            truncation="auto"
        )
        
        # Continue the loop with the new response
        return self.computer_use_loop(response)

    def action(self, input, user_input=None):
        """
        Execute an action and handle any required user input.
        
        Args:
            input: The initial command or action to execute, or a stored response
            user_input: Optional user input to continue a previous interaction
            
        Returns:
            dict: Contains 'result' with the final response, and optionally 'needs_input'
                  with messages if user input is required
        """
        # Wrap docker exec
        container = self.docker_client.containers.get(self.container_name)

        if not user_input:
            # Initial action
            response = self.openai_client.responses.create(
                model="computer-use-preview",
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": 1024,
                    "display_height": 768,
                    "environment": "linux" # other possible values: "mac", "windows", "ubuntu"
                }],
                input=[
                    {
                        "role": "user",
                        "content": input
                    }
                ],
                reasoning={
                    "generate_summary": "concise",
                },
                truncation="auto"
            )
        else:
            # Continue with user input from previous response
            response = self.openai_client.responses.create(
                model="computer-use-preview",
                previous_response_id=input.id,  # Access id directly from Response object
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": 1024,
                    "display_height": 768,
                    "environment": "linux"
                }],
                input=[{  # Format user input as expected by the API
                    "role": "user",
                    "content": user_input
                }],
                truncation="auto"
            )

        output, messages = self.computer_use_loop(response)
        
        if messages:
            # Return messages that need user input
            return {
                "result": output,
                "needs_input": messages
            }
        
        return {
            "result": output
        }
