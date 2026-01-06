import os

class brute_force:
    def __init__(self):
        pass

    def generate_numbers(self, min_len, max_len, limit=None):
        """
        Generate numbers with lengths from min_len to max_len.

        Args:
            min_len: minimum length of the genarated number.
            max_len: maximum length.
            limit(optional): limit on how many numbers to generate.

        Returns:
            num: integer number in range of lengths.
        """
        count = 0
        # Loop through each length
        for length in range(min_len, max_len + 1):
            start = 10**(length - 1)
            end = 10**length
            for num in range(start, end):
                yield num # Return num but not end the function
                count += 1
                if limit and count >= limit:
                    return