# 🏥 HealthStack - Hospital & Pharmacy Management System

HealthStack is a robust, all-in-one web application designed to digitize hospital operations. It integrates **Hospital Administration**, **Pharmacy Inventory**, and **Communication (Chat)** into a single platform using Python and Django.

## 🚀 Key Features

### 🏥 Hospital Module
* **Patient Management:** Secure registration and medical history tracking.
* **Doctor Dashboard:** View appointments, manage schedules, and write prescriptions.
* **Appointment Booking:** Seamless scheduling system for patients.

### 💊 Pharmacy Module
* **Inventory Management:** Track medicine stock levels in real-time.
* **Billing System:** Generate invoices for medicines.
* **Expiry Alerts:** Notifications for expiring stock (optional feature).

### 💬 Chat Module
* **Internal Communication:** Real-time chat between Doctors and Staff.
* **Support Channel:** Direct line for patients to ask quick queries.

### 🔐 Authentication & Security
* **Role-Based Access Control (RBAC):** Separate logins for Admin, Doctor, Pharmacist, and Patient.
* **Secure Data:** Encrypted passwords and secure database handling.

## 🛠️ Tech Stack
* **Backend:** Python, Django
* **Frontend:** HTML5, CSS3, Bootstrap
* **Database:** SQLite (Default)
* **Real-time:** AJAX / Django Channels (for Chat)

## 📦 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/vijayainala3/HealthStack.git](https://github.com/vijayainala3/HealthStack.git)
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd HealthStack
    ```
3.  **Create and activate virtual environment:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install django
    ```
5.  **Apply Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
6.  **Create Superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    ```
7.  **Run the Server:**
    ```bash
    python manage.py runserver
    ```

## 📷 Screenshots
*(Add screenshots of your dashboard here later)*

## 👤 Author
**Vijay Inala**
* **Email:** vijayainala3@gmail.com
* **GitHub:** [vijayainala3](https://github.com/vijayainala3)

---
*This project is for educational and portfolio purposes.*
