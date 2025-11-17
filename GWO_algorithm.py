import random, time, tkinter as tk
from algorithm import create_individual, repair, fitness

def gwo_algorithm(teachers, classes, subjects, rooms, timeslots, log,
                       pop_size=60, generations=200):
    """
    GWO chuẩn cho lập lịch TKB
    Repair chỉ thực hiện 1 lần cuối cùng
    """

    # Khởi tạo quần thể
    population = [create_individual(classes, teachers, rooms, timeslots, subjects)
                  for _ in range(pop_size)]

    best_ind, best_fit = None, 0
    start = time.time()
    history = []

    # Tạo dict mapping nhanh
    timeslot_idx = {s: i for i, s in enumerate(timeslots)}
    teacher_by_sub = {}
    for t, d in teachers.items():
        for sub in d.get("subjects", []):
            teacher_by_sub.setdefault(sub, []).append(t)
    room_by_type = {}
    for r, d in rooms.items():
        room_by_type.setdefault(d.get("type"), []).append(r)

    for gen in range(generations):
        # Tính fitness
        fits = [fitness(ind, teachers, rooms, classes, subjects) for ind in population]
        sorted_pack = sorted(zip(fits, population), key=lambda x: x[0], reverse=True)

        # Alpha, Beta, Delta
        alpha = sorted_pack[0][1]
        beta  = sorted_pack[1][1] if len(sorted_pack) > 1 else alpha
        delta = sorted_pack[2][1] if len(sorted_pack) > 2 else alpha

        if sorted_pack[0][0] > best_fit:
            best_fit, best_ind = sorted_pack[0][0], alpha

        a = 2 - 2 * gen / generations
        new_population = [alpha]  # giữ Alpha

        for wolf in population:
            new_wolf = []
            for i, (cls, sub, teacher, room, slot) in enumerate(wolf):
                # Danh sách hợp lệ
                valid_teachers = teacher_by_sub.get(sub, list(teachers.keys()))
                valid_rooms = room_by_type.get(subjects.get(sub, "Lecture"), list(rooms.keys()))
                num_slots = len(timeslots)

                # Index hiện tại
                xi = timeslot_idx.get(slot, random.randrange(num_slots))
                t_idx = valid_teachers.index(teacher) if teacher in valid_teachers else random.randrange(len(valid_teachers))
                r_idx = valid_rooms.index(room) if room in valid_rooms else random.randrange(len(valid_rooms))

                # Index Alpha/Beta/Delta
                xa, xb, xd = [timeslot_idx.get(w[i][4], xi) for w in (alpha, beta, delta)]
                ta, tb, td = [valid_teachers.index(w[i][2]) if w[i][2] in valid_teachers else t_idx for w in (alpha, beta, delta)]
                ra, rb, rd = [valid_rooms.index(w[i][3]) if w[i][3] in valid_rooms else r_idx for w in (alpha, beta, delta)]

                # Hệ số ngẫu nhiên
                rand = random.random
                A1, C1 = 2*a*rand() - a, 2*rand()
                A2, C2 = 2*a*rand() - a, 2*rand()
                A3, C3 = 2*a*rand() - a, 2*rand()

                # Cập nhật theo vector GWO
                new_x = round((xa - A1*abs(C1*xa - xi) +
                               xb - A2*abs(C2*xb - xi) +
                               xd - A3*abs(C3*xd - xi)) / 3)
                new_t = round((ta - A1*abs(C1*ta - t_idx) +
                               tb - A2*abs(C2*tb - t_idx) +
                               td - A3*abs(C3*td - t_idx)) / 3)
                new_r = round((ra - A1*abs(C1*ra - r_idx) +
                               rb - A2*abs(C2*rb - r_idx) +
                               rd - A3*abs(C3*rd - r_idx)) / 3)

                # Giữ trong phạm vi
                new_slot = timeslots[max(0, min(num_slots-1, new_x))]
                new_teacher = valid_teachers[max(0, min(len(valid_teachers)-1, new_t))]
                new_room = valid_rooms[max(0, min(len(valid_rooms)-1, new_r))]

                new_wolf.append((cls, sub, new_teacher, new_room, new_slot))

            new_population.append(new_wolf)

        # Chỉ repair 1 lần sau khi tạo xong cả population
        population = [repair(wolf, teachers, rooms, timeslots, subjects) for wolf in new_population[:pop_size]]

        history.append(best_fit)
        if gen % 20 == 0:
            avg_fit = sum(fits)/len(fits)
            log.insert(tk.END, f"GWO Gen {gen}: best={best_fit:.4f}, avg={avg_fit:.4f}\n")
            log.see(tk.END)
            log.update()

    elapsed = time.time() - start
    log.insert(tk.END, f"\n🎯 GWO Fitness cao nhất: {best_fit:.4f} (Time: {elapsed:.2f}s)\n")
    log.see(tk.END)
    log.update()

    return best_ind, best_fit, history