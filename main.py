import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import requests
import sys
import time
import subprocess
import re
import threading

class LockerKioskApplication:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.base_url = "https://smartpalms.vercel.app/api"
        
        # Map locker numbers to GPIO pins
        self.locker_pins = {
            "1": 17,  # GPIO pin for locker 1
            "2": 27,  # GPIO pin for locker 2
            "3": 22,  # GPIO pin for locker 3
            "4": 23,  # GPIO pin for locker 4
            "5": 24,  # GPIO pin for locker 5
            "6": 25,  # GPIO pin for locker 6
            "7": 4,   # GPIO pin for locker 7
        }
        
        # Exit code
        self.exit_code = "9999EXIT"
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        # Setup all locker pins as outputs
        for pin in self.locker_pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Ensure all lockers are closed initially
        
        self.main_frame = None
        self.wifi_frame = None
        self.setup_ui()
        self.setup_keyboard_bindings()
        
        # Check WiFi on startup
        self.check_wifi_and_proceed()

    def check_wifi_connection(self):
        try:
            # Try to make a request to a reliable server
            requests.get("https://8.8.8.8", timeout=3)
            return True
        except requests.RequestException:
            return False

    def get_available_networks(self):
        try:
            # Scan for WiFi networks using iwlist
            cmd = ["sudo", "iwlist", "wlan0", "scan"]
            output = subprocess.check_output(cmd).decode()
            
            # Extract SSIDs using regex
            networks = re.findall(r'ESSID:"([^"]*)"', output)
            return list(set(networks))  # Remove duplicates
        except:
            return []

    def connect_to_wifi(self, ssid, password):
        try:
            # Create wpa_supplicant configuration
            config = (
                f'network={{\n'
                f'    ssid="{ssid}"\n'
                f'    psk="{password}"\n'
                f'}}\n'
            )
            
            # Write to temporary file
            with open('/tmp/wpa_supplicant.conf', 'w') as f:
                f.write(config)
            
            # Move file and restart wireless interface
            subprocess.run(['sudo', 'mv', '/tmp/wpa_supplicant.conf', '/etc/wpa_supplicant/wpa_supplicant.conf'])
            subprocess.run(['sudo', 'systemctl', 'restart', 'wpa_supplicant'])
            subprocess.run(['sudo', 'wpa_cli', 'reconfigure'])
            
            # Wait for connection
            time.sleep(5)
            return self.check_wifi_connection()
        except:
            return False

    def show_wifi_screen(self):
        if self.main_frame:
            self.main_frame.place_forget()
        
        if not self.wifi_frame:
            self.wifi_frame = ttk.Frame(self.root, padding="20")
        self.wifi_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Clear previous widgets
        for widget in self.wifi_frame.winfo_children():
            widget.destroy()
        
        # Title
        ttk.Label(
            self.wifi_frame,
            text="WiFi Connection Required",
            font=('Arial', 20)
        ).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Network selection
        ttk.Label(
            self.wifi_frame,
            text="Select Network:",
            font=('Arial', 14)
        ).grid(row=1, column=0, pady=5)
        
        networks = self.get_available_networks()
        network_var = tk.StringVar()
        network_dropdown = ttk.Combobox(
            self.wifi_frame,
            textvariable=network_var,
            values=networks,
            font=('Arial', 14),
            width=20
        )
        network_dropdown.grid(row=1, column=1, pady=5)
        
        # Password entry
        ttk.Label(
            self.wifi_frame,
            text="Password:",
            font=('Arial', 14)
        ).grid(row=2, column=0, pady=5)
        
        password_var = tk.StringVar()
        password_entry = ttk.Entry(
            self.wifi_frame,
            textvariable=password_var,
            font=('Arial', 14),
            show="*",
            width=20
        )
        password_entry.grid(row=2, column=1, pady=5)
        
        # Status label
        status_label = ttk.Label(
            self.wifi_frame,
            text="",
            font=('Arial', 12)
        )
        status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        def connect():
            ssid = network_var.get()
            password = password_var.get()
            
            if not ssid:
                status_label.config(text="Please select a network", foreground="red")
                return
                
            status_label.config(text="Connecting...", foreground="black")
            self.root.update()
            
            def connection_thread():
                if self.connect_to_wifi(ssid, password):
                    status_label.config(text="Connected!", foreground="green")
                    self.root.after(1000, self.check_wifi_and_proceed)
                else:
                    status_label.config(text="Connection failed", foreground="red")
            
            threading.Thread(target=connection_thread).start()
        
        # Connect button
        ttk.Button(
            self.wifi_frame,
            text="Connect",
            command=connect
        ).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Refresh button
        ttk.Button(
            self.wifi_frame,
            text="Refresh Networks",
            command=lambda: network_dropdown.config(values=self.get_available_networks())
        ).grid(row=5, column=0, columnspan=2, pady=5)

    def check_wifi_and_proceed(self):
        if self.check_wifi_connection():
            if self.wifi_frame:
                self.wifi_frame.place_forget()
            if not self.main_frame:
                self.setup_main_ui()
            self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.show_wifi_screen()

    def setup_main_ui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        
        # Create and configure input
        self.otp_var = tk.StringVar()
        self.otp_entry = ttk.Entry(
            self.main_frame, 
            textvariable=self.otp_var,
            font=('Arial', 24),
            width=10
        )
        self.otp_entry.grid(row=0, column=0, padx=5, pady=5)
        
        # Create submit button
        self.submit_button = ttk.Button(
            self.main_frame,
            text="Submit",
            command=self.handle_submit
        )
        self.submit_button.grid(row=1, column=0, pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="",
            font=('Arial', 16)
        )
        self.status_label.grid(row=2, column=0, pady=5)
        
        # Focus on entry
        self.otp_entry.focus()

    def setup_ui(self):
        # Configure the window to be fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # Initial UI will be set up by check_wifi_and_proceed

    def setup_keyboard_bindings(self):
        self.root.bind('<Return>', lambda e: self.handle_submit())

    def open_locker(self, locker_number: str):
        if locker_number in self.locker_pins:
            pin = self.locker_pins[locker_number]
            GPIO.output(pin, GPIO.HIGH)  # Open the locker
            time.sleep(1)  # Keep it activated for 1 second
            GPIO.output(pin, GPIO.LOW)   # Close the locker
            return True
        return False

    def handle_submit(self):
        otp = self.otp_var.get().strip()
        
        # Check for exit code
        if otp == self.exit_code:
            self.cleanup_and_exit()
            return
            
        if not otp:
            self.show_status("Please enter OTP", error=True)
            return
        
        try:
            # First, verify OTP and get locker number
            response = requests.get(f"{self.base_url}/{otp}")
            data = response.json()
            
            if data.get("success"):
                locker_number = data["data"]["number"]
                
                # Open the corresponding locker
                if self.open_locker(locker_number):
                    self.show_status(f"Opening locker {locker_number}!", error=False)
                    
                    # Clear the OTP by making PATCH request
                    patch_response = requests.patch(f"{self.base_url}/{otp}")
                    if not patch_response.ok:
                        print(f"Warning: Failed to clear OTP: {patch_response.status_code}")
                else:
                    self.show_status(f"Invalid locker number: {locker_number}", error=True)
            else:
                self.show_status("Invalid OTP", error=True)
                
        except requests.exceptions.RequestException as e:
            self.show_status("Network error", error=True)
            print(f"API error: {str(e)}")
        except Exception as e:
            self.show_status("System error", error=True)
            print(f"System error: {str(e)}")
        
        # Clear input and refocus
        self.otp_var.set("")
        self.otp_entry.focus()

    def show_status(self, message: str, error: bool = False):
        self.status_label.config(
            text=message,
            foreground='red' if error else 'green'
        )
        # Clear status after 2 seconds
        self.root.after(2000, lambda: self.status_label.config(text=""))

    def cleanup_and_exit(self):
        GPIO.cleanup()
        self.root.quit()
        sys.exit(0)

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.cleanup_and_exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = LockerKioskApplication(root)
    app.run()