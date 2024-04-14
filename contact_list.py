from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableView, QInputDialog
from PyQt5.QtCore import Qt, QModelIndex

from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Step 2: Define database schema using SQLAlchemy
Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)

# Step 3: Connect to SQLite database using SQLAlchemy
engine = create_engine('sqlite:///contacts.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Step 4: Implement Model-View architecture using PyQt's QSqlTableModel
class ContactTableModel(QSqlTableModel):
    def __init__(self):
        super().__init__()
        self.setTable('contacts')
        self.select()

# Step 5: Develop the GUI Application
class ContactListApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Contact List")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        self.model = ContactTableModel()
        self.table_view.setModel(self.model)

        # Add buttons for CRUD operations
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)

        add_button = QPushButton("Add Contact")
        add_button.clicked.connect(self.add_contact)
        button_layout.addWidget(add_button)

        edit_button = QPushButton("Edit Contact")
        edit_button.clicked.connect(self.edit_contact)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete Contact")
        delete_button.clicked.connect(self.delete_contact)
        button_layout.addWidget(delete_button)

        view_all_button = QPushButton("View All Contacts")
        view_all_button.clicked.connect(self.view_all_contacts)
        button_layout.addWidget(view_all_button)

    def add_contact(self):
        name, ok = QInputDialog.getText(self, 'Add Contact', 'Enter name:')
        if ok:
            phone, ok = QInputDialog.getText(self, 'Add Contact', 'Enter phone number:')
            if ok:
                email, ok = QInputDialog.getText(self, 'Add Contact', 'Enter email address:')
                if ok:
                    new_contact = Contact(name=name, phone=phone, email=email)
                    session.add(new_contact)
                    session.commit()
                    print("Contact added:", name, phone, email)  # Check if contact is added
                    self.model.select()  # Refresh the model
                    # Find the index of the newly added contact
                    index = self.model.index(self.model.rowCount() - 1, 0)
                    # Scroll to the newly added contact
                    self.table_view.scrollTo(index, QTableView.PositionAtBottom)

    def edit_contact(self):
        selected_row = self.table_view.selectionModel().currentIndex().row()
        if selected_row >= 0:
            contact_id = self.model.index(selected_row, 0).data()
            contact = session.query(Contact).get(contact_id)
            if contact:
                name, ok = QInputDialog.getText(self, 'Edit Contact', 'Enter name:', text=contact.name)
                if ok:
                    phone, ok = QInputDialog.getText(self, 'Edit Contact', 'Enter phone number:', text=contact.phone)
                    if ok:
                        email, ok = QInputDialog.getText(self, 'Edit Contact', 'Enter email address:', text=contact.email)
                        if ok:
                            contact.name = name
                            contact.phone = phone
                            contact.email = email
                            session.commit()
                            self.model.select()

    def delete_contact(self):
        selected_row = self.table_view.selectionModel().currentIndex().row()
        if selected_row >= 0:
            contact_id = self.model.index(selected_row, 0).data()
            contact = session.query(Contact).get(contact_id)
            if contact:
                session.delete(contact)
                session.commit()
                self.model.select()

    def view_all_contacts(self):
        contacts = session.query(Contact).all()
        if contacts:
            message = "All Contacts:\n"
            for contact in contacts:
                message += f"Name: {contact.name}, Phone: {contact.phone}, Email: {contact.email}\n"
            QMessageBox.information(self, "All Contacts", message)
        else:
            QMessageBox.information(self, "All Contacts", "No contacts found.")

if __name__ == '__main__':
    app = QApplication([])
    window = ContactListApp()
    window.show()
    app.exec_()
