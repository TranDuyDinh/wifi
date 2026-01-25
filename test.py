import os
from password import password
from itertools import product

password = password()
for num in password.gen_number(11):
    print(num)

# __NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# __WPA2_MIN_LENGTH = 1
# __WPA2_MAX_LENGTH = 3

# for len in range(__WPA2_MIN_LENGTH, __WPA2_MAX_LENGTH + 1):
#     print(f"Length: {len}")

# password = ['0'] * __WPA2_MIN_LENGTH


# for password in product(__NUMBER, repeat=__WPA2_MIN_LENGTH):
#     print(''.join(password))


# for i in __NUMBER:
#     for j in __NUMBER:
#         for k in __NUMBER:
#             password[0] = i
#             password[1] = j
#             password[2] = k
#             print(''.join(password))
        

