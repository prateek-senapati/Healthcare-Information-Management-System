# Healthcare-Information-Management-System

__Healthcare Information Management System (HIMS)__ is an application created as a DBMS project for one of our institute's courses on database management systems. The __HIMS__ application can be used by hospitals, clinics and healthcare centres to manage data/records for patients, doctors, prescriptions, medical tests and various departments within the healthcare facility. Besides the basic DBMS functionalities such as addition, deletion, update and search, other useful features are also present in this application. 

The application uses [__sqlite3__](https://docs.python.org/3/library/sqlite3.html) module for database management purposes, [__streamlit__](https://www.streamlit.io/) to create the user interface and make the application work, and [__pandas__](https://pandas.pydata.org/) to facilitate working with the data.

### Requirements

* __Python 3.7.4__ or any higher version
* __pandas__ and __streamlit__
  * To install the packages mentioned above, go to command prompt/terminal and execute the following commands:
  ```cmd
  > pip install pandas
  > pip install streamlit
  ```

## Instructions to run the application

1. Clone this repository to your local system.
2. After cloning this repository to your local system, create a __config.py__ file in the same repository.
3. Add the following Python statements to __config.py__ :
  ```python
  # configuration file containing confidential credentials
  # user authentication password is used to login to the application
  # edit mode password is required to add, delete or update any patient, doctor or department record 
  # doctor/medical lab scientist (MLS) access code is given only to the doctors and MLSs, using which they can add, delete or update any prescription and/or medical test record

  password = '<user_authentication_password>'                               # e.g. password = '1234'
  database_name = '<current_database_name>'                                 # e.g. database_name = 'database_1A'
  edit_mode_password = '<edit_mode_password>'                               # e.g. edit_mode_password = 'allow_edit'
  dr_mls_access_code = '<doctor_or_medical_lab_scientist_access_code>'      # e.g. dr_mls_access_code = 'access_auth'
  ```
4. Move to the same directory in command prompt/terminal and execute the following command (running this command will open the application in a new tab in your default browser automatically; you don't need internet connection to work with this application):
```cmd
> streamlit run hims_app.py
```

#### NOTE:

* Here's a [link](https://drive.google.com/file/d/1DXUKgfrbsullwRjFxDKvNSSHKqBZ2Xur/view?usp=sharing) to a screen cast (video) of the working of this application. Please note that this video is for an older version, but there are not a lot of changes in the updated version. The changes in the updated version include:
  * __Edit mode password__ - this is to ensure that only the people who are authorised to add, delete and update the patient, doctor and department records can do so. Viewing the data doesn't require this second level of authentication.
  * __Doctor/ Medical Lab Scientist access code__ - this is to ensure that only doctors and medical lab scientists are able to add, delete and update prescription and medical test details. Viewing prescriptions and medical tests of a patient doesn't require this second level of authentication.
  * The functionality of *'Listing doctors of a particular department using the department unique ID'* has been moved from the *Doctor* module to the *Department* module.
