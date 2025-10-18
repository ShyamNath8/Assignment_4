#!/usr/bin/env python3
"""
Employee schedule manager (Python)
Save as schedule.py
"""
import random
import argparse
from collections import defaultdict, Counter

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
SHIFTS = ["morning","afternoon","evening"]
MAX_DAYS_PER_EMP = 5
MIN_PER_SHIFT = 2


def parse_ranked(pref_str):
    """Parse a preference string. Examples:
    - "morning" -> ["morning"]
    - "morning,evening,afternoon" -> ["morning","evening","afternoon"]
    """
    parts = [p.strip().lower() for p in pref_str.split(",") if p.strip()]
    # validate
    res = [p for p in parts if p in SHIFTS]
    return res


def collect_input():
    employees = {}
    n = int(input("Number of employees: ").strip())
    for i in range(n):
        name = input(f"Employee #{i+1} name: ").strip()
        prefs = {}
        print(f"Enter preferences for {name}. For each day enter either a single shift (morning/afternoon/evening) or a comma-separated ranked list (e.g. 'morning,evening'). Leave blank for no preference.")
        for day in DAYS:
            s = input(f"  {day}: ").strip()
            prefs[day] = parse_ranked(s) if s else []
        employees[name] = {"prefs": prefs, "days_worked": 0}
    return employees


def sample_employees():
    # Produce 8 sample employees with varied preferences
    names = ["David","Shyam","Mary","Gilbert","Wayne","Palmer","Audrey","Tasha"]
    employees = {}
    random.seed(1)
    for name in names:
        prefs = {}
        for day in DAYS:
            # random single or ranked pref
            choice = random.choice([0,1,2])
            if choice == 0:
                prefs[day] = [random.choice(SHIFTS)]
            elif choice == 1:
                first = random.choice(SHIFTS)
                rest = [s for s in SHIFTS if s != first]
                prefs[day] = [first] + random.sample(rest, k=2)
            else:
                prefs[day] = []
        employees[name] = {"prefs": prefs, "days_worked": 0}
    return employees


def find_eligible(employees, day, shift, assigned):
    # eligible employees who prefer this shift for the day, not assigned that day, and under max days
    res = []
    for name, data in employees.items():
        if data['days_worked'] >= MAX_DAYS_PER_EMP:
            continue
        if name in assigned.get(day, set()):
            continue
        # if they prefer this shift today (preference list may be empty)
        prefs = data['prefs'].get(day, [])
        if shift in prefs:
            res.append(name)
    return res


def random_fill(employees, day, needed, assigned):
    # pick random eligible employees who are not assigned that day and haven't hit max days
    pool = [n for n,d in employees.items() if d['days_worked'] < MAX_DAYS_PER_EMP and n not in assigned.get(day, set())]
    random.shuffle(pool)
    selected = []
    for name in pool:
        if len(selected) >= needed:
            break
        selected.append(name)
    return selected


def schedule(employees):
    # assignments: day -> shift -> list of names
    assignments = {day: {shift: [] for shift in SHIFTS} for day in DAYS}
    assigned_by_day = {day: set() for day in DAYS}
    random.seed(42)

    # First pass: try to honor preferences by day and shift
    for day in DAYS:
        for shift in SHIFTS:
            # candidates who explicitly prefer this shift
            candidates = find_eligible(employees, day, shift, assigned_by_day)
            # sort to try to be fair: by fewest days worked first
            candidates.sort(key=lambda n: employees[n]['days_worked'])
            while len(assignments[day][shift]) < MIN_PER_SHIFT and candidates:
                pick = candidates.pop(0)
                assignments[day][shift].append(pick)
                assigned_by_day[day].add(pick)
                employees[pick]['days_worked'] += 1

    # Second pass: ensure MIN_PER_SHIFT by random assignment
    # Also handle employees who had a preference but couldn't be assigned because they later would be over quota
    for day in DAYS:
        for shift in SHIFTS:
            while len(assignments[day][shift]) < MIN_PER_SHIFT:
                needed = MIN_PER_SHIFT - len(assignments[day][shift])
                picks = random_fill(employees, day, needed, assigned_by_day)
                if not picks:
                    # no eligible employees left (all at max or assigned). Relax constraint: allow employees already assigned this day but under max days? no, requirement: no more than one shift per day.
                    break
                for p in picks:
                    assignments[day][shift].append(p)
                    assigned_by_day[day].add(p)
                    employees[p]['days_worked'] += 1

    # Third pass: deal with conflicts where employees had a pref but were not assigned to it because full
    # We'll iterate through employees and days, and if they have a pref for that day and are not assigned anywhere that day, try to place them in another shift same day or next day
    for name, data in employees.items():
        for i, day in enumerate(DAYS):
            if data['days_worked'] >= MAX_DAYS_PER_EMP:
                break
            # check if assigned that day
            if name in assigned_by_day[day]:
                continue
            prefs = data['prefs'].get(day, [])
            assigned_flag = False
            # try ranked preferences first (if provided)
            for pref_shift in prefs:
                if len(assignments[day][pref_shift]) < MIN_PER_SHIFT:
                    assignments[day][pref_shift].append(name)
                    assigned_by_day[day].add(name)
                    data['days_worked'] += 1
                    assigned_flag = True
                    break
            if assigned_flag:
                continue
            # try any shift same day with space (even if not preferred)
            for s in SHIFTS:
                if len(assignments[day][s]) < MIN_PER_SHIFT:
                    assignments[day][s].append(name)
                    assigned_by_day[day].add(name)
                    data['days_worked'] += 1
                    assigned_flag = True
                    break
            if assigned_flag:
                continue
            # try next day (one day ahead) if exists
            if i+1 < len(DAYS):
                next_day = DAYS[i+1]
                for s in SHIFTS:
                    if len(assignments[next_day][s]) < MIN_PER_SHIFT and name not in assigned_by_day[next_day] and data['days_worked'] < MAX_DAYS_PER_EMP:
                        assignments[next_day][s].append(name)
                        assigned_by_day[next_day].add(name)
                        data['days_worked'] += 1
                        assigned_flag = True
                        break
            # otherwise leave unassigned (no further action)

    return assignments, employees


def print_schedule(assignments, employees):
    print("\nFinal weekly schedule:\n")
    for day in DAYS:
        print(f"{day}:")
        for shift in SHIFTS:
            names = assignments[day][shift]
            print(f"  {shift.title():9}: {', '.join(names) if names else '(none)'}")
        print("")
    print("Employee summary (days worked):")
    for name, data in employees.items():
        print(f"  {name}: {data['days_worked']} days")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', action='store_true', help='Run sample demo with prefilled employees')
    args = parser.parse_args()

    if args.sample:
        employees = sample_employees()
        print("Running sample demo with auto-generated employee preferences...")
    else:
        employees = collect_input()

    assignments, employees = schedule(employees)
    print_schedule(assignments, employees)