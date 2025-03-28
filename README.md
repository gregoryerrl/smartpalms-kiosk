# Smart Palms Kiosk

A Raspberry Pi-based kiosk system for controlling Smart Palms lockers using OTP verification or user login. This application provides a dual-mode interface for both delivery staff and locker owners to access lockers via GPIO pins, with automatic UV sterilization after each access.

## Features

- Fullscreen kiosk interface
- Dual-mode access:
  - Delivery staff access via OTP codes
  - Locker owner access via email/password login
- API integration for authentication and verification
- GPIO control for 7 lockers
- Automatic UV light sterilization after locker access
- Multi-threaded UV light operation
- Secure admin exit functionality
- Automatic startup on boot
- Error handling and status display
- Internet connectivity monitoring

## Hardware Requirements

- Raspberry Pi 4 Model B
- Display with HDMI connection
- USB Keyboard
- 7 GPIO-controlled lockers
- 7 GPIO-controlled UV lights
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

#### Locker Control Pins:

- Locker 1: GPIO 17
- Locker 2: GPIO 27
- Locker 3: GPIO 22
- Locker 4: GPIO 23
- Locker 5: GPIO 24
- Locker 6: GPIO 25
- Locker 7: GPIO 4

#### UV Light Control Pins:

- UV Light 1: GPIO 5
- UV Light 2: GPIO 6
- UV Light 3: GPIO 12
- UV Light 4: GPIO 13
- UV Light 5: GPIO 16
- UV Light 6: GPIO 19
- UV Light 7: GPIO 20

Ensure your lockers and UV lights are connected to these pins or modify `main.py` to match your wiring.

## User Flow

The application supports two user flows:

### Delivery Staff (Riders)

1. Select "For Riders" on the main screen
2. Enter the OTP code
3. If valid, the corresponding locker will open
4. UV light will automatically activate for 5 minutes

### Locker Owners (Users)

1. Select "For Users" on the main screen
2. Enter email and password
3. View all assigned lockers with details
4. Click "Open" on any locker to access it
5. UV light will automatically activate for 5 minutes

For a detailed user flow description, see the [USER-FLOW.md](USER-FLOW.md) file.

## UV Light System

The application includes an automatic UV light sterilization system:

- Each locker has a corresponding UV light
- UV lights activate automatically after a locker is opened
- Each UV light runs for 5 minutes (configurable in code)
- Multiple UV lights can run simultaneously using separate threads
- UV lights continue to run even if users navigate to different screens
- All UV lights are safely turned off when the application exits

## Troubleshooting

### HTTPS Certificate Issues

When running on a Raspberry Pi, you might encounter "unverified HTTPS request" errors. This happens because the Raspberry Pi OS might not have all the required certificates installed. The application is already configured to bypass certificate verification with `verify=False` in the requests, but here are better solutions:

1. **Install Certificate Authorities**:

   ```bash
   sudo apt install -y ca-certificates
   sudo update-ca-certificates
   ```

2. **Install Certifi Package**:

   ```bash
   pip3 install certifi
   ```

   Then update your code to use the certifi certificate bundle:

   ```python
   import certifi
   response = requests.get("https://example.com", verify=certifi.where())
   ```

3. **Manually Set Certificate Path** (if above solutions don't work):
   ```bash
   export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
   ```
   Add this line to your `.bashrc` file to make it permanent.

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

5. **UV Lights Not Working**
   - Check GPIO connections for UV lights
   - Verify relay module is properly powered
   - Check logs for UV light errors: `journalctl -u smartpalms-kiosk.service | grep "UV light"`

## Security Considerations

- Application runs in kiosk mode
- No mouse required/supported
- Secure exit code prevents unauthorized closing
- API endpoints use HTTPS
- GPIO pins are reset on program exit
- Service runs under user permissions, not root
- UV light threads are daemon threads that terminate with the main program

## Support

For issues, please file a bug report in the GitHub repository issues section or contact:

gregoryerrl@gmail.com
