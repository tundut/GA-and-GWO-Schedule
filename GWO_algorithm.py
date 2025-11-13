import random, time, tkinter as tk
from algorithm import create_individual, repair, fitness

def gwo_algorithm(teachers, classes, subjects, rooms, timeslots, log,
                  pop_size=60, generations=200):
    """
    Grey Wolf Optimizer (GWO) cho bài lập lịch TKB (phiên bản chuẩn rời rạc)
    """
    population = [
        repair(create_individual(classes, teachers, rooms, timeslots, subjects),
               teachers, rooms, timeslots, subjects)
        for _ in range(pop_size)
    ]
    start = time.time()
    best_ind, best_fit = None, 0
    stagnation = 0
    history = []

    # Precompute lookups
    timeslot_to_idx = {s: i for i, s in enumerate(timeslots)}
    valid_teachers_by_sub = {}
    valid_teachers_index = {}
    for t, d in teachers.items():
        for sub in d.get("subjects", []):
            valid_teachers_by_sub.setdefault(sub, []).append(t)
    for sub, lst in valid_teachers_by_sub.items():
        valid_teachers_index[sub] = {v: i for i, v in enumerate(lst)}
    valid_rooms_by_subtype = {}
    valid_rooms_index = {}
    for r, d in rooms.items():
        valid_rooms_by_subtype.setdefault(d.get("type"), []).append(r)
    for st, lst in valid_rooms_by_subtype.items():
        valid_rooms_index[st] = {v: i for i, v in enumerate(lst)}

    for gen in range(generations):
        fits = [fitness(ind, teachers, rooms, classes, subjects) for ind in population]
        sorted_pack = sorted(zip(fits, population), key=lambda x: x[0], reverse=True)
        
        # Elite Selection - Bảo tồn các cá thể tốt nhất
        elites = sorted_pack[:3]
        alpha = elites[0][1]
        beta = elites[1][1] if len(elites) > 1 else alpha
        delta = elites[2][1] if len(elites) > 2 else alpha
        
        gen_best = sorted_pack[0][0]
        if gen_best > best_fit:
            best_fit, best_ind, stagnation = gen_best, alpha, 0
        else:
            stagnation += 1

        a = 2 - 2 * gen / generations
        num_slots = len(timeslots)
        new_population = []
        rand = random.random
        rrand = random.randrange
        for wolf in population:
            new_wolf = []
            for i in range(len(wolf)):
                cls, sub, teacher, room, slot = wolf[i]
                # Timeslot update
                xi = timeslot_to_idx.get(slot, rrand(num_slots))
                x_alpha_slot = timeslot_to_idx.get(alpha[i][4], xi)
                x_beta_slot = timeslot_to_idx.get(beta[i][4], xi)
                x_delta_slot = timeslot_to_idx.get(delta[i][4], xi)
                A1, C1 = 2 * a * rand() - a, 2 * rand()
                A2, C2 = 2 * a * rand() - a, 2 * rand()
                A3, C3 = 2 * a * rand() - a, 2 * rand()
                D_alpha = abs(C1 * x_alpha_slot - xi)
                D_beta = abs(C2 * x_beta_slot - xi)
                D_delta = abs(C3 * x_delta_slot - xi)
                X1 = x_alpha_slot - A1 * D_alpha
                X2 = x_beta_slot - A2 * D_beta
                X3 = x_delta_slot - A3 * D_delta
                X_new = (X1 + X2 + X3) / 3.0
                new_idx = int(round(max(0, min(num_slots - 1, X_new))))
                new_slot = timeslots[new_idx]

                # Teacher update
                valid_teachers = valid_teachers_by_sub.get(sub)
                if not valid_teachers:
                    valid_teachers = list(teachers.keys())
                    vt_index = {v: i for i, v in enumerate(valid_teachers)}
                else:
                    vt_index = valid_teachers_index.get(sub, {})
                ti = vt_index.get(teacher, rrand(len(valid_teachers)))
                x_alpha_t = vt_index.get(alpha[i][2], ti)
                x_beta_t = vt_index.get(beta[i][2], ti)
                x_delta_t = vt_index.get(delta[i][2], ti)
                A1t, C1t = 2 * a * rand() - a, 2 * rand()
                A2t, C2t = 2 * a * rand() - a, 2 * rand()
                A3t, C3t = 2 * a * rand() - a, 2 * rand()
                D_alpha_t = abs(C1t * x_alpha_t - ti)
                D_beta_t = abs(C2t * x_beta_t - ti)
                D_delta_t = abs(C3t * x_delta_t - ti)
                T1 = x_alpha_t - A1t * D_alpha_t
                T2 = x_beta_t - A2t * D_beta_t
                T3 = x_delta_t - A3t * D_delta_t
                T_new = int(round((T1 + T2 + T3) / 3.0))
                T_new = max(0, min(len(valid_teachers) - 1, T_new))
                new_teacher = valid_teachers[T_new]

                # Room update
                subj_type = subjects.get(sub, "Lecture")
                valid_rooms = valid_rooms_by_subtype.get(subj_type)
                if not valid_rooms:
                    valid_rooms = list(rooms.keys())
                    vr_index = {v: i for i, v in enumerate(valid_rooms)}
                else:
                    vr_index = valid_rooms_index.get(subj_type, {})
                ri = vr_index.get(room, rrand(len(valid_rooms)))
                x_alpha_r = vr_index.get(alpha[i][3], ri)
                x_beta_r = vr_index.get(beta[i][3], ri)
                x_delta_r = vr_index.get(delta[i][3], ri)
                A1r, C1r = 2 * a * rand() - a, 2 * rand()
                A2r, C2r = 2 * a * rand() - a, 2 * rand()
                A3r, C3r = 2 * a * rand() - a, 2 * rand()
                D_alpha_r = abs(C1r * x_alpha_r - ri)
                D_beta_r = abs(C2r * x_beta_r - ri)
                D_delta_r = abs(C3r * x_delta_r - ri)
                R1 = x_alpha_r - A1r * D_alpha_r
                R2 = x_beta_r - A2r * D_beta_r
                R3 = x_delta_r - A3r * D_delta_r
                R_new = int(round((R1 + R2 + R3) / 3.0))
                R_new = max(0, min(len(valid_rooms) - 1, R_new))
                new_room = valid_rooms[R_new]

                new_wolf.append((cls, sub, new_teacher, new_room, new_slot))
            new_population.append(repair(new_wolf, teachers, rooms, timeslots, subjects))
        population = new_population
        
        # Stagnation Detection & Dynamic Mutation
        if stagnation >= 30:
            for _ in range(5):
                population.append(repair(
                    create_individual(classes, teachers, rooms, timeslots, subjects),
                    teachers, rooms, timeslots, subjects))
            stagnation = 0
        
        history.append(best_fit)
        
        avg_fit = sum(fits) / len(fits)
        log.insert(tk.END, f"GWO Gen {gen}: best={best_fit:.4f}, avg={avg_fit:.4f}\n")
        log.see(tk.END)
        log.update()
        
        # Early Termination - Dừng sớm khi tìm được giải pháp hoàn hảo
        if best_fit == 1.0:
            log.insert(tk.END, f"\n🎉 GWO: Lịch hoàn hảo ở thế hệ {gen}!\n")
            break
    elapsed = time.time() - start
    log.insert(tk.END, f"\n🎯 GWO Fitness cuối cùng: {best_fit:.4f} (Time: {elapsed:.2f}s)\n")
    log.see(tk.END)
    log.update()
    return best_ind, best_fit, history
