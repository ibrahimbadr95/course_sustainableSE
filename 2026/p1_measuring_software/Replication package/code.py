import time
import random
import subprocess
import ctypes
from pathlib import Path

# ===============================
# CONFIGURATION
# ===============================

VIDEO_URL = "https://www.youtube.com/watch?v=N22Vd0DY3Lw&autoplay=1&mute=1"

BRIGHTNESS_LEVEL = 0.5       # fixed brightness for all runs
ORIGINAL_BRIGHTNESS = 1.0    # restored after experiment

RUNS_PER_BROWSER = 30
STABILIZATION_TIME = 15      # seconds before measurement
MEASUREMENT_SECONDS = 180    # measurement duration in seconds
COOLDOWN_TIME = 60          # seconds between runs
WARM_UP_TIME = 300

BROWSERS = ["Brave", "Chrome", "Firefox"]

RESULTS_DIR = Path(__file__).parent / "results"

BACKGROUND_APPS = [
    "Slack", "Spotify", "zoom.us", "MSTeams", "Discord",
    "WhatsApp", "Telegram", "Skype", "Messages", "Mail",
    "Dropbox", "OneDrive", "Google Drive", "Steam", "Notion",
    "Google Chrome", "Firefox", "Brave Browser",
]


ds = ctypes.CDLL('/System/Library/PrivateFrameworks/DisplayServices.framework/DisplayServices')
ds.DisplayServicesSetBrightness.argtypes = [ctypes.c_uint32, ctypes.c_float]
ds.DisplayServicesSetBrightness.restype = ctypes.c_int32

def set_brightness(level: float):
    result = ds.DisplayServicesSetBrightness(1, ctypes.c_float(level))
    if result != 0:
        print(f"Warning: could not set brightness (error {result})")


def get_running_apps():
    result = subprocess.run(
        ["osascript", "-e",
         'tell application "System Events" to get name of every process whose background only is false'],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return [a.strip() for a in result.stdout.strip().split(",")]
    return []

def quit_background_apps():
    running = get_running_apps()
    quit_apps = []
    for app in BACKGROUND_APPS:
        if app in running:
            subprocess.run(["osascript", "-e", f'quit app "{app}"'], capture_output=True)
            time.sleep(0.5)
            subprocess.run(["killall", app], capture_output=True) 
            quit_apps.append(app)
            print(f"  Quit {app}")
    return quit_apps

def reopen_apps(apps):
    for app in apps:
        subprocess.run(["open", "-a", app], capture_output=True)
        print(f"  Reopened {app}")


BAR_WIDTH = 35

def bar(elapsed, total):
    pct = min(elapsed / total, 1.0)
    filled = int(BAR_WIDTH * pct)
    bar = "█" * filled + "░" * (BAR_WIDTH - filled)
    remaining = max(0, total - elapsed)
    return f"[{bar}] {int(pct*100):3d}%  {int(elapsed):3d}/{total}s  ({int(remaining)}s left)"

def progress_sleep(seconds, label, proc=None):
    start = time.time()
    while True:
        elapsed = min(time.time() - start, seconds)
        print(f"\r  {label} {bar(elapsed, seconds)}", end="", flush=True)
        done = (proc.poll() is not None) if proc is not None else (elapsed >= seconds)
        if done:
            break
        time.sleep(0.5)
    if proc is not None:
        proc.wait()
    print(f"\r  {label} {bar(seconds, seconds)}{' ' * 12}")

# ===============================
# WARMUP
# ===============================

def warm_up(duration_in_seconds):
    print(f"Warming up system for {duration_in_seconds} seconds...")
    start_time = time.time()
    last_print = -1
    while True:
        a, b = 0, 1
        for _ in range(20000):
            a, b = b, a + b
        elapsed = min(time.time() - start_time, duration_in_seconds)
        if int(elapsed) != last_print:
            print(f"\r  Warming up  {bar(elapsed, duration_in_seconds)}", end="", flush=True)
            last_print = int(elapsed)
        if elapsed >= duration_in_seconds:
            break
    print(f"\r  Warming up  {bar(duration_in_seconds, duration_in_seconds)}{' ' * 12}")
    print("  Done.\n")

# ===============================
# BROWSER LAUNCHER
# ===============================

def launch_browser(browser, url):
    if browser == "Chrome":
        cmd = [
            "open", "-n", "-a", "Google Chrome",
            "--args",
            "--autoplay-policy=no-user-gesture-required",
            f"--app={url}"   
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

    RESULTS_DIR.mkdir(exist_ok=True)

    set_brightness(BRIGHTNESS_LEVEL)
    print(f"Brightness fixed at {BRIGHTNESS_LEVEL}\n")

    print("Quitting background apps...")
    quit_apps = quit_background_apps()
    if not quit_apps:
        print("  None found.")
    progress_sleep(3, "Closing apps")

    warm_up(WARM_UP_TIME)

    print("Starting automated browser energy benchmark using Energibridge...\n")

    try:
        for overall_index, browser in enumerate(executions):

            run_counts[browser] += 1
            current_run = run_counts[browser]

            # Changed to .csv for Energibridge
            output_filename = str(RESULTS_DIR / f"power_data_{browser}_run{current_run}.csv")

            print(f"\nOverall {overall_index+1}/{len(executions)}")
            print(f"Testing {browser} (Run {current_run}/{RUNS_PER_BROWSER})")

            process_name = launch_browser(browser, VIDEO_URL)

            progress_sleep(STABILIZATION_TIME, "Stabilising ")

            # ===============================
            # ENERGIBRIDGE COMMAND
            # ===============================
            energibridge_cmd = [
                "energibridge",
                "-o", output_filename,
                "--summary",
                "sleep", str(MEASUREMENT_SECONDS)
            ]

            print(f"Recording power data to {output_filename}")
            proc = subprocess.Popen(energibridge_cmd)
            progress_sleep(MEASUREMENT_SECONDS, "Measuring   ", proc=proc)

            print(f"Closing {browser} cleanly...")
            subprocess.run(["osascript", "-e", f'quit app "{process_name}"'])
            progress_sleep(15, "Closing     ")
            subprocess.run(["killall", process_name], stderr=subprocess.DEVNULL)

            progress_sleep(COOLDOWN_TIME, "Cooling down")

    finally:
        set_brightness(ORIGINAL_BRIGHTNESS)
        print(f"\nBrightness restored to {ORIGINAL_BRIGHTNESS}")
        if quit_apps:
            print("Reopening background apps...")
            reopen_apps(quit_apps)

    print("\nData collection complete!")

if __name__ == "__main__":
    main()