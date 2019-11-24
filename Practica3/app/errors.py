ERROR = -1
OK = 0
ERROR_CREDITCARD = 1
ERROR_EMAIL_USED = 2
ERROR_USER_NOT_EXIST = 3
ERROR_INCORRECT_PASSWORD = 4
ERROR_INTERNAL_BASKET = 5

def errorToString(errorcode):
	switcher = {
		ERROR: 'General error',
		OK: 'Success',
		ERROR_CREDITCARD: 'Credit card already in use.',
		ERROR_EMAIL_USED: 'Email already in use.',
		ERROR_USER_NOT_EXIST: 'User does not exist.',
		ERROR_INCORRECT_PASSWORD: 'Wrong password.',
		ERROR_INTERNAL_BASKET: 'Internal server error related to shopping cart.'
	}

	return switcher.get(errorcode, 'Error not defined')