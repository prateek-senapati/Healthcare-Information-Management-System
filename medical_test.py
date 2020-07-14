import streamlit as st
from datetime import datetime, time
import database as db
import pandas as pd
import patient
import doctor

# function to verify medical test id
def verify_medical_test_id(medical_test_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM medical_test_record;
            """
        )
    for id in c.fetchall():
        if id[0] == medical_test_id:
            verify = True
            break
    conn.close()
    return verify

# function to show the details of medical test(s) given in a list (provided as a parameter)
def show_medical_test_details(list_of_medical_tests):
    medical_test_titles = ['Medical Test ID', 'Test name', 'Patient ID',
                          'Patient name', 'Doctor ID', 'Doctor name',
                          'Medical Lab Scientist ID',
                          'Test date and time [DD-MM-YYYY (hh:mm)]',
                          'Result date and time [DD-MM-YYYY (hh:mm)]',
                          'Result and diagnosis', 'Description',
                          'Comments', 'Cost (INR)']
    if len(list_of_medical_tests) == 0:
        st.warning('No data to show')
    elif len(list_of_medical_tests) == 1:
        medical_test_details = [x for x in list_of_medical_tests[0]]
        series = pd.Series(data = medical_test_details, index = medical_test_titles)
        st.write(series)
    else:
        medical_test_details = []
        for medical_test in list_of_medical_tests:
            medical_test_details.append([x for x in medical_test])
        df = pd.DataFrame(data = medical_test_details, columns = medical_test_titles)
        st.write(df)

# function to generate unique medical test id using current date and time
def generate_medical_test_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'T-{id_1}-{id_2}'
    return id

# function to fetch patient name from the database for the given patient id
def get_patient_name(patient_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM patient_record
            WHERE id = :id;
            """,
            { 'id': patient_id }
        )
    return c.fetchone()[0]

# function to fetch doctor name from the database for the given doctor id
def get_doctor_name(doctor_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM doctor_record
            WHERE id = :id;
            """,
            { 'id': doctor_id }
        )
    return c.fetchone()[0]

# class containing all the fields and methods required to work with the medical tests' table in the database
class Medical_Test:

    def __init__(self):
        self.id = str()
        self.test_name = str()
        self.patient_id = str()
        self.patient_name = str()
        self.doctor_id = str()
        self.doctor_name = str()
        self.medical_lab_scientist_id = str()
        self.test_date_time = str()
        self.result_date_time = str()
        self.cost = int()
        self.result_and_diagnosis = str()
        self.description = str()
        self.comments = str()

    # method to add a new medical test record to the database
    def add_medical_test(self):
        st.write('Enter medical test details:')
        self.test_name = st.text_input('Test name')
        patient_id = st.text_input('Patient ID')
        if patient_id == '':
            st.empty()
        elif not patient.verify_patient_id(patient_id):
            st.error('Invalid Patient ID')
        else:
            st.success('Verified')
            self.patient_id = patient_id
            self.patient_name = get_patient_name(patient_id)
        doctor_id = st.text_input('Doctor ID')
        if doctor_id == '':
            st.empty()
        elif not doctor.verify_doctor_id(doctor_id):
            st.error('Invalid Doctor ID')
        else:
            st.success('Verified')
            self.doctor_id = doctor_id
            self.doctor_name = get_doctor_name(doctor_id)
        self.medical_lab_scientist_id = st.text_input('Medical lab scientist ID')
        test_date = st.date_input('Test date (YYYY/MM/DD)').strftime('%d-%m-%Y')
        st.info('If the required date is not in the calendar, please type it in the box above.')
        test_time = st.time_input('Test time (hh:mm)', time(0, 0)).strftime('%H:%M')
        st.info('If the required time is not in the drop down list, please type it in the box above.')
        self.test_date_time = f'{test_date} ({test_time})'
        result_date = st.date_input('Result date (YYYY/MM/DD)').strftime('%d-%m-%Y')
        st.info('If the required date is not in the calendar, please type it in the box above.')
        result_time = st.time_input('Result time (hh:mm)', time(0, 0)).strftime('%H:%M')
        st.info('If the required time is not in the drop down list, please type it in the box above.')
        self.result_date_time = f'{result_date} ({result_time})'
        self.cost = st.number_input('Cost (INR)', value = 0, min_value = 0, max_value = 10000)
        result_and_diagnosis = st.text_area('Result and diagnosis')
        self.result_and_diagnosis = (lambda res_diag : 'Test result awaited' if res_diag == '' else res_diag)(result_and_diagnosis)
        description = st.text_area('Description')
        self.description = (lambda desc : None if desc == '' else desc)(description)
        comments = st.text_area('Comments (if any)')
        self.comments = (lambda comments : None if comments == '' else comments)(comments)
        self.id = generate_medical_test_id()
        save = st.button('Save')

        # executing SQLite statements to save the new medical test record to the database
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO medical_test_record
                    (
                        id, test_name, patient_id, patient_name, doctor_id,
                        doctor_name, medical_lab_scientist_id, test_date_time,
                        result_date_time, cost, result_and_diagnosis, description,
                        comments
                    )
                    VALUES (
                        :id, :name, :p_id, :p_name, :dr_id, :dr_name, :mls_id,
                        :test_date_time, :result_date_time, :cost,
                        :result_diagnosis, :desc, :comments
                    );
                    """,
                    {
                        'id': self.id, 'name': self.test_name,
                        'p_id': self.patient_id, 'p_name': self.patient_name,
                        'dr_id': self.doctor_id, 'dr_name': self.doctor_name,
                        'mls_id': self.medical_lab_scientist_id,
                        'test_date_time': self.test_date_time,
                        'result_date_time': self.result_date_time, 'cost': self.cost,
                        'result_diagnosis': self.result_and_diagnosis,
                        'desc': self.description, 'comments': self.comments
                    }
                )
            st.success('Medical test details saved successfully.')
            st.write('The Medical Test ID is: ', self.id)
            conn.close()

    # method to update an existing medical test record in the database
    def update_medical_test(self):
        id = st.text_input('Enter Medical Test ID of the medical test to be updated')
        if id == '':
            st.empty()
        elif not verify_medical_test_id(id):
            st.error('Invalid Medical Test ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the medical test before updating
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM medical_test_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the current details of the medical:')
                show_medical_test_details(c.fetchall())

            st.write('Enter new details of the medical test:')
            result_and_diagnosis = st.text_area('Result and diagnosis')
            self.result_and_diagnosis = (lambda res_diag : 'Test result awaited' if res_diag == '' else res_diag)(result_and_diagnosis)
            description = st.text_area('Description')
            self.description = (lambda desc : None if desc == '' else desc)(description)
            comments = st.text_area('Comments (if any)')
            self.comments = (lambda comments : None if comments == '' else comments)(comments)
            update = st.button('Update')

            # executing SQLite statements to update this medical test's record in the database
            if update:
                with conn:
                    c.execute(
                        """
                        UPDATE medical_test_record
                        SET result_and_diagnosis = :result_diagnosis,
                        description = :description, comments = :comments
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'result_diagnosis': self.result_and_diagnosis,
                            'description': self.description, 'comments': self.comments
                        }
                    )
                st.success('Medical test details updated successfully.')
                conn.close()

    # method to delete an existing medical test record from the database
    def delete_medical_test(self):
        id = st.text_input('Enter Medical Test ID of the medical test to be deleted')
        if id == '':
            st.empty()
        elif not verify_medical_test_id(id):
            st.error('Invalid Medical Test ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the medical test before deletion
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM medical_test_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the medical test to be deleted:')
                show_medical_test_details(c.fetchall())

                confirm = st.checkbox('Check this box to confirm deletion')
                if confirm:
                    delete = st.button('Delete')

                    # executing SQLite statements to delete this medical test's record from the database
                    if delete:
                        c.execute(
                            """
                            DELETE FROM medical_test_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Medical test details deleted successfully.')
            conn.close()

    # method to show all the medical tests of a particular patient (using patient id)
    def medical_tests_by_patient(self):
        patient_id = st.text_input('Enter Patient ID to get the medical test record of that patient')
        if patient_id == '':
            st.empty()
        elif not patient.verify_patient_id(patient_id):
            st.error('Invalid Patient ID')
        else:
            st.success('Verified')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM medical_test_record
                    WHERE patient_id = :p_id;
                    """,
                    { 'p_id': patient_id }
                )
                st.write('Here is the medical test record of', get_patient_name(patient_id), ':')
                show_medical_test_details(c.fetchall())
            conn.close()
