import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import requests
import sys
import time
import subprocess
import threading
import certifi

class LockerKioskApplication:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.base_url = "https://smartpalms.vercel.app/api"
        
        # Use certifi for certificate verification
        self.cert_path = certifi.where()
        
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
        
        # Map locker numbers to UV light GPIO pins
        self.uv_light_pins = {
            "1": 5,   # GPIO pin for UV light 1
            "2": 6,   # GPIO pin for UV light 2
            "3": 12,  # GPIO pin for UV light 3
            "4": 13,  # GPIO pin for UV light 4
            "5": 16,  # GPIO pin for UV light 5
            "6": 19,  # GPIO pin for UV light 6
            "7": 20,  # GPIO pin for UV light 7
        }
        
        # Track active UV light threads
        self.active_uv_threads = {}
        
        # UV light duration in seconds (30 seconds)
        self.uv_light_duration = 30
        
        # Exit code
        self.exit_code = "9999EXIT"
        
        # Setup GPIO
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)  # Disable warnings about channel in use
            
            # Setup all locker pins as inputs first (default state)
            for pin in self.locker_pins.values():
                GPIO.setup(pin, GPIO.IN)  # First set as input (default state)
                time.sleep(0.1)  # Small delay between operations
                
            # Then configure as outputs with proper state
            for pin in self.locker_pins.values():
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)  # Set as output with initial HIGH
                time.sleep(0.1)  # Small delay between operations
                GPIO.output(pin, GPIO.HIGH)  # Ensure relay is inactive (HIGH)
            
            # Setup all UV light pins
            for pin in self.uv_light_pins.values():
                GPIO.setup(pin, GPIO.IN)  # First set as input (default state)
                time.sleep(0.1)  # Small delay between operations
                
            # Then configure UV light pins as outputs with proper state (initially off)
            for pin in self.uv_light_pins.values():
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)  # Set as output with initial HIGH (off)
                time.sleep(0.1)  # Small delay between operations
                GPIO.output(pin, GPIO.HIGH)  # Ensure relay is inactive (HIGH)
                
        except Exception as e:
            print(f"GPIO Setup Error: {str(e)}")
            self.show_error_and_exit("Failed to initialize GPIO. Please check permissions and hardware.")
        
        self.current_frame = None
        self.setup_ui()
        self.setup_keyboard_bindings()
        # Show OTP screen as the landing page instead of mode selection
        self.show_otp_screen()
        
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
            requests.get("https://8.8.8.8", timeout=3, verify=self.cert_path)
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
            response = requests.get(f"{self.base_url}/test", timeout=5, verify=self.cert_path)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"API check error: {str(e)}")
            return False

    def check_connection_periodically(self):
        """Check connection every 30 seconds and update status"""
        if not self.check_wifi_connection():
            self.show_global_status("No internet connection. Please check your WiFi settings.", error=True)
        elif not self.check_api_availability():
            self.show_global_status("Cannot connect to server. Please try again later.", error=True)
        else:
            self.show_global_status("")
        
        # Schedule next check in 30 seconds
        self.root.after(30000, self.check_connection_periodically)

    def show_global_status(self, message: str, error: bool = False):
        """Show status message on the current screen"""
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=message, foreground='red' if error else 'green')
        elif hasattr(self, 'login_status_label') and self.login_status_label.winfo_exists():
            self.login_status_label.config(text=message, foreground='red' if error else 'green')
        elif hasattr(self, 'locker_status_label') and self.locker_status_label.winfo_exists():
            self.locker_status_label.config(text=message, foreground='red' if error else 'green')

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

    def setup_ui(self):
        # Configure the window to be fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')

    def setup_keyboard_bindings(self):
        # We'll handle specific bindings for each screen separately
        # The global binding is removed
        pass

    def open_locker(self, locker_number: str):
        if locker_number in self.locker_pins:
            pin = self.locker_pins[locker_number]
            GPIO.output(pin, GPIO.LOW)   # Pull LOW to activate relay
            time.sleep(10)                # Keep it activated for 1 second
            GPIO.output(pin, GPIO.HIGH)  # Set back to HIGH to deactivate relay
            
            # Start UV light for this locker
            self.start_uv_light(locker_number)
            
            return True
        return False
    
    def start_uv_light(self, locker_number: str):
        """Start UV light for a specific locker in a separate thread"""
        if locker_number in self.uv_light_pins:
            # Cancel any existing UV thread for this locker
            if locker_number in self.active_uv_threads and self.active_uv_threads[locker_number].is_alive():
                # We don't actually cancel the thread, just let it continue
                print(f"UV light for locker {locker_number} already running")
            else:
                # Create and start a new thread for this UV light
                uv_thread = threading.Thread(
                    target=self.run_uv_light,
                    args=(locker_number,),
                    daemon=True  # Make thread daemon so it exits when main program exits
                )
                self.active_uv_threads[locker_number] = uv_thread
                uv_thread.start()
                print(f"Started UV light for locker {locker_number}")
    
    def run_uv_light(self, locker_number: str):
        """Run UV light for the specified duration"""
        try:
            pin = self.uv_light_pins[locker_number]
            
            # Turn on UV light (LOW activates the relay)
            GPIO.output(pin, GPIO.LOW)
            print(f"UV light {locker_number} ON")
            
            # Keep UV light on for the specified duration
            time.sleep(self.uv_light_duration)
            
            # Turn off UV light (HIGH deactivates the relay)
            GPIO.output(pin, GPIO.HIGH)
            print(f"UV light {locker_number} OFF")
            
        except Exception as e:
            print(f"UV light error for locker {locker_number}: {str(e)}")
            # Ensure relay is turned off in case of error
            try:
                GPIO.output(self.uv_light_pins[locker_number], GPIO.HIGH)
            except:
                pass

    def show_otp_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title label
        ttk.Label(
            self.current_frame,
            text="Smart Palms Kiosk",
            font=('Arial', 28, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Instructions label
        ttk.Label(
            self.current_frame,
            text="Enter your OTP code:",
            font=('Arial', 16)
        ).grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Create and configure input
        self.otp_var = tk.StringVar()
        self.otp_entry = ttk.Entry(
            self.current_frame, 
            textvariable=self.otp_var,
            font=('Arial', 24),
            width=10,
            justify='center'
        )
        self.otp_entry.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        # Bind Enter key to submit
        self.otp_entry.bind('<Return>', lambda e: self.handle_submit())
        
        # Submit button
        submit_button = ttk.Button(
            self.current_frame,
            text="Submit",
            command=self.handle_submit,
            width=15
        )
        submit_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Login button
        ttk.Button(
            self.current_frame,
            text="Locker Owner Login",
            command=self.show_login_screen,
            width=20
        ).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.current_frame,
            text="",
            font=('Arial', 16),
            wraplength=300,
            justify='center'
        )
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Focus on entry
        self.otp_entry.focus()

    def show_login_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        ttk.Label(
            self.current_frame,
            text="Locker Owner Login",
            font=('Arial', 28, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 40))
        
        # Email field
        ttk.Label(
            self.current_frame,
            text="Email:",
            font=('Arial', 14)
        ).grid(row=1, column=0, sticky='e', padx=5)
        
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(
            self.current_frame,
            textvariable=self.email_var,
            font=('Arial', 14),
            width=30
        )
        email_entry.grid(row=1, column=1, padx=5, pady=10)
        
        # Password field
        ttk.Label(
            self.current_frame,
            text="Password:",
            font=('Arial', 14)
        ).grid(row=2, column=0, sticky='e', padx=5)
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(
            self.current_frame,
            textvariable=self.password_var,
            font=('Arial', 14),
            width=30,
            show='*'
        )
        password_entry.grid(row=2, column=1, padx=5, pady=10)
        
        # Bind Enter key to login for both fields
        email_entry.bind('<Return>', lambda e: self.handle_login())
        password_entry.bind('<Return>', lambda e: self.handle_login())
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.current_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            buttons_frame,
            text="Back",
            command=self.show_otp_screen,
            width=15
        ).grid(row=0, column=0, padx=5)
        
        login_button = ttk.Button(
            buttons_frame,
            text="Login",
            command=self.handle_login,
            width=15
        )
        login_button.grid(row=0, column=1, padx=5)
        
        # Status label
        self.login_status_label = ttk.Label(
            self.current_frame,
            text="",
            font=('Arial', 14),
            wraplength=400,
            justify='center'
        )
        self.login_status_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Set focus
        email_entry.focus()

    def show_lockers_screen(self, user_data):
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = ttk.Frame(self.root, padding="20")
        self.current_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Welcome message
        ttk.Label(
            self.current_frame,
            text=f"Welcome, {user_data['user']['name']}!",
            font=('Arial', 24, 'bold')
        ).grid(row=0, column=0, columnspan=5, pady=(0, 20))
        
        # Headers
        headers = ['Locker #', 'Size', 'Status', 'Expires At', 'Action']
        for i, header in enumerate(headers):
            ttk.Label(
                self.current_frame,
                text=header,
                font=('Arial', 12, 'bold')
            ).grid(row=1, column=i, padx=10, pady=(0, 10))
        
        # Store locker IDs for access history
        self.current_user_locker_ids = {}
        
        # Lockers list
        for i, locker in enumerate(user_data['lockers']):
            row = i + 2
            
            # Store locker ID mapped to locker number
            self.current_user_locker_ids[locker['number']] = locker['id']
            
            # Locker number
            ttk.Label(
                self.current_frame,
                text=locker['number'],
                font=('Arial', 12)
            ).grid(row=row, column=0, padx=10, pady=5)
            
            # Size
            ttk.Label(
                self.current_frame,
                text=locker['size'].capitalize(),
                font=('Arial', 12)
            ).grid(row=row, column=1, padx=10, pady=5)
            
            # Status
            ttk.Label(
                self.current_frame,
                text=locker['subscription']['status'].capitalize(),
                font=('Arial', 12)
            ).grid(row=row, column=2, padx=10, pady=5)
            
            # Expiry date
            expiry = locker['subscription']['expiresAt'].split('T')[0]
            ttk.Label(
                self.current_frame,
                text=expiry,
                font=('Arial', 12)
            ).grid(row=row, column=3, padx=10, pady=5)
            
            # Open button
            ttk.Button(
                self.current_frame,
                text="Open",
                command=lambda n=locker['number']: self.open_locker_and_show_status(n)
            ).grid(row=row, column=4, padx=10, pady=5)
        
        # Logout button
        ttk.Button(
            self.current_frame,
            text="Logout",
            command=self.show_otp_screen,  # Go back to OTP screen instead of mode selection
            width=15
        ).grid(row=len(user_data['lockers']) + 2, column=0, columnspan=5, pady=20)
        
        # Status label
        self.locker_status_label = ttk.Label(
            self.current_frame,
            text="",
            font=('Arial', 14),
            wraplength=400,
            justify='center'
        )
        self.locker_status_label.grid(row=len(user_data['lockers']) + 3, column=0, columnspan=5, pady=10)

    def handle_login(self):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            self.show_login_status("Please enter both email and password", error=True)
            return
            
        try:
            response = requests.post(
                f"{self.base_url}/lockers/external",
                json={"email": email, "password": password},
                timeout=5,
                verify=self.cert_path
            )
            
            if response.ok:
                data = response.json()
                self.show_lockers_screen(data)
            else:
                self.show_login_status("Invalid email or password", error=True)
                
        except requests.exceptions.RequestException as e:
            self.show_login_status("Connection error. Please try again.", error=True)
            print(f"Login error: {str(e)}")

    def show_login_status(self, message: str, error: bool = False):
        self.login_status_label.config(
            text=message,
            foreground='red' if error else 'green'
        )
        if not error:
            self.root.after(5000, lambda: self.login_status_label.config(text=""))

    def open_locker_and_show_status(self, locker_number: str):
        try:
            if self.open_locker(locker_number):
                self.locker_status_label.config(
                    text=f"Opening locker {locker_number}!",
                    foreground='green'
                )
                self.root.after(5000, lambda: self.locker_status_label.config(text=""))
                
                # Create access history for type "Kiosk Log In"
                try:
                    access_history_data = {
                        "type": "Kiosk Log In",
                        "lockerId": self.current_user_locker_ids.get(locker_number, "")
                    }
                    # Only send if we have the locker ID
                    if access_history_data["lockerId"]:
                        requests.post(
                            f"{self.base_url}/access-history",
                            json=access_history_data,
                            timeout=5,
                            verify=self.cert_path
                        )
                except Exception as e:
                    print(f"Failed to create access history: {str(e)}")
            else:
                self.locker_status_label.config(
                    text=f"Failed to open locker {locker_number}",
                    foreground='red'
                )
        except Exception as e:
            self.locker_status_label.config(
                text="System error. Please try again.",
                foreground='red'
            )
            print(f"Locker operation error: {str(e)}")

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
                response = requests.get(f"{self.base_url}/{otp}", timeout=5, verify=self.cert_path)
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
                locker_number = data["locker"]["number"]
                
                # Open the corresponding locker
                try:
                    if self.open_locker(locker_number):
                        self.show_status(f"Opening locker {locker_number}!", error=False)
                        
                        # Clear the OTP by making PATCH request
                        try:
                            patch_response = requests.patch(f"{self.base_url}/{otp}", timeout=5, verify=self.cert_path)
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
                # Try to get error message from either "Error" or "message" field
                error_message = data.get("Error") or data.get("message", "Invalid OTP code")
                self.show_status(error_message, error=True)
                
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
        # Only clear success messages after 5 seconds
        if not error:
            self.root.after(5000, lambda: self.status_label.config(text=""))

    def cleanup_and_exit(self):
        # Turn off all UV lights before exiting
        for pin in self.uv_light_pins.values():
            try:
                GPIO.output(pin, GPIO.HIGH)  # Ensure all relays are inactive
            except:
                pass
                
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