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
   - Choose "Raspberry Pi OS (64-bit)" as the operating system
   - Select your SD card as the storage
   - Click on the settings gear icon (⚙️) and:
     - Set hostname (optional)
     - Enable SSH
     - Set username and password
     - Configure WiFi (for initial setup)
   - Click "Write" and wait for the process to complete

### 2. First Boot and System Configuration

1. Insert the SD card into your Raspberry Pi and power it on
2. Complete the initial setup wizard that appears on first boot
3. Open Terminal and update the system:

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Install Required Packages

```bash
# Install git and pip if not already installed
sudo apt install -y git python3-pip

# Add your user to the gpio group
sudo usermod -a -G gpio $USER
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

1. Create the autostart directories:

```bash
mkdir -p ~/.config/autostart
mkdir -p ~/.config/lxsession/LXDE-pi/
```

2. Create the autostart entry (replace 'pi' with your username if different):

```bash
echo "[Desktop Entry]
Type=Application
Name=SmartPalms Kiosk
Exec=lxterminal -e python3 $HOME/smartpalms-kiosk/main.py
Path=$HOME/smartpalms-kiosk
X-GNOME-Autostart-enabled=true
Terminal=false
Hidden=false" > ~/.config/autostart/kiosk.desktop
```

3. Make the desktop entry executable:

```bash
chmod +x ~/.config/autostart/kiosk.desktop
```

4. Create a backup autostart method:

```bash
echo "@lxterminal -e python3 $HOME/smartpalms-kiosk/main.py" > ~/.config/lxsession/LXDE-pi/autostart
```

5. Verify the files:

```bash
# Check desktop entry
cat ~/.config/autostart/kiosk.desktop

# Check file permissions
ls -l ~/.config/autostart/kiosk.desktop

# Check Python script exists
ls -l ~/smartpalms-kiosk/main.py
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

### 7. Disable Screen Saver and Power Management (Optional)

1. Create a new file for power management settings:

```bash
sudo nano /etc/xdg/autostart/disable-power-management.desktop
```

2. Add the following content:

```
[Desktop Entry]
Type=Application
Name=Disable Power Management
Exec=xset s off -dpms
```

### 8. GPIO Configuration

The application uses the following GPIO pins by default:

- Locker 1: GPIO 17
- Locker 2: GPIO 27
- Locker 3: GPIO 22
- Locker 4: GPIO 23
- Locker 5: GPIO 24
- Locker 6: GPIO 25
- Locker 7: GPIO 4

Ensure your lockers are connected to these pins or modify `main.py` to match your wiring.

### 9. Final Steps

1. Reboot the system:

```bash
sudo reboot
```

2. The kiosk application should start automatically after boot
3. To exit the application, enter the admin code: 9999EXIT

## Troubleshooting

### Check Application Status

```bash
# Check if Python process is running
ps aux | grep python3

# Check system logs
journalctl -f
```

### WiFi Issues

```bash
# Open Raspberry Pi Configuration
sudo raspi-config
# Navigate to System Options > Wireless LAN to configure WiFi

# Or check WiFi status from terminal
iwconfig
```

### GPIO Issues

```bash
# Check GPIO permissions
ls -l /dev/gpiomem

# Verify gpio group membership
groups $USER

# If needed, add your user to the gpio group again:
sudo usermod -a -G gpio $USER
```

### Display Issues

```bash
# Check display settings
xrandr

# Reset display settings
xrandr --auto
```

## Security Considerations

- Application runs in kiosk mode
- No mouse required/supported
- Secure exit code prevents unauthorized closing
- API endpoints use HTTPS
- GPIO pins are reset on program exit
- WiFi credentials are stored securely in system settings

## Support

For issues, please file a bug report in the GitHub repository issues section or contact:

gregoryerrl@gmail.com
