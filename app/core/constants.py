from app.core.user_roles_enum import UserRoles

ALLOWED_USER_ROLES = [role.value for role in UserRoles]
ALLOWED_CENT_COINS = [5, 10, 20, 50, 100]

# JWT token related
ACCESS_TOKEN_EXPIRE_MINUTES = 3600
ALGORITHM = "HS256"
SECRET_KEY = "33a1b8783c1c9d8afb2be7664cd1b9cc8d06511ff17a1b029d5068c40f5927a6"
