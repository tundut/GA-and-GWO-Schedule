# GA.py
import random, time, tkinter as tk
from algorithm import create_individual, repair, fitness, selection, crossover, mutate

def genetic_algorithm(teachers, classes, subjects, rooms, timeslots, log,
                      pop_size=60, generations=200, mutation_rate=0.2):
    population = [create_individual(classes, teachers, rooms, timeslots, subjects)
                  for _ in range(pop_size)]
    best_fit, best_ind, stagnation = 0, None, 0
    start = time.time()
    history = []

    for gen in range(generations):
        fits = [fitness(ind, teachers, rooms, classes, subjects) for ind in population]
        elites = sorted(zip(fits, population), key=lambda x: x[0], reverse=True)[:1]
        new_pop = [e[1] for e in elites]

        while len(new_pop) < pop_size:
            p1, p2 = selection(population, fits)
            c1, c2 = crossover(p1, p2)
            c1 = mutate(c1, mutation_rate, teachers, rooms, timeslots)
            c2 = mutate(c2, mutation_rate, teachers, rooms, timeslots)
            c1 = repair(c1, teachers, rooms, timeslots, subjects)
            c2 = repair(c2, teachers, rooms, timeslots, subjects)
            new_pop += [c1, c2]

        population = new_pop[:pop_size]

        gen_best = elites[0][0]
        if gen_best > best_fit:
            best_fit, best_ind, stagnation = gen_best, elites[0][1], 0
        else:
            stagnation += 1

        history.append(best_fit)

        if stagnation >= 30:
            for _ in range(5):
                population.append(create_individual(classes, teachers, rooms, timeslots, subjects))
            stagnation = 0
            mutation_rate = min(0.5, mutation_rate + 0.05)

        if gen % 20 == 0:
            avg_fit = sum(fits) / len(fits)
            log.insert(tk.END, f"GA Gen {gen}: best={best_fit:.4f}, avg={avg_fit:.4f}\n")
            log.see(tk.END)
            log.update()

        if best_fit == 1.0:
            log.insert(tk.END, f"\n🎉 GA: Lịch hoàn hảo ở thế hệ {gen}!\n")
            break

    elapsed = time.time() - start
    log.insert(tk.END, f"\n🎯 GA Fitness cuối cùng: {best_fit:.4f} (Time: {elapsed:.2f}s)\n")
    return best_ind, best_fit, history
