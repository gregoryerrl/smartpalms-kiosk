# Smart Palms Kiosk - User Flow

This document outlines the user flow for the Smart Palms Kiosk application, which provides access to lockers for both delivery staff and locker owners.

## Main Screen

Upon starting the application, users are presented with a mode selection screen:

- **For Riders** - For delivery staff to access lockers using OTP codes
- **For Users** - For locker owners to access their lockers using email/password

## Delivery Staff Flow (Riders)

### 1. OTP Entry Screen

After selecting "For Riders", delivery staff will:

1. See the OTP entry screen
2. Enter the OTP code provided to them
3. Click "Submit" or press Enter

### 2. OTP Validation

The system will validate the OTP:

- **If valid**: The system will:

  - Open the corresponding locker
  - Display a success message
  - Automatically activate the UV light for that locker (runs for 5 minutes)
  - Clear the OTP by making a PATCH request to the server
  - Clear the input field for the next entry

- **If invalid**: The system will:
  - Display an error message
  - Clear the input field
  - Allow the user to try again

### 3. Connection Issues

If there are connection issues:

- The system will display appropriate error messages
- Periodically check for connection restoration

### 4. Return to Main Screen

Users can click the "Back" button to return to the mode selection screen.

## Locker Owner Flow (Users)

### 1. Login Screen

After selecting "For Users", locker owners will:

1. See the login screen
2. Enter their email address
3. Enter their password
4. Click "Login"

### 2. Login Validation

The system will validate the login credentials:

- **If valid**: The system will:

  - Display the locker management screen
  - Show a welcome message with the user's name
  - List all lockers associated with the user

- **If invalid**: The system will:
  - Display an error message
  - Allow the user to try again

### 3. Locker Management Screen

On the locker management screen, users will see:

1. A welcome message with their name
2. A table of their lockers showing:
   - Locker number
   - Size
   - Subscription status
   - Expiration date
   - Open button for each locker

### 4. Opening a Locker

When a user clicks "Open" for a specific locker:

1. The system will activate the corresponding locker
2. Display a success message
3. Automatically activate the UV light for that locker (runs for 5 minutes)
4. The UV light will continue to run even if the user logs out or opens other lockers

### 5. Return to Main Screen

Users can click the "Logout" button to return to the mode selection screen.

## UV Light Operation

The UV light system operates as follows:

1. When a locker is opened (by either delivery staff or locker owner), the corresponding UV light is automatically activated
2. The UV light runs for 5 minutes
3. Multiple UV lights can run simultaneously
4. UV lights operate in separate threads, allowing the kiosk to remain responsive
5. If a locker is opened again while its UV light is already running, the existing cycle continues

## System Exit

The application can be exited by:

1. Delivery staff entering the exit code "9999EXIT" in the OTP field
2. System administrators using keyboard shortcuts

Upon exit, the system will:

1. Turn off all active UV lights
2. Clean up GPIO resources
3. Exit gracefully

## Error Handling

The system provides clear error messages for various scenarios:

- Network connectivity issues
- Server unavailability
- Invalid credentials
- Hardware failures
- System errors

Error messages are displayed in red, while success messages are displayed in green.
