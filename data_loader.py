import csv, os
from tkinter import messagebox

def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_all_data(folder="data_TH1(small)"):
    """Đọc dữ liệu từ thư mục được chọn (TH1, TH2, TH3)."""
    try:
        teachers_data = load_csv(os.path.join(folder, "teachers.csv"))
        classes_data = load_csv(os.path.join(folder, "classes.csv"))
        subjects_data = load_csv(os.path.join(folder, "subjects.csv"))
        rooms_data = load_csv(os.path.join(folder, "rooms.csv"))
        timeslots_data = load_csv(os.path.join(folder, "timeslots.csv"))
    except FileNotFoundError as e:
        messagebox.showerror("Lỗi", f"Không tìm thấy file trong thư mục: {folder}\n{e}")
        return None

    teachers = {
        t["TeacherID"]: {
            "name": t.get("TeacherName", t["TeacherID"]),
            "subjects": t["Subjects"].split("|"),
            "available": t["AvailableSlots"].split("|")
        }
        for t in teachers_data
    }

    classes = {
        c["ClassID"]: {
            "name": c.get("ClassName", c["ClassID"]),
            "students": int(c["Students"]),
            "subjects": c["Subjects"].split("|")
        }
        for c in classes_data
    }

    subjects = {
        s["SubjectName"]: s["SubjectType"]
        for s in subjects_data
    }

    rooms = {
        r["RoomID"]: {"capacity": int(r["Capacity"]), "type": r["RoomType"]}
        for r in rooms_data
    }

    timeslots = [t["SlotID"] for t in timeslots_data]

    teacher_names = {t["TeacherID"]: t.get("TeacherName", t["TeacherID"]) for t in teachers_data}
    class_names = {c["ClassID"]: c.get("ClassName", c["ClassID"]) for c in classes_data}
    subject_names = {s["SubjectName"]: s.get("SubjectDisplayName", s["SubjectName"]) for s in subjects_data}

    return teachers, classes, subjects, rooms, timeslots, teacher_names, class_names, subject_names
