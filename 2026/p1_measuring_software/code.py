import time
import random
import subprocess
import os

# ===============================
# CONFIGURATION
# ===============================

VIDEO_URL = "https://www.youtube.com/watch?v=N22Vd0DY3Lw&autoplay=1&mute=1"

RUNS_PER_BROWSER = 30
STABILIZATION_TIME = 15      # seconds before measurement
MEASUREMENT_SECONDS = 300     # measurement duration in seconds
COOLDOWN_TIME = 120          # seconds between runs

BROWSERS = ["Brave", "Chrome", "Firefox"]

# ===============================
# WARMUP
# ===============================

def warm_up(duration_in_seconds):
    print(f"Warming up system for {duration_in_seconds} seconds...")
    start_time = time.time()
    while time.time() - start_time < duration_in_seconds:
        a, b = 0, 1
        for _ in range(20000):
            a, b = b, a + b
    print("Warm-up complete.\n")

# ===============================
# BROWSER LAUNCHER
# ===============================

def launch_browser(browser, url):
    if browser == "Chrome":
        cmd = [
            "open", "-n", "-a", "Google Chrome",
            "--args",
            "--autoplay-policy=no-user-gesture-required",
            f"--app={url}"   # <--- FIX 1: Forces a fresh, single-window kiosk mode
        ]
        process_name = "Google Chrome"

    elif browser == "Firefox":
        cmd = [
            "open", "-n", "-a", "Firefox",
            "--args",
            url
        ]
        process_name = "Firefox"

    elif browser == "Brave":
        cmd = [
            "open", "-n", "-a", "Brave Browser", 
            "--args",
            "--autoplay-policy=no-user-gesture-required",
            f"--app={url}"  
        ]   
        process_name = "Brave Browser"

    subprocess.Popen(cmd)
    return process_name

# ===============================
# MAIN EXPERIMENT
# ===============================

def main():
    executions = BROWSERS * RUNS_PER_BROWSER
    random.shuffle(executions)

    run_counts = {browser: 0 for browser in BROWSERS}

    warm_up(120)  

    print("Starting automated browser energy benchmark...\n")

    for overall_index, browser in enumerate(executions):

        run_counts[browser] += 1
        current_run = run_counts[browser]

        output_filename = f"power_data_{browser}_run{current_run}.txt"

        print(f"\nOverall {overall_index+1}/{len(executions)}")
        print(f"Testing {browser} (Run {current_run}/{RUNS_PER_BROWSER})")

        process_name = launch_browser(browser, VIDEO_URL)

        print(f"Waiting {STABILIZATION_TIME}s for stabilization...")
        time.sleep(STABILIZATION_TIME)

        # Powermetrics command
        powermetrics_cmd = [
            "powermetrics",
            "--samplers", "tasks,cpu_power,gpu_power",
            "-i", "1000",
            "-n", str(MEASUREMENT_SECONDS)
        ]

        print(f"Recording power data to {output_filename} for {MEASUREMENT_SECONDS} seconds...")

        with open(output_filename, "w") as outfile:
            subprocess.run(powermetrics_cmd, stdout=outfile, stderr=subprocess.DEVNULL)

        print(f"Closing {browser} cleanly...")
        
        subprocess.run(["osascript", "-e", f'quit app "{process_name}"'])
        
        # Give the browser 2 seconds to save its state and close its windows
        time.sleep(15)
        
        # Safety net: Force kill any invisible background helper processes that got stuck
        subprocess.run(["killall", process_name], stderr=subprocess.DEVNULL)

        print(f"Cooling down for {COOLDOWN_TIME} seconds...")
        time.sleep(COOLDOWN_TIME)

    print("Data collection complete!")

if __name__ == "__main__":
    main()
