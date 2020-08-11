# ==== Libraries ====
import telegram
from conf.settings import GROUP_ID

from commands import markdownfy
# ===================

# ===== Jobs =====
def agua_reminder(context):
    """ AGUA_REMINDER(CONTEXT)

        This is a daily job that checks the AGUA status in the house and send a notification in
        case there is no water still in the morning.
    """

    try:
        # Retrieves the current status
        with open("data/agua_status", "r") as f:
            status = int(f.read())

    except FileNotFoundError:   # If the file does not exists, the Job does nothing
        status = 1

    # If there is no water, the job sends a notification to the chat
    if not status:
        message = ("There is *NO* water at home :(\n"+
                    "Remember to buy a new refil and then send me `/agua yes` to register the purchase :)")

        context.bot.send_message(chat_id=GROUP_ID,
                                 text=markdownfy(message), parse_mode=telegram.ParseMode.MARKDOWN_V2)


# ================
