# helpers.py
import random

def create_individual(classes, teachers, rooms, timeslots, subjects):
    """Tạo một cá thể (lịch trình) ngẫu nhiên ban đầu."""
    individual = []
    for cls, info in classes.items():
        for sub in info["subjects"]:
            valid_teachers = [t for t, d in teachers.items() if sub in d["subjects"]]
            if not valid_teachers:
                continue
            teacher = random.choice(valid_teachers)
            subj_type = subjects.get(sub, "Lecture")
            valid_rooms = [r for r, d in rooms.items() if d["type"] == subj_type]
            if not valid_rooms:
                valid_rooms = list(rooms.keys())
            room = random.choice(valid_rooms)
            slot = random.choice(timeslots)
            individual.append((cls, sub, teacher, room, slot))
    return individual


def repair(individual, teachers, rooms, timeslots, subjects):
    """Sửa các xung đột cứng và phòng sai loại."""
    fixed = []
    used_teacher, used_class, used_room = {}, {}, {}

    for (cls, sub, teacher, room, slot) in individual:
        max_tries = 100
        tries = 0
        
        # Lặp cho đến khi tìm được (teacher, slot, room) hợp lệ không có xung đột
        while tries < max_tries:
            # Kiểm tra xung đột cứng
            if (teacher, slot) in used_teacher or \
               (cls, slot) in used_class or \
               (room, slot) in used_room:
                # Chọn slot mới
                slot = random.choice(timeslots)
                # Chọn phòng mới
                room = random.choice(list(rooms.keys()))
                # Chọn giáo viên mới có thể dạy môn học này
                valid_teachers = [t for t, d in teachers.items() if sub in d["subjects"]]
                if valid_teachers:
                    teacher = random.choice(valid_teachers)
                tries += 1
            else:
                # Không có xung đột, thoát vòng lặp
                break
        
        # Sửa phòng không đúng loại
        subj_type = subjects.get(sub, "Lecture")
        if subj_type != rooms[room]["type"]:
            valid_rooms = [r for r, d in rooms.items() if d["type"] == subj_type]
            if valid_rooms:
                room = random.choice(valid_rooms)
        
        used_teacher[(teacher, slot)] = 1
        used_class[(cls, slot)] = 1
        used_room[(room, slot)] = 1
        fixed.append((cls, sub, teacher, room, slot))
    
    return fixed


def fitness(individual, teachers, rooms, classes, subjects):
    """Tính độ 'tốt' (fitness) của lịch trình."""
    penalty = 0
    used_teacher, used_class, used_room = {}, {}, {}

    for (cls, sub, teacher, room, slot) in individual:
        if (teacher, slot) in used_teacher: penalty += 10
        else: used_teacher[(teacher, slot)] = 1

        if (cls, slot) in used_class: penalty += 10
        else: used_class[(cls, slot)] = 1

        if (room, slot) in used_room: penalty += 8
        else: used_room[(room, slot)] = 1

        if rooms[room]["capacity"] < classes[cls]["students"]: penalty += 0.003
        subj_type = subjects.get(sub, "Lecture")
        if subj_type != rooms[room]["type"]: penalty += 0.002
        if slot not in teachers[teacher]["available"]: penalty += 0.002

    return 1 / (1 + penalty)


def selection(pop, fits):
    """Chọn lọc Roulette Wheel."""
    total = sum(fits)
    if total == 0:
        return random.sample(pop, 2)
    probs = [f / total for f in fits]
    return random.choices(pop, weights=probs, k=2)


def crossover(p1, p2):
    """Lai ghép một điểm cắt."""
    if len(p1) < 2: return p1, p2
    point = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]


def mutate(ind, rate, teachers, rooms, timeslots, subjects):
    """Đột biến ngẫu nhiên một gen."""
    for i in range(len(ind)):
        if random.random() < rate:
            cls, sub, teacher, room, slot = ind[i]
            choice = random.choice(["room", "slot", "teacher"])
            if choice == "room":
                subj_type = subjects.get(sub, "Lecture")
                valid_rooms = [r for r, d in rooms.items() if d["type"] == subj_type]
                room = random.choice(valid_rooms) if valid_rooms else random.choice(list(rooms.keys()))
            elif choice == "slot":
                avail = teachers.get(teacher, {}).get("available", [])
                slot = random.choice(avail) if avail else random.choice(timeslots)
            elif choice == "teacher":
                valid_teachers = [t for t, d in teachers.items() if sub in d["subjects"]]
                if valid_teachers:
                    teacher = random.choice(valid_teachers)
                    # Khi đổi giáo viên, ưu tiên chọn slot phù hợp với lịch rảnh của GV mới
                    avail_new = teachers.get(teacher, {}).get("available", [])
                    if avail_new:
                        slot = random.choice(avail_new)
            ind[i] = (cls, sub, teacher, room, slot)
    return ind
