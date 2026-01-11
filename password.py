import os
from itertools import product

class password:
    def __init__(self):
        self.__WPA2_MIN_LENGTH = 8
        self.__WPA2_MAX_LENGTH = 15
        self.__NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.__LOWERCASE_LETTER = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        self.__UPPERCASE_LETTER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    def __combine_elements(self, arr):
        """
        Combine the array of characters into a single string.
        """
        return ''.join(arr)

    def generator(self, type_password, limit=None):
        """
        Generate passwords consisting of numbers only.

        Args:
            type_password: type to generate password
            limit(optional): limit on how many numbers to generate.

        Returns:
            password: password(string) as numbers or letters in range of lengths.
        """
        count = 0
        if type_password == 1: # numbers only
            elements = self.__NUMBER
        elif type_password == 2: # numbers + lowercase letters
            elements = self.__NUMBER + self.__LOWERCASE_LETTER
        elif type_password == 3: # letters
            elements = self.__LOWERCASE_LETTER + self.__UPPERCASE_LETTER
        elif type_password == 4: # numbers + letters
            elements = self.__NUMBER + self.__LOWERCASE_LETTER + self.__UPPERCASE_LETTER

        for len in range(self.__WPA2_MIN_LENGTH, self.__WPA2_MAX_LENGTH + 1):
            for password in product(elements, repeat=len):
                yield self.__combine_elements(password)
                count += 1
                if limit and count >= limit:
                    return
