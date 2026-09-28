# ══════════════════════════════════════════════════
#  autocal.py — finds your wiring AND prints config
# ══════════════════════════════════════════════════
import time
import RPi.GPIO as GPIO

PHYS = {4:7, 5:29, 6:31, 12:32, 13:33, 16:36, 17:11, 18:12, 19:35,
        22:15, 23:16, 24:18, 25:22, 26:37, 27:13}

try:
    import config
    CAND = [config.IN1, config.IN2, config.IN3, config.IN4]
except Exception:
    CAND = [18, 6, 22, 25]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for p in CAND:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, GPIO.LOW)
print("[SAFETY] All pins LOW")

def ask(q):
    return (input(q).strip().lower() + "n")[0]

mapping, dead = {}, []

try:
    input("\nWheels off ground! ENTER to start...")
    for bcm in CAND:
        print(f"\n>> Pi pin {PHYS.get(bcm,'?')} (BCM {bcm}) — HIGH for 3s")
        GPIO.output(bcm, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(bcm, GPIO.LOW)
        l = ask("   LEFT  wheel? [f]wd/[b]wd/[n]one: ")
        r = ask("   RIGHT wheel? [f]wd/[b]wd/[n]one: ")
        if l == "n" and r == "n":
            dead.append(bcm)
        if l in ("f", "b"): mapping[("left", l)] = bcm
        if r in ("f", "b"): mapping[("right", r)] = bcm

    print("\n" + "=" * 55)
    print("  AUTO-CALIBRATION RESULT")
    print("=" * 55)

    if dead:
        print("[X] DEAD signal paths (nothing spun):")
        for b in dead:
            print(f"    BCM {b} — Pi physical pin {PHYS.get(b,'?')}")
        print("    Fix that wire/terminal first, run autocal again.")

    need = [("left","b"), ("left","f"), ("right","b"), ("right","f")]
    if not dead and all(k in mapping for k in need):
        IN1 = mapping[("left","b")];  IN2 = mapping[("left","f")]
        IN3 = mapping[("right","b")]; IN4 = mapping[("right","f")]
        print("\n[OK] FOUND EVERYTHING! Replace the 4 IN lines in config.py:\n")
        print("IN1 = %d   # Pi pin %s — Left  Motor Backward" % (IN1, PHYS.get(IN1,'?')))
        print("IN2 = %d   # Pi pin %s — Left  Motor Forward"  % (IN2, PHYS.get(IN2,'?')))
        print("IN3 = %d   # Pi pin %s — Right Motor Backward" % (IN3, PHYS.get(IN3,'?')))
        print("IN4 = %d   # Pi pin %s — Right Motor Forward"  % (IN4, PHYS.get(IN4,'?')))

        input("\nFINAL VERIFY — ENTER and watch it drive!")
        for name, hi in [("FORWARD",    [IN2, IN4]),
                         ("BACKWARD",   [IN1, IN3]),
                         ("TURN LEFT",  [IN1, IN4]),
                         ("TURN RIGHT", [IN2, IN3])]:
            print("   %s ..." % name)
            for p in hi: GPIO.output(p, GPIO.HIGH)
            time.sleep(2)
            for p in CAND: GPIO.output(p, GPIO.LOW)
            time.sleep(0.5)
        print("\nIf those 4 moves looked right -> paste lines into config.py, then:")
        print("   sudo pkill -9 -f python3 ; python3 main.py   DONE!")
    else:
        print("[!] Not all directions found:", [k for k in need if k not in mapping])
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    for p in CAND:
        GPIO.output(p, GPIO.LOW)
    GPIO.cleanup()
    print("[CLEANUP] done")
