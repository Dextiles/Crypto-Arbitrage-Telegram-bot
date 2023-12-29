from vedis import Vedis
from config_data import config
from states.userstates import arbitrage_states


def get_current_state(user_id):
    with Vedis(config.STATES_db) as db:
        try:
            return db[user_id].decode()
        except KeyError:
            return arbitrage_states.CryptoArbitrageFull.INVOKE.value


def set_state(user_id, value):
    with Vedis(config.STATES_db) as db:
        try:
            db[user_id] = value
            return True
        except Exception as ex:
            with open('database/error.log', 'a') as log_file:
                log_file.write(str(ex))
            with open(config.STATES_db, 'w'):
                pass
            set_state(user_id, value)
            return True
