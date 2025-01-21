# System Agent

## Overview

The **System Agent** is an AI-powered automation tool designed to interact with the Windows operating system. It simulates human-like actions such as opening applications, clicking buttons, typing, scrolling, and performing other system-level tasks. The agent leverages the Windows Accessibility (A11y) tree to analyze the system state and intelligently perform actions to complete a task.

With the latest update, the agent now includes screenshot-based annotation capabilities, allowing users to provide additional context. The agent analyzes the provided screenshot alongside the A11y tree, makes decisions, and performs the appropriate actions.

## Demo

https://github.com/user-attachments/assets/836a85ff-439d-4004-b190-ec6820c43ff6

## Features

- **System Interaction**: Perform actions like opening applications, clicking buttons, typing text, scrolling, and more.
- **A11y Tree Analysis**: Leverages the Windows Accessibility (A11y) tree to observe the current system state and locate interactive elements.
- **Screenshot Annotation**: Accepts user-provided screenshots with annotations for additional decision-making context.
- **Intelligent Action Execution**: Based on the system state and annotations, selects the appropriate interactive element and performs the required action.
- **Tool-based Actions**: Uses various tools such as Click Tool, Type Tool, Scroll Tool, Shortcut Tool, and Key Tool for system interaction.
- **Windows OS Compatibility**: Exclusively designed for Windows operating systems.

## How It Works

1. **Input**: The user provides a natural language query (e.g., "Open Notepad and type hello world") and optionally a screenshot with annotations.
2. **A11y Tree Analysis & Screenshot Processing**: 
   - The agent retrieves and analyzes the A11y tree of the system to understand the current state and interactive elements. 
   - It also processes any user-provided screenshot annotations for additional context.
3. **Decision Making**: Combines insights from the A11y tree and screenshot annotations to decide on the next action.
4. **Action Execution**: Executes actions like clicking, typing, scrolling, or using shortcuts based on its decision.
5. **Output**: Provides feedback on whether the task was successfully completed.

## Example Usage

### Opening Calculator and perform computation"

```plaintext
Enter your query: Can you open calculator and add 3+2=
Thought: First, I need to open the calculator app. I can do this by clicking on the start button and then typing "calculator" to search for the app.
Action Name: Click Tool
Action Input: {'index': 6, 'button': 'left'}
Observation: Single left clicked on the element at index 6.
Thought: The start menu is open. Now I need to type "calculator" in the search box to find the calculator app.
Action Name: Type Tool
Action Input: {'index': 22, 'text': 'calculator'}
Observation: Typed calculator on the element at index 22.
Thought: The calculator app is listed as the best match. I need to click on it to open the app.
Action Name: Click Tool
Action Input: {'index': 14, 'button': 'left'}
Observation: Single left clicked on the element at index 14.
Thought: The calculator app is now open. I need to click on the number 3, then the plus sign, then the number 2, and finally the equals sign.
Action Name: Click Tool
Action Input: {'index': 50, 'button': 'left'}
Observation: Single left clicked on the element at index 50.
Thought: I have clicked on the number 3. Now I need to click on the plus sign.
Action Name: Click Tool
Action Input: {'index': 45, 'button': 'left'}
Observation: Single left clicked on the element at index 45.
Thought: I have clicked on the plus sign. Now I need to click on the number 2.
Action Name: Click Tool
Action Input: {'index': 49, 'button': 'left'}
Observation: Single left clicked on the element at index 49.
Thought: I have clicked on the number 2. Now I need to click on the equals sign to get the result.
Action Name: Click Tool
Action Input: {'index': 46, 'button': 'left'}
Observation: Single left clicked on the element at index 46.
Thought: I have clicked the equals sign and the result is displayed as 5. The task is complete.
Final Answer: The calculator app was opened and the calculation 3 + 2 = 5 was performed.
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repository/system-agent.git
   cd system-agent
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the agent:

   ```bash
   python app.py
   ```

## Known Limitations

- **Non-standard UI Elements**: May encounter issues with complex or non-standard UI components. These are under active development. (Example application made using electron)
- **OS Limitation**: Currently supports only Windows operating systems.

## Caution

The System Agent interacts directly with your operating system to perform actions. While the agent is designed to act intelligently and safely, it can make mistakes that might disrupt system behavior or cause unintended changes. Use with caution and avoid deploying the agent in environments where such risks cannot be tolerated.

## Contribution

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a detailed description of your changes.

If you encounter any issues or have feature requests, feel free to create an issue in the repository.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.