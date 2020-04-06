import threading

def TIMEOUT_COMMAND(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, os, time, signal
    cmd = command.split(" ")
    print(cmd)
    start = datetime.datetime.now()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        time.sleep(0.2)
        now = datetime.datetime.now()
        if (now - start).seconds> timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            print("ERROR: Timeout, setting %d seconds"%timeout)
            return False
    result = process.stderr.readlines() 
    if result != []:
        print("ERROR: %s"%result[0].decode())
        return False
    return True

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, name, article):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.article = article
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数 
        self.article.download_pdf()

if __name__ == "__main__":
    result = TIMEOUT_COMMAND('curl 1.jpg -i 1.jpg --fail --silent --show-error', 30)
    print(result)