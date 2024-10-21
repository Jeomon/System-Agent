# System Agent

## Overview

The **System Agent** is an AI-powered automation tool designed to interact with the Windows operating system. It simulates human actions, such as opening applications, clicking buttons, typing, scrolling, and performing other system-level tasks. By utilizing the Windows accessibility (A11y) tree, the agent can intelligently analyze the current system state and perform actions to complete a given task.

[Demo of the Project](https://github.com/Jeomon/System-Agent/tree/main/assets/)

## Features

- **System Interaction**: The agent can perform actions like opening applications, clicking on buttons, typing text, scrolling, and more.
- **A11y Tree Analysis**: Leverages the Windows A11y (Accessibility) tree to observe the system state and find interactive elements.
- **Tool-based Actions**: Uses different tools such as Click Tool, Type Tool, Scroll Tool, Shortcut Tool, and Key Tool to perform specific actions.
- **Problem Solving**: Given a problem statement, the agent analyzes the scenario and solves the problem step by step, interacting with the operating system as needed.

## How It Works

1. **Input**: The user provides a natural language query (e.g., "Can you open Notepad?").
2. **A11y Tree Analysis**: The agent retrieves and analyzes the A11y tree of the system to gather details about the current state and the interactive elements available.
3. **Action Execution**: The agent uses a series of tools to interact with the system (click, type, scroll, etc.).
4. **Output**: After executing the necessary actions, the agent provides feedback on whether the task was completed successfully.

## Example Usage

### 1. Opening Notepad and write some text

```plaintext
Enter your query: can open notepad and type hello world
Thought: The user wants to open Notepad and type "hello world". To do this, we need to open the Start Menu first to locate Notepad.
Action Name: Single Click Tool
Action Input: {'role': 'ButtonControl', 'name': 'Start'}
Observation: Single clicked the item ButtonControl Start.
Thought: The Start Menu is open. Now, we need to type "Notepad" into the search box to find the Notepad application.
Action Name: Type Tool
Action Input: {'role': 'EditControl', 'name': 'Search box', 'text': 'Notepad'}
Observation: Typed Notepad in EditControl Search box.
Thought: The search results for "Notepad" are displayed. We need to select the "Notepad" application from the list of results.
Action Name: Single Click Tool
Action Input: {'role': 'ListItemControl', 'name': 'Notepad, App, Press right to switch preview'}
Observation: Single clicked the item ListItemControl Notepad, App, Press right to switch preview.
Thought: Notepad is now open. We can proceed to type "hello world" into the application.
Action Name: Type Tool
Action Input: {'role': 'PaneControl', 'name': '', 'text': 'hello world'}
Observation: Typed hello world in PaneControl .
Thought: We have successfully opened Notepad and typed "hello world". The task is complete and we can present the final answer.
Final Answer: Notepad has been opened and "hello world" has been typed in it.
```

## Installation

1. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the agent:

   ```bash
   python app.py
   ```

## Known Limitations

- The agent may occasionally encounter errors when dealing with complex scenarios, especially when interacting with non-standard UI elements. These are being addressed in ongoing updates.

## Contribution

Contributions are welcome! If you'd like to contribute, feel free to fork the repository and submit a pull request. If you encounter issues, please create an issue in the repository.

## License

This project is licensed under the MIT License.