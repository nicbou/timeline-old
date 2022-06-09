from oauth2_provider.contrib.rest_framework import TokenMatchesOASRequirements
from rest_framework.permissions import IsAdminUser

AdminOrTokenMatchesOASRequirements = IsAdminUser | TokenMatchesOASRequirements