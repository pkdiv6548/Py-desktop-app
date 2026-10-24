import sys
import sqlite3
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QLineEdit, QTextEdit,
    QCheckBox, QMessageBox, QScrollArea, QGraphicsOpacityEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)

APP_NAME = "Py Desktop App"
APP_DIR = Path.home() / ".py_desktop_app"
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "app.db"

DARK_STYLE = """
* { font-family: 'Segoe UI', sans-serif; }
QMainWindow, QWidget#root { background: #0b1020; color: #e8ecf8; }
QWidget { color: #e8ecf8; font-size: 13px; }
QFrame#sidebar { background: #0f172a; border-right: 1px solid #25304a; }
QLabel#brand { font-size: 21px; font-weight: 800; color: #ffffff; padding: 8px; }
QLabel#muted { color: #9aa7c2; }
QLabel#pageTitle { font-size: 28px; font-weight: 800; color: #f8fafc; }
QLabel#metricValue { font-size: 27px; font-weight: 800; color: #ffffff; }
QLabel#metricCaption { color: #9aa7c2; font-size: 12px; }
QFrame#card { background: #131c31; border: 1px solid #26324c; border-radius: 16px; }
QPushButton { background: #1a2540; border: 1px solid #2a3858; border-radius: 9px; padding: 10px 13px; text-align: left; }
QPushButton:hover { background: #253457; border-color: #637cff; }
QPushButton#primary { background: #6658f5; border: 1px solid #8176ff; color: white; font-weight: 700; }
QPushButton#primary:hover { background: #7b70ff; }
QPushButton#nav { background: transparent; border: 0; padding: 12px; text-align: left; color: #aeb9d2; }
QPushButton#nav:hover { background: #1a2540; color: white; }
QPushButton#navActive { background: #242b57; border: 1px solid #4849a5; color: #ffffff; padding: 12px; text-align: left; border-radius: 9px; }
QLineEdit, QTextEdit { background: #0c1427; border: 1px solid #2a3858; border-radius: 9px; padding: 10px; selection-background-color: #6658f5; }
QLineEdit:focus, QTextEdit:focus { border-color: #8176ff; }
QCheckBox { spacing: 10px; padding: 8px; }
QCheckBox::indicator { width: 17px; height: 17px; }
QTableWidget { background: #111a2e; alternate-background-color: #151f35; border: 1px solid #26324c; border-radius: 10px; gridline-color: #26324c; }
QHeaderView::section { background: #1a2540; color: #b8c4df; border: 0; padding: 10px; font-weight: 700; }
QScrollArea { border: none; }
"""

class Store:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.db.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created TEXT NOT NULL
        )""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created TEXT NOT NULL
        )""")
        self.db.commit()

    def tasks(self, query=""):
        return self.db.execute(
            "SELECT id,title,done,created FROM tasks WHERE title LIKE ? ORDER BY id DESC",
            (f"%{query}%",)
        ).fetchall()

    def add_task(self, title):
        self.db.execute("INSERT INTO tasks(title,created) VALUES(?,?)",
                        (title, datetime.now().strftime("%Y-%m-%d %H:%M")))
        self.db.commit()

    def set_task(self, task_id, done):
        self.db.execute("UPDATE tasks SET done=? WHERE id=?", (int(done), task_id))
        self.db.commit()

    def delete_task(self, task_id):
        self.db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.db.commit()

    def notes(self, query=""):
        return self.db.execute(
            "SELECT id,title,body,created FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id DESC",
            (f"%{query}%", f"%{query}%")
        ).fetchall()

    def add_note(self, title, body):
        self.db.execute("INSERT INTO notes(title,body,created) VALUES(?,?,?)",
                        (title, body, datetime.now().strftime("%Y-%m-%d %H:%M")))
        self.db.commit()

    def delete_note(self, note_id):
        self.db.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self.db.commit()

    def counts(self):
        total = self.db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        done = self.db.execute("SELECT COUNT(*) FROM tasks WHERE done=1").fetchone()[0]
        notes = self.db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        return total, done, notes

class MetricCard(QFrame):
    def __init__(self, caption, value, accent):
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        stripe = QFrame()
        stripe.setFixedHeight(4)
        stripe.setStyleSheet(f"background:{accent}; border-radius:2px;")
        label = QLabel(caption)
        label.setObjectName("metricCaption")
        self.value = QLabel(str(value))
        self.value.setObjectName("metricValue")
        layout.addWidget(stripe)
        layout.addSpacing(7)
        layout.addWidget(label)
        layout.addWidget(self.value)
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.store = Store()
        self.current_page = "Dashboard"
        self.setWindowTitle(APP_NAME)
        self.resize(1180, 760)
        self.setMinimumSize(850, 580)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 20, 16, 18)
        side.setSpacing(7)

        brand = QLabel("✦  PY DESKTOP")
        brand.setObjectName("brand")
        side.addWidget(brand)
        subtitle = QLabel("YOUR PERSONAL WORKSPACE")
        subtitle.setObjectName("muted")
        subtitle.setStyleSheet("font-size:9px; letter-spacing:1px; padding: 4px 8px 18px;")
        side.addWidget(subtitle)

        self.nav_buttons = {}
        for name, icon in [("Dashboard", "◈"), ("Tasks", "✓"), ("Notes", "▤"), ("Settings", "⚙")]:
            btn = QPushButton(f"{icon}    {name}")
            btn.setObjectName("nav")
            btn.clicked.connect(lambda checked=False, n=name: self.navigate(n))
            self.nav_buttons[name] = btn
            side.addWidget(btn)
        side.addStretch()

        local_label = QLabel("●  LOCAL DATABASE")
        local_label.setObjectName("muted")
        local_label.setStyleSheet("padding:8px; font-size:10px;")
        side.addWidget(local_label)
        version = QLabel("Version 1.0.0  •  Offline")
        version.setObjectName("muted")
        version.setStyleSheet("padding: 0 8px; font-size:10px;")
        side.addWidget(version)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 22, 28, 24)
        content_layout.setSpacing(18)

        top = QHBoxLayout()
        self.breadcrumb = QLabel("WORKSPACE  /  DASHBOARD")
        self.breadcrumb.setObjectName("muted")
        self.clock = QLabel()
        self.clock.setObjectName("muted")
        top.addWidget(self.breadcrumb)
        top.addStretch()
        top.addWidget(self.clock)
        content_layout.addLayout(top)

        self.pages = QStackedWidget()
        content_layout.addWidget(self.pages, 1)
        shell.addWidget(sidebar)
        shell.addWidget(content, 1)

        self.build_dashboard()
        self.build_tasks()
        self.build_notes()
        self.build_settings()
        self.navigate("Dashboard")

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

    def heading(self, title, description):
        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 4)
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        desc = QLabel(description)
        desc.setObjectName("muted")
        layout.addWidget(title_label)
        layout.addWidget(desc)
        return wrap

    def card(self):
        frame = QFrame()
        frame.setObjectName("card")
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        return frame

    def build_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.addWidget(self.heading("Good to see you. ✨", "Your work, organized in one calm space."))
        metrics = QHBoxLayout()
        metrics.setSpacing(14)
        self.metric_tasks = MetricCard("TOTAL TASKS", 0, "#8b7cff")
        self.metric_done = MetricCard("COMPLETED", 0, "#32d6a0")
        self.metric_notes = MetricCard("SAVED NOTES", 0, "#4eb5ff")
        for m in [self.metric_tasks, self.metric_done, self.metric_notes]:
            metrics.addWidget(m, 1)
        layout.addLayout(metrics)

        quick = self.card()
        ql = QVBoxLayout(quick)
        ql.setContentsMargins(20, 18, 20, 18)
        title = QLabel("Quick capture")
        title.setStyleSheet("font-size:18px;font-weight:700;")
        ql.addWidget(title)
        ql.addWidget(QLabel("Add a task without leaving your dashboard."))
        row = QHBoxLayout()
        self.quick_task = QLineEdit()
        self.quick_task.setPlaceholderText("What would you like to get done?")
        self.quick_task.returnPressed.connect(self.add_quick_task)
        add = QPushButton("＋  Add task")
        add.setObjectName("primary")
        add.clicked.connect(self.add_quick_task)
        row.addWidget(self.quick_task, 1)
        row.addWidget(add)
        ql.addLayout(row)
        layout.addWidget(quick)

        recent = self.card()
        rl = QVBoxLayout(recent)
        rl.setContentsMargins(20, 18, 20, 18)
        title = QLabel("Recent tasks")
        title.setStyleSheet("font-size:18px;font-weight:700;")
        rl.addWidget(title)
        self.recent_list = QVBoxLayout()
        rl.addLayout(self.recent_list)
        layout.addWidget(recent, 1)
        self.pages.addWidget(page)

    def build_tasks(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.addWidget(self.heading("Tasks", "Keep the next step clear. Your tasks are saved locally."))
        row = QHBoxLayout()
        self.task_search = QLineEdit()
        self.task_search.setPlaceholderText("Search tasks…")
        self.task_search.textChanged.connect(self.refresh_tasks)
        row.addWidget(self.task_search, 1)
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("New task title")
        self.task_input.returnPressed.connect(self.add_task)
        row.addWidget(self.task_input, 2)
        add = QPushButton("＋ Add")
        add.setObjectName("primary")
        add.clicked.connect(self.add_task)
        row.addWidget(add)
        layout.addLayout(row)

        self.task_table = QTableWidget(0, 4)
        self.task_table.setHorizontalHeaderLabels(["Done", "Task", "Created", "Action"])
        self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.task_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.task_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.task_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.task_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.task_table.setAlternatingRowColors(True)
        layout.addWidget(self.task_table, 1)
        self.pages.addWidget(page)

    def build_notes(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)
        layout.addWidget(self.heading("Notes", "Capture ideas, reminders and useful details."))
        form = self.card()
        fl = QVBoxLayout(form)
        fl.setContentsMargins(18, 16, 18, 16)
        self.note_title = QLineEdit()
        self.note_title.setPlaceholderText("Note title")
        self.note_body = QTextEdit()
        self.note_body.setPlaceholderText("Write your note here…")
        self.note_body.setMaximumHeight(105)
        row = QHBoxLayout()
        row.addWidget(self.note_title, 1)
        save = QPushButton("Save note")
        save.setObjectName("primary")
        save.clicked.connect(self.add_note)
        row.addWidget(save)
        fl.addLayout(row)
        fl.addWidget(self.note_body)
        layout.addWidget(form)
        self.note_search = QLineEdit()
        self.note_search.setPlaceholderText("Search saved notes…")
        self.note_search.textChanged.connect(self.refresh_notes)
        layout.addWidget(self.note_search)
        self.notes_area = QVBoxLayout()
        notes_widget = QWidget()
        notes_widget.setLayout(self.notes_area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(notes_widget)
        layout.addWidget(scroll, 1)
        self.pages.addWidget(page)

    def build_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self.heading("Settings", "A few details about this local application."))
        panel = self.card()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(22, 22, 22, 22)
        for title, detail in [
            ("Application", "Py Desktop App · Version 1.0.0"),
            ("Storage", f"SQLite database saved at: {DB_PATH}"),
            ("Privacy", "Your tasks and notes stay on this computer. No external API is used."),
            ("Theme", "Dark theme is enabled for this starter release."),
        ]:
            h = QLabel(title)
            h.setStyleSheet("font-size:15px;font-weight:700;")
            d = QLabel(detail)
            d.setObjectName("muted")
            d.setWordWrap(True)
            pl.addWidget(h)
            pl.addWidget(d)
            pl.addSpacing(14)
        layout.addWidget(panel)
        layout.addStretch()
        self.pages.addWidget(page)

    def navigate(self, name):
        names = ["Dashboard", "Tasks", "Notes", "Settings"]
        index = names.index(name)
        self.pages.setCurrentIndex(index)
        self.current_page = name
        self.breadcrumb.setText(f"WORKSPACE  /  {name.upper()}")
        for n, button in self.nav_buttons.items():
            button.setObjectName("navActive" if n == name else "nav")
            button.style().unpolish(button)
            button.style().polish(button)
        if name == "Dashboard":
            self.refresh_dashboard()
        elif name == "Tasks":
            self.refresh_tasks()
        elif name == "Notes":
            self.refresh_notes()
        self.animate_page()

    def animate_page(self):
        page = self.pages.currentWidget()
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(220)
        anim.setStartValue(0.55)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: page.setGraphicsEffect(None))
        self._page_animation = anim
        anim.start()

    def update_clock(self):
        self.clock.setText(datetime.now().strftime("%a, %d %b  •  %I:%M:%S %p"))

    def add_quick_task(self):
        title = self.quick_task.text().strip()
        if not title:
            return
        self.store.add_task(title)
        self.quick_task.clear()
        self.refresh_dashboard()

    def add_task(self):
        title = self.task_input.text().strip()
        if not title:
            self.task_input.setFocus()
            return
        self.store.add_task(title)
        self.task_input.clear()
        self.refresh_tasks()
        self.refresh_dashboard()

    def refresh_tasks(self):
        if not hasattr(self, "task_table"):
            return
        rows = self.store.tasks(self.task_search.text() if hasattr(self, "task_search") else "")
        self.task_table.setRowCount(0)
        for task_id, title, done, created in rows:
            r = self.task_table.rowCount()
            self.task_table.insertRow(r)
            check = QCheckBox()
            check.setChecked(bool(done))
            check.stateChanged.connect(lambda state, tid=task_id: self.toggle_task(tid, state))
            self.task_table.setCellWidget(r, 0, check)
            item = QTableWidgetItem(title)
            if done:
                item.setForeground(Qt.GlobalColor.gray)
            self.task_table.setItem(r, 1, item)
            self.task_table.setItem(r, 2, QTableWidgetItem(created))
            delete = QPushButton("Delete")
            delete.clicked.connect(lambda checked=False, tid=task_id: self.delete_task(tid))
            self.task_table.setCellWidget(r, 3, delete)
            self.task_table.setRowHeight(r, 43)

    def toggle_task(self, task_id, state):
        self.store.set_task(task_id, state == Qt.CheckState.Checked.value)
        self.refresh_tasks()
        self.refresh_dashboard()

    def delete_task(self, task_id):
        self.store.delete_task(task_id)
        self.refresh_tasks()
        self.refresh_dashboard()

    def add_note(self):
        title = self.note_title.text().strip()
        body = self.note_body.toPlainText().strip()
        if not title or not body:
            QMessageBox.information(self, "Missing details", "Please enter both a note title and its content.")
            return
        self.store.add_note(title, body)
        self.note_title.clear()
        self.note_body.clear()
        self.refresh_notes()

    def delete_note(self, note_id):
        self.store.delete_note(note_id)
        self.refresh_notes()

    def refresh_notes(self):
        if not hasattr(self, "notes_area"):
            return
        while self.notes_area.count():
            item = self.notes_area.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        query = self.note_search.text() if hasattr(self, "note_search") else ""
        rows = self.store.notes(query)
        if not rows:
            empty = QLabel("No notes yet. Add your first note above.")
            empty.setObjectName("muted")
            self.notes_area.addWidget(empty)
        for note_id, title, body, created in rows:
            card = self.card()
            cl = QVBoxLayout(card)
            header = QHBoxLayout()
            heading = QLabel(title)
            heading.setStyleSheet("font-size:16px;font-weight:700;")
            date = QLabel(created)
            date.setObjectName("muted")
            delete = QPushButton("Delete")
            delete.clicked.connect(lambda checked=False, nid=note_id: self.delete_note(nid))
            header.addWidget(heading, 1)
            header.addWidget(date)
            header.addWidget(delete)
            content = QLabel(body)
            content.setWordWrap(True)
            cl.addLayout(header)
            cl.addWidget(content)
            self.notes_area.addWidget(card)
        self.notes_area.addStretch()

    def refresh_dashboard(self):
        total, done, notes = self.store.counts()
        self.metric_tasks.value.setText(str(total))
        self.metric_done.value.setText(str(done))
        self.metric_notes.value.setText(str(notes))
        while self.recent_list.count():
            item = self.recent_list.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        rows = self.store.tasks()[:5]
        if not rows:
            label = QLabel("Nothing here yet — add a task above to get started.")
            label.setObjectName("muted")
            self.recent_list.addWidget(label)
        for task_id, title, is_done, created in rows:
            line = QHBoxLayout()
            mark = QLabel("✓" if is_done else "○")
            mark.setStyleSheet("color:#32d6a0;font-size:17px;font-weight:800;")
            text = QLabel(title)
            if is_done:
                text.setStyleSheet("color:#7f8ba6;text-decoration:line-through;")
            date = QLabel(created)
            date.setObjectName("muted")
            line.addWidget(mark)
            line.addWidget(text, 1)
            line.addWidget(date)
            self.recent_list.addLayout(line)
        self.recent_list.addStretch()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
