from loader import bot
from telebot.custom_filters import StateFilter  # noqa
import handlers  # noqa
from utils.set_bot_commands import set_default_commands


if __name__ == "__main__":
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    bot.infinity_polling()
