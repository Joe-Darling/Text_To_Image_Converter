"""
name: main.py
author: Joe Darling
Date: 3/9/2017
Description: This example prompts the user to enter some text or a text file and then calls the converter to turn the
text input into a image.
"""
import data_to_image


def main():
    response = input("Would you like to enter a file or text? ").lower()
    data = ""
    while response != "t" and response != "f":
        print("Incorrect input, please enter 'f' for file or 't' for text.")
        response = input("Would you like to enter a [f]ile or [t]ext? ").lower()
    if response == "t":
        data = input("Enter text: ")
    elif response == "f":
        file_name = input("Enter file path: ")
        data = open(file_name, "r").read()

    data_to_image.create_bitmap(data, squarify=False)


main()
