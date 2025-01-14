# Smart Palms Kiosk

A Raspberry Pi-based kiosk system for controlling Smart Palms lockers using OTP verification. This application provides a minimal interface for users to enter OTP codes, which are verified through an API to control individual lockers via GPIO pins.

## Features

- Fullscreen kiosk interface
- Single OTP input field
- API integration for OTP verification
- GPIO control for 7 lockers
- Secure admin exit functionality
- Automatic startup on boot
- Error handling and status display
- Internet connectivity monitoring

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

### 5. Configure Startup Service

1. Make the startup script executable:

```bash
chmod +x run_kiosk.sh
```

2. Copy the service file to systemd directory:

```bash
sudo cp smartpalms-kiosk.service /etc/systemd/system/
```

3. Edit the service file to match your username (if not 'smartpalms'):

```bash
sudo nano /etc/systemd/system/smartpalms-kiosk.service
```

Replace all instances of `/home/smartpalms` with your home directory path (e.g., `/home/yourusername`).

4. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable smartpalms-kiosk.service
sudo systemctl start smartpalms-kiosk.service
```

5. Verify the service is running:

```bash
sudo systemctl status smartpalms-kiosk.service
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

## Troubleshooting

### Service Issues

```bash
# View service status
sudo systemctl status smartpalms-kiosk.service

# View service logs
journalctl -u smartpalms-kiosk.service -f

# Restart service
sudo systemctl restart smartpalms-kiosk.service

# Stop service
sudo systemctl stop smartpalms-kiosk.service

# Disable service autostart
sudo systemctl disable smartpalms-kiosk.service
```

### Display Issues

```bash
# Check display settings
xrandr

# Reset display settings
xrandr --auto
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

### Common Problems and Solutions

1. **Black Screen on Startup**

   - Check if the service is running: `systemctl status smartpalms-kiosk.service`
   - Verify DISPLAY environment variable: `echo $DISPLAY`
   - Check X server logs: `cat ~/.local/share/xorg/Xorg.0.log`

2. **GPIO Permission Denied**

   - Log out and log back in after adding user to gpio group
   - Verify group membership: `groups $USER`

3. **Network Connection Issues**

   - Use the desktop's network manager to configure WiFi
   - Check connection: `ping 8.8.8.8`
   - Verify DNS: `ping google.com`

4. **Service Won't Start**
   - Check logs: `journalctl -u smartpalms-kiosk.service -f`
   - Verify file permissions: `ls -l ~/smartpalms-kiosk/`
   - Check Python dependencies: `pip3 list`

## Security Considerations

- Application runs in kiosk mode
- No mouse required/supported
- Secure exit code prevents unauthorized closing
- API endpoints use HTTPS
- GPIO pins are reset on program exit
- Service runs under user permissions, not root

## Support

For issues, please file a bug report in the GitHub repository issues section or contact:

gregoryerrl@gmail.com
