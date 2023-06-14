#!/bin/bash

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --bot_name)
        bot_name="$2"
        shift # past argument
        shift # past value
        ;;
        --bot_key)
        bot_key="$2"
        shift # past argument
        shift # past value
        ;;
        *)  # unknown option
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Check if bot_name and bot_key were provided
if [ -z "$bot_name" ]; then
    echo "bot_name argument is required."
    exit 1
fi

if [ -z "$bot_key" ]; then
    echo "bot_key argument is required."
    exit 1
fi


# Check the Linux distribution
if [ -x "$(command -v apt)" ]; then
    package_manager="apt"
elif [ -x "$(command -v yum)" ]; then
    package_manager="yum"
else
    echo "Unsupported package manager. Please install 'apt' or 'yum' and try again."
    exit 1
fi

# Update the package manager
echo "Updating $package_manager..."
sudo $package_manager update -y
echo "Updated $package_manager..."

# Install python3 and python3-venv if needed
if ! [ -x "$(command -v python3)" ]; then
    echo "Installing python3..."
    sudo $package_manager install python3 -y
fi

if ! [ -x "$(command -v python3-venv)" ]; then
    echo "Installing python3-venv..."
    sudo $package_manager install python3-venv -y
fi

git clone https://github.com/zkanga/DiscordBotTemplate.git
echo "Cloned repo ..."

# Creating updated venv
rm -rf ~/"$bot_name"Venv
python3 -m venv ~/"$bot_name"Venv
. ~/"$bot_name"Venv/bin/activate
pip install -r ~/DiscordBotTemplate/manuals/requirements.txt
echo "Updated venv ..."


# Copy service file to systemd directory
sudo cp ~/"$bot_name"Repo/manuals/ServiceTemplate.service /etc/systemd/system/"$bot_name".service
sudo sed -i "s/BOT_NAME/$project_name/g" /etc/systemd/system/"$bot_name".service
sudo sed -i "s/BOT_NAME/$BOT_KEY/g" /etc/systemd/system/"$bot_name".service

sudo systemctl daemon-reload
sudo systemctl enable "$bot_name"
sudo systemctl start "$bot_name"