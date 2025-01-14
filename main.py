import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import requests
import sys
import time
import subprocess

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
        try:
            GPIO.setmode(GPIO.BCM)
            # Setup all locker pins as outputs
            for pin in self.locker_pins.values():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)  # Ensure all lockers are closed initially
        except Exception as e:
            print(f"GPIO Setup Error: {str(e)}")
            self.show_error_and_exit("Failed to initialize GPIO. Please check permissions and hardware.")
        
        self.main_frame = None
        self.setup_ui()
        self.setup_keyboard_bindings()
        self.setup_main_ui()
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Start periodic connection check
        self.check_connection_periodically()

    def check_wifi_connection(self):
        try:
            # First check if wlan0 exists and is up
            iwconfig_output = subprocess.check_output(['iwconfig', 'wlan0']).decode()
            if "ESSID:off/any" in iwconfig_output:
                print("WiFi not connected")
                return False
                
            # Then try to reach a reliable server
            requests.get("http://8.8.8.8", timeout=3)  # Using http to avoid SSL issues
            return True
        except requests.exceptions.Timeout:
            print("Network timeout - server not reachable")
            return False
        except requests.exceptions.SSLError as e:
            print(f"SSL Error: {str(e)}")
            # If we get SSL error, try without verification
            try:
                requests.get("https://8.8.8.8", timeout=3, verify=False)
                return True
            except:
                return False
        except subprocess.CalledProcessError:
            print("WiFi interface not found")
            return False
        except Exception as e:
            print(f"Unexpected network error: {str(e)}")
            return False

    def check_api_availability(self):
        try:
            response = requests.get(f"{self.base_url}/test", timeout=5, verify=False)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"API check error: {str(e)}")
            return False

    def check_connection_periodically(self):
        """Check connection every 30 seconds and update status"""
        if not self.check_wifi_connection():
            self.show_status("No internet connection. Please check your WiFi settings.", error=True)
        elif not self.check_api_availability():
            self.show_status("Cannot connect to server. Please try again later.", error=True)
        else:
            self.status_label.config(text="")
        
        # Schedule next check in 30 seconds
        self.root.after(30000, self.check_connection_periodically)

    def show_error_and_exit(self, message: str):
        """Show error message and exit application after delay"""
        error_window = tk.Toplevel(self.root)
        error_window.title("Fatal Error")
        error_window.geometry("400x200")
        
        ttk.Label(
            error_window,
            text=message,
            font=('Arial', 14),
            wraplength=350
        ).pack(pady=20)
        
        ttk.Button(
            error_window,
            text="Exit",
            command=lambda: self.cleanup_and_exit()
        ).pack(pady=10)
        
        # Auto exit after 10 seconds
        self.root.after(10000, self.cleanup_and_exit)

    def setup_main_ui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        
        # Title label
        self.title_label = ttk.Label(
            self.main_frame,
            text="Smart Palms Kiosk",
            font=('Arial', 28, 'bold')
        )
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Instructions label
        self.instructions_label = ttk.Label(
            self.main_frame,
            text="Enter your OTP code:",
            font=('Arial', 16)
        )
        self.instructions_label.grid(row=1, column=0, pady=(0, 10))
        
        # Create and configure input
        self.otp_var = tk.StringVar()
        self.otp_entry = ttk.Entry(
            self.main_frame, 
            textvariable=self.otp_var,
            font=('Arial', 24),
            width=10,
            justify='center'
        )
        self.otp_entry.grid(row=2, column=0, padx=5, pady=5)
        
        # Create submit button
        self.submit_button = ttk.Button(
            self.main_frame,
            text="Submit",
            command=self.handle_submit
        )
        self.submit_button.grid(row=3, column=0, pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="",
            font=('Arial', 16),
            wraplength=300,
            justify='center'
        )
        self.status_label.grid(row=4, column=0, pady=5)
        
        # Focus on entry
        self.otp_entry.focus()

    def setup_ui(self):
        # Configure the window to be fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')

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
        
        # Check internet connection first
        if not self.check_wifi_connection():
            self.show_status("No internet connection. Please check your WiFi settings.", error=True)
            return
            
        if not self.check_api_availability():
            self.show_status("Cannot connect to server. Please try again later.", error=True)
            return
            
        try:
            # First, verify OTP and get locker number
            try:
                response = requests.get(f"{self.base_url}/{otp}", timeout=5, verify=False)
                response.raise_for_status()  # Raise exception for bad status codes
                data = response.json()
            except requests.exceptions.Timeout:
                self.show_status("Server not responding. Please try again.", error=True)
                return
            except requests.exceptions.ConnectionError:
                self.show_status("Cannot connect to server. Please check your internet connection.", error=True)
                return
            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    self.show_status("Invalid OTP code", error=True)
                else:
                    self.show_status(f"Server error ({response.status_code}). Please try again later.", error=True)
                return
            except ValueError:  # JSON decode error
                self.show_status("Invalid server response. Please try again.", error=True)
                return
            
            if data.get("success"):
                locker_number = data["data"]["number"]
                
                # Open the corresponding locker
                try:
                    if self.open_locker(locker_number):
                        self.show_status(f"Opening locker {locker_number}!", error=False)
                        
                        # Clear the OTP by making PATCH request
                        try:
                            patch_response = requests.patch(f"{self.base_url}/{otp}", timeout=5, verify=False)
                            if not patch_response.ok:
                                print(f"Warning: Failed to clear OTP: {patch_response.status_code}")
                        except requests.exceptions.RequestException as e:
                            print(f"Warning: Failed to clear OTP: {str(e)}")
                    else:
                        self.show_status(f"Invalid locker number: {locker_number}", error=True)
                except Exception as e:
                    self.show_status("Failed to operate locker. Please try again.", error=True)
                    print(f"Locker operation error: {str(e)}")
            else:
                self.show_status(data.get("message", "Invalid OTP code"), error=True)
                
        except Exception as e:
            self.show_status("System error. Please try again.", error=True)
            print(f"Unexpected error: {str(e)}")
        
        # Clear input and refocus
        self.otp_var.set("")
        self.otp_entry.focus()

    def show_status(self, message: str, error: bool = False):
        self.status_label.config(
            text=message,
            foreground='red' if error else 'green'
        )
        # Only clear success messages after 2 seconds
        if not error:
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