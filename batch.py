from subprocess import Popen, PIPE
import time

for i in range(0, 400):
    text = '{{"type": "alias", "creator": null, "specificChatroom": null, "body": "{}", "suppress": false}}\n'.format(str(i)).encode()
    #t2 = '{{"type": "create_chatroom", "creator": {}, "specificChatroom": null, "body": "{}", "suppress": false}}\n'.format(str(i), str(i)).encode()
    proc = Popen(['python', 'client.py'], stdin=PIPE, stdout=PIPE)

    proc.stdin.write(text)
    proc.stdin.flush()
    #proc.stdin.write(t2)
    proc.stdin.flush()

    time.sleep(.04)
input()