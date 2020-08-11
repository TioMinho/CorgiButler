# ==== Libraries ====
import telegram
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, Job
from conf.settings import TELEGRAM_TOKEN, GROUP_ID, MARIANA_ID, MINHO_ID

from commands import *
from jobs import *

from time import time
from datetime import datetime, timedelta, time

import pickle
# ===================

# ==== Global Variables ====
LIST_OF_ADMINS = [GROUP_ID, MARIANA_ID, MINHO_ID]

JOBS_PICKLE = 'tmp/job_tuples.pickle'
JOB_DATA  = ('callback', 'interval', 'repeat', 'context', 'days', 'name', 'tzinfo')
JOB_STATE = ('_remove', '_enabled')
# ==========================

# ==== Functions ====
# Loads previously saved Jobs to continue their pooling
def load_jobs(jq):
    with open(JOBS_PICKLE, 'rb') as fp:
        while True:
            try:
                next_t, data, state = pickle.load(fp)
            except EOFError:
                break  # loaded all jobs

            # New object with the same data
            job = Job(**{var: val for var, val in zip(JOB_DATA, data)})

            # Restore the state it had
            for var, val in zip(JOB_STATE, state):
                attribute = getattr(job, var)
                getattr(attribute, 'set' if val else 'clear')()

            job.job_queue = jq
            jq._put(job, next_t-time())
# --

# Saves Jobs that are still running (to keep tracking of the intervals)
def save_jobs(jq):
    with jq._queue.mutex:
        if jq:
            job_tuples = jq._queue.queue
        else:
            job_tuples = []

        with open(JOBS_PICKLE, 'wb') as fp:
            for next_t, job in job_tuples:
                # This job is always created at the start
                if job.name in ['save_jobs_job', 'agua_reminder']:
                    continue

                # Threading primitives are not pickleable
                data  = tuple(getattr(job, var) for var in JOB_DATA)
                state = tuple(getattr(job, var).is_set() for var in JOB_STATE)

                # Pickle the job
                pickle.dump((next_t, data, state), fp)
# --

# Wrapper to save all Jobs within a context
def save_jobs_job(context):
    save_jobs(context.job_queue)
# --
# ===================

# ===== MAIN =====
def main():
    # Creates the updater to get the Bot token and the dispatcher
    #   who will handle the commands and messages received
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Creates the JobQueue handler
    jobs = updater.job_queue

    # Add listeners/handlers for specific commands
    dispatcher.add_handler(CommandHandler('start',          start))
    dispatcher.add_handler(CommandHandler('foto',           foto))
    dispatcher.add_handler(CommandHandler('compra',         compra, pass_args=True))
    dispatcher.add_handler(CommandHandler('list_compras',   list_compras))
    dispatcher.add_handler(CommandHandler('agua',           agua, pass_args=True))
    dispatcher.add_handler(CommandHandler('falta',          falta, pass_args=True))
    dispatcher.add_handler(CommandHandler('falta_remove',   falta_remove, pass_args=True))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Add jobs to the JobQueue
    jobs.run_repeating(save_jobs_job, timedelta(minutes=1))
    jobs.run_daily(agua_reminder, time(hour=10, minute=0, second=0))

    # This checks if no Jobs pickle has still been created
    try:
        load_jobs(jobs)
    except FileNotFoundError:
        pass # First run

    # Start the updater and put it in idle mode
    updater.start_polling()
    updater.idle()

    # Save current running Jobs if the process is stopped
    save_jobs(jobs)
# --

# ===================
if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()
# ===================
