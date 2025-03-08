
<div align="center">
  <img 
    src="./static/spongecake-light.png" 
    alt="spongecake logo" 
    width="500" 
  >
</div>




<h1 align="center">Open source SDK to launch OpenAI computer use agents 🤖</h1>
<div style="text-align: center;">

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./static/spongecake-demo.gif" />
    <img 
      alt="[coming soon] Shows a demo of spongecake in action" 
      src="./static/spongecake-demo.gif" 
      style="width: 100%; max-width: 700px;"
    />
  </picture>

  <p style="color: gray; font-size: 14px; margin-top: 8px;">
    (coming soonsies) Spinning up a computer use agent with sponge box 
  </p>

</div>


### What is spongecake?
🚀 spongecake is the easiest way to launch OpenAI computer use agents.

## Prerequisites
You’ll need the following to get started (click to download):
- [Docker](https://docs.docker.com/get-docker/)  
- **OpenAI API Key** (sign up at [OpenAI](https://platform.openai.com/))

> **Note**: The versions mentioned above are tested references. Other versions may work, but haven’t been fully validated.

# Quick Start

### Install the spongecake package using pip:
```bash
pip install spongecake
```
Clone the repo and run test.py...

```bash
cd spongecake/test
python3 test.py
```
Done! Edit the script in test.py to test out sponge bob 

## Usage Details
[coming soon]

# How it works
[coming soon]

# Appendix

## Contributing

Feel free to open issues for any feature requests or if you encounter any bugs! We love and appreciate contributions of all forms.

### Pull Request Guidelines
1. **Fork the repo** and **create a new branch** from `main`.  
2. **Commit changes** with clear and descriptive messages.  
3. **Include tests**, if possible. If adding a feature or fixing a bug, please include or update the relevant tests.  
4. **Open a Pull Request** with a clear title and description explaining your work.

## Roadmap
[coming soon]

## Team

 <div align="center"> <img src="./static/team.png" width="200"/> 
  
 </div>

<div align="center">
Made with ❤️ in San Francisco
 </div>





Backend set-up 
- Set-up .env in the backend folder with OpenAI Key and Port 

SDK set-up 
- cd sdk
- (in spongecake) pip3 install --upgrade pip setuptools wheel build
- (in spongecake)  pip install --upgrade openai # Make sure you get the latest responses API 
- (in spongecake) python3.11 -m build
- (in spongecake)  pip3 install dist/spongecake-0.1.2-py3-none-any.whl
- (in root) pip3 install -e spongecake/
- pip3 install dotenv

Testing the app
- python3 test.py


Building and running the docker container
- cd sdk/docker
- docker build -t local-lxde-vm
- docker run -d -p 5900:5900 --name myvm local-lxde-vm
- docker exec -it myvm bash


Connecting to virtual desktop 
- Open TigerVNC viewer
- Connect to `localhost:5900`