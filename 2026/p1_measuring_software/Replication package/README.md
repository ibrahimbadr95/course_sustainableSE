# Replication Package — Browser Energy Consumption Experiment

This experiment measures and compares the energy consumption of **Brave**, **Chrome**, and **Firefox** while streaming a YouTube video on macOS.

---

## Requirements

### System
- macOS (Apple Silicon or Intel)
- Python 3.10+
- The following browsers installed:
  - [Google Chrome](https://www.google.com/chrome/)
  - [Firefox](https://www.mozilla.org/firefox/)
  - [Brave Browser](https://brave.com/)

### EnergiBridge

EnergiBridge is the power measurement tool used by this experiment.

**Step 1 — Install Rust (if not already installed):**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Step 2 — Install EnergiBridge from source:**
```bash
cargo install --git https://github.com/tdurieux/EnergiBridge energibridge
```

**Step 3 — Add EnergiBridge to your PATH:**
```bash
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verify the installation:
```bash
energibridge --version
```

---

## Before Running

Only two manual steps are required — everything else is handled automatically by the script:

1. **Disable auto-brightness** — go to System Settings → Displays and turn off "Automatically adjust brightness" to prevent macOS overriding the fixed brightness level
2. **Enable Do Not Disturb** — to prevent notifications interfering during measurements
3. **Connect to power** — plug in your laptop to avoid battery throttling effects
4. **Ensure all three browsers are installed** and can open without login prompts

---

## Running the Experiment

Navigate into the `Replication package` directory first, then run the script:

```bash
cd "2026/p1_measuring_software/Replication package"
python3 code.py
```

The script will automatically:
1. Create the `results/` output directory
2. Fix screen brightness at a consistent level
3. Quit known background apps (Slack, Teams, Spotify, browsers, etc.) to minimise interference
4. Warm up the CPU for thermal stabilisation
5. Randomly shuffle the order of browser runs to avoid ordering bias
6. For each run: open the browser, wait 15s to stabilise, record power for 180s, cool down, then repeat
7. Show a live progress bar for every timed phase
8. Restore brightness and reopen background apps when finished

---

## Output

Each run produces a CSV file inside the `results/` directory:

```
results/power_data_Brave_run1.csv
results/power_data_Chrome_run1.csv
results/power_data_Firefox_run1.csv
...
```

Each file contains timestamped power readings collected by EnergiBridge.

---

## Configuration

You can adjust the experiment parameters at the top of `code.py`:

| Parameter | Default | Description |
|---|---|---|
| `RUNS_PER_BROWSER` | 30 | Number of trials per browser |
| `STABILIZATION_TIME` | 15s | Wait time after browser opens |
| `MEASUREMENT_SECONDS` | 180s | Duration of power recording |
| `COOLDOWN_TIME` | 60s | Rest period between runs |
| `WARM_UP_TIME` | 300s | CPU warm-up duration |
| `BRIGHTNESS_LEVEL` | 0.5 | Fixed screen brightness (0.0–1.0) |
| `BACKGROUND_APPS` | see code | List of apps to quit before the experiment |
