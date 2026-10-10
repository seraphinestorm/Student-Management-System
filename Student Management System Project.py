import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

# ---------------------------
# Database setup
# ---------------------------
connection = sqlite3.connect("management.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    student_section TEXT,
    student_address TEXT,
    student_phone TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT,
    section TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject_id INTEGER,
    exam_name TEXT,
    grade REAL,
    FOREIGN KEY(student_id) REFERENCES students(student_id),
    FOREIGN KEY(subject_id) REFERENCES subjects(subject_id)
);
""")
connection.commit()

# ---------------------------
# Helper functions for DB lists
# ---------------------------
def get_all_students():
    cursor.execute("SELECT student_id, student_name FROM students ORDER BY student_name")
    return cursor.fetchall()  # list of (id, name)

def get_all_subjects():
    cursor.execute("SELECT subject_id, subject_name FROM subjects ORDER BY subject_name")
    return cursor.fetchall()

def student_display_string(sid, name):
    return f"{name} — {sid}"

def subject_display_string(sid, name):
    return f"{name} — {sid}"

def get_sections():
    cursor.execute("SELECT DISTINCT student_section FROM students WHERE student_section IS NOT NULL AND student_section<>''")
    s1 = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT section FROM subjects WHERE section IS NOT NULL AND section<>''")
    s2 = [r[0] for r in cursor.fetchall()]
    sections = sorted(set(s1 + s2))
    return sections

# ---------------------------
# Global state
# ---------------------------
logged_in_student = {"id": None, "name": None}

# ---------------------------
# Login / Register window
# ---------------------------
def open_dashboard_window():
    login_win.destroy()
    build_dashboard()

def register_and_login(name, section, phone, address):
    cursor.execute("INSERT INTO students (student_name, student_section, student_address, student_phone) VALUES (?, ?, ?, ?)",
                   (name, section, address, phone))
    connection.commit()
    cursor.execute("SELECT student_id FROM students WHERE student_name=? AND student_phone=? ORDER BY student_id DESC LIMIT 1",
                   (name, phone))
    sid = cursor.fetchone()[0]
    logged_in_student["id"] = sid
    logged_in_student["name"] = name
    open_dashboard_window()

def attempt_register():
    name = reg_name.get().strip()
    section = reg_section.get().strip()
    phone = reg_phone.get().strip()
    address = reg_address.get().strip()
    if not all([name, section, phone, address]):
        messagebox.showerror("Error", "PLEASE fill out the form for registration")
        return
    if not phone.isdigit():
        messagebox.showerror("Error", "PLEASE try again. Phone must contain numbers only")
        return
    register_and_login(name, section, phone, address)

def attempt_login():
    name = login_name.get().strip()
    phone = login_phone.get().strip()
    if not (name and phone):
        messagebox.showerror("Error", "PLEASE enter a name and phone to login.")
        return
    cursor.execute("SELECT student_id FROM students WHERE student_name=? AND student_phone=? LIMIT 1", (name, phone))
    r = cursor.fetchone()
    if not r:
        messagebox.showerror("Error", "Student NOT FOUND. PLEASE Check the name and phone or register first")
        return
    sid = r[0]
    logged_in_student["id"] = sid
    logged_in_student["name"] = name
    open_dashboard_window()

# build login window UI
login_win = tk.Tk()
login_win.title("Login / Register - Student Management")
login_win.geometry("600x420")
login_win.configure(bg="#f7f9fb")

tk.Label(login_win, text="Welcome to REGISTER OR LOGIN System", font=("Arial", 16, "bold"), bg="#f7f9fb").pack(pady=12)

notebook = ttk.Notebook(login_win)
notebook.pack(expand=True, fill="both", padx=20, pady=12)

# Register tab
reg_tab = tk.Frame(notebook, bg="white")
notebook.add(reg_tab, text="Register")

reg_frame = tk.Frame(reg_tab, bg="white")
reg_frame.pack(pady=20)

tk.Label(reg_frame, text="Name:", bg="white").grid(row=0, column=0, sticky="w", padx=6, pady=6)
tk.Label(reg_frame, text="Section:", bg="white").grid(row=1, column=0, sticky="w", padx=6, pady=6)
tk.Label(reg_frame, text="Phone:", bg="white").grid(row=2, column=0, sticky="w", padx=6, pady=6)
tk.Label(reg_frame, text="Address:", bg="white").grid(row=3, column=0, sticky="w", padx=6, pady=6)

reg_name = tk.Entry(reg_frame, width=35)
reg_section = tk.Entry(reg_frame, width=35)
reg_phone = tk.Entry(reg_frame, width=35)
reg_address = tk.Entry(reg_frame, width=35)

reg_name.grid(row=0, column=1, padx=6, pady=6)
reg_section.grid(row=1, column=1, padx=6, pady=6)
reg_phone.grid(row=2, column=1, padx=6, pady=6)
reg_address.grid(row=3, column=1, padx=6, pady=6)

tk.Button(reg_tab, text="Register to Open Dashboard", bg="#1abc9c", fg="white", command=attempt_register).pack(pady=12)

# Login tab
login_tab = tk.Frame(notebook, bg="white")
notebook.add(login_tab, text="Login")

login_frame = tk.Frame(login_tab, bg="white")
login_frame.pack(pady=20)

tk.Label(login_frame, text="Name:", bg="white").grid(row=0, column=0, sticky="w", padx=6, pady=6)
tk.Label(login_frame, text="Phone:", bg="white").grid(row=1, column=0, sticky="w", padx=6, pady=6)

login_name = tk.Entry(login_frame, width=35)
login_phone = tk.Entry(login_frame, width=35)
login_name.grid(row=0, column=1, padx=6, pady=6)
login_phone.grid(row=1, column=1, padx=6, pady=6)

tk.Button(login_tab, text="Login to Open Dashboard", bg="#1abc9c", fg="white", command=attempt_login).pack(pady=12)

# ---------------------------
# Dashboard builder
# ---------------------------
def build_dashboard():
    global root, status_var, frames
    root = tk.Tk()
    root.title("Student Management Dashboard")
    root.geometry("1100x650")
    root.configure(bg="#f7f9fb")

    # Sidebar
    sidebar = tk.Frame(root, bg="#2c3e50", width=220, height=650)
    sidebar.pack(side="left", fill="y")

    logo = tk.Label(sidebar, text="STUDENT\nMANAGEMENT", fg="white", bg="#2c3e50",
                    font=("Arial", 14, "bold"), wraplength=180, justify="center")
    logo.pack(pady=12)

    # status
    status_var = tk.StringVar(value=f"Logged in: {logged_in_student['name']} ({logged_in_student['id']})")
    status_label = tk.Label(sidebar, textvariable=status_var, fg="white", bg="#2c3e50", font=("Arial", 10))
    status_label.pack(side="bottom", pady=12)

    # Section filter area
    tk.Label(sidebar, text="Sections", fg="white", bg="#2c3e50", font=("Arial", 11, "bold")).pack(pady=(6,0))
    sections_frame = tk.Frame(sidebar, bg="#2c3e50")
    sections_frame.pack(pady=6)

    # dynamic menu buttons
    menu_frame = tk.Frame(sidebar, bg="#2c3e50")
    menu_frame.pack(pady=8)

    menu_buttons = ["Dashboard", "Students", "Attendance", "Subjects", "Grades", "Report"]
    frames = {}

    def show_frame(name):
        for f in frames.values():
            f.pack_forget()
        frames[name].pack(fill="both", expand=True)
        # if report shown, refresh it
        if name == "Report":
            refresh_reports()

    for name in menu_buttons:
        b = tk.Button(menu_frame, text=name, bg="#34495e", fg="white",
                      font=("Arial", 12), relief="flat", activebackground="#1abc9c",
                      activeforeground="white", width=22,
                      command=lambda n=name: show_frame(n))
        b.pack(pady=4)

    # main container
    main_container = tk.Frame(root, bg="white")
    main_container.pack(side="left", fill="both", expand=True)

    # ---------------------------
    # DASHBOARD frame (overview)
    # ---------------------------
    dashboard_frame = tk.Frame(main_container, bg="white")
    frames["Dashboard"] = dashboard_frame

    tk.Label(dashboard_frame, text="STUDENT MANAGEMENT SYSTEM APPLICATION", font=("Arial", 18, "bold"), bg="white").pack(pady=12)

    # quick stats
    card = tk.Frame(dashboard_frame, bg="white", bd=1, relief="solid", padx=16, pady=12)
    card.pack(pady=10, padx=20, fill="x")

    stats_var = tk.StringVar()
    stats_label = tk.Label(card, textvariable=stats_var, justify="left", bg="white", font=("Arial", 11))
    stats_label.pack()

    def update_stats():
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM subjects")
        total_subjects = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM grades")
        total_grades = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_att = cursor.fetchone()[0]
        stats_var.set(f"Total students: {total_students}\nTotal subjects: {total_subjects}\nTotal grades: {total_grades}\nTotal attendance records: {total_att}")

    # ---------------------------
    # STUDENTS frame (list + add/edit/delete + filter by section)
    # ---------------------------
    student_frame = tk.Frame(main_container, bg="white")
    frames["Students"] = student_frame

    tk.Label(student_frame, text="Students Management", font=("Arial", 18, "bold"), bg="white").pack(pady=8)

    # search + section filter row
    top_controls = tk.Frame(student_frame, bg="white")
    top_controls.pack(fill="x", padx=12)

    tk.Label(top_controls, text="Search:", bg="white").pack(side="left", padx=(4,6))
    search_var = tk.StringVar()
    search_entry = tk.Entry(top_controls, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=(0,8))

    tk.Label(top_controls, text="Filter Section:", bg="white").pack(side="left", padx=(6,6))
    section_filter_var = tk.StringVar(value="")
    section_filter_menu = ttk.Combobox(top_controls, textvariable=section_filter_var, width=20)
    section_filter_menu.pack(side="left", padx=(0,8))

    def refresh_section_buttons():
        # update sections in sidebar and combobox
        for widget in sections_frame.winfo_children():
            widget.destroy()
        secs = get_sections()
        # Add "All" button
        def make_filter_handler(s):
            def handle():
                section_filter_var.set(s)
                refresh_students()
                show_frame("Students")
            return handle
        all_btn = tk.Button(sections_frame, text="All", bg="#34495e", fg="white", relief="flat", width=18, command=make_filter_handler(""))
        all_btn.pack(pady=3)
        for s in secs:
            btn = tk.Button(sections_frame, text=s, bg="#34495e", fg="white", relief="flat", width=18, command=make_filter_handler(s))
            btn.pack(pady=3)
        section_filter_menu.config(values=[""] + secs)

    student_tree = ttk.Treeview(student_frame, columns=("Name", "Section", "Address", "Phone"))
    student_tree.heading("#0", text="ID")
    student_tree.heading("Name", text="Name")
    student_tree.heading("Section", text="Section")
    student_tree.heading("Address", text="Address")
    student_tree.heading("Phone", text="Phone")
    student_tree.column("#0", width=60)
    student_tree.pack(pady=10, fill="both", expand=True, padx=20)

    btn_frame_students = tk.Frame(student_frame, bg="white")
    btn_frame_students.pack(pady=6)

    def refresh_students():
        q = search_var.get().strip()
        sec = section_filter_var.get().strip()
        for row in student_tree.get_children():
            student_tree.delete(row)
        sql = "SELECT * FROM students WHERE 1=1"
        params = []
        if sec:
            sql += " AND student_section=?"
            params.append(sec)
        if q:
            sql += " AND (student_name LIKE ? OR student_phone LIKE ? OR student_section LIKE ?)"
            params.extend([f"%{q}%"]*3)
        sql += " ORDER BY student_name"
        cursor.execute(sql, tuple(params))
        for r in cursor.fetchall():
            student_tree.insert("", "end", text=r[0], values=(r[1], r[2], r[3], r[4]))

    def add_student_popup():
        popup = tk.Toplevel(root)
        popup.title("Add New Student")
        popup.geometry("420x260")
        frame = tk.Frame(popup, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        tk.Label(frame, text="Section:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        tk.Label(frame, text="Phone:").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        tk.Label(frame, text="Address:").grid(row=3, column=0, sticky="w", padx=6, pady=6)

        e_name = tk.Entry(frame, width=35); e_section = tk.Entry(frame, width=35)
        e_phone = tk.Entry(frame, width=35); e_address = tk.Entry(frame, width=35)
        e_name.grid(row=0, column=1, padx=6, pady=6)
        e_section.grid(row=1, column=1, padx=6, pady=6)
        e_phone.grid(row=2, column=1, padx=6, pady=6)
        e_address.grid(row=3, column=1, padx=6, pady=6)

        def save():
            name = e_name.get().strip(); section = e_section.get().strip()
            phone = e_phone.get().strip(); address = e_address.get().strip()
            if not (name and section and phone and address):
                messagebox.showerror("Error", "All fields required.")
                return
            if not phone.isdigit():
                messagebox.showerror("Error", "It must be numbers only")
                return
            cursor.execute("INSERT INTO students (student_name, student_section, student_address, student_phone) VALUES (?, ?, ?, ?)",
                           (name, section, address, phone))
            connection.commit()
            refresh_students(); refresh_section_buttons(); update_stats(); refresh_all_ui()
            popup.destroy()
            messagebox.showinfo("Success", "New Student is Added")

        tk.Button(frame, text="Save", bg="#1abc9c", fg="white", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def edit_selected_student():
        sel = student_tree.selection()
        if not sel:
            messagebox.showerror("Error", "PLEASE select a student to edit")
            return
        item = sel[0]
        sid = student_tree.item(item, "text")
        cursor.execute("SELECT student_name, student_section, student_address, student_phone FROM students WHERE student_id=?", (sid,))
        r = cursor.fetchone()
        if not r:
            messagebox.showerror("Error", "Student NOT FOUND")
            return

        popup = tk.Toplevel(root)
        popup.title("Edit Student")
        popup.geometry("420x260")
        frame = tk.Frame(popup, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        tk.Label(frame, text="Section:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        tk.Label(frame, text="Phone:").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        tk.Label(frame, text="Address:").grid(row=3, column=0, sticky="w", padx=6, pady=6)

        e_name = tk.Entry(frame, width=35); e_section = tk.Entry(frame, width=35)
        e_phone = tk.Entry(frame, width=35); e_address = tk.Entry(frame, width=35)
        e_name.grid(row=0, column=1, padx=6, pady=6)
        e_section.grid(row=1, column=1, padx=6, pady=6)
        e_phone.grid(row=2, column=1, padx=6, pady=6)
        e_address.grid(row=3, column=1, padx=6, pady=6)

        e_name.insert(0, r[0]); e_section.insert(0, r[1]); e_address.insert(0, r[2]); e_phone.insert(0, r[3])

        def save():
            name = e_name.get().strip(); section = e_section.get().strip()
            phone = e_phone.get().strip(); address = e_address.get().strip()
            if not (name and section and phone and address):
                messagebox.showerror("Error", "All fields required")
                return
            if not phone.isdigit():
                messagebox.showerror("Error", "It must be numbers only")
                return
            cursor.execute("UPDATE students SET student_name=?, student_section=?, student_address=?, student_phone=? WHERE student_id=?",
                           (name, section, address, phone, sid))
            connection.commit()
            popup.destroy()
            refresh_students(); refresh_section_buttons(); update_stats(); refresh_all_ui()
            messagebox.showinfo("Success", "Student updated")

        tk.Button(frame, text="Save Changes", bg="#3498db", fg="white", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def delete_selected_student():
        sel = student_tree.selection()
        if not sel:
            messagebox.showerror("Error", "PLEASE select a student to delete")
            return
        item = sel[0]
        sid = student_tree.item(item, "text")
        name = student_tree.item(item, "values")[0]
        if messagebox.askyesno("Confirm Delete", f"Delete student '{name}' (ID: {sid})? This will also remove their grades & attendance"):
            cursor.execute("DELETE FROM grades WHERE student_id=?", (sid,))
            cursor.execute("DELETE FROM attendance WHERE student_id=?", (sid,))
            cursor.execute("DELETE FROM students WHERE student_id=?", (sid,))
            connection.commit()
            refresh_students(); refresh_section_buttons(); update_stats(); refresh_all_ui()
            messagebox.showinfo("Deleted", f"Student '{name}' is deleted")

    tk.Button(btn_frame_students, text="Add Student", bg="#1abc9c", fg="white", command=add_student_popup).pack(side="left", padx=6)
    tk.Button(btn_frame_students, text="Edit Selected", bg="#3498db", fg="white", command=edit_selected_student).pack(side="left", padx=6)
    tk.Button(btn_frame_students, text="Delete Selected", bg="#e74c3c", fg="white", command=delete_selected_student).pack(side="left", padx=6)

    # search binds
    def on_search_change(*args):
        refresh_students()
    search_var.trace_add("write", on_search_change)
    section_filter_var.trace_add("write", lambda *a: refresh_students())

    # ---------------------------
    # ATTENDANCE frame
    # ---------------------------
    attendance_frame = tk.Frame(main_container, bg="white")
    frames["Attendance"] = attendance_frame

    tk.Label(attendance_frame, text="Attendance Management", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    form_a = tk.Frame(attendance_frame, bg="white")
    form_a.pack(pady=8)

    tk.Label(form_a, text="Select Student:", bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk.Label(form_a, text="Date (YYYY-MM-DD):", bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    tk.Label(form_a, text="Status:", bg="white").grid(row=2, column=0, padx=10, pady=5, sticky="w")

    student_var_att = tk.StringVar()
    students_list_for_att = [student_display_string(sid, name) for sid, name in get_all_students()]
    student_menu = ttk.Combobox(form_a, textvariable=student_var_att, values=students_list_for_att, width=34)
    student_menu.grid(row=0, column=1, padx=10, pady=5)
    if students_list_for_att:
        student_var_att.set(students_list_for_att[0])

    date_entry = tk.Entry(form_a, width=32)
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    date_entry.grid(row=1, column=1, padx=10, pady=5)

    status_var_att = tk.StringVar(value="Present")
    status_menu = ttk.Combobox(form_a, textvariable=status_var_att, values=["Present", "Absent"], width=34)
    status_menu.grid(row=2, column=1, padx=10, pady=5)

    def mark_attendance():
        sel = student_var_att.get()
        if not sel:
            messagebox.showerror("Error","No student is selected")
            return
        try:
            sid = int(sel.split("—")[-1].strip())
        except:
            messagebox.showerror("Error", "Student selection is invalid")
            return
        date = date_entry.get().strip()
        status = status_var_att.get()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return
        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (sid, date, status))
        connection.commit()
        refresh_attendance()
        messagebox.showinfo("Success", "Student attendance is successfully recorded")

    tk.Button(form_a, text="Mark Attendance", bg="#1abc9c", fg="white", width=20, command=mark_attendance).grid(row=3, column=0, columnspan=2, pady=10)

    attendance_tree = ttk.Treeview(attendance_frame, columns=("Name", "Date", "Status"))
    attendance_tree.heading("#0", text="ID")
    attendance_tree.heading("Name", text="Student Name")
    attendance_tree.heading("Date", text="Date")
    attendance_tree.heading("Status", text="Status")
    attendance_tree.column("#0", width=60)
    attendance_tree.pack(pady=10, fill="both", expand=True, padx=20)

    def refresh_attendance():
        for row in attendance_tree.get_children():
            attendance_tree.delete(row)
        cursor.execute("""SELECT a.attendance_id, s.student_name, a.date, a.status
                          FROM attendance a
                          JOIN students s ON a.student_id = s.student_id
                          ORDER BY a.date DESC""")
        for r in cursor.fetchall():
            attendance_tree.insert("", "end", text=r[0], values=(r[1], r[2], r[3]))

    # delete attendance
    def delete_attendance():
        sel = attendance_tree.selection()
        if not sel:
            messagebox.showerror("Error", "Select student attendance to delete record")
            return
        aid = attendance_tree.item(sel[0], "text")
        if messagebox.askyesno("Confirm Delete", "Do you want to delete this attendance record?"):
            cursor.execute("DELETE FROM attendance WHERE attendance_id=?", (aid,))
            connection.commit()
            refresh_attendance()
            messagebox.showinfo("Deleted", " Student Attendance deleted")

    tk.Button(attendance_frame, text="Delete Selected Attendance", bg="#e74c3c", fg="white", command=delete_attendance).pack(pady=6)

    # ---------------------------
    # GRADES frame (Add / Edit / Delete)
    # ---------------------------
    grades_frame = tk.Frame(main_container, bg="white")
    frames["Grades"] = grades_frame

    tk.Label(grades_frame, text="Grades", font=("Arial", 18, "bold"), bg="white").pack(pady=8)

    grade_tree = ttk.Treeview(grades_frame, columns=("Student", "Subject", "Activity", "Grade"))
    grade_tree.heading("#0", text="ID")
    grade_tree.heading("Student", text="Student")
    grade_tree.heading("Subject", text="Subject")
    grade_tree.heading("Activity", text="Activity")
    grade_tree.heading("Grade", text="Grade")
    grade_tree.column("#0", width=60)
    grade_tree.pack(pady=10, fill="both", expand=True, padx=20)

    form_g = tk.Frame(grades_frame, bg="white")
    form_g.pack(pady=6)

    tk.Label(form_g, text="Student:", bg="white").grid(row=0, column=0, padx=6, pady=4, sticky="e")
    tk.Label(form_g, text="Subject:", bg="white").grid(row=1, column=0, padx=6, pady=4, sticky="e")
    tk.Label(form_g, text="Activity Name:", bg="white").grid(row=2, column=0, padx=6, pady=4, sticky="e")
    tk.Label(form_g, text="Grade:", bg="white").grid(row=3, column=0, padx=6, pady=4, sticky="e")

    grade_student_var = tk.StringVar()
    grade_subject_var = tk.StringVar()
    grade_student_menu = ttk.Combobox(form_g, textvariable=grade_student_var, width=36)
    grade_subject_menu = ttk.Combobox(form_g, textvariable=grade_subject_var, width=36)
    grade_student_menu.grid(row=0, column=1, padx=6, pady=4)
    grade_subject_menu.grid(row=1, column=1, padx=6, pady=4)

    exam_entry = tk.Entry(form_g, width=38)
    grade_entry = tk.Entry(form_g, width=38)
    exam_entry.grid(row=2, column=1, padx=6, pady=4)
    grade_entry.grid(row=3, column=1, padx=6, pady=4)

    btn_frame = tk.Frame(grades_frame, bg="white")
    btn_frame.pack(pady=8)

    def refresh_grades():
        for row in grade_tree.get_children():
            grade_tree.delete(row)
        cursor.execute("""
            SELECT g.grade_id, s.student_name, sub.subject_name, g.exam_name, g.grade
            FROM grades g
            JOIN students s ON g.student_id = s.student_id
            JOIN subjects sub ON g.subject_id = sub.subject_id
            ORDER BY sub.subject_name, s.student_name
        """)
        for r in cursor.fetchall():
            grade_tree.insert("", "end", text=r[0], values=(r[1], r[2], r[3], r[4]))

        # Refresh dropdowns
        grade_student_menu.config(values=[student_display_string(sid, name) for sid, name in get_all_students()])
        grade_subject_menu.config(values=[subject_display_string(sid, name) for sid, name in get_all_subjects()])

    def clear_grade_form():
        grade_student_var.set("")
        grade_subject_var.set("")
        exam_entry.delete(0, tk.END)
        grade_entry.delete(0, tk.END)

    def add_grade():
        student_sel = grade_student_var.get()
        subject_sel = grade_subject_var.get()
        exam_name = exam_entry.get().strip()
        grade_text = grade_entry.get().strip()
        if not all([student_sel, subject_sel, exam_name, grade_text]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        try:
            student_id = int(student_sel.split("—")[-1].strip())
            subject_id = int(subject_sel.split("—")[-1].strip())
            grade_val = float(grade_text)
        except ValueError:
            messagebox.showerror("Error", "Numeric values is INVALID")
            return
        cursor.execute("INSERT INTO grades (student_id, subject_id, exam_name, grade) VALUES (?, ?, ?, ?)",
                       (student_id, subject_id, exam_name, grade_val))
        connection.commit()
        refresh_grades(); update_stats(); refresh_all_ui()
        clear_grade_form()
        messagebox.showinfo("Success", "Student Grade added successfully")

    def delete_grade():
        sel = grade_tree.selection()
        if not sel:
            messagebox.showerror("Error", "PLEASE select a grade to delete")
            return
        gid = grade_tree.item(sel[0], "text")
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student grade?"):
            cursor.execute("DELETE FROM grades WHERE grade_id=?", (gid,))
            connection.commit()
            refresh_grades(); update_stats(); refresh_all_ui()
            messagebox.showinfo("Deleted", "Students Grade deleted successfully")

    def on_grade_select(event):
        sel = grade_tree.selection()
        if not sel:
            return
        gid = grade_tree.item(sel[0], "text")
        values = grade_tree.item(sel[0], "values")
        student_name, subject_name, exam, grade_val = values
        # set the dropdowns to the display strings (we need to find the ids)
        cursor.execute("SELECT student_id FROM students WHERE student_name=? LIMIT 1", (student_name,))
        srow = cursor.fetchone()
        if srow:
            grade_student_var.set(student_display_string(srow[0], student_name))
        cursor.execute("SELECT subject_id FROM subjects WHERE subject_name=? LIMIT 1", (subject_name,))
        srow = cursor.fetchone()
        if srow:
            grade_subject_var.set(subject_display_string(srow[0], subject_name))
        exam_entry.delete(0, tk.END)
        exam_entry.insert(0, exam)
        grade_entry.delete(0, tk.END)
        grade_entry.insert(0, grade_val)
        # visual
        for iid in grade_tree.get_children():
            grade_tree.item(iid, tags=())
        grade_tree.item(sel[0], tags=("selected",))
        grade_tree.tag_configure("selected", background="#d1f7d1")

    def update_grade():
        sel = grade_tree.selection()
        if not sel:
            messagebox.showerror("Error", "PLEASE select a grade to update")
            return
        gid = grade_tree.item(sel[0], "text")
        student_sel = grade_student_var.get()
        subject_sel = grade_subject_var.get()
        exam_name = exam_entry.get().strip()
        grade_text = grade_entry.get().strip()
        if not all([student_sel, subject_sel, exam_name, grade_text]):
            messagebox.showerror("Error", "All fields required")
            return
        try:
            student_id = int(student_sel.split("—")[-1].strip())
            subject_id = int(subject_sel.split("—")[-1].strip())
            grade_val = float(grade_text)
        except ValueError:
            messagebox.showerror("Error", "Grade value INVALID")
            return
        cursor.execute("""
            UPDATE grades
            SET student_id=?, subject_id=?, exam_name=?, grade=?
            WHERE grade_id=?
        """, (student_id, subject_id, exam_name, grade_val, gid))
        connection.commit()
        refresh_grades(); update_stats(); refresh_all_ui()
        clear_grade_form()
        messagebox.showinfo("Updated", "Student grade updated successfully")

    tk.Button(btn_frame, text="Add Grade", bg="#1abc9c", fg="white", width=16, command=add_grade).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Update Selected", bg="#3498db", fg="white", width=16, command=update_grade).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Delete Selected", bg="#e74c3c", fg="white", width=16, command=delete_grade).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Clear Fields", bg="#95a5a6", fg="white", width=16, command=clear_grade_form).pack(side="left", padx=6)

    grade_tree.bind("<<TreeviewSelect>>", on_grade_select)

    # ---------------------------
    # SUBJECTS frame
    # ---------------------------
    subjects_frame = tk.Frame(main_container, bg="white")
    frames["Subjects"] = subjects_frame

    tk.Label(subjects_frame, text="Subjects Management", font=("Arial", 18, "bold"), bg="white").pack(pady=8)

    subject_tree = ttk.Treeview(subjects_frame, columns=("Subject", "Section"))
    subject_tree.heading("#0", text="ID")
    subject_tree.heading("Subject", text="Subject Name")
    subject_tree.heading("Section", text="Section")
    subject_tree.column("#0", width=60)
    subject_tree.pack(pady=10, fill="both", expand=True, padx=20)

    form_s = tk.Frame(subjects_frame, bg="white")
    form_s.pack(pady=8)

    tk.Label(form_s, text="Subject Name:", bg="white").grid(row=0, column=0, padx=6, pady=3)
    tk.Label(form_s, text="Section:", bg="white").grid(row=1, column=0, padx=6, pady=3)

    subject_name_entry = tk.Entry(form_s, width=35)
    section_subject_entry = tk.Entry(form_s, width=35)
    subject_name_entry.grid(row=0, column=1, padx=6, pady=3)
    section_subject_entry.grid(row=1, column=1, padx=6, pady=3)

    def save_subject():
        name = subject_name_entry.get().strip()
        section = section_subject_entry.get().strip()
        if not (name and section):
            messagebox.showerror("Error", "All fields required!")
            return
        cursor.execute("INSERT INTO subjects (subject_name, section) VALUES (?, ?)", (name, section))
        connection.commit()
        refresh_subjects(); refresh_section_buttons(); refresh_grades(); update_stats(); refresh_all_ui()
        subject_name_entry.delete(0, tk.END)
        section_subject_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Subject successfully added")

    tk.Button(form_s, text="Add Subject", bg="#1abc9c", fg="white", width=18, command=save_subject).grid(row=2, column=0, columnspan=2, pady=6)

    def refresh_subjects():
        for row in subject_tree.get_children():
            subject_tree.delete(row)
        cursor.execute("SELECT * FROM subjects ORDER BY subject_name")
        for r in cursor.fetchall():
            subject_tree.insert("", "end", text=r[0], values=(r[1], r[2]))

    def edit_selected_subject():
        sel = subject_tree.selection()
        if not sel:
            messagebox.showerror("Error", "PLEASE select a subject to edit")
            return
        sid = subject_tree.item(sel[0], "text")
        cursor.execute("SELECT subject_name, section FROM subjects WHERE subject_id=?", (sid,))
        r = cursor.fetchone()
        if not r:
            messagebox.showerror("Error", "Subject NOT FOUND")
            return
        popup = tk.Toplevel(root)
        popup.title("Edit Subject")
        popup.geometry("420x200")
        f = tk.Frame(popup, padx=10, pady=10); f.pack()
        tk.Label(f, text="Subject Name:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        tk.Label(f, text="Section:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        e_name = tk.Entry(f, width=35); e_section = tk.Entry(f, width=35)
        e_name.grid(row=0, column=1, padx=6, pady=6); e_section.grid(row=1, column=1, padx=6, pady=6)
        e_name.insert(0, r[0]); e_section.insert(0, r[1])
        def save():
            name = e_name.get().strip(); section = e_section.get().strip()
            if not (name and section):
                messagebox.showerror("Error", "All fields required")
                return
            cursor.execute("UPDATE subjects SET subject_name=?, section=? WHERE subject_id=?", (name, section, sid))
            connection.commit()
            popup.destroy(); refresh_subjects(); refresh_section_buttons(); refresh_grades(); update_stats(); refresh_all_ui()
            messagebox.showinfo("Updated", "Subject is updated")
        tk.Button(f, text="Save Changes", bg="#3498db", fg="white", command=save).grid(row=2, column=0, columnspan=2, pady=8)

    def delete_selected_subject():
        sel = subject_tree.selection()
        if not sel:
            messagebox.showerror("Error", "PLEASE select a subject to delete")
            return
        sid = subject_tree.item(sel[0], "text")
        name = subject_tree.item(sel[0], "values")[0]
        if messagebox.askyesno("Confirm Delete", f"Delete subject '{name}' (ID: {sid})? This will remove related grades"):
            cursor.execute("DELETE FROM grades WHERE subject_id=?", (sid,))
            cursor.execute("DELETE FROM subjects WHERE subject_id=?", (sid,))
            connection.commit()
            refresh_subjects(); refresh_grades(); refresh_section_buttons(); update_stats(); refresh_all_ui()
            messagebox.showinfo("Deleted", "Subject deleted")

    subject_buttons = tk.Frame(subjects_frame, bg="white")
    subject_buttons.pack(pady=6)
    tk.Button(subject_buttons, text="Edit Selected Subject", bg="#3498db", fg="white", command=edit_selected_subject).pack(side="left", padx=6)
    tk.Button(subject_buttons, text="Delete Selected Subject", bg="#e74c3c", fg="white", command=delete_selected_subject).pack(side="left", padx=6)

    # double-click subject to quick add grade
    def on_subject_double_click(event):
        item = subject_tree.identify_row(event.y)
        if not item:
            return
        sid = subject_tree.item(item, "text")
        subject_name = subject_tree.item(item, "values")[0]
        open_grade_popup(subject_id=sid, subject_name=subject_name)
    subject_tree.bind("<Double-1>", on_subject_double_click)

    # ---------------------------
    # Grade-entry popup used by subjects double-click
    # ---------------------------
    def open_grade_popup(subject_id, subject_name):
        students = get_all_students()
        if not students:
            messagebox.showwarning("No Students", "No students available. PLEASE register students first")
            return
        popup = tk.Toplevel(root)
        popup.title(f"Add Grade - {subject_name}")
        popup.geometry("420x300")
        popup.transient(root); popup.grab_set()

        tk.Label(popup, text=f"Subject: {subject_name}", font=("Arial", 14, "bold")).pack(pady=8)
        form = tk.Frame(popup); form.pack(pady=8)
        tk.Label(form, text="Student:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        tk.Label(form, text="Activity Name:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        tk.Label(form, text="Grade:").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        student_display_list = [student_display_string(sid, name) for sid, name in students]
        student_sel_var = tk.StringVar(value=student_display_list[0])
        student_combo = ttk.Combobox(form, values=student_display_list, textvariable=student_sel_var, width=30)
        student_combo.grid(row=0, column=1, padx=6, pady=6)
        exam_e = tk.Entry(form, width=32); grade_e = tk.Entry(form, width=32)
        exam_e.grid(row=1, column=1, padx=6, pady=6); grade_e.grid(row=2, column=1, padx=6, pady=6)
        def save_grade_for_subject(activity_e=None):
            sel = student_sel_var.get()
            if not sel:
                messagebox.showerror("Error", "PLEASE select a student")
                return
            try:
                sid = int(sel.split("—")[-1].strip())
            except:
                messagebox.showerror("Error", "Student selection INVALID")
                return
            activity = activity_e.get().strip()
            grade_text = grade_e.get().strip()
            try:
                grade_val = float(grade_text)
            except ValueError:
                messagebox.showerror("Error", "Grade must be a number (e.g., 85 or 92.5)")
                return
            if not activity:
                messagebox.showerror("Error", "Enter an activity name")
                return
            cursor.execute("INSERT INTO grades (student_id, subject_id, activity_name, grade) VALUES (?, ?, ?, ?)",
                           (sid, subject_id, activity, grade_val))
            connection.commit()
            refresh_grades(); update_stats(); refresh_all_ui()
            popup.destroy()
            messagebox.showinfo("Success", f"Grade saved for {sel.split('—')[0].strip()} in {subject_name}.")
        tk.Button(popup, text="Save Grade", bg="#1abc9c", fg="white", width=18, command=save_grade_for_subject).pack(pady=12)

    # ---------------------------
    # REPORT frame
    # ---------------------------
    report_frame = tk.Frame(main_container, bg="white")
    frames["Report"] = report_frame

    tk.Label(report_frame, text="Reports", font=("Arial", 18, "bold"), bg="white").pack(pady=8)

    # Summary Card
    summary_card = tk.Frame(report_frame, bg="white", bd=1, relief="solid", padx=12, pady=12)
    summary_card.pack(fill="x", padx=20, pady=8)

    summary_text_var = tk.StringVar()
    summary_label = tk.Label(summary_card, textvariable=summary_text_var, justify="left", bg="white", font=("Arial", 11))
    summary_label.pack(anchor="w")

    # Average per subject tree
    avg_frame = tk.Frame(report_frame, bg="white")
    avg_frame.pack(fill="both", expand=False, pady=6, padx=20)
    tk.Label(avg_frame, text="Average grade per subject:", bg="white").pack(anchor="w")
    avg_tree = ttk.Treeview(avg_frame, columns=("Subject", "Average"))
    avg_tree.heading("#0", text="ID")
    avg_tree.heading("Subject", text="Subject")
    avg_tree.heading("Average", text="Average Grade")
    avg_tree.column("#0", width=60)
    avg_tree.pack(fill="x", pady=6)

    # Searchable report area
    search_frame = tk.Frame(report_frame, bg="white")
    search_frame.pack(fill="both", expand=True, padx=20, pady=8)

    left = tk.Frame(search_frame, bg="white")
    right = tk.Frame(search_frame, bg="white")
    left.pack(side="left", fill="both", expand=True, padx=(0,10))
    right.pack(side="left", fill="both", expand=True)

    # Search controls
    tk.Label(left, text="Search by student:", bg="white").pack(anchor="w")
    report_student_var = tk.StringVar()
    report_student_menu = ttk.Combobox(left, textvariable=report_student_var, width=40)
    report_student_menu.pack(anchor="w", pady=4)

    tk.Label(left, text="Or search by subject:", bg="white").pack(anchor="w", pady=(8,0))
    report_subject_var = tk.StringVar()
    report_subject_menu = ttk.Combobox(left, textvariable=report_subject_var, width=40)
    report_subject_menu.pack(anchor="w", pady=4)

    tk.Button(left, text="Show Report", bg="#1abc9c", fg="white", command=lambda: show_search_report()).pack(anchor="w", pady=8)
    tk.Button(left, text="Refresh", bg="#3498db", fg="white", command=lambda: refresh_reports()).pack(anchor="w")

    # Results: grades and attendance
    tk.Label(right, text="Grades / Activities:", bg="white").pack(anchor="w")
    report_grade_tree = ttk.Treeview(right, columns=("Subject", "Exam", "Grade"))
    report_grade_tree.heading("#0", text="ID")
    report_grade_tree.heading("Subject", text="Subject")
    report_grade_tree.heading("Exam", text="Exam")
    report_grade_tree.heading("Grade", text="Grade")
    report_grade_tree.column("#0", width=60)
    report_grade_tree.pack(fill="both", expand=True, pady=6)

    tk.Label(right, text="Attendance summary:", bg="white").pack(anchor="w", pady=(8,0))
    attendance_summary_var = tk.StringVar()
    tk.Label(right, textvariable=attendance_summary_var, bg="white").pack(anchor="w")

    # Report helper functions
    def refresh_reports():
        # Update summary
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM subjects")
        total_subjects = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(grade) FROM grades")
        overall_avg = cursor.fetchone()[0] or 0.0

        # average per subject
        cursor.execute("""
            SELECT sub.subject_id, sub.subject_name, AVG(g.grade)
            FROM subjects sub
            LEFT JOIN grades g ON sub.subject_id = g.subject_id
            GROUP BY sub.subject_id
            ORDER BY sub.subject_name
        """)
        avg_rows = cursor.fetchall()

        summary_text_var.set(f"Total students: {total_students}\nTotal subjects: {total_subjects}\nOverall average grade: {overall_avg:.2f}")

        # populate avg_tree
        for row in avg_tree.get_children():
            avg_tree.delete(row)
        for r in avg_rows:
            sid, sname, avg = r
            avg_display = f"{avg:.2f}" if avg is not None else "N/A"
            avg_tree.insert("", "end", text=sid, values=(sname, avg_display))

        # refresh combobox lists
        report_student_menu.config(values=[student_display_string(sid, name) for sid, name in get_all_students()])
        report_subject_menu.config(values=[subject_display_string(sid, name) for sid, name in get_all_subjects()])

        # clear results
        for row in report_grade_tree.get_children():
            report_grade_tree.delete(row)
        attendance_summary_var.set("")

    def show_search_report():
        student_sel = report_student_var.get().strip()
        subject_sel = report_subject_var.get().strip()

        # clear old results
        for row in report_grade_tree.get_children():
            report_grade_tree.delete(row)
        attendance_summary_var.set("")

        if student_sel:
            try:
                sid = int(student_sel.split("—")[-1].strip())
            except:
                messagebox.showerror("Error", "Invalid student selection.")
                return
            # fetch grades for student
            cursor.execute("""
                SELECT g.grade_id, sub.subject_name, g.exam_name, g.grade
                FROM grades g
                JOIN subjects sub ON g.subject_id = sub.subject_id
                WHERE g.student_id=?
                ORDER BY sub.subject_name, g.exam_name
            """, (sid,))
            rows = cursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No grades found in this student")
            for r in rows:
                report_grade_tree.insert("", "end", text=r[0], values=(r[1], r[2], r[3]))
            # attendance summary
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id=?", (sid,))
            total_att = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'", (sid,))
            present = cursor.fetchone()[0]
            attendance_summary_var.set(f"Attendance: Present {present} / Total {total_att}")

        elif subject_sel:
            try:
                subid = int(subject_sel.split("—")[-1].strip())
            except:
                messagebox.showerror("Error", "Invalid subject selection")
                return
            cursor.execute("""
                SELECT g.grade_id, s.student_name, g.exam_name, g.grade
                FROM grades g
                JOIN students s ON g.student_id = s.student_id
                WHERE g.subject_id=?
                ORDER BY s.student_name, g.exam_name
            """, (subid,))
            rows = cursor.fetchall()
            if not rows:
                messagebox.showinfo("Info", "No grades found in subject")
            for r in rows:
                # use student name as 'Subject' column for context
                report_grade_tree.insert("", "end", text=r[0], values=(r[1], r[2], r[3]))
            attendance_summary_var.set("Attendance summary is per-student; choose one student to view their attendance")
        else:
            messagebox.showerror("Error", "PLEASE select a student and subject to show a report")

    # ---------------------------
    # Utility: refresh everything that depends on DB and student lists
    # ---------------------------
    def refresh_all_ui():
        refresh_students()
        # attendance combobox
        students_list_for_att_local = [student_display_string(sid, name) for sid, name in get_all_students()]
        student_menu.config(values=students_list_for_att_local)
        if students_list_for_att_local:
            student_var_att.set(students_list_for_att_local[0])
        else:
            student_var_att.set("")
        refresh_grades()
        refresh_subjects()
        refresh_attendance()
        refresh_section_buttons()
        update_stats()
        # if report visible, refresh it
        refresh_reports()

    # initial refresh actions
    refresh_all_ui()

    # initial view
    show_frame("Dashboard")
    update_stats()
    root.mainloop()

# start with login window
login_win.mainloop()