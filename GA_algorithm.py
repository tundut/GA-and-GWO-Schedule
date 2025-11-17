# GA.py
import random, time, tkinter as tk
from algorithm import create_individual, repair, fitness, selection, crossover, mutate

def genetic_algorithm(teachers, classes, subjects, rooms, timeslots, log,
                      pop_size=60, generations=200, mutation_rate=0.2):

    # Khởi tạo quần thể ban đầu
    population = [
        create_individual(classes, teachers, rooms, timeslots, subjects)
        for _ in range(pop_size)
    ]

    best_fit, best_ind, stagnation = 0, None, 0
    start = time.time()
    history = []

    for gen in range(generations):

        # ---------------------------------------------
        # Tính fitness
        # ---------------------------------------------
        fits = [fitness(ind, teachers, rooms, classes, subjects) for ind in population]

        # Lấy elite (1 cá thể tốt nhất)
        elites = sorted(zip(fits, population), key=lambda x: x[0], reverse=True)[:1]
        best_current_fit, best_current_ind = elites[0]
        new_pop = [best_current_ind]  # elitism

        # Theo dõi tốt nhất toàn bộ quá trình
        if best_current_fit > best_fit:
            best_fit, best_ind = best_current_fit, best_current_ind
            stagnation = 0
        else:
            stagnation += 1

        history.append(best_fit)

        # ---------------------------------------------
        # Sinh thế hệ mới
        # ---------------------------------------------
        while len(new_pop) < pop_size:
            p1, p2 = selection(population, fits)
            c1, c2 = crossover(p1, p2)

            # --- Mutation (thứ tự chuẩn) ---
            c1 = mutate(c1, mutation_rate, teachers, rooms, timeslots, subjects)
            c2 = mutate(c2, mutation_rate, teachers, rooms, timeslots, subjects)

            # --- Repair (chỉ 1 lần sau mutation) ---
            c1 = repair(c1, teachers, rooms, timeslots, subjects)
            c2 = repair(c2, teachers, rooms, timeslots, subjects)

            new_pop += [c1, c2]

        # Cắt đúng số lượng quần thể
        population = new_pop[:pop_size]

        # ---------------------------------------------
        # Cơ chế chống mắc kẹt local optimum
        # ---------------------------------------------
        if stagnation >= 30:
            # loại 5 cá thể kém nhất
            bad_remove = 5
            population = population[:-bad_remove]

            # thêm cá thể hoàn toàn mới
            for _ in range(bad_remove):
                population.append(create_individual(classes, teachers, rooms, timeslots, subjects))

            stagnation = 0
            mutation_rate = min(0.5, mutation_rate + 0.05)

        # ---------------------------------------------
        # Log theo từng 20 thế hệ
        # ---------------------------------------------
        if gen % 20 == 0:
            avg_fit = sum(fits) / len(fits)
            log.insert(tk.END, f"GA Gen {gen}: best={best_fit:.4f}, avg={avg_fit:.4f}\n")
            log.see(tk.END)
            log.update()

    # ---------------------------------------------
    # Kết thúc
    # ---------------------------------------------
    elapsed = time.time() - start
    log.insert(tk.END, f"\n🎯 GA Fitness cao nhất: {best_fit:.4f} (Time: {elapsed:.2f}s)\n")

    return best_ind, best_fit, history
