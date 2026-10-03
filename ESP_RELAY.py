from machine import Pin
import sys

# Configuration: GPIO 26
RELAY_PIN = 26
relay = Pin(RELAY_PIN, Pin.OUT)

def appliance_on():
    relay.value(0) # Logic 0 usually triggers the relay
    print(">> [RELAY ON]")

def appliance_off():
    relay.value(1) # Logic 1 usually turns it off
    print(">> [RELAY OFF]")

# Start-up state
appliance_off()

print("--- Relay Test Mode ---")
print("Instructions: Type '1' to turn ON, '0' to turn OFF, or 'exit' to stop.")

while True:
    # This waits for you to type in the Thonny console
    cmd = input("Enter Command: ").strip()
    
    if cmd == "1":
        appliance_on()
    elif cmd == "0":
        appliance_off()
    elif cmd == "exit":
        print("Exiting test mode.")
        appliance_off()
        break
    else:
        print("Invalid input. Use '1', '0', or 'exit'.")