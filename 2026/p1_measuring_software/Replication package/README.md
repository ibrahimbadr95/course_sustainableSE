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

EnergiBridge is the power measurement tool used by this experiment. It must be installed and available in your `PATH`.

**Step 1 — Install Rust (if not already installed):**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Step 2 — Install EnergiBridge from source:**
```bash
cargo install --git https://github.com/tdurieux/EnergiBridge energibridge
```



---

## Before Running

To ensure clean and reproducible measurements:

1. **Fix screen brightness** — set it to a consistent level manually before starting
2. **Minimise background processes** — close unnecessary apps (Slack, Spotify, etc.)
3. **Disable notifications** — enable Do Not Disturb
4. **Connect to power** — plug in your laptop to avoid battery throttling effects
5. **Ensure all three browsers are installed** and can open without login prompts

---

## Running the Experiment

Navigate into the `Replication package` directory first, then run the script:

```bash
cd "2026/p1_measuring_software/Replication package"
python3 code.py
```

The script will:
1. Warm up the CPU for a few seconds
2. Randomly shuffle the order of browser runs to avoid ordering bias
3. For each run: open the browser, wait 15s to stabilise, record power for 180s, then close the browser and cool down

---

## Output

Each run produces a CSV file in the current directory:

```
power_data_Brave_run1.csv
power_data_Chrome_run1.csv
power_data_Firefox_run1.csv
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
