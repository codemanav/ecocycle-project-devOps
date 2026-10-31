"""Ghost Hunter CLI — for humans, scripts, and coding agents (see SKILL.md).

  ghosthunter status                       health of every service in the target
  ghosthunter diagnose                     investigate + ask Gemma 4 for root cause and action (changes nothing)
  ghosthunter recover --dry-run            same as diagnose, plus allowlist validation of the proposed action
  ghosthunter recover --yes                full loop: diagnose -> act -> verify, then write a postmortem
  ghosthunter watch                        continuous watch mode (handles incidents on its own)
  ghosthunter scenarios                    list fault-injection scenarios in the target
  ghosthunter haunt A                      inject a scenario;  `ghosthunter haunt reset` to undo
  ghosthunter postmortems [--show N]       list / print Gemma-written postmortems

Global flags: --json (machine-readable output), --backend gemini|ollama, --target path/to/target.yaml,
              --chart (sample metrics for ~20s and send the chart image to Gemma; slower, multimodal)
Exit codes: 0 ok / healthy / recovered, 1 unhealthy or not recovered, 2 proposed action rejected, 3 usage/config error.
"""
import argparse, json, os, sys, time

def _pre_args():
    """--backend/--target must be set in the environment before core/model are imported."""
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--backend"); p.add_argument("--target")
    a, _ = p.parse_known_args()
    if a.backend: os.environ["GHOSTHUNTER_MODEL_BACKEND"] = a.backend
    if a.target: os.environ["GHOSTHUNTER_TARGET"] = os.path.abspath(a.target)

_pre_args()
import agent, core, metrics, model, postmortem  # noqa: E402

def out(args, data, human):
    if args.json:
        print(json.dumps(data, indent=1, default=str))
    else:
        print(human)

def _chart(args):
    if not args.chart:
        return None
    metrics.boost()
    print(f"sampling container metrics for {args.chart_seconds}s for the chart…", file=sys.stderr)
    time.sleep(args.chart_seconds)
    return metrics.chart_png()

def _thought_printer(args):
    if args.json or not args.think:
        return None
    return lambda c: print(c, end="", file=sys.stderr, flush=True) if c else print("\n💭 ", end="", file=sys.stderr)

def cmd_status(args):
    h = core.check_health()
    bad = core.unhealthy(h)
    out(args, {"target": core.TARGET["name"], "health": h, "healthy": not bad},
        f"🎃 {core.TARGET['name']}\n" + "\n".join(f"  {'🟢' if v == 'UP' else '👻'} {k}: {v}" for k, v in h.items()))
    return 1 if bad else 0

def _diagnose(args):
    h = core.check_health()
    bad = core.unhealthy(h)
    if not bad and not args.force:
        return h, None, None, None
    ev = core.collect_evidence(bad)
    chart = _chart(args)
    t = time.time()
    d = model.decide(ev, chart=chart, on_thought=_thought_printer(args))
    d["_model"] = model.describe(); d["_seconds"] = round(time.time() - t, 1)
    ok, why = core.validate(d)
    return h, d, ok, why

def _fmt_decision(d, ok, why):
    lines = [f"🔮 root cause : {d.get('root_cause')}",
             f"🪄 action     : {d.get('action')} {d.get('params')}  (confidence {d.get('confidence')})",
             f"🛡  allowlist  : {'allowed' if ok else 'REJECTED — ' + why}"]
    if d.get("chart_observation") and d["chart_observation"] != "no chart":
        lines.append(f"📈 chart      : {d['chart_observation']}")
    lines += ["🕯  evidence   :"] + [f"     - {e}" for e in d.get("evidence", [])]
    lines.append(f"   ({d.get('_model')}, {d.get('_seconds')}s)")
    return "\n".join(lines)

def cmd_diagnose(args):
    h, d, ok, why = _diagnose(args)
    if d is None:
        out(args, {"healthy": True, "health": h}, "🟢 all services healthy — no ghosts here (use --force to diagnose anyway)")
        return 0
    out(args, {"health": h, "decision": d, "allowed": ok, "validation": why},
        "👻 unhealthy: " + ", ".join(f"{k}={v}" for k, v in h.items() if v != "UP") + "\n" + _fmt_decision(d, ok, why))
    return 0 if ok else 2

def cmd_recover(args):
    if args.dry_run or not args.yes:
        rc = cmd_diagnose(args)
        if not args.dry_run and not args.json:
            print("\n(dry run — nothing changed. Re-run with --yes to let Ghost Hunter act.)")
        return rc
    if not core.unhealthy(core.check_health()):
        out(args, {"healthy": True}, "🟢 all services healthy — nothing to recover")
        return 0
    def emit(name, data, dt):
        if args.json or isinstance(data, bytes):
            return
        if name.startswith("reason"):
            print(_fmt_decision({**data, "_model": model.describe(), "_seconds": dt}, *core.validate(data)))
        else:
            print(f"⏱  {name} ({dt}s): {json.dumps(data, default=str)[:200]}")
    use_chart = bool(args.chart)
    if use_chart:
        metrics.boost(); time.sleep(args.chart_seconds)
    try:
        rec = agent.run_incident(emit, use_chart=use_chart, on_thought=_thought_printer(args), trigger="cli")
    except agent.Busy as e:
        out(args, {"busy": True, "message": str(e)}, f"⏸ {e} — try again shortly")
        return 1
    if rec.get("note") == "nothing wrong":
        out(args, {"healthy": True}, "🟢 healthy again before Ghost Hunter acted — nothing to do")
        return 0
    pm = None if args.no_postmortem else postmortem.write(rec)
    summary = {k: rec.get(k) for k in ("id", "recovered", "outcome", "duration", "decision", "verify")}
    summary["postmortem"] = str(pm) if pm else None
    out(args, summary, f"\n{'✅ exorcised' if rec['recovered'] else '❌ ' + str(rec.get('outcome'))} in {rec.get('duration')}s"
        + (f"\n📝 postmortem: {pm}" if pm else ""))
    return 0 if rec["recovered"] else 1

def cmd_watch(args):
    from watch import Watcher
    w = Watcher(slow_interval=args.interval, use_events=not args.no_events, use_chart=bool(args.chart),
                log=lambda m: print(time.strftime("%H:%M:%S"), m, flush=True))
    import signal
    signal.signal(signal.SIGTERM, lambda *_: w.stop())      # launchd/systemd/docker stop
    signal.signal(signal.SIGINT, signal.default_int_handler)  # Ctrl-C, even when started in the background
    w.start()
    try:
        while w.running:
            time.sleep(1)
    except KeyboardInterrupt:
        w.stop(); time.sleep(1)
    return 0

def cmd_scenarios(args):
    sc = core.scenarios()
    out(args, sc, "\n".join(f"  {k}: {v['title']} — {v.get('story', '')}" for k, v in sc.items()))
    return 0

def cmd_haunt(args):
    if args.scenario != "reset" and args.scenario not in core.scenarios():
        print(f"unknown scenario {args.scenario!r}; see `ghosthunter scenarios`", file=sys.stderr)
        return 3
    steps = core.inject(args.scenario)
    out(args, {"scenario": args.scenario, "steps": steps},
        ("🧹 reset:\n" if args.scenario == "reset" else f"👻 haunted with {args.scenario}:\n") + "\n".join(steps))
    return 0

def cmd_postmortems(args):
    files = postmortem.list_all()
    if args.show is not None:
        if not files or args.show >= len(files):
            print("no such postmortem", file=sys.stderr); return 3
        print(files[args.show].read_text()); return 0
    out(args, [str(f) for f in files], "\n".join(f"  [{i}] {f.name}" for i, f in enumerate(files)) or "  (none yet)")
    return 0

def main(argv=None):
    ap = argparse.ArgumentParser(prog="ghosthunter", description="🎃 Ghost Hunter — Gemma 4 incident response",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--backend", choices=["gemini", "ollama"], help="model backend (default: gemini)")
    ap.add_argument("--target", help="target YAML (default: targets/ecocycle.yaml)")
    ap.add_argument("--chart", action="store_true", help="send a metrics chart image to Gemma (multimodal)")
    ap.add_argument("--chart-seconds", type=int, default=20, help="metrics sampling time before charting")
    ap.add_argument("--think", action="store_true", help="stream Gemma's reasoning to stderr")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    d = sub.add_parser("diagnose"); d.add_argument("--force", action="store_true", help="diagnose even if healthy")
    d.set_defaults(fn=cmd_diagnose)
    r = sub.add_parser("recover")
    r.add_argument("--dry-run", action="store_true"); r.add_argument("--yes", action="store_true", help="allow actions")
    r.add_argument("--no-postmortem", action="store_true"); r.add_argument("--force", action="store_true")
    r.set_defaults(fn=cmd_recover)
    w = sub.add_parser("watch")
    w.add_argument("--interval", type=float, default=30, help="fallback health-check interval (s)")
    w.add_argument("--no-events", action="store_true", help="poll only; don't listen for Docker events")
    w.set_defaults(fn=cmd_watch)
    sub.add_parser("scenarios").set_defaults(fn=cmd_scenarios)
    h = sub.add_parser("haunt"); h.add_argument("scenario"); h.set_defaults(fn=cmd_haunt)
    p = sub.add_parser("postmortems"); p.add_argument("--show", type=int); p.set_defaults(fn=cmd_postmortems)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except Exception as e:
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 3

if __name__ == "__main__":
    sys.exit(main())
