package main

import (
	"fmt"
	"math/rand"
	"strings"
	"time"
)

var DAYS = []string{"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
var SHIFTS = []string{"morning", "afternoon", "evening"}
const MAX_DAYS_PER_EMP = 5
const MIN_PER_SHIFT = 2

type Employee struct {
	Prefs      map[string][]string
	DaysWorked int
}

// ✅ Inline employee list here
func sampleEmployees() map[string]*Employee {
	names := []struct {
		name  string
		prefs []string
	}{
		{"David", []string{"morning", "afternoon", "evening"}},
		{"Shyam", []string{"morning", "evening"}},
		{"Mary", []string{"afternoon"}},
		{"Gilbert", []string{"morning"}},
		{"Wayne", []string{"evening", "afternoon"}},
		{"Palmer", []string{"morning"}},
		{"Audrey", []string{"evening"}},
		{"Tasha", []string{"morning", "evening"}},
	}

	employees := make(map[string]*Employee)
	for _, e := range names {
		prefs := make(map[string][]string)
		for _, day := range DAYS {
			prefs[day] = make([]string, len(e.prefs))
			copy(prefs[day], e.prefs)
		}
		employees[e.name] = &Employee{Prefs: prefs, DaysWorked: 0}
	}
	return employees
}

func findEligible(employees map[string]*Employee, day, shift string, assigned map[string]map[string]bool) []string {
	result := []string{}
	for name, emp := range employees {
		if emp.DaysWorked >= MAX_DAYS_PER_EMP {
			continue
		}
		if assigned[day][name] {
			continue
		}
		for _, p := range emp.Prefs[day] {
			if p == shift {
				result = append(result, name)
				break
			}
		}
	}
	return result
}

func randomFill(employees map[string]*Employee, day string, needed int, assigned map[string]map[string]bool) []string {
	result := []string{}
	pool := []string{}
	for name, emp := range employees {
		if emp.DaysWorked < MAX_DAYS_PER_EMP && !assigned[day][name] {
			pool = append(pool, name)
		}
	}
	rand.Shuffle(len(pool), func(i, j int) { pool[i], pool[j] = pool[j], pool[i] })
	for i := 0; i < len(pool) && len(result) < needed; i++ {
		result = append(result, pool[i])
	}
	return result
}

func schedule(employees map[string]*Employee) map[string]map[string][]string {
	assignments := make(map[string]map[string][]string)
	assigned := make(map[string]map[string]bool)
	rand.Seed(time.Now().UnixNano())

	// initialize structures
	for _, day := range DAYS {
		assignments[day] = make(map[string][]string)
		assigned[day] = make(map[string]bool)
		for _, shift := range SHIFTS {
			assignments[day][shift] = []string{}
		}
	}

	// First pass: assign based on preferences
	for _, day := range DAYS {
		for _, shift := range SHIFTS {
			candidates := findEligible(employees, day, shift, assigned)
			// sort by fewest days worked (simple selection sort)
			for i := 0; i < len(candidates); i++ {
				for j := i + 1; j < len(candidates); j++ {
					if employees[candidates[i]].DaysWorked > employees[candidates[j]].DaysWorked {
						candidates[i], candidates[j] = candidates[j], candidates[i]
					}
				}
			}
			for len(assignments[day][shift]) < MIN_PER_SHIFT && len(candidates) > 0 {
				name := candidates[0]
				candidates = candidates[1:]
				assignments[day][shift] = append(assignments[day][shift], name)
				assigned[day][name] = true
				employees[name].DaysWorked++
			}
		}
	}

	// Second pass: fill randomly to meet min requirements
	for _, day := range DAYS {
		for _, shift := range SHIFTS {
			for len(assignments[day][shift]) < MIN_PER_SHIFT {
				needed := MIN_PER_SHIFT - len(assignments[day][shift])
				additional := randomFill(employees, day, needed, assigned)
				if len(additional) == 0 {
					break
				}
				for _, name := range additional {
					assignments[day][shift] = append(assignments[day][shift], name)
					assigned[day][name] = true
					employees[name].DaysWorked++
				}
			}
		}
	}

	return assignments
}

func printSchedule(assignments map[string]map[string][]string, employees map[string]*Employee) {
	fmt.Println("\nFinal weekly schedule:\n")
	for _, day := range DAYS {
		fmt.Printf("%s:\n", day)
		for _, shift := range SHIFTS {
			names := assignments[day][shift]
			if len(names) == 0 {
				fmt.Printf("  %-10s: (none)\n", strings.Title(shift))
			} else {
				fmt.Printf("  %-10s: %s\n", strings.Title(shift), strings.Join(names, ", "))
			}
		}
		fmt.Println()
	}
	fmt.Println("Employee summary (days worked):")
	for name, emp := range employees {
		fmt.Printf("  %s: %d days\n", name, emp.DaysWorked)
	}
}

func main() {
	employees := sampleEmployees()
	assignments := schedule(employees)
	printSchedule(assignments, employees)
}
