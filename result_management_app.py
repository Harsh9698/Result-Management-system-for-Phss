import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

STUDENTS_FILE = "students.json"

def load_students():
    if os.path.exists(STUDENTS_FILE):
        try:
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # If file is corrupted, start fresh
            return {}
    return {}

def save_students(data):
    try:
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save students data: {e}")

students = load_students()

class ResultManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Result Management")
        self.geometry("600x600")
        self.configure(bg="#121212")
        self._build_ui()

    def _build_ui(self):
        title = tk.Label(self, text="Admin Panel - Manage Data",
                         font=("Helvetica", 16, "bold"),
                         fg="white", bg="#121212")
        title.pack(pady=10)

        # Student ID
        tk.Label(self, text="Student ID", fg="white", bg="#121212").pack(anchor="w", padx=20, pady=2)
        self.student_id_entry = tk.Entry(self, bg="#333333", fg="white", insertbackground="white")
        self.student_id_entry.pack(fill="x", padx=20, pady=5)

        # Name
        tk.Label(self, text="Name", fg="white", bg="#121212").pack(anchor="w", padx=20, pady=2)
        self.name_entry = tk.Entry(self, bg="#333333", fg="white", insertbackground="white")
        self.name_entry.pack(fill="x", padx=20, pady=5)

        # Class
        tk.Label(self, text="Class", fg="white", bg="#121212").pack(anchor="w", padx=20, pady=2)
        self.class_var = tk.StringVar()
        # include placeholder in values for readonly combobox
        self.class_combo = ttk.Combobox(self, textvariable=self.class_var,
                                        values=["Select Class", "11", "12"], state="readonly", justify="center")
        self.class_combo.pack(fill="x", padx=20, pady=5)
        self.class_combo.set("Select Class")

        # Roll No
        tk.Label(self, text="Roll No", fg="white", bg="#121212").pack(anchor="w", padx=20, pady=2)
        self.roll_no_entry = tk.Entry(self, bg="#333333", fg="white", insertbackground="white")
        self.roll_no_entry.pack(fill="x", padx=20, pady=5)

        # Section
        tk.Label(self, text="Section", fg="white", bg="#121212").pack(anchor="w", padx=20, pady=2)
        self.section_entry = tk.Entry(self, bg="#333333", fg="white", insertbackground="white")
        self.section_entry.pack(fill="x", padx=20, pady=5)

        # Grades (as comma separated "Subject:Grade")
        tk.Label(self, text="Grades (Subject:Grade, ...)", fg="white", bg="#121212").pack(anchor="w", padx=20, pady=2)
        self.grades_entry = tk.Entry(self, bg="#333333", fg="white", insertbackground="white")
        self.grades_entry.pack(fill="x", padx=20, pady=5)

        # Buttons Frame
        btn_frame = tk.Frame(self, bg="#121212")
        btn_frame.pack(pady=20)

        add_btn = tk.Button(btn_frame, text="Add/Update Student", bg="#4caf50", fg="white",
                            command=self.add_update_student)
        add_btn.grid(row=0, column=0, padx=10)

        delete_btn = tk.Button(btn_frame, text="Delete Student", bg="#f44336", fg="white",
                               command=self.delete_student)
        delete_btn.grid(row=0, column=1, padx=10)

        view_all_btn = tk.Button(self, text="View All Students", bg="#2196f3", fg="white",
                                 command=self.view_all_students)
        view_all_btn.pack(pady=10)

    def clear_fields(self):
        self.student_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.class_combo.set("Select Class")
        self.roll_no_entry.delete(0, tk.END)
        self.section_entry.delete(0, tk.END)
        self.grades_entry.delete(0, tk.END)

    def parse_grades(self, grades_str):
        """
        Parse grades string of format 'Subject:Grade, Subject2:Grade2'
        Returns a dict mapping subject -> grade (float when numeric, else string).
        """
        grades = {}
        if not grades_str:
            return grades
        items = [it.strip() for it in grades_str.split(",") if it.strip()]
        for item in items:
            if ":" not in item:
                # ignore malformed piece but you may want to raise or notify
                continue
            subj, grade_str = item.split(":", 1)
            subj = subj.strip()
            grade_str = grade_str.strip()
            # try numeric, otherwise keep string (e.g., "A+")
            try:
                if "." in grade_str:
                    grade_val = float(grade_str)
                else:
                    grade_val = int(grade_str)
                grades[subj] = grade_val
            except ValueError:
                grades[subj] = grade_str
        return grades

    def add_update_student(self):
        sid = self.student_id_entry.get().strip()
        name = self.name_entry.get().strip()
        class_ = self.class_var.get()
        roll = self.roll_no_entry.get().strip()
        section = self.section_entry.get().strip()
        grades_str = self.grades_entry.get().strip()

        if not sid or not name or class_ not in ["11", "12"] or not roll or not section:
            messagebox.showerror("Error", "Please fill all required fields (Student ID, Name, Class, Roll No, Section).")
            return

        try:
            roll_no = int(roll)
        except ValueError:
            messagebox.showerror("Error", "Roll No must be an integer.")
            return

        grades = self.parse_grades(grades_str)

        # Add or update student
        class_data = students.setdefault(class_, {})
        class_data[sid] = {
            "name": name,
            "roll_no": roll_no,
            "section": section,
            "grades": grades
        }

        save_students(students)
        messagebox.showinfo("Success", f"Student {sid} added/updated successfully.")
        self.clear_fields()

    def delete_student(self):
        sid = self.student_id_entry.get().strip()
        class_ = self.class_var.get()
        if not sid or class_ not in ["11", "12"]:
            messagebox.showerror("Error", "Please provide valid Student ID and Class.")
            return

        if class_ not in students or sid not in students[class_]:
            messagebox.showinfo("Not found", "Student ID not found.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student {sid} from class {class_}?")
        if not confirm:
            return

        del students[class_][sid]
        # If class becomes empty, we can remove the class entry to keep file tidy
        if not students[class_]:
            del students[class_]

        save_students(students)
        messagebox.showinfo("Deleted", f"Student {sid} deleted from class {class_}.")
        self.clear_fields()

    def view_all_students(self):
        window = tk.Toplevel(self)
        window.title("All Students")
        window.geometry("600x400")
        window.configure(bg="#121212")

        text = tk.Text(window, bg="#333333", fg="white")
        text.pack(fill="both", expand=True)

        for cls in sorted(students.keys(), key=lambda x: (int(x) if x.isdigit() else x)):
            students_dict = students.get(cls, {})
            text.insert(tk.END, f"Class {cls}:\n")
            if not students_dict:
                text.insert(tk.END, "  No students\n\n")
                continue
            for sid, info in students_dict.items():
                grades = info.get("grades", {})
                if grades:
                    grades_str = ", ".join(f"{subj}:{grade}" for subj, grade in grades.items())
                else:
                    grades_str = "None"
                roll_display = info.get("roll_no", "")
                text.insert(tk.END,
                            f"  ID: {sid}, Name: {info.get('name','')}, Roll: {roll_display}, Section: {info.get('section','')}, Grades: {grades_str}\n")
            text.insert(tk.END, "\n")

        text.config(state='disabled')


if __name__ == "__main__":
    app = ResultManagementApp()
    app.mainloop()