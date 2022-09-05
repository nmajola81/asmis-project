# A web-based appointment and scheduling management information system (ASMIS)
 
##Description

This project is a fully-functional prototype ASMIS system. It provides all of the functionality to demonstrate basic appointment booking and consultation capturing. The point of the exercise was to implement some amount of the system proposed in Unit 9, and specifically focus on a few aspects of cyber-security.

The main data of interest for hackers / cyber-criminals in such a system are the patient details and patient medical records. It is therefore of utmost importance to ensure that these data are secured as far as possible.

##Security Features

For this demo, and building on the submission of Unit 9, I decided to generally incorporate and demonstrate the following security features:

1. A strict password policy (at least 8 characters long, consisting of at least 1 upper-case, 1 lower-case, 1 special and 1 numeric character) that would help mitigate the threat of spoofing via brute force / dictionary attacks

2. Storing passwords in the form of salted hashes in the database. This helps prevent information disclosure if the database were to be breached; coupled with the strict password policy, passwords with salted encryption provide extra security, making it difficult for hackers to do a hash look up.

3. Extensive logging of all key actions in the system along with exact date and time e.g. user login and logout activities, to appointment booking, patient detail viewing, patient consultation notes viewing, updating details etc. This fosters an environment of responsible use; a malicious user (especially Admin user) would be far more reluctant to engage in abusive activities, knowing that every action is recorded as having been carried out by that user.

4. Admin user permission levels. For this prototype, a basic access control system was provided whereby Admin users are either permission level 2 i.e. Super Admin user, who will have over-sight over other Admins, or a normal Admin user with permission level 1 who has to obtain authorization from a Super Admin for key activities that may be susceptible to abuse. In practice a more extensive access control system would need to be implemented to systematically control access to a variety of activities.

5. Multi-factor authentication to foster an environment of consent and over-sight for key activities.  i.e.:
   - When a Physician tries to access a patient's previous consultation notes, an OTP is sent to the relevant patient, and the Physician will only be granted access with this OTP. 
   - When an Admin user tries to view or edit a patient's details, an OTP is sent to the relevant patient, and the Admin user will only be granted access with this OTP.
   - When a normal Admin user (permission level 1) tries to register a new Physician account or to Cancel an appointment, an OTP is sent to the super Admin user (permission level 2), and the normal Admin user will only be granted access to these actions with this OTP.

6. SQL injection protection by using standard SQL querying libraries and using safe query practices in the form of safe parameter substitution.

## Dependencies

The following libraries need to be installed (installable via pip install):

- bcrypt  (https://github.com/pyca/bcrypt/)
- PasswordValidator (https://pypi.org/project/password-validator/)
- pyotp (https://github.com/pyauth/pyotp)
 
The following libraries that (should) ship with standard Python 3.x are also used:

- sqlite3
- os
- datetime
- random

## Usage

###The program can be started up via the command:

python main.py

###The following demo accounts are available:

Super Admin account: admin | p1234

Normal Admin account: admin2 | p1234

Patient account: pat1 | p1234

Patient account: pat2 | p1234

Patient account: pat3 | p1234

Physician account: phy1 | ph1234

Physician account: phy2 | ph1234


## Assumptions / Limitations / Caveats

The main focus of this project was to demonstrate some cyber-security principles in action in a prototype system. While a lot of functionality has been implemented in the system, many functions have been left out or simplified to make the project feasible e.g.:

1. Some user input fields are not validated for correct formatting etc. e.g. first name, last name, practice no. etc. 
2. Currently, only patients can register themselves and physicians can be registered by Admin users. I haven't implemented the creation of new Admin users, although this can quite easily be implemented using the functions already in the code.
3. I didn't include MFA or CAPTCHA for registration. In practice, this would be a necessity to prevent spam accounts.
4. The access control system implemented is very simple and hard-coded into the code. In practice, a more systematic and flexible system of assigning specific actions to specific users would be required.
5. I didn't include a password confirmation entry when a user is being registered or updated. This just made the interface easier to use and test. In practice, this would be required to prevent users putting in a typo when tpying in their password.
6. The password entry fields are also not cloaked i.e. they are displayed in raw text currently. This makes it vulnerable to eavesdropping and leakage. In practice, the password entry would have to be cloaked.
7. The booking system implemented is very simple one with very limited operational limitations/assumptions/validation, including:
   - For this prototype, I used SQLite to make the database completely portable for submission purposes. In practice, a standard secure DBMS with access controls and encryption etc. such as MySQL should be used. 
   - For this prototype, the OTP had to be stored in the database which is then retrieved by the patient's interface and displayed. In practice storing the OTP in the database can be a security risk and the OTP should be sent directly to the patient's device/email.
   - Patients can book an appointment for any specialization a week in advance.
   - It is assumed that there are no limits to the number of appointments taken on by each physician on each given day. Implementing this would have been possible but adding this restriction would have made testing the system a bit more tricky / limited, so I decided to leave it out.
   - The only limitation around booking appointments is that patients can't book two appointments scheduled for the same day.
   - A physician among all those registered on the system with the specified specialization is randomly assigned to the appointment.
   - The clinic is assumed to be open and operational every day of the week, and all physicians work every day. These assumptions are all made to make the project feasible in the timeframe.
   - Some user interface elements have been simplified e.g. when displaying patient consultation notes, ALL of them are listed. In practice, one would need to consider a case where a large number of records are being listed and to think about how to sensibly present them on the screen.
   - The physician is currently allowed to change their specialization at will. In practice, this would have huge implications on the booking system and would need to be carefully re-thought.

