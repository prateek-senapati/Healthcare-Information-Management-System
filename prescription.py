import streamlit as st
from datetime import datetime
import database as db
import pandas as pd
import patient
import doctor

# function to verify prescription id
def verify_prescription_id(prescription_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM prescription_record;
            """
        )
    for id in c.fetchall():
        if id[0] == prescription_id:
            verify = True
            break
    conn.close()
    return verify

# function to show the details of prescription(s) given in a list (provided as a parameter)
def show_prescription_details(list_of_prescriptions):
    prescription_titles = ['Prescription ID', 'Patient ID', 'Patient name',
                          'Doctor ID', 'Doctor name', 'Diagnosis', 'Comments',
                          'Medicine 1 name', 'Medicine 1 dosage and description',
                          'Medicine 2 name', 'Medicine 2 dosage and description',
                          'Medicine 3 name', 'Medicine 3 dosage and description',]
    if len(list_of_prescriptions) == 0:
        st.warning('No data to show')
    elif len(list_of_prescriptions) == 1:
        prescription_details = [x for x in list_of_prescriptions[0]]
        series = pd.Series(data = prescription_details, index = prescription_titles)
        st.write(series)
    else:
        prescription_details = []
        for prescription in list_of_prescriptions:
            prescription_details.append([x for x in prescription])
        df = pd.DataFrame(data = prescription_details, columns = prescription_titles)
        st.write(df)

# function to generate unique prescription id using current date and time
def generate_prescription_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'M-{id_1}-{id_2}'
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

# class containing all the fields and methods required to work with the prescriptions' table in the database
class Prescription:

    def __init__(self):
        self.id = str()
        self.patient_id = str()
        self.patient_name = str()
        self.doctor_id = str()
        self.doctor_name = str()
        self.diagnosis = str()
        self.comments = str()
        self.medicine_1_name = str()
        self.medicine_1_dosage_description = str()
        self.medicine_2_name = str()
        self.medicine_2_dosage_description = str()
        self.medicine_3_name = str()
        self.medicine_3_dosage_description = str()

    # method to add a new prescription record to the database
    def add_prescription(self):
        st.write('Enter prescription details:')
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
        self.diagnosis = st.text_area('Diagnosis')
        comments = st.text_area('Comments (if any)')
        self.comments = (lambda comments : None if comments == '' else comments)(comments)
        self.medicine_1_name = st.text_input('Medicine 1 name')
        self.medicine_1_dosage_description = st.text_area('Medicine 1 dosage and description')
        med_2_name = st.text_input('Medicine 2 name (if any)')
        self.medicine_2_name = (lambda name : None if name == '' else name)(med_2_name)
        med_2_dose_desc = st.text_area('Medicine 2 dosage and description')
        self.medicine_2_dosage_description = (lambda dose_desc: None if dose_desc == '' else dose_desc)(med_2_dose_desc)
        med_3_name = st.text_input('Medicine 3 name (if any)')
        self.medicine_3_name = (lambda name : None if name == '' else name)(med_3_name)
        med_3_dose_desc = st.text_area('Medicine 3 dosage and description')
        self.medicine_3_dosage_description = (lambda dose_desc: None if dose_desc == '' else dose_desc)(med_3_dose_desc)
        self.id = generate_prescription_id()
        save = st.button('Save')

        # executing SQLite statements to save the new prescription record to the database
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO prescription_record
                    (
                        id, patient_id, patient_name, doctor_id,
                        doctor_name, diagnosis, comments,
                        medicine_1_name, medicine_1_dosage_description,
                        medicine_2_name, medicine_2_dosage_description,
                        medicine_3_name, medicine_3_dosage_description
                    )
                    VALUES (
                        :id, :p_id, :p_name, :dr_id, :dr_name, :diagnosis,
                        :comments, :med_1_name, :med_1_dose_desc, :med_2_name,
                        :med_2_dose_desc, :med_3_name, :med_3_dose_desc
                    );
                    """,
                    {
                        'id': self.id, 'p_id': self.patient_id,
                        'p_name': self.patient_name, 'dr_id': self.doctor_id,
                        'dr_name': self.doctor_name, 'diagnosis': self.diagnosis,
                        'comments': self.comments,
                        'med_1_name': self.medicine_1_name,
                        'med_1_dose_desc': self.medicine_1_dosage_description,
                        'med_2_name': self.medicine_2_name,
                        'med_2_dose_desc': self.medicine_2_dosage_description,
                        'med_3_name': self.medicine_3_name,
                        'med_3_dose_desc': self.medicine_3_dosage_description,
                    }
                )
            st.success('Prescription details saved successfully.')
            st.write('The Prescription ID is: ', self.id)
            conn.close()

    # method to update an existing prescription record in the database
    def update_prescription(self):
        id = st.text_input('Enter Prescription ID of the prescription to be updated')
        if id == '':
            st.empty()
        elif not verify_prescription_id(id):
            st.error('Invalid Prescription ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the prescription before updating
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM prescription_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the current details of the prescription:')
                show_prescription_details(c.fetchall())

            st.write('Enter new details of the prescription:')
            self.diagnosis = st.text_area('Diagnosis')
            comments = st.text_area('Comments (if any)')
            self.comments = (lambda comments : None if comments == '' else comments)(comments)
            self.medicine_1_name = st.text_input('Medicine 1 name')
            self.medicine_1_dosage_description = st.text_area('Medicine 1 dosage and description')
            med_2_name = st.text_input('Medicine 2 name (if any)')
            self.medicine_2_name = (lambda name : None if name == '' else name)(med_2_name)
            med_2_dose_desc = st.text_area('Medicine 2 dosage and description')
            self.medicine_2_dosage_description = (lambda dose_desc: None if dose_desc == '' else dose_desc)(med_2_dose_desc)
            med_3_name = st.text_input('Medicine 3 name (if any)')
            self.medicine_3_name = (lambda name : None if name == '' else name)(med_3_name)
            med_3_dose_desc = st.text_area('Medicine 3 dosage and description')
            self.medicine_3_dosage_description = (lambda dose_desc: None if dose_desc == '' else dose_desc)(med_3_dose_desc)
            update = st.button('Update')

            # executing SQLite statements to update this prescription's record in the database
            if update:
                with conn:
                    c.execute(
                        """
                        UPDATE prescription_record
                        SET diagnosis = :diagnosis, comments = :comments,
                        medicine_1_name = :med_1_name,
                        medicine_1_dosage_description = :med_1_dose_desc,
                        medicine_2_name = :med_2_name,
                        medicine_2_dosage_description = :med_2_dose_desc,
                        medicine_3_name = :med_3_name,
                        medicine_3_dosage_description = :med_3_dose_desc
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'diagnosis': self.diagnosis,
                            'comments': self.comments,
                            'med_1_name': self.medicine_1_name,
                            'med_1_dose_desc': self.medicine_1_dosage_description,
                            'med_2_name': self.medicine_2_name,
                            'med_2_dose_desc': self.medicine_2_dosage_description,
                            'med_3_name': self.medicine_3_name,
                            'med_3_dose_desc': self.medicine_3_dosage_description
                        }
                    )
                st.success('Prescription details updated successfully.')
                conn.close()

    # method to delete an existing prescription record from the database
    def delete_prescription(self):
        id = st.text_input('Enter Prescription ID of the prescription to be deleted')
        if id == '':
            st.empty()
        elif not verify_prescription_id(id):
            st.error('Invalid Prescription ID')
        else:
            st.success('Verified')
            conn, c = db.connection()

            # shows the current details of the prescription before deletion
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM prescription_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Here are the details of the prescription to be deleted:')
                show_prescription_details(c.fetchall())

                confirm = st.checkbox('Check this box to confirm deletion')
                if confirm:
                    delete = st.button('Delete')

                    # executing SQLite statements to delete this prescription's record from the database
                    if delete:
                        c.execute(
                            """
                            DELETE FROM prescription_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Prescription details deleted successfully.')
            conn.close()

    # method to show all the prescriptions of a particular patient (using patient id)
    def prescriptions_by_patient(self):
        patient_id = st.text_input('Enter Patient ID to get the prescription record of that patient')
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
                    FROM prescription_record
                    WHERE patient_id = :p_id;
                    """,
                    { 'p_id': patient_id }
                )
                st.write('Here is the prescription record of', get_patient_name(patient_id), ':')
                show_prescription_details(c.fetchall())
            conn.close()
