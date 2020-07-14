import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd
import department

# function to verify doctor id
def verify_doctor_id(doctor_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM doctor_record;
            """
        )
    for id in c.fetchall():
        if id[0] == doctor_id:
            verify = True
            break
    conn.close()
    return verify

# function to show the details of doctor(s) given in a list (provided as a parameter)
def show_doctor_details(list_of_doctors):
    doctor_titles = ['Doctor ID', 'Name', 'Age', 'Gender', 'Date of birth (DD-MM-YYYY)',
                     'Blood group', 'Department ID', 'Department name',
                     'Contact number', 'Alternate contact number', 'Aadhar ID / Voter ID',
                     'Email ID', 'Qualification', 'Specialisation',
                     'Years of experience', 'Address', 'City', 'State', 'PIN code']
    if len(list_of_doctors) == 0:
        st.warning('No data to show')
    elif len(list_of_doctors) == 1:
        doctor_details = [x for x in list_of_doctors[0]]
        series = pd.Series(data = doctor_details, index = doctor_titles)
        st.write(series)
    else:
        doctor_details = []
        for doctor in list_of_doctors:
            doctor_details.append([x for x in doctor])
        df = pd.DataFrame(data = doctor_details, columns = doctor_titles)
        st.write(df)

# function to calculate age using given date of birth
def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((dob.month, dob.day) > (today.month, today.day))
    return age

# function to generate unique doctor id using current date and time
def generate_doctor_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'DR-{id_1}-{id_2}'
    return id

# function to fetch department name from the database for the given department id
def get_department_name(dept_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM department_record
            WHERE id = :id;
            """,
            { 'id': dept_id }
        )
    return c.fetchone()[0]

# class containing all the fields and methods required to work with the doctors' table in the database
class Doctor:

    def __init__(self):
        self.name = str()
        self.id = str()
        self.age = int()
        self.gender = str()
        self.date_of_birth = str()
        self.blood_group = str()
        self.department_id = str()
        self.department_name = str()
        self.contact_number_1 = str()
        self.contact_number_2 = str()
        self.aadhar_or_voter_id = str()
        self.email_id = str()
        self.qualification = str()
        self.specialisation = str()
        self.years_of_experience = int()
        self.address = str()
        self.city = str()
        self.state = str()
        self.pin_code = str()

    # method to add a new doctor record to the database
    def add_doctor(self):
        st.write('Enter doctor details:')
        self.name = st.text_input('Full name')
        gender = st.radio('Gender', ['Female', 'Male', 'Other'])
        if gender == 'Other':
            gender = st.text_input('Please mention')
        self.gender = gender
        dob = st.date_input('Date of birth (YYYY/MM/DD)')
        st.info('If the required date is not in the calendar, please type it in the box above.')
        self.date_of_birth = dob.strftime('%d-%m-%Y')       # converts date of birth to the desired string format
        self.age = calculate_age(dob)
        self.blood_group = st.text_input('Blood group')
        department_id = st.text_input('Department ID')
        if department_id == '':
            st.empty()
        elif not department.verify_department_id(department_id):
            st.error('Invalid Department ID')
        else:
            st.success('Verified')
            self.department_id = department_id
            self.department_name = get_department_name(department_id)
        self.contact_number_1 = st.text_input('Contact number')
        contact_number_2 = st.text_input('Alternate contact number (optional)')
        self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
        self.aadhar_or_voter_id = st.text_input('Aadhar ID / Voter ID')
        self.email_id = st.text_input('Email ID')
        self.qualification = st.text_input('Qualification')
        self.specialisation = st.text_input('Specialisation')
        self.years_of_experience = st.number_input('Years of experience', value = 0, min_value = 0, max_value = 100)
        self.address = st.text_area('Address')
        self.city = st.text_input('City')
        self.state = st.text_input('State')
        self.pin_code = st.text_input('PIN code')
        self.id = generate_doctor_id()
        save = st.button('Save')

        # executing SQLite statements to save the new doctor record to the database
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO doctor_record
                    (
                        id, name, age, gender, date_of_birth, blood_group,
                        department_id, department_name, contact_number_1,
                        contact_number_2, aadhar_or_voter_id, email_id,
                        qualification, specialisation, years_of_experience,
                        address, city, state, pin_code
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :blood_group, :dept_id,
                        :dept_name, :phone_1, :phone_2, :uid, :email_id, :qualification,
                        :specialisation, :experience, :address, :city, :state, :pin
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'blood_group': self.blood_group,
                        'dept_id': self.department_id,
                        'dept_name': self.department_name,
                        'phone_1': self.contact_number_1,
                        'phone_2': self.contact_number_2,
                        'uid': self.aadhar_or_voter_id, 'email_id': self.email_id,
                        'qualification': self.qualification,
                        'specialisation': self.specialisation,
                        'experience': self.years_of_experience,
                        'address': self.address, 'city': self.city,
                        'state': self.state, 'pin': self.pin_code
                    }
                )
            st.success('Doctor details saved successfully.')
            st.write('Your Doctor ID is: ', self.id)
            conn.close()

    # method to update an existing doctor record in the database
    def update_doctor(self):
        id = st.text_input('Enter Doctor ID of the doctor to be updated')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('Invalid Doctor ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the doctor before updating
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the current details of the doctor:')
                show_doctor_details(c.fetchall())

            st.write('Enter new details of the doctor:')
            department_id = st.text_input('Department ID')
            if department_id == '':
                st.empty()
            elif not department.verify_department_id(department_id):
                st.error('Invalid Department ID')
            else:
                st.success('Verified')
                self.department_id = department_id
                self.department_name = get_department_name(department_id)
            self.contact_number_1 = st.text_input('Contact number')
            contact_number_2 = st.text_input('Alternate contact number (optional)')
            self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
            self.email_id = st.text_input('Email ID')
            self.qualification = st.text_input('Qualification')
            self.specialisation = st.text_input('Specialisation')
            self.years_of_experience = st.number_input('Years of experience', value = 0, min_value = 0, max_value = 100)
            self.address = st.text_area('Address')
            self.city = st.text_input('City')
            self.state = st.text_input('State')
            self.pin_code = st.text_input('PIN code')
            update = st.button('Update')

            # executing SQLite statements to update this doctor's record in the database
            if update:
                with conn:
                    c.execute(
                        """
                        SELECT date_of_birth
                        FROM doctor_record
                        WHERE id = :id;
                        """,
                        { 'id': id }
                    )

                    # converts date of birth to the required format for age calculation
                    dob = [int(d) for d in c.fetchone()[0].split('-')[::-1]]
                    dob = date(dob[0], dob[1], dob[2])
                    self.age = calculate_age(dob)

                with conn:
                    c.execute(
                        """
                        UPDATE doctor_record
                        SET age = :age, department_id = :dept_id,
                        department_name = :dept_name, contact_number_1 = :phone_1,
                        contact_number_2 = :phone_2, email_id = :email_id,
                        qualification = :qualification, specialisation = :specialisation,
                        years_of_experience = :experience, address = :address,
                        city = :city, state = :state, pin_code = :pin
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'age': self.age, 'dept_id': self.department_id,
                            'dept_name': self.department_name,
                            'phone_1': self.contact_number_1,
                            'phone_2': self.contact_number_2, 'email_id': self.email_id,
                            'qualification': self.qualification,
                            'specialisation': self.specialisation,
                            'experience': self.years_of_experience,
                            'address': self.address, 'city': self.city,
                            'state': self.state, 'pin': self.pin_code
                        }
                    )
                st.success('Doctor details updated successfully.')
                conn.close()

    # method to delete an existing doctor record from the database
    def delete_doctor(self):
        id = st.text_input('Enter Doctor ID of the doctor to be deleted')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('Invalid Doctor ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the doctor before deletion
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the doctor to be deleted:')
                show_doctor_details(c.fetchall())

                confirm = st.checkbox('Check this box to confirm deletion')
                if confirm:
                    delete = st.button('Delete')

                    # executing SQLite statements to delete this doctor's record from the database
                    if delete:
                        c.execute(
                            """
                            DELETE FROM doctor_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Doctor details deleted successfully.')
            conn.close()

    # method to show the complete doctor record
    def show_all_doctors(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT *
                FROM doctor_record;
                """
            )
            show_doctor_details(c.fetchall())
        conn.close()

    # method to search and show a particular doctor's details in the database using doctor id
    def search_doctor(self):
        id = st.text_input('Enter Doctor ID of the doctor to be searched')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('Invalid Doctor ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the doctor you searched for:')
                show_doctor_details(c.fetchall())
            conn.close()
