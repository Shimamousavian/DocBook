# DocBook - Doctor Appointment Booking System

## Overview
DocBook is a Django-based web application that allows patients to book appointments with doctors. It provides an intuitive platform for managing doctor schedules and patient bookings, offering seamless workflows for both parties.

## Features
- **User Authentication**: Patients can log in and manage their appointments.
- **Search Doctors**: Dynamic search functionality to find doctors by name or specialization.
- **View Doctor Schedules**: Patients can view available time slots and select a convenient one.
- **Appointment Management**: Patients can book, view, and confirm their appointments.
- **REST API**: Integrated API endpoints for searching doctors and managing data.

## Main Workflows

### Patient Workflow
1. **Login/Registration**:
   - Users can sign in or register using the registration form.
   - Registered users can manage appointments via the dashboard.

2. **Search Doctors**:
   - Search by name or specialization using the search bar on the dashboard.
   - Results display dynamically without reloading the page.

3. **View Doctor Schedule**:
   - Click on a doctor from the search results to view their available time slots.
   - Slots are color-coded:
     - **Green**: Available
     - **Red**: Taken
     - **Blue**: Reserved by the user

4. **Book Appointment**:
   - Select a time slot and confirm the appointment.
   - Notifications display the booking status.

5. **Dashboard Management**:
   - View all appointments with details (doctor, date, status).

### Admin Workflow
- Admin users can manage doctors, appointments, and other related data through the Django admin panel.

## API Endpoints
- **Search Doctors**: `/api/doctors/search/`
  - Accepts query parameters (`q`) for searching by name or specialization.
  - Returns JSON data with matching doctors.

## Technologies Used
- **Backend**: Django, Django REST Framework
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Authentication**: Django's built-in authentication system

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Shimamousavian/docbook.git
   cd docbook
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the database in `settings.py`.
4. Apply migrations:
   ```bash
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage
1. Access the app at `http://127.0.0.1:8000/`.
2. Register as a patient, log in, and start booking appointments.
3. Admins can manage the application through the admin panel at `/admin`.
