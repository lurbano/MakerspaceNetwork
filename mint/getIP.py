import subprocess

def getIP():
    cmd = f'hostname -I'
    result = subprocess.run(cmd, shell = True, 
                            capture_output=True, text=True)
    # print(cmd)
    # print(result.stdout)
    ip = result.stdout.split(" ")
    return ip[0]

if __name__ == "__main__":
    x = getIP()
    print(f"ip: {x}")