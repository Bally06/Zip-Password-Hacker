# File:     ballys-zipcrack.py
# Version:  v1.0
# Author:   Ian Ballantyne
# Date:     21/04/2024
# Purpose:  Command line WinRAR brute force & dictionary attack script, customisable with own charset


import signal
import zipfile
import sys
import itertools
import argparse
import threading
from termcolor import colored
import pyfiglet


# Variable to signal the script to stop gracefully
stop_script = threading.Event()

# Handle for when Ctrl+C is received to allow any necessary cleanup or termination before exiting
def signal_handler(sig, frame):
    global stop_script
    print(colored(f'\nballys-zipcrack ended via CTRL/C \n', color="light_blue"))
    stop_script.set()
    sys.exit()

# Define the get_password function
def get_password(zip_file,
                min_length,
                max_length,
                charset,
                wordlist=None,):

 # Generate passwords
    if wordlist:
        with open(wordlist, 'r') as w:
            passwords = [line.strip() for line in w]

# Passwords will only be generated to the specified variables set (min-max)
        passwords = [p for p in passwords if min_length <= len(p) <= max_length]

# Print the dictionary attack is starting
        print(colored(f'\nStarting the dictionary attack: ', color="light_blue"))

# Start the dictionary attack using the wordlist, and then switch to a brute-force attack
        for i, password in enumerate(passwords, start=1):
            if stop_script.is_set():
                return None

# Print the password and the number of attempts in red, supporting text in yellow
            try:
                zip_file.extractall(pwd=password.encode())
                print(colored(f'Password found:  {colored(password, "red")}', "light_yellow"))
                print(colored(f'Total attempts:  {colored(i, "green")}\n', "light_yellow"))

# Return the password and print switching to brute-force attack
                return password
            except Exception:
                pass
        print(colored(f'The password has not been found in the Wordlist, switching to a brute-force attack: ', color="light_yellow"))

# Generate all possible passwords from the charset
    passwords = (''.join(password) for length in range(min_length, max_length + 1) for password in
                 itertools.product(charset, repeat=length))

# Print brute-force attack is starting
    print(colored(f'Starting the brute-force attack: ', color="light_blue"))

    for i, password in enumerate(passwords, start=1):
        if len(password) > max_length:
            break

        if stop_script.is_set():
            return None

# Try to extract the WinRAR file with the current password, file will be created in directory if successful
        try:
            zip_file.extractall(pwd=password.encode())
            print(colored(f'Password found:', "light_yellow"), colored(password, "red"))
            print(colored(f'Total number of passwords tried:', "light_yellow"), colored(i, "green"))
            print()
            return password
        except Exception:
            global count
            count = i
            pass

# Print password not found and the number of attempts
    print(colored(f'\nPassword not found:', "light_yellow"))
    print(colored(f'Total attempts:', "light_yellow"), colored(count, "green"))
    return None

# Main to control code executed directly as a cmd line script and parse command-line arguments and informative usage messages for help
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Brute-force & Dictionary attack to extract a WinRAR file ')
    parser.add_argument('-zip', type=str, required=True, help='Enter the WinRAR file name and path if not run from same folder.')
    parser.add_argument('-wordlist', type=str, help='Specify the path to a wordlist of possible passwords.')
    parser.add_argument('-charset', type=str, default='abcdefghijklmnopqrstuvwxyz',
        help='The default character set to use for the brute-force attack.')
    parser.add_argument('-min', type=int, default=1, help='Enter the minimum length to start the password attempt.')
    parser.add_argument('-max', type=int, default=8, help='Enter the maximum length of the password to attempt.')
    args = parser.parse_args()

# Register the signal handler to allow handling a graceful interruption via CTRL-C
    signal.signal(signal.SIGINT, signal_handler)

# print the script name in ascii art
#    print(pyfiglet.figlet_format('ballys-zipcrack'))
    ascii_art = pyfiglet.figlet_format("ballys-zipcrack")
    colored_ascii_art = colored(ascii_art, color="red")
    print(colored_ascii_art)

# Open the WinRAR file and exception handling for file opening
    try:
        zip_file = zipfile.ZipFile(args.zip)
    except Exception as e:
        parser.error('Failed to open WinRAR file: ' + str(e))

# Extract WinRAR with brute-force
    password = get_password(zip_file, args.min, args.max, args.charset, args.wordlist)
