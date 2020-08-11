# == Libraries ==
import os
from dotenv import load_dotenv
# ===============

# == CONFIGURATIONS ==
# Loads the environment variables from '.env'
load_dotenv()

# Stores the environment variables as Python variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID       = int(os.getenv("GROUP_ID"))
MINHO_ID       = int(os.getenv("MINHO_ID"))
MARIANA_ID     = int(os.getenv("MARIANA_ID"))
# ===============
