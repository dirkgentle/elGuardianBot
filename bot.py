import datetime
import login
import pickle
import traceback

import praw


def update_log(mods, mods_backup_path):  # para respaldar los mods
    with open(mods_backup_path, 'wb') as my_backup:
        pickle.dump(mods, my_backup, protocol=pickle.HIGHEST_PROTOCOL)


def load_log(mods_backup_path):  # para recuperar los mods respaldados
    with open(mods_backup_path) as my_backup:
        return pickle.load(my_backup)


def output_log(text):  # lo uso para ver el output del bot
    output_log_path = "output_log.txt"
    with open(output_log_path, 'a') as myLog:
        s = "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
        s = s + text + "\n"
        myLog.write(s)


def get_mods_format(mods):
    s = ''
    for mod in mods:
        s = s + str(mod) + " -> " + str(mod.mod_permissions) + "\n\n"
    return s[:-2]


def get_reply(mods, mods_old):
    s = '**Antes:**\n\n'
    s = s + get_mods_format(mods_old) + "\n\n"
    s = s + "**Ahora:**\n\n"
    s = s + get_mods_format(mods) + "\n\n"
    s = s + "*****\n\n"
    s = s + "*I stand for democracy*"
    return s


def send_alert(mods, mods_old, reddit, current_subreddit, concerned_redditors):
    body = get_reply(mods, mods_old)
    subject = "Cambio en el modteam de /r/" + current_subreddit
    output_log(body)
    output_log(subject)
    for concerned_redditor in concerned_redditors:
        reddit.redditor(concerned_redditor).message(subject, body)
        output_log('To: ' + str(concerned_redditor))


def main():
    mods_backup_path = 'mods.pickle'
    current_subreddit = 'Uruguay'
    concerned_redditors = ['DirkGentle']

    reddit = praw.Reddit(
        client_id=login.client_id,
        client_secret=login.client_secret,
        password=login.password,
        username=login.username,
        user_agent='testcript for /u/elGuardianBot'
    )
    output_log('Login to reddit as: ' + reddit.user.me().name)

    try:
        mods_old = load_log(mods_backup_path)
#        output_log('Successful load from backup file')
    except Exception:
        mods_old = reddit.subreddit(current_subreddit).moderator()
        update_log(mods_old, mods_backup_path)
        output_log('Error reading file, getting mods from the internet')
        output_log("Mods of /r/" + current_subreddit)
        output_log(get_mods_format(mods_old))
        return

    mods = reddit.subreddit(current_subreddit).moderator()
    if set(mods) != set(mods_old):
        send_alert(
            mods, mods_old, reddit, current_subreddit, concerned_redditors
        )
        update_log(mods, mods_backup_path)
    else:
        for i in range(len(mods)):
            if mods[i].mod_permissions != mods_old[i].mod_permissions:
                send_alert(
                    mods,
                    mods_old,
                    reddit,
                    current_subreddit,
                    concerned_redditors
                )
                update_log(mods, mods_backup_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exception:
        output_log(str(exception))
        output_log(traceback.format_exc())
