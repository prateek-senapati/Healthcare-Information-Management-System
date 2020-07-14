import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd

# function to verify patient id
def verify_patient_id(patient_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM patient_record;
            """
        )
    for id in c.fetchall():
        if id[0] == patient_id:
            verify = True
            break
    conn.close()
    return verify

# function to generate unique patient id using current date and time
def generate_patient_id(reg_date, reg_time):
    id_1 = ''.join(reg_time.split(':')[::-1])
    id_2 = ''.join(reg_date.split('-')[::-1])[2:]
    id = f'P-{id_1}-{id_2}'
    return id

# function to calculate age using given date of birth
def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((dob.month, dob.day) > (today.month, today.day))
    return age

# function to show the details of patient(s) given in a list (provided as a parameter)
def show_patient_details(list_of_patients):
    patient_titles = ['Patient ID', 'Name', 'Age', 'Gender', 'Date of birth (DD-MM-YYYY)',
                     'Blood group', 'Contact number', 'Alternate contact number',
                     'Aadhar ID / Voter ID', 'Weight (kg)', 'Height (cm)', 'Address',
                     'City', 'State', 'PIN code', "Next of kin's name",
                     "Next of kin's relation to patient",
                     "Next of kin's contact number", 'Email ID',
                     'Date of registration (DD-MM-YYYY)', 'Time of registration (hh:mm:ss)']
    if len(list_of_patients) == 0:
        st.warning('No data to show')
    elif len(list_of_patients) == 1:
        patient_details = [x for x in list_of_patients[0]]
        series = pd.Series(data = patient_details, index = patient_titles)
        st.write(series)
    else:
        patient_details = []
        for patient in list_of_patients:
            patient_details.append([x for x in patient])
        df = pd.DataFrame(data = patient_details, columns = patient_titles)
        st.write(df)

# class containing all the fields and methods required to work with the patients' table in the database
class Patient:

    def __init__(self):
        self.name = str()
        self.id = str()
        self.gender = str()
        self.age = int()
        self.contact_number_1 = str()
        self.contact_number_2 = str()
        self.date_of_birth = str()
        self.blood_group = str()
        self.date_of_registration = str()
        self.time_of_registration = str()
        self.email_id = str()
        self.aadhar_or_voter_id = str()
        self.height = int()
        self.weight = int()
        self.next_of_kin_name = str()
        self.next_of_kin_relation_to_patient = str()
        self.next_of_kin_contact_number = str()
        self.address = str()
        self.city = str()
        self.state = str()
        self.pin_code = str()

    # method to add a new patient record to the database
    def add_patient(self):
        st.write('Enter patient details:')
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
        self.contact_number_1 = st.text_input('Contact number')
        contact_number_2 = st.text_input('Alternate contact number (optional)')
        self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
        self.aadhar_or_voter_id = st.text_input('Aadhar ID / Voter ID')
        self.weight = st.number_input('Weight (in kg)', value = 0, min_value = 0, max_value = 400)
        self.height = st.number_input('Height (in cm)', value = 0, min_value = 0, max_value = 275)
        self.address = st.text_area('Address')
        self.city = st.text_input('City')
        self.state = st.text_input('State')
        self.pin_code = st.text_input('PIN code')
        self.next_of_kin_name = st.text_input("Next of kin's name")
        self.next_of_kin_relation_to_patient = st.text_input("Next of kin's relation to patient")
        self.next_of_kin_contact_number = st.text_input("Next of kin's contact number")
        email_id = st.text_input('Email ID (optional)')
        self.email_id = (lambda email : None if email == '' else email)(email_id)
        self.date_of_registration = datetime.now().strftime('%d-%m-%Y')
        self.time_of_registration = datetime.now().strftime('%H:%M:%S')
        self.id = generate_patient_id(self.date_of_registration,
                    self.time_of_registration)
        save = st.button('Save')

        # executing SQLite statements to save the new patient record to the database
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO patient_record
                    (
                        id, name, age, gender, date_of_birth, blood_group,
                        contact_number_1, contact_number_2, aadhar_or_voter_id,
                        weight, height, address,city, state, pin_code,
                        next_of_kin_name, next_of_kin_relation_to_patient,
                        next_of_kin_contact_number, email_id,
                        date_of_registration, time_of_registration
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :blood_group,
                        :phone_1, :phone_2, :uid, :weight, :height,
                        :address, :city, :state, :pin,
                        :kin_name, :kin_relation, :kin_phone, :email_id,
                        :reg_date, :reg_time
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'blood_group': self.blood_group,
                        'phone_1': self.contact_number_1,
                        'phone_2': self.contact_number_2,
                        'uid': self.aadhar_or_voter_id, 'weight': self.weight,
                        'height': self.height, 'address': self.address,
                        'city': self.city, 'state': self.state,
                        'pin': self.pin_code, 'kin_name': self.next_of_kin_name,
                        'kin_relation': self.next_of_kin_relation_to_patient,
                        'kin_phone': self.next_of_kin_contact_number,
                        'email_id': self.email_id,
                        'reg_date': self.date_of_registration,
                        'reg_time': self.time_of_registration
                    }
                )
            st.success('Patient details saved successfully.')
            st.write('Your Patient ID is: ', self.id)
            conn.close()

    # method to update an existing patient record in the database
    def update_patient(self):
        id = st.text_input('Enter Patient ID of the patient to be updated')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Invalid Patient ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the patient before updating
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the current details of the patient:')
                show_patient_details(c.fetchall())

            st.write('Enter new details of the patient:')
            self.contact_number_1 = st.text_input('Contact number')
            contact_number_2 = st.text_input('Alternate contact number (optional)')
            self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
            self.weight = st.number_input('Weight (in kg)', value = 0, min_value = 0, max_value = 400)
            self.height = st.number_input('Height (in cm)', value = 0, min_value = 0, max_value = 275)
            self.address = st.text_area('Address')
            self.city = st.text_input('City')
            self.state = st.text_input('State')
            self.pin_code = st.text_input('PIN code')
            self.next_of_kin_name = st.text_input("Next of kin's name")
            self.next_of_kin_relation_to_patient = st.text_input("Next of kin's relation to patient")
            self.next_of_kin_contact_number = st.text_input("Next of kin's contact number")
            email_id = st.text_input('Email ID (optional)')
            self.email_id = (lambda email : None if email == '' else email)(email_id)
            update = st.button('Update')

            # executing SQLite statements to update this patient's record in the database
            if update:
                with conn:
                    c.execute(
                        """
                        SELECT date_of_birth
                        FROM patient_record
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
                        UPDATE patient_record
                        SET age = :age, contact_number_1 = :phone_1,
                        contact_number_2 = :phone_2, weight = :weight,
                        height = :height, address = :address, city = :city,
                        state = :state, pin_code = :pin, next_of_kin_name = :kin_name,
                        next_of_kin_relation_to_patient = :kin_relation,
                        next_of_kin_contact_number = :kin_phone, email_id = :email_id
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'age': self.age,
                            'phone_1': self.contact_number_1,
                            'phone_2': self.contact_number_2,
                            'weight': self.weight, 'height': self.height,
                            'address': self.address, 'city': self.city,
                            'state': self.state, 'pin': self.pin_code,
                            'kin_name': self.next_of_kin_name,
                            'kin_relation': self.next_of_kin_relation_to_patient,
                            'kin_phone': self.next_of_kin_contact_number,
                            'email_id': self.email_id
                        }
                    )
                st.success('Patient details updated successfully.')
                conn.close()

    # method to delete an existing patient record from the database
    def delete_patient(self):
        id = st.text_input('Enter Patient ID of the patient to be deleted')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Invalid Patient ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the patient before deletion
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the patient to be deleted:')
                show_patient_details(c.fetchall())

                confirm = st.checkbox('Check this box to confirm deletion')
                if confirm:
                    delete = st.button('Delete')

                    # executing SQLite statements to delete this patient's record from the database
                    if delete:
                        c.execute(
                            """
                            DELETE FROM patient_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Patient details deleted successfully.')
            conn.close()

    # method to show the complete patient record
    def show_all_patients(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT *
                FROM patient_record;
                """
            )
            show_patient_details(c.fetchall())
        conn.close()

    # method to search and show a particular patient's details in the database using patient id
    def search_patient(self):
        id = st.text_input('Enter Patient ID of the patient to be searched')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Invalid Patient ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the patient you searched for:')
                show_patient_details(c.fetchall())
            conn.close()
