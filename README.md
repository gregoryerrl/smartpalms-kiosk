# Smart Palms Kiosk

A Raspberry Pi-based kiosk system for controlling Smart Palms lockers using OTP verification. This application provides a minimal interface for users to enter OTP codes, which are verified through an API to control individual lockers via GPIO pins.

## Features

- Fullscreen kiosk interface
- WiFi network selection and connection
- Single OTP input field
- API integration for OTP verification
- GPIO control for 7 lockers
- Secure admin exit functionality
- Automatic startup on boot
- Error handling and status display

## Hardware Requirements

- Raspberry Pi 4 Model B
- Display with HDMI connection
- USB Keyboard
- 7 GPIO-controlled lockers
- Power supply
- Internet connection

## Detailed Setup Instructions

### 1. Initial Raspberry Pi Setup

1. Download and install Raspberry Pi Imager from https://www.raspberrypi.com/software/
2. Insert your SD card into your computer
3. Open Raspberry Pi Imager and:
   - Choose "Raspberry Pi OS Lite (64-bit)" as the operating system
   - Select your SD card as the storage
   - Click on the settings gear icon (⚙️) and:
     - Set hostname (optional)
     - Enable SSH
     - Set username and password
     - Configure WiFi (for initial setup)
   - Click "Write" and wait for the process to complete

### 2. First Boot and System Configuration

1. Insert the SD card into your Raspberry Pi and power it on
2. Log in using the credentials you set during imaging
3. Update the system:

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Install Required System Packages

```bash
# Install X server and required packages
sudo apt install -y xserver-xorg x11-xserver-utils xinit python3-pip python3-tk git

# Install display manager
sudo apt install -y lightdm

# Enable auto-login for the pi user (replace 'your_username' with your actual username)
sudo mkdir -p /etc/lightdm/lightdm.conf.d/
echo "[Seat:*]
autologin-user=your_username
autologin-user-timeout=0" | sudo tee /etc/lightdm/lightdm.conf.d/autologin.conf
```

### 4. Clone and Setup the Project

```bash
# Clone the repository
cd ~
git clone https://github.com/yourusername/smartpalms-kiosk.git
cd smartpalms-kiosk

# Install Python dependencies
pip3 install -r requirements.txt
```

### 5. Configure Autostart

1. Create the autostart directory:

```bash
mkdir -p ~/.config/autostart
```

2. Create the autostart entry:

```bash
echo "[Desktop Entry]
Type=Application
Name=SmartPalms Kiosk
Exec=/usr/bin/python3 /home/your_username/smartpalms-kiosk/main.py
Path=/home/your_username/smartpalms-kiosk" > ~/.config/autostart/kiosk.desktop
```

### 6. Configure Display Settings (if needed)

If your display is rotated, edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

Add one of these lines depending on desired rotation:

```
# For 90° rotation
display_rotate=1
# For 180° rotation
display_rotate=2
# For 270° rotation
display_rotate=3
```

### 7. GPIO Configuration

The application uses the following GPIO pins by default:

- Locker 1: GPIO 17
- Locker 2: GPIO 27
- Locker 3: GPIO 22
- Locker 4: GPIO 23
- Locker 5: GPIO 24
- Locker 6: GPIO 25
- Locker 7: GPIO 4

Ensure your lockers are connected to these pins or modify `main.py` to match your wiring.

### 8. Final Steps

1. Reboot the system:

```bash
sudo reboot
```

2. The kiosk application should start automatically after boot
3. To exit the application, enter the admin code: 9999EXIT

## Troubleshooting

### Check Application Status

```bash
# View application logs
journalctl -u lightdm

# Check if X server is running
ps aux | grep X
```

### WiFi Issues

```bash
# Check WiFi status
iwconfig

# Scan for networks
sudo iwlist wlan0 scan

# Check network connectivity
ping 8.8.8.8
```

### GPIO Issues

```bash
# Check GPIO permissions
ls -l /dev/gpiomem
# If needed, add your user to the gpio group:
sudo usermod -a -G gpio your_username
```

## Security Considerations

- Application runs in kiosk mode
- No mouse required/supported
- Secure exit code prevents unauthorized closing
- API endpoints use HTTPS
- GPIO pins are reset on program exit
- WiFi credentials are stored securely in wpa_supplicant.conf

## Support

For issues, please file a bug report in the GitHub repository issues section.

gregoryerrl@gmail.com
