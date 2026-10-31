"""Background sampler of `docker stats` + chart rendering for Gemma's multimodal input."""
import io, json, subprocess, threading, time
from collections import defaultdict, deque
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from core import CFG

WINDOW_S = 120
_hist = defaultdict(lambda: deque(maxlen=200))  # name -> (ts, cpu%, mem_mb, limit_mb)
_lock = threading.Lock()
_started = False

def _mb(s):
    s = s.strip()
    for unit, f in (("GiB", 1024), ("MiB", 1), ("KiB", 1 / 1024), ("GB", 1000), ("MB", 1), ("kB", 1 / 1000), ("B", 1 / 2**20)):
        if s.endswith(unit):
            return float(s[: -len(unit)]) * f
    return 0.0

def _loop():
    names = [c for c in CFG["containers"] if c != "ecocycle-frontend"]
    while True:
        try:
            out = subprocess.run(["docker", "stats", "--no-stream", "--format", "{{json .}}", *names],
                                 capture_output=True, text=True, timeout=15).stdout
            now = time.time()
            seen = set()
            for line in out.splitlines():
                d = json.loads(line)
                used, limit = d["MemUsage"].split("/")
                with _lock:
                    _hist[d["Name"]].append((now, float(d["CPUPerc"].rstrip("%") or 0), _mb(used), _mb(limit)))
                seen.add(d["Name"])
            # stopped containers don't report: record zeros so the drop is visible on the chart
            for n in set(names) - seen:
                with _lock:
                    _hist[n].append((now, 0.0, 0.0, 0.0))
        except Exception:
            pass
        time.sleep(2)

def start():
    global _started
    if not _started:
        _started = True
        threading.Thread(target=_loop, daemon=True).start()

def chart_png():
    """Render CPU% and memory MB per container over the last WINDOW_S seconds. Returns PNG bytes or None."""
    now = time.time()
    with _lock:
        data = {n: [p for p in h if now - p[0] <= WINDOW_S] for n, h in _hist.items()}
    data = {n: pts for n, pts in data.items() if len(pts) >= 2}
    if not data:
        return None
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    for n, pts in sorted(data.items()):
        t = [p[0] - now for p in pts]
        ax1.plot(t, [p[1] for p in pts], label=n)
        ax2.plot(t, [p[2] for p in pts], label=n)
        lim = [p[3] for p in pts if p[3] and p[3] < 4000]  # only draw real (small) limits
        if lim:
            ax2.axhline(lim[-1], ls="--", lw=1, color=ax2.lines[-1].get_color())
    ax1.set_ylabel("CPU %"); ax1.set_title("EcoCycle containers, last 2 min (0 = now)")
    ax2.set_ylabel("Memory MB (dashed = limit)"); ax2.set_xlabel("seconds")
    ax1.legend(fontsize=7, ncol=3, loc="upper left")
    for a in (ax1, ax2):
        a.grid(alpha=0.3)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90)
    plt.close(fig)
    return buf.getvalue()
