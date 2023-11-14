# Cloudflare DDNS Updater Application

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

This Python application provides a Dynamic Domain Name System (DDNS) solution specialized for Cloudflare, with a specific focus on supporting Minecraft servers that are hosted with a dynamic IP. The application allows you to automatically update your Cloudflare DNS records whenever your server's IP address changes.

## Features

- **Cloudflare Integration**: Seamless integration with Cloudflare's API for updating DNS records.
- **Minecraft Server Support**: Tailored for Minecraft servers hosted with dynamic IP addresses.
- **Tkinter GUI**: User-friendly graphical interface for easy configuration and monitoring.
- **Configurability**: Customize settings through a configuration file for flexibility.

## Prerequisites

Before using this application, ensure you have the following installed:

- Python 3.x
- Required Python packages: `requests`, `tkinter`, `customtkinter`

Install the required packages using:

```bash
pip install requests tkinter customtkinter
```

## Usage

1. Clone the repository:

```bash
git clone https://github.com/rajdhal/DDNS
cd your-repo
```

2. Configure the application by editing `config.json` with your Cloudflare API key, email, zone ID, and other settings.

3. Run the application:

```bash
python App.py
```

4. The Tkinter GUI will appear, allowing you to monitor and update your Cloudflare DNS records.

## Configuration

Modify the `config.json` file to set up the following parameters:

- `api_email`: Your Cloudflare account email.
- `api_key`: Your Cloudflare API key.

## Acknowledgments

Special thanks to the following libraries and modules used in this project:

- `requests`: Simplifies HTTP requests.
- `tkinter`: GUI toolkit for Python.
- `customtkinter`: Customized tkinter widgets for enhanced GUI.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```

Feel free to modify and expand the README file based on additional features, use cases, or any other details you'd like to highlight.
```
