<div align="center">
  <img 
    src="./static/spongecake-light.png" 
    alt="spongecake logo" 
    width="700" 
  >
</div>


<h1 align="center">Open source SDK to launch OpenAI computer use agents</h1>
<div style="text-align: center;">

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./static/spongecake-demo.gif" />
    <img 
      alt="[coming soon] Shows a demo of spongecake in action" 
      src="./static/spongecake-demo.gif" 
      style="width: 100%; max-width: 700px;"
    />
  </picture>
</div>


## What is spongecake?

**spongecake** is the easiest way to launch OpenAI-powered “computer use” agents. It simplifies:
- **Spinning up** a Docker container with a virtual desktop (including Xfce, VNC, etc.).
- **Controlling** that virtual desktop programmatically using an SDK (click, scroll, keyboard actions).
- **Integrating** with OpenAI to drive an agent that can interact with a real Linux-based GUI.

---

## Prerequisites

You’ll need the following to get started (click to download):
- [**Docker**](https://docs.docker.com/get-docker/)  
- [**OpenAI API Key**](https://platform.openai.com/)

# Quick Start

1. **Clone the repo** (if you haven’t already):
   ```bash
   git clone https://github.com/aditya-nadkarni/spongecake.git
   cd spongecake/test
   ```
2. **Set up a Python virtual environment and install the spongecake package**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate

   python3 -m pip install --upgrade spongecake
   python3 -m pip install --upgrade dotenv
   python3 -m pip install --upgrade openai  # Make sure you have the latest version of openai for the responses API
   ```
3. **Run the test script**:  
   ```bash
   cd test # If needed
   ```
   ```bash
   python3 test.py
   ```
   Feel free to edit the `test.py` script to try out your own commands.  
   <br>
   > **Note:** This deploys a Docker container in your local Docker environment. If the spongecake default image isn't available, it will pull the image from Docker Hub.

4. **Create your own scripts**:
  The test script is largely for demonstration purposes. To make this work for own use cases, create your own scripts using the SDK or integrate it into your own systems.

---

# (Optional) Building & Running the Docker Container

If you want to manually build and run the included Docker image for a virtual desktop environment you can follow these steps. To make your own changes to the docker container, fork the repository and edit however you need. This is perfect for adding dependencies specific to your workflows.

1. **Navigate to the Docker folder** (e.g., `cd spongecake/docker`).
2. **Build the image**:
   ```bash
   docker build -t <name of your image> .
   ```
3. **Run the container**:
   ```bash
   docker run -d -p 5900:5900 --name <name of your container> <name of your image>
   ```
   - This starts a container that you name and exposes VNC on port **5900**.

4. **Shell into the container** (optional):
   ```bash
   docker exec -it <name of your container> bash
   ```
   This is useful for debugging, installing extra dependencies, etc.

5. You can then specify the name of your container / image when using the SDK

---

# Connecting to the Virtual Desktop
**If you're working on a mac**:
1. Right click `Finder` and select `Connect to server...`  
      OR  
   In the `Finder` window, navigate to `Go > Connect to server...` in the menu bar
2. Enter the VNC host and port - should be `vnc://localhost:5900` in the default container
3. It will ask for a password, which will be set to "`secret`" in the default docker container
4. Your mac will connect to the VNC server. You can view and control the container's desktop through here

**Other options**:
1. **Install a VNC Viewer**, such as [TigerVNC](https://tigervnc.org/) or [RealVNC](https://www.realvnc.com/en/connect/download/viewer/).
2. **Open the VNC client** and connect to:
   ```
   localhost:5900
   ```
3. Enter the password when needed (set to "`secret`" in the default docker container).

---

<br>
<br>

# Documentation

## Desktop Client Documentation

Below is the **Desktop** class, which provides functionality for managing and interacting with a Docker container that simulates a Linux desktop environment. This class enables you to control mouse/keyboard actions, retrieve screenshots, and integrate with OpenAI for higher-level agent logic.

---

## Class: `Desktop`

**Arguments**:
1. **name** *(str)*: A unique name for the container. Defaults to `"newdesktop"`. This should be unique for different containers
2. **docker_image** *(str)*: The Docker image name to pull/run if not already available. Defaults to `"spongebox/spongecake:latest"`.
3. **vnc_port** *(int)*: The host port mapped to the container’s VNC server. Defaults to **5900**.
4. **api_port** *(int)*: The host port mapped to the container’s internal API. Defaults to **8000**.
5. **openai_api_key** *(str)*: An optional API key for OpenAI. If not provided, the class attempts to read `OPENAI_API_KEY` from the environment.

**Raises**:
- **SpongecakeException** if any port is in use.
- **SpongecakeException** if no OpenAI API key is supplied.

**Description**: Creates a Docker client, sets up container parameters, and initializes an internal OpenAI client for agent integration.

---

### **`start()`**

```python
def start(self) -> Container:
    """
    Starts the container if it's not already running.
    """
```

**Behavior**:
- Starts the docker container thats initialized in the Desktop() constructor
- Checks if a container with the specified `name` already exists.
- If the container exists but is not running, it starts it.  
  Note: In this case, it will not pull the latest image
- If the container does not exist, the method attempts to run it:
  - It will attempt to pull the latest image before starting the container
- Waits a short time (2 seconds) for services to initialize.
- Returns the running container object.

**Returns**:
- A Docker `Container` object representing the running container.

**Exceptions**:
- **RuntimeError** if it fails to find or pull the specified image
- **docker.errors.APIError** For any issue with running the container
---

### **`stop()`**

```python
def stop(self) -> None:
    """
    Stops and removes the container.
    """
```

**Behavior**:
- Stops + removes the container.
- Prints a status message.
- If the container does not exist, prints a warning.

**Returns**:
- `None`

---

### **`exec(command)`**

```python
def exec(self, command: str) -> dict:
    """
    Runs a shell command inside the container.
    """
```

**Arguments**:
- **command** *(str)*: The shell command to execute.

**Behavior**:
- Runs a shell command in the docker container
- Captures stdout and stderr.
- Logs the command output.

**Returns**:
A dictionary with:
```json
{
  "result": (string output),
  "returncode": (integer exit code)
}
```

---

## Desktop Actions

### **`click(x, y, click_type="left")`**

```python
def click(self, x: int, y: int, click_type: str = "left") -> None:
    """
    Move the mouse to (x, y) and click the specified button.
    click_type can be 'left', 'middle', or 'right'.
    """
```

**Arguments**:
- **x, y** *(int)*: The screen coordinates to move the mouse.
- **click_type** *(str)*: The mouse button to click (`"left"`, `"middle"`, or `"right"`).

**Returns**:
- `None`

---

### **`scroll(x, y, scroll_x=0, scroll_y=0)`**

```python
def scroll(
    self,
    x: int,
    y: int,
    scroll_x: int = 0,
    scroll_y: int = 0
) -> None:
    """
    Move to (x, y) and scroll horizontally or vertically.
    """
```

**Arguments**:
- **x, y** *(int)*: The screen coordinates to move the mouse.
- **scroll_x** *(int)*: Horizontal scroll offset.
  - Negative => Scroll left (button 6)
  - Positive => Scroll right (button 7)
- **scroll_y** *(int)*: Vertical scroll offset.
  - Negative => Scroll up (button 4)
  - Positive => Scroll down (button 5)

**Behavior**:
- Moves the mouse to `(x, y)`.
- Scrolls by scroll_x and scroll_y

**Returns**:
- `None`

---

### **`keypress(keys: list[str])`**

```python
def keypress(self, keys: list[str]) -> None:
    """
    Press (and possibly hold) keys in sequence.
    """
```

**Arguments**:
- **keys** *(list[str])*: A list of keys to press. Example: `["CTRL", "f"]` for Ctrl+F.

**Behavior**:
- Executes a keypress
- Supports shortcuts like Ctrl+Fs

**Returns**:
- `None`

---

### **`type_text(text: str)`**

```python
def type_text(self, text: str) -> None:
    """
    Type a string of text (like using a keyboard) at the current cursor location.
    """
```

**Arguments**:
- **text** *(str)*: The string of text to type.

**Behavior**:
- Types a string of text at the current cursor location.

**Returns**:
- `None`

---

### **`get_screenshot()`**

```python
def get_screenshot(self) -> str:
    """
    Takes a screenshot of the current desktop.
    Returns the base64-encoded PNG screenshot.
    """
```

**Behavior**:
- Takes a screenshot as a png
- Captures the base64 result.
- Returns that base64 string.

**Returns**:
- *(str)*: A base64-encoded PNG screenshot.

**Exceptions**:
- **RuntimeError** if the screenshot command fails.

---

## OpenAI Agent Integration

### **`action(input, user_input=None, safety_checks=None)`**

```python
def action(self, input, user_input=None, safety_checks=None) -> dict:
    """
    Uses OpenAI's computer-use-preview model to control the container environment
    and possibly handle user input or safety checks.
    """
```

**Arguments**:
- **`input`**:  
  The initial command (string) for the agent to run, or a "stored response" object from a previous call.  
- **`user_input`** (string, optional):  
  If the agent has requested additional information from the user, you provide that input here.  
- **`safety_checks`** (list, optional):  
  An optional list of safety check objects that have been acknowledged by the user and should be passed back to the agent.

**Behavior**:

1. If **`user_input`** is **not** provided, it creates a new OpenAI response with the "computer-use-preview" model using **`input`**.  
2. If **`user_input`** **is** provided, the function continues the conversation from the previously returned response, optionally including **`safety_checks`** if needed.  
3. The "computer use" agent performs actions in the environment
4. Returns final or updated response, plus any needed user input messages and safety that need acknowledgement.

**Returns**:
A dictionary with the following fields:

```json
{
  "result": { ... },         // The final or in-progress response object
  "needs_input": [ ... ],    // (optional) A list of messages if the agent requests user input
  "safety_checks": true|false // Boolean indicating whether new safety checks are pending
}
```

- **`result`**: Always present. Contains the agent’s most recent output/state.  
- **`needs_input`**: Present only if the agent needs user input to continue.  
- **`safety_checks`**: A boolean (`true`/`false`) indicating whether there are pending safety checks in `result.pending_safety_checks`. If `true`, the caller will need to handle acknowledging these checks. Pass the acknowledged checks back to continue



# Appendix

## Contributing

Feel free to open issues for any feature requests or if you encounter any bugs! We love and appreciate contributions of all forms.

### Pull Request Guidelines
1. **Fork the repo** and **create a new branch** from `main`.
2. **Commit changes** with clear and descriptive messages.
3. **Include tests**, if possible. If adding a feature or fixing a bug, please include or update the relevant tests.
4. **Open a Pull Request** with a clear title and description explaining your work.

## Roadmap

- Support for other computer-use agents
- Support for browser-only envrionments
- Integrating human-in-the-loop
- (and much more...)

## Team

<div align="center">
  <img src="./static/team.png" width="200"/>
</div>

<div align="center">
Made with ❤️ in San Francisco
</div>
