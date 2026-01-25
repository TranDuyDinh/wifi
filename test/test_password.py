import unittest
from password import password


class TestPasswordClass(unittest.TestCase):
    """Test cases for the password class using PyUnit"""

    def setUp(self):
        """Set up test fixtures"""
        self.pwd = password()

    def test_generator_type_1_numbers_only(self):
        """Test generator with type 1 (numbers only)"""
        gen = self.pwd.generator(1, limit=5)
        passwords = list(gen)
        self.assertEqual(len(passwords), 5)
        # Check all passwords contain only digits
        for pwd in passwords:
            self.assertTrue(pwd.isdigit())
            # Check password length is between 8 and 15
            self.assertGreaterEqual(len(pwd), 8)
            self.assertLessEqual(len(pwd), 15)

    def test_generator_type_2_numbers_lowercase(self):
        """Test generator with type 2 (numbers + lowercase letters)"""
        gen = self.pwd.generator(2, limit=5)
        passwords = list(gen)
        self.assertEqual(len(passwords), 5)
        for pwd in passwords:
            # Check password contains only digits and lowercase letters
            self.assertTrue(pwd.isalnum() and pwd.islower() or pwd.isdigit())
            self.assertGreaterEqual(len(pwd), 8)
            self.assertLessEqual(len(pwd), 15)

    def test_generator_type_3_letters_only(self):
        """Test generator with type 3 (letters only)"""
        gen = self.pwd.generator(3, limit=5)
        passwords = list(gen)
        self.assertEqual(len(passwords), 5)
        for pwd in passwords:
            # Check password contains only letters
            self.assertTrue(pwd.isalpha())
            self.assertGreaterEqual(len(pwd), 8)
            self.assertLessEqual(len(pwd), 15)

    def test_generator_type_4_numbers_letters(self):
        """Test generator with type 4 (numbers + letters)"""
        gen = self.pwd.generator(4, limit=5)
        passwords = list(gen)
        self.assertEqual(len(passwords), 5)
        for pwd in passwords:
            # Check password contains alphanumeric characters
            self.assertTrue(pwd.isalnum())
            self.assertGreaterEqual(len(pwd), 8)
            self.assertLessEqual(len(pwd), 15)

    def test_generator_without_limit(self):
        """Test generator without limit generates many passwords"""
        gen = self.pwd.generator(1)
        passwords = list(gen)
        # Should generate many passwords (more than 100)
        self.assertGreater(len(passwords), 100)

    def test_generator_limit_respected(self):
        """Test that generator respects the limit parameter"""
        limits = [1, 10, 50, 100]
        for limit in limits:
            gen = self.pwd.generator(1, limit=limit)
            passwords = list(gen)
            self.assertEqual(len(passwords), limit)

    def test_total_type_1(self):
        """Test total calculation for type 1 (numbers only)"""
        total = self.pwd.total(1)
        # 10^8 + 10^9 + ... + 10^15
        expected = sum(10**i for i in range(8, 16))
        self.assertEqual(total, expected)

    def test_total_type_2(self):
        """Test total calculation for type 2 (numbers + lowercase)"""
        total = self.pwd.total(2)
        # 36^8 + 36^9 + ... + 36^15
        expected = sum(36**i for i in range(8, 16))
        self.assertEqual(total, expected)

    def test_total_type_3(self):
        """Test total calculation for type 3 (letters only)"""
        total = self.pwd.total(3)
        # 52^8 + 52^9 + ... + 52^15
        expected = sum(52**i for i in range(8, 16))
        self.assertEqual(total, expected)

    def test_total_type_4(self):
        """Test total calculation for type 4 (numbers + letters)"""
        total = self.pwd.total(4)
        # 62^8 + 62^9 + ... + 62^15
        expected = sum(62**i for i in range(8, 16))
        self.assertEqual(total, expected)

    def test_total_with_limit(self):
        """Test total calculation with limit"""
        limit = 1000
        total = self.pwd.total(1, limit=limit)
        self.assertEqual(total, limit)

    def test_total_limit_greater_than_actual(self):
        """Test total when limit is greater than actual total"""
        total_no_limit = self.pwd.total(1)
        total_with_high_limit = self.pwd.total(1, limit=total_no_limit * 2)
        self.assertEqual(total_with_high_limit, total_no_limit)

    def test_invalid_type_password(self):
        """Test generator with invalid type_password"""
        # Type 5 is invalid, should handle gracefully or raise error
        gen = self.pwd.generator(5, limit=1)
        passwords = list(gen)
        # Generator should not yield anything for invalid type
        self.assertEqual(len(passwords), 0)

    def test_generator_produces_different_passwords(self):
        """Test that generator produces different passwords"""
        gen = self.pwd.generator(1, limit=20)
        passwords = list(gen)
        # Check that all passwords are unique (for this small sample)
        unique_passwords = set(passwords)
        self.assertEqual(len(passwords), len(unique_passwords))

    def test_password_min_length(self):
        """Test that all generated passwords meet minimum length"""
        gen = self.pwd.generator(4, limit=50)
        for pwd in gen:
            self.assertGreaterEqual(len(pwd), 8)

    def test_password_max_length(self):
        """Test that all generated passwords don't exceed maximum length"""
        gen = self.pwd.generator(4, limit=50)
        for pwd in gen:
            self.assertLessEqual(len(pwd), 15)


if __name__ == '__main__':
    unittest.main()
