import sqlite3
import bcrypt  #https://github.com/pyca/bcrypt/
import os
from password_validator import PasswordValidator #https://pypi.org/project/password-validator/
import datetime
import random
import pyotp #https://github.com/pyauth/pyotp

#Create the password validator with required security rules
passvalid = PasswordValidator()
passvalid.min(8).max(16).has().uppercase().has().lowercase().has().symbols().has().digits().has().letters()


#In actual fact, the list of specializations below should be stored in the database
#and should be updateable via the interface e.g. by an admin
#For simplicity in the demo, I hard-coded into the dict below with only 4 specializations
#Having a dict like the one below helps prevent typos e.g. SPECIALIZATION['Cardiolgy'] (missing 'o') will throw an error
SPECIALIZATION = {"Cardiology":"Cardiology", "Radiology":"Radiology", "Dermatology":"Dermatology", "Neurology":"Neurology"}

#Setup a time-based OTP generator using a secret seed
#Make sure to keep the source code safe
totp = pyotp.TOTP('base32secret3232',digits=4,interval=30)

class Model:
    """
    A class that manages all access to the database. It currently uses an SQLite connection to an SQLite database. In practice, a standard secure DBMS should be used. This can be done quite simply by changing the type of connection set to the connection handler 'conn' in the __init__

    ...

    Attributes
    ----------
    conn : connection handler to the database object

    """

    def __init__(self):
        # Path to the SQLite database used for this demonstration software
        # In practice, one would rather use a secure DBMS e.g. MySQL, Oracle etc.
        dbfile = "db.db"
        self.conn = sqlite3.connect(dbfile)

    def closeModel(self):
        """Closes the connection to the database.
         """
        self.conn.commit()
        self.conn.close()

    def purgeAllTables(self):
        """Deletes/Refreshes all database tables. This method is a serious security risk and should not be left in any final implementation. It has only been included to make it possible to refresh the demo if need be.
         """
        conn = self.conn
        # Delete all the users
        conn.execute("delete from User")
        conn.execute("delete from Admin")
        conn.execute("delete from Patient")
        conn.execute("delete from Physician")
        conn.execute("delete from Consultation")
        conn.execute("delete from Appointment")
        conn.execute("delete from EventLog")
        conn.execute("delete from Authorization")
        conn.commit()


    def resetUsers(self):
        """Sets up some demo data. This method is a serious security risk and should not be left in any final implementation. It has only been included to make it possible to refresh the demo if need be.
         """
        conn = self.conn
        #Delete all the users
        self.purgeAllTables()

        #Create and add in the super admin (ADM_PERMLEVEL = 2)
        adm = Admin("admin","a1234")
        adm.setUserDetails("Super","Admin")
        adm.setAdminDetails(2)
        self.addUser(adm)

        #Create and add in a normal admin (ADM_PERMLEVEL = 1)
        adm = Admin("admin2", "a21234")
        adm.setUserDetails("Normal1", "Admin1")
        adm.setAdminDetails(1)
        self.addUser(adm)

        #Create and add in a normal admin (ADM_PERMLEVEL = 1)
        adm = Admin("admin3", "a31234")
        adm.setUserDetails("Normal2", "Admin2")
        adm.setAdminDetails(1)
        self.addUser(adm)

        #Create and add in a patient
        pat = Patient("pat1","p1234")
        pat.setUserDetails("Abe","Ants")
        pat.setPatientDetails("0123123","Abe's Dad")
        self.addUser(pat)

        #Create and add in a 2nd patient
        pat = Patient("pat2","p21234")
        pat.setUserDetails("Bob","Buffalo")
        pat.setPatientDetails("03245787","Bob's Mother")
        self.addUser(pat)

        #Create and add in a 3rd patient
        pat = Patient("pat3","p31234")
        pat.setUserDetails("Candice","Candida")
        pat.setPatientDetails("24325234","Candy's Brother")
        self.addUser(pat)

        #Create and add in a 4th patient
        pat = Patient("pat4","p41234")
        pat.setUserDetails("Drew","Darius")
        pat.setPatientDetails("98948753","Drew's Nephew")
        self.addUser(pat)

        #Create and add in a 5th patient
        pat = Patient("pat5","p51234")
        pat.setUserDetails("Ellie","Elephant")
        pat.setPatientDetails("9987373","Ellie's Cousin")
        self.addUser(pat)


        #Create and add in physicians
        phy = Physician("phy1","ph1234")
        phy.setUserDetails("Fred","Fredricks")
        phy.setPhysicianDetails("345345",SPECIALIZATION["Cardiology"])
        self.addUser(phy)

        phy = Physician("phy2", "ph21234")
        phy.setUserDetails("Gail", "Gailin")
        phy.setPhysicianDetails("56234", SPECIALIZATION["Cardiology"])
        self.addUser(phy)

        phy = Physician("phy3", "ph31234")
        phy.setUserDetails("Henry", "Hendricks")
        phy.setPhysicianDetails("0912897213", SPECIALIZATION["Dermatology"])
        self.addUser(phy)

        phy = Physician("phy4", "ph41234")
        phy.setUserDetails("Ian", "Induso")
        phy.setPhysicianDetails("1291823", SPECIALIZATION["Dermatology"])
        self.addUser(phy)

        phy = Physician("phy5", "ph51234")
        phy.setUserDetails("Jill", "Jelloliker")
        phy.setPhysicianDetails("2882732", SPECIALIZATION["Dermatology"])
        self.addUser(phy)

        phy = Physician("phy6", "ph61234")
        phy.setUserDetails("Katy", "Katrina")
        phy.setPhysicianDetails("2123122", SPECIALIZATION["Neurology"])
        self.addUser(phy)

        phy = Physician("phy7", "ph71234")
        phy.setUserDetails("Luna", "Lumino")
        phy.setPhysicianDetails("22112112", SPECIALIZATION["Neurology"])
        self.addUser(phy)

        phy = Physician("phy8", "ph81234")
        phy.setUserDetails("Marty", "Marsno")
        phy.setPhysicianDetails("99287278", SPECIALIZATION["Neurology"])
        self.addUser(phy)

        phy = Physician("phy9", "ph91234")
        phy.setUserDetails("Nolene", "Maolana-Sanqu")
        phy.setPhysicianDetails("993038783", SPECIALIZATION["Radiology"])
        self.addUser(phy)

        #Add in some appointments




    def addLogEntry(self, logentry):
        """Writes a LogEntry object to the database

         :param logentry: LogEntry
             The LogEntry object to write.
         """
        self.conn.execute("insert into EventLog (EventDateTime, EventDescription) values (?,?)",(logentry.EventDateTime, logentry.EventDescription))
        self.conn.commit()

    def cancelAppointment(self, appointment):
        """Removes an appointment from the database

         :param appointment: Appointment
             The Appointment object to remove.
         """
        self.conn.execute("delete from appointment where app_id = ?", (appointment.app_id,))
        self.conn.commit()

    def getPhysicians(self, phy_specialization):
        """Retrieves a list of physician ids (phy_id) without repetition currently registered on the system with a given specialization

         :param phy_specialization: str
             Desired physician specialization
         :return: list containing phy_ids
         """
        cursor = self.conn.execute("select phy_id  from physician where phy_specialization = ?", (phy_specialization,))

        ls = [it[0] for it in cursor.fetchall()]

        return ls

    def getPatientOTPs(self, user):
        """Retrieves a list of OTPs currently issued towards a given user

         :param user : User
             A User object of the target user

         :return: list of (auth_otp, auth_requesting_usr_id) pairs

         """
        cursor = self.conn.execute("select auth_otp, auth_requesting_usr_id from authorization where auth_pat_id = ?",(user.usr_id,))

        otps = cursor.fetchall()

        # otps = [otp[0] for otp in otps]

        return otps


    def deregisterOTP(self, auth_id):
        """Removes a given authorization OTP from the database (after it has been used/expired)

         Parameters
         ----------
         auth_id : int
             auth_id of the row in the Authorization table

         """
        self.conn.execute("delete from Authorization where auth_id = ?",(auth_id,))
        self.conn.commit()



    def registerOTP(self, targetuser, requestinguser, otp):
        """Inserts a required authorization OTP into the database

         :param targetuser: User
             User object of user to which the OTP is being issued.

         :param requestinguser: User
             User object of user that requested access to some protected resource.

        :return: auth_id of the newly created row in the Authorization table
         """

        self.conn.execute("insert into Authorization (auth_pat_id, auth_requesting_usr_id, auth_otp) values (?,?,?)", (targetuser.usr_id, requestinguser.usr_id, otp))

        self.conn.commit()

        #Get the auth_id assigned by sql via auto-increment
        cursor = self.conn.execute("select last_insert_rowid()")
        auth_id = cursor.fetchone()[0]

        return auth_id

    def bookAppointment(self, appointment):
        """Insert an appointment into the database

         :param appointment: Appointment object containing information to be inserted.

        :return: app_id of the newly created row in the Appointment table
         """
        self.conn.execute("insert into appointment (app_created_datetime, app_date, phy_id, pat_id) values (?,?,?,?)", (appointment.app_created_datetime, appointment.app_date, appointment.physician.usr_id, appointment.patient.usr_id))
        self.conn.commit()

        cursor = self.conn.execute("select last_insert_rowid()")
        app_id = cursor.fetchone()[0]
        return app_id

    def checkRepeatBooking(self, usr_id, app_date):
        """Checks whether a given usr_id already has an appointment booking on a specific date

         :param usr_id: usr_id of user.

         :param app_date: str containing date in '%Y-%m-%d' format.

        :return: boolean; whether or not the user has an appointment on the given date.
         """
        cursor = self.conn.execute("select *  from appointment where pat_id = ? and app_date = ?", (usr_id, app_date))

        if len(cursor.fetchall()) > 0:
            return True

        return False

    def getAvailablePhysicianTypes(self):
        """Get a list of the available physician specializations at the clinic by checking the specializations of the physicians we've currently got

        :return: list of strings; specializations.
         """

        cursor = self.conn.execute("select distinct PHY_SPECIALIZATION from Physician order by PHY_SPECIALIZATION asc")

        allres = cursor.fetchall()

        allres = [it[0] for it in allres]

        return allres

    def getPatientAppointments(self, pat):
        """Get appointments assigned to a specific patient from today's date onwards

         :param pat: Patient object of patient.

        :return: list of Appointment objects
         """
        #SELECT Appointment.APP_ID, (case when Consultation.APP_ID != NULL then 1 else 0 end) FROM	Appointment LEFT JOIN Consultation ON Appointment.APP_ID = Consultation.APP_ID

        todaydate = datetime.datetime.today().strftime("%Y-%m-%d")

        #Get a list of appointments assigned to this patient from today onwards that have already been consulted (i.e. already have an entry in the consultation table)
        cursor = self.conn.execute("select distinct app_id from Consultation where APP_ID in (select app_id from Appointment where PAT_ID = ? and app_date >= ?) order by APP_ID asc", (pat.usr_id,todaydate))
        results = cursor.fetchall()
        consultedlist = [it[0] for it in results]

        #Get a list of all today and onwards' appointments (consulted or not) assigned to this patient
        cursor = self.conn.execute("select app_id, app_created_datetime, app_date, phy_id, usr_fname, usr_lname from appointment, user where PAT_ID = ? and phy_id = usr_id and app_date >= ? order by app_created_datetime asc", (pat.usr_id,todaydate))
        results = cursor.fetchall()

        appointmentslist = []

        for app_id, app_created_datetime, app_date, phy_id, usr_fname, usr_lname in results:
            phy = Physician(usr_id=phy_id)
            phy.setUserDetails(usr_fname, usr_lname)

            consulted = 0
            if app_id in consultedlist:
                consulted = 1

            appointmentslist.append(Appointment(app_id=app_id, app_created_datetime=app_created_datetime, app_date=app_date, physician=phy, patient=pat, consulted=consulted))




        return appointmentslist

    def getPhysicianAppointments(self, phy):

        """Get appointments assigned to a specific physician today

         :param phy: Physician object of physician.

        :return: list of Appointment objects
         """

        todaydate = datetime.datetime.today().strftime("%Y-%m-%d")

        #Get a list of today's appointments assigned to this physician that have already been consulted
        cursor = self.conn.execute("select distinct app_id from Consultation where APP_ID in (select app_id from Appointment where PHY_ID = ? and app_date = ?) order by APP_ID asc", (phy.usr_id,todaydate))
        results = cursor.fetchall()
        consultedlist = [it[0] for it in results]

        #Get a list of all today's appointments (consulted or not) assigned to this physician
        cursor = self.conn.execute("select app_id, app_created_datetime, pat_id, usr_fname, usr_lname from appointment, user where PHY_ID = ? and pat_id = usr_id and app_date = ? order by app_created_datetime asc", (phy.usr_id,todaydate))
        results = cursor.fetchall()

        appointmentslist = []

        for app_id, app_created_datetime, pat_id, usr_fname, usr_lname in results:
            pat = Patient(usr_id=pat_id)
            pat.setUserDetails(usr_fname, usr_lname)

            consulted = 0
            if app_id in consultedlist:
                consulted = 1

            appointmentslist.append(Appointment(app_id=app_id, app_created_datetime=app_created_datetime, physician=phy, patient=pat, consulted=consulted))




        return appointmentslist

    def getPatientConsultations(self, patient):
        """Get all Consultations (prescriptions and notes) pertaining to a specific patient

         :param patient: Patient object of patient.

        :return: list of Consultation objects
         """
        cursor = self.conn.execute("select cons_id, cons_datetime, cons_notes, cons_prescription from consultation, appointment where appointment.pat_id = ? and appointment.app_id = consultation.app_id order by cons_id asc", (patient.usr_id,))
        results = cursor.fetchall()

        consultslist = []

        for cons_id, cons_datetime, cons_notes, cons_prescription in results:
            consultslist.append(Consultation(cons_id=cons_id, cons_datetime=cons_datetime, cons_notes=cons_notes, cons_prescription=cons_prescription))

        return consultslist

    def addConsultationInfo(self, consultation):
        """Add a info a Consultation object into the database

         :param consultation: Consultation object of the consultation.

         """
        #cons = Consultation(cons_datetime=cons_datetime, appointment=app, cons_notes=cons_notes, cons_prescription=cons_prescription)

        self.conn.execute("insert into Consultation (CONS_DATETIME, APP_ID, CONS_NOTES, CONS_PRESCRIPTION) VALUES (?,?,?,?)", (consultation.cons_datetime, consultation.appointment.app_id, consultation.cons_notes, consultation.cons_prescription))

        self.conn.commit()

    def retrieveUser(self, usr_login="", usr_id = ""):
        """Retrieve info of a given User from the database. Either set the usr_login or the usr_id. If both are set the usr_id is used (and usr_login is ignored)

         :param usr_login: usr_login of desired patient.

         :param usr_id: usr_id of desired patient.

        :return: Admin, Patient or Physician object depending on the user's User.usr_type
         """
        if usr_id == "":

            cursor = self.conn.execute("select usr_id, usr_type, usr_pass from User where usr_login = ?", (usr_login,))

            (usr_id, usr_type, usr_pass) = cursor.fetchone()

        else:

            cursor = self.conn.execute("select usr_login, usr_type, usr_pass from User where usr_id = ?", (usr_id,))

            (usr_login, usr_type, usr_pass) = cursor.fetchone()

        user = None

        if usr_type == "admin":
            cursor = self.conn.execute("select USR_FNAME, USR_LNAME, ADM_PERMLEVEL from user, admin where usr_id = ? and user.USR_ID = admin.ADM_ID", (usr_id,))
            usr_fname, usr_lname, adm_permlevel = cursor.fetchone()
            user = Admin(usr_login=usr_login,usr_id=usr_id, usr_pass=usr_pass)
            user.setUserDetails(usr_fname, usr_lname)
            user.setAdminDetails(adm_permlevel)

        elif usr_type == "patient":
            cursor = self.conn.execute(
                "select USR_FNAME, USR_LNAME, PAT_SECONDCONTACTNO, PAT_SECONDCONTACTNAME from user, patient where usr_id = ? and user.USR_ID = patient.PAT_ID",
                (usr_id,))
            usr_fname, usr_lname, pat_secondcontactno, pat_secondcontactname = cursor.fetchone()
            user = Patient(usr_login=usr_login,usr_id=usr_id, usr_pass=usr_pass)
            user.setUserDetails(usr_fname, usr_lname)
            user.setPatientDetails(pat_secondcontactno, pat_secondcontactname)

        elif usr_type == "physician":
            cursor = self.conn.execute(
                "select USR_FNAME, USR_LNAME, PHY_PRACTICENO, PHY_SPECIALIZATION from user, physician where usr_id = ? and user.USR_ID = physician.PHY_ID",
                (usr_id,))
            usr_fname, usr_lname, phy_practiceno, phy_specialization = cursor.fetchone()
            user = Physician(usr_login=usr_login,usr_id=usr_id, usr_pass=usr_pass)
            user.setUserDetails(usr_fname, usr_lname)
            user.setPhysicianDetails(phy_practiceno, phy_specialization)

        return user





    def checkUsernameExists(self, usr_login):
        """Check if a given user login already exists

         :param usr_login: usr_login of the user to check.

        :return: boolean; whether or not the usr_login already exists
         """
        cursor = self.conn.execute("select usr_login from User where usr_login = ?",(usr_login,))

        #If the login already exists, don't continue
        if len(cursor.fetchall()) > 0:
            return True

        return False

    def checkPasswordValid(self, usr_login, usr_pass):

        cursor = self.conn.execute("select usr_pass from User where usr_login = ?", (usr_login,))

        passhash = cursor.fetchone()[0]

        return bcrypt.checkpw(usr_pass.encode(), passhash.encode())

    def updateUser(self, user):
        """Updates a user in the database given a Patient, Physician or Admin object

         :param user: Patient, Physician or Admin object containing fields and info to update
         """
        conn = self.conn

        usr_id = user.usr_id

        #Otherwise, proceed to create the user

        #If password was set/changed by the user, then add it in
        if user.usr_pass != "":
            passwhash = bcrypt.hashpw(user.usr_pass.encode(), bcrypt.gensalt()).decode()
            conn.execute("update User set USR_PASS = ? where USR_ID = ? ", (passwhash, user.usr_id))

        #Set user's other attributes
        conn.execute("update User set USR_FNAME = ?, USR_LNAME = ? where USR_ID = ?", (user.usr_fname, user.usr_lname, usr_id))


        if user.usr_type == "admin":
            pass

        elif user.usr_type == "patient":
            conn.execute("update Patient set PAT_SECONDCONTACTNO = ?, PAT_SECONDCONTACTNAME = ? where PAT_ID = ?", (user.pat_secondcontactno, user.pat_secondcontactname, usr_id))

        elif user.usr_type == "physician":
            conn.execute("update Physician set PHY_PRACTICENO = ?, PHY_SPECIALIZATION = ? where PHY_ID = ?",
                         (user.phy_practiceno, user.phy_specialization, usr_id))


        conn.commit()


    def addUser(self, user):
        """Adds a given user into the database

         :param user: User object containing fields and info the create

        :return: usr_id of the newly created user
         """
        conn = self.conn

        # Decided not to encrypt the login; keep it simple for now, but very useful to
        # encrypt the login which will add a layer of security and guard against e.g.
        # tampering, data leakage, repudiation etc.
        login = user.usr_login

        #Otherwise, proceed to create the user
        passwhash = bcrypt.hashpw(user.usr_pass.encode(), bcrypt.gensalt()).decode()

        conn.execute("insert into User (USR_LOGIN, USR_PASS, USR_FNAME, USR_LNAME, USR_TYPE) " \
                     "VALUES (?,?,?,?,?)", (login, passwhash, user.usr_fname, user.usr_lname, user.usr_type))

        #Get the usr_id assigned by sql via auto-increment

        cursor = conn.execute("select last_insert_rowid()")
        usr_id = cursor.fetchone()[0]

        #And also add the user into the appropriate sub-type table: patient, admin or physician

        if user.usr_type == "admin":
            conn.execute("insert into Admin (ADM_ID, ADM_PERMLEVEL) values (?,?)", (usr_id, user.adm_permlevel))

        elif user.usr_type == "patient":
            conn.execute("insert into Patient (PAT_ID, PAT_SECONDCONTACTNO, PAT_SECONDCONTACTNAME) values (?,?,?)", (usr_id, user.pat_secondcontactno, user.pat_secondcontactname))

        elif user.usr_type == "physician":
            conn.execute("insert into Physician (PHY_ID, PHY_PRACTICENO, PHY_SPECIALIZATION) values (?,?,?)",
                         (usr_id, user.phy_practiceno, user.phy_specialization))


        conn.commit()
        return usr_id



class User:
    """
        Base class representing a user of the system

        ...

        Attributes
        ----------
        usr_login : str
            User's login username
        usr_pass : str
            User's password
        usr_id : int
            usr_id of the associated row in the User table
        usr_fname: str
            User's first name
        usr_lname: str
            User's last name
        """

    def __init__(self, usr_login, usr_pass, usr_id = -1):
        self.usr_login = usr_login
        self.usr_pass = usr_pass
        self.usr_id = usr_id

    def __str__(self):
        return "%s %s %s %s %s" % (self.usr_id,self.usr_login,self.usr_pass,self.usr_fname,self.usr_lname)

    def setUserDetails(self, usr_fname, usr_lname):
        """Helper function to set attributes of this User

         :param usr_fname: str
             User's first name
         :param usr_lname: str
             User's last name

         """
        self.usr_fname = usr_fname
        self.usr_lname = usr_lname

    def setUserLoginDetails(self, usr_login, usr_pass):
        """Helper function to set attributes

         :param usr_login: str
             User's login username
         :param usr_pass: str
             User's password

         """
        self.usr_login = usr_login
        self.usr_pass = usr_pass

class Admin(User):
    """
            Class based on User class representing an Admin

            ...

            Attributes
            ----------
            adm_permlevel : int
                Admin's permission level

    """
    def __init__(self, usr_login="", usr_pass="", usr_id=-1):
        User.__init__(self,usr_login,usr_pass, usr_id)
        self.usr_type = "admin"

    def __str__(self):
        return("%s %s %s %s %s %s" % (self.usr_id,self.usr_login,self.usr_pass,self.usr_fname,self.usr_lname,self.adm_permlevel))

    def setAdminDetails(self, adm_permlevel):
        """Helper function to set attributes of this Admin

         :param adm_permlevel: str
             Admin's permission level

         """
        self.adm_permlevel = adm_permlevel

    def createFromUser(self, user):
        """Helper function to populate this admin's User attributes using a User object

         :param user: User object
             User object to use
        """
        self.usr_login = user.usr_login
        self.usr_pass = user.usr_pass
        self.usr_fname = user.usr_fname
        self.usr_lname = user.usr_lname


class Patient(User):
    """
        Class based on User class representing a Patient

        ...

        Attributes
        ----------
        pat_secondcontactno : str
            Patient's next of kin contact number
        pat_secondcontactname : str
            Patient's next of kin name
        """
    def __init__(self, usr_login = "", usr_pass = "", usr_id = -1):
        User.__init__(self,usr_login,usr_pass,usr_id)
        self.usr_type = "patient"
        self.pat_secondcontactno = ""
        self.pat_secondcontactname = ""

    def __str__(self):
        return("%s %s %s %s %s %s %s" % (self.usr_id,self.usr_login,self.usr_pass,self.usr_fname,self.usr_lname,self.pat_secondcontactno,self.pat_secondcontactname))

    def setPatientDetails(self, pat_secondcontactno, pat_secondcontactname):
        """Helper function to set attributes of this Patient

         :param pat_secondcontactno: str
             Patient's next of kin contact number
         :param pat_secondcontactname: str
             Patient's next of kin name

         """
        self.pat_secondcontactno = pat_secondcontactno
        self.pat_secondcontactname = pat_secondcontactname

    def createFromUser(self, user):
        """Helper function to populate this patient's User attributes using a User object

         :param user: User object
             User object to use
         """
        self.usr_login = user.usr_login
        self.usr_pass = user.usr_pass
        self.usr_fname = user.usr_fname
        self.usr_lname = user.usr_lname

class Physician(User):
    """
        Class based on User class representing a Physician

        ...

        Attributes
        ----------
        phy_practiceno : str
            Physician's practice number
        phy_specialization : str
            Physician's specialization field
        """
    def __init__(self, usr_login = "", usr_pass = "", usr_id = -1):
        User.__init__(self,usr_login,usr_pass,usr_id)
        self.usr_type = "physician"
        self.phy_practiceno = ""
        self.phy_specialization = ""

    def __str__(self):
        return("%s %s %s %s %s %s %s" % (self.usr_id,self.usr_login,self.usr_pass,self.usr_fname,self.usr_lname,self.phy_practiceno,self.phy_specialization))

    def setPhysicianDetails(self, phy_practiceno, phy_specialization):
        """Helper function to set attributes of this Physician

        :param phy_practiceno : str
            Physician's practice number
        :param phy_specialization : str
            Physician's specialization field

         """
        self.phy_practiceno = phy_practiceno
        self.phy_specialization = phy_specialization

    def createFromUser(self, user):
        """Helper function to populate this physician's User attributes using a User object

         :param user: User object
             User object to use
         """
        self.usr_login = user.usr_login
        self.usr_pass = user.usr_pass
        self.usr_fname = user.usr_fname
        self.usr_lname = user.usr_lname

class Appointment():

    """
    Class representing an Appointment

    ...

    Attributes
    ----------
    app_id : int
        app_id of the Appointment in the Appointment table
    app_created_datetime : str
        str containing the date and time the appointment was created in '%Y-%m-%d %H:%M:%S' format
    app_date : str
        str containing the actual appointment date in '%Y-%m-%d' format
    physician : Physician
        Physician object assigned to this Appointment
    patient : Patient
        Patient object assigned to this Appointment
    consulted : boolean
        Whether or not this Appointment has already been Consulted by a Physician i.e. whether or not it has an associated entry in the Consultation table
    """

    def __init__(self, app_id = -1, app_created_datetime = "", app_date = "", physician = Physician(), patient = Patient(), consulted=0):
        self.app_id = app_id
        self.app_created_datetime = app_created_datetime
        self.app_date = app_date
        self.physician = physician
        self.patient = patient
        self.consulted = consulted

    def __str__(self):
        return "%s "*10 % (self.app_id, self.app_created_datetime, self.app_date, self.physician.usr_id, self.physician.usr_fname, self.physician.usr_fname, self.patient.usr_id, self.patient.usr_fname, self.patient.usr_lname, self.consulted)


class Consultation():

    """
    Class representing a Consultation

    ...

    Attributes
    ----------
    cons_id : int
        cons_id of the Consultation in the Consultation table
    cons_datetime : str
        str containing the consultation date and time in '%Y-%m-%d %H:%M:%S' format
    appointment : Appointment
        Appointment object associated with this Consultation
    cons_notes : str
        Consultation notes entered by the Physician
    cons_presciption : str
        Consultation prescription information entered by the Physician
            """

    def __init__(self, cons_id = -1, cons_datetime = "", appointment = Appointment(), cons_notes = "", cons_prescription = ""):
        self.cons_id = cons_id
        self.cons_datetime = cons_datetime
        self.appointment = appointment
        self.cons_notes = cons_notes
        self.cons_prescription = cons_prescription

    def __str__(self):
        disp = (self.cons_id, self.cons_datetime, self.appointment.patient.usr_fname, self.appointment.patient.usr_lname, self.appointment.physician.usr_fname, self.appointment.physician.usr_lname)
        return "%s "*len(disp) % disp

class LogEntry:

    """
    Class representing an entry into the Log in the database

    ...

    Attributes
    ----------
    EventDescription : str
        Description of the event
    EventDateTime : str
        str containing the date and time Event was logged in '%Y-%m-%d %H:%M:%S' format
    """

    def __init__(self, EventDescription=""):
        self.EventDescription = EventDescription
        self.EventDateTime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        disp = (self.EventDateTime, self.EventDescription)
        return "%s "*len(disp) % disp



class View:
    """
    A class that manages all capture and display of information to user.
    ...

    Attributes
    ----------
    model : Model object that provides access to the database

    """
    def __init__(self, model):
        self.model = model

    def clearScr(self):
        """Helper function that clears all output from the terminal window.
        """
        try:
            if os.name == "posix":
                os.system("clear")
            else:
                os.system("cls")
        except:
            #Unable to clear screen: not a train wreck, just won't look as nice
            pass

    def capturePatientDetails(self, pat):
        """Reads in patient-specific attributes (see Patient object) pertaining to a given patient

         :param pat: Patient
             The patient for which information is being captured.

         :return: Patient object with information populated in it
         """
        pat_secondcontactno = pat.pat_secondcontactno
        pat_secondcontactname = pat.pat_secondcontactname

        pat_secondcontactno_tmp = input("Next of kin contact number (in case of emergency): ")
        pat_secondcontactname_tmp = input("Next of kin name: ")

        #This stuff is used when the user is trying to edit their details
        #If the user enters "" for either field, just use the detail already in pat
        #Only if the user actually puts something in, replace them
        if pat_secondcontactno_tmp != "":
            pat_secondcontactno = pat_secondcontactno_tmp

        if pat_secondcontactname_tmp != "":
            pat_secondcontactname = pat_secondcontactname_tmp

        pat.setPatientDetails(pat_secondcontactno, pat_secondcontactname)

        return pat

    def updateUserDetails(self, user):


        #Note: For this demo, there is no built-in way to get out of this procedure once in

        #These are all the details of a patient that need to be captured

        usr_pass = ""
        usr_fname = user.usr_fname
        usr_lname = user.usr_lname

        self.clearScr()

        print("-" * 80)
        print("Update Details")
        print("-" * 80)
        self.displayUserDetail(user)

        print("-" * 80)
        print("Update the following fields OR leave blank to leave unchanged:\n")

        print("Note: For security purposes, your desired password should meet the following criteria:")
        print("Min 8 and max 16 characters, contain at least: 1 uppercase letter, 1 lowercase letter,")
        print("  1 special character, and 1 number (good luck :D)\n")

        while True:
            usr_pass = input("Desired password: ")

            if usr_pass == "":
                break

            success = passvalid.validate(usr_pass)

            if success == True:
                usr_pass = usr_pass
                break

            print("**Invalid password**")
            print("For security purposes, your desired password should meet the following criteria:")
            print("Min 8 and max 16 characters, contain at least: 1 uppercase letter, 1 lowercase letter,")
            print("  1 special character, and 1 number (good luck :D)\n")


        print("")
        #No user validation done on these fields for this demo
        usr_fname_tmp = input("First Name: ")

        if usr_fname_tmp != "":
            usr_fname = usr_fname_tmp

        usr_lname_tmp = input("Last Name: ")

        if usr_lname_tmp != "":
            usr_lname = usr_lname_tmp

        user.setUserDetails(usr_fname,usr_lname)
        user.usr_pass = usr_pass

        return user

    def displayUserDetail(self, user):

        """Displays user attributes along with relevant Patient/Admin/Physician attributes to the screen

         :param user: User or Patient or Admin or Physician object
             The User to be displayed.

         """

        print("The current details are:")
        print("-" * 80)
        print("Login: %s" % (user.usr_login))
        print("First Name: %s" % (user.usr_fname))
        print("Last Name: %s" % (user.usr_lname))

        if user.usr_type == "admin":
            print("Permission Level: %s" % (user.adm_permlevel))
        elif user.usr_type == "patient":
            print("Next of kin contact number (in case of emergency): %s" % (user.pat_secondcontactno))
            print("Next of kin name: %s" % (user.pat_secondcontactname))
        elif user.usr_type == "physician":
            print("Practice No: %s" % (user.phy_practiceno))
            print("Specialization: %s" % (user.phy_specialization))

        print("-" * 80)



    def captureBookingDetails(self):

        """Captures information pertaining to an appointment request i.e. type of specialist and date (upto 7 days in advance). It randomly picks a Physician with the required specialization. It returns the appointment date and the physician's phy_id


         :return: Appointment date in in '%Y-%m-%d' format, phy_id of Physician
         """

        model = self.model



        opt = -1
        msg = ""
        while True:
            self.clearScr()
            print("-" * 80)
            print("Book an Appointment")
            print("-" * 80)
            print("Note: You can make appointments upto 7 days in advance. No exact times slots are provided.")
            print("  Patients will be attended to on a first-come-first-served basis on their appointment day.")
            print("")
            if (msg != ""):
                print("** " + msg + " **\n")
                msg = ""
            print("Below is a list of the specializations of our physicians.")
            phytypes = model.getAvailablePhysicianTypes()
            for ind,phytype in enumerate(phytypes):
                print("(%s) %s" % (ind+1,phytype))

            phytype = input("Please select your required option: ")

            if phytype.isdigit() != True or int(phytype) < 1 or int(phytype) > len(phytypes):
                msg = "Error: Unknown option. Please select one of the options in the menu"
                continue

            phy_specialization = phytypes[int(phytype)-1]
            break


        opt = -1
        msg = ""
        while True:
            self.clearScr()
            print("-" * 80)
            print("Book an Appointment")
            print("-" * 80)
            print("Physician required: %s" % (phy_specialization))
            print("")
            if (msg != ""):
                print("** " + msg + " **\n")
                msg = ""
            print("The following days are currently available. Please enter the option of the day you'd prefer:")

            #Today's date:
            today = datetime.datetime.today()

            #Get a list of the next 7 days of the week

            next7daysdates = [(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 8)]


            for ind,day in enumerate(next7daysdates):
                print("(%s) %s" % (ind+1,day))

            app_date_opt = input("Please select your preferred day: ")

            if app_date_opt.isdigit() != True or int(app_date_opt) < 1 or int(app_date_opt) > len(next7daysdates):
                msg = "Error: Unknown option. Please select one of the options in the menu"
                continue

            app_date = next7daysdates[int(app_date_opt)-1]
            break

        #Randomly pick a physician
        phys = model.getPhysicians(phy_specialization)
        phy_id = phys[random.randint(0,len(phys)-1)]

        return app_date, phy_id


    def displayOTPRequests(self, user):

        """Displays the OTPs of access requests requested from a given user

         :param user: User object of the user from whom access request is required

         """

        otps = model.getPatientOTPs(user)

        self.clearScr()
        print("-" * 80)
        print("Access Request Authorization")
        print("-" * 80)

        if len(otps) == 0:
            input("No OTPs have been issued. Press Enter to return to the previous menu...")
            return

        print("The following OTPs have been issued:")

        for auth_otp, auth_requesting_usr_id in otps:
            requesting_user = model.retrieveUser(usr_id=auth_requesting_usr_id)
            print("- %s from %s %s" % (auth_otp, requesting_user.usr_fname, requesting_user.usr_lname))

        input("\nPress the Enter key to return to the previous menu...")


    def patientMenuScr(self, user):

        """Displays the Patient main menu and handles all Patient actions.

         :param user: User object containing to the logged in Patient

        :return: str message to be sent back to the previous screen
         """

        model = self.model

        opt = -1
        msg = ""

        while True:

            self.clearScr()
            print("-" * 80)
            print("Patient Menu")
            print("User: %s" % (user.usr_login))
            print("%s %s" % (user.usr_fname, user.usr_lname))
            print("-" * 80)
            if (msg != ""):
                print("** " + msg + " **\n")
                msg = ""

            print("Below are your current options:\n")

            print("(1) View my details")
            print("(2) Update my details")
            print("(3) Book an appointment")
            print("(4) Edit an appointment (NOT IMPLEMENTED)")
            print("(5) Cancel an appointment (NOT IMPLEMENTED)")
            print("(6) Display my consultation notes")
            print("(7) Authorize access requests")
            print("")
            print("(q) Logout")

            opt = input("Please enter an option to continue: ").lower()

            #Update the user in case some admin made a change to the details of this user in a separate terminal
            user = model.retrieveUser(user.usr_login)

            if (opt == "1"):
                self.clearScr()
                self.displayUserDetail(user)
                input("\nPress the Enter key to return to the menu...")
                msg = ""
                model.addLogEntry(LogEntry("Patient %s viewed their own details" % (
                user.usr_id, )))

            elif (opt == "2"):
                user = self.updateUserDetails(user)
                user = self.capturePatientDetails(user)
                model.updateUser(user)
                msg = "Your details have been successfully changed"
                model.addLogEntry(LogEntry("Patient %s updated their own details" % (
                user.usr_id, )))


            elif (opt == "3"):
                app_date, phy_id = self.captureBookingDetails()
                if model.checkRepeatBooking(user.usr_id, app_date) == True:
                    msg = "You already have an appointment scheduled for that day.\nPlease select another day and try again."
                    continue

                timestamp = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

                app = Appointment(app_created_datetime=timestamp, app_date=app_date, physician=Physician(usr_id=phy_id), patient=user)

                app_id = model.bookAppointment(app)
                msg = "Your appointment has been successfully registered."

                model.addLogEntry(LogEntry("Patient %s added Appointment %s" % (user.usr_id,app_id)))




            elif (opt == "4"):
                msg = "This feature is not implemented in this demo version"

            elif (opt == "5"):
                msg = "This feature is not implemented in this demo version"

            elif (opt == "6"):
                self.displayPatientConsultations(user)
                model.addLogEntry(LogEntry("Patient %s viewed all their own Consultations Notes" % (user.usr_id,)))

            elif (opt == "7"):
                self.displayOTPRequests(user)

            elif (opt == "q"):
                model.addLogEntry(LogEntry("Patient %s logged out" % (user.usr_id,)))
                return "You have successfully logged out"

            else:
                msg = "Error: Unknown option. Please select one of the options in the menu"



    def adminMenuScr(self, user):

        """Displays the Admin main menu and handles all Admin actions.

         :param user: User object containing to the logged in Admin user

        :return: str message to be sent back to the previous screen
         """

        opt = -1
        msg = ""

        while (True):
            self.clearScr()
            print("-" * 80)
            print("Admin Menu")
            print("User: %s" % (user.usr_login))
            print("%s %s" % (user.usr_fname, user.usr_lname))
            print("-" * 80)
            if (msg != ""):
                print("** " + msg + " **\n")
                msg = ""
            print("Below are your current options:\n")

            # if user.adm_permlevel == 2:

            print("(1) View patient details (requires patient OTP)")
            print("(2) Edit patient details (requires patient OTP)")

            if user.adm_permlevel == 2:
                print("(3) Register a new Physician")
                print("(4) Cancel an Appointment")

            else:
                print("(3) Register a new Physician (requires super admin OTP)")
                print("(4) Cancel an Appointment (requires super admin OTP)")

            print("")
            print("(5) Search and list patients (NOT IMPLEMENTED)")
            print("(6) Add a new admin user (NOT IMPLEMENTED)")
            print("(7) Edit admin user permissions (NOT IMPLEMENTED)")
            print("(8) Update Physician details (NOT IMPLEMENTED)")
            print("(9) Delete User account (NOT IMPLEMENTED)")
            print("")
            print("(10) Authorize access requests")

            #LAST DOING: Deciding what super admin can do to then decide what normal admin can do
            #Delete user

            print("\n(q) Logout")

            opt = input("Please enter an option to continue: ").lower()

            if (opt == "1"):

                patient = self.captureUsername("patient")

                if patient == None:
                    continue

                msg = self.authorizationScr(targetuser=patient,requestinguser=user)

                if msg == "":
                    self.clearScr()
                    self.displayUserDetail(patient)
                    input("\nPress the Enter key to return to the menu...")
                    msg = ""
                    model.addLogEntry(LogEntry("Admin %s viewed details of Patient %s" % (user.usr_id, patient.usr_id)))

                continue



            elif (opt == "2"):

                patient = self.captureUsername("patient")

                if patient == None:
                    continue

                msg = self.authorizationScr(targetuser=patient,requestinguser=user)

                if msg == "":
                    patient = self.updateUserDetails(patient)
                    patient = self.capturePatientDetails(patient)
                    model.updateUser(patient)
                    msg = "The patient details have been successfully changed"
                    model.addLogEntry(LogEntry("Admin %s updated details of Patient %s" % (user.usr_id, patient.usr_id)))

                continue

            elif (opt == "3"):

                msg = ""

                if user.adm_permlevel < 2:

                    # superadmin = self.captureUsername("admin")
                    #
                    # if superadmin == None:
                    #     continue
                    superadmin = model.retrieveUser(usr_login="admin")

                    msg = self.authorizationScr(targetuser=superadmin, requestinguser=user)

                if msg == "":
                    newuser = self.captureUserDetails()
                    phy = Physician()
                    phy.createFromUser(newuser)

                    phy = self.capturePhysicianDetails(phy)
                    phy_id = model.addUser(phy)
                    msg = "The new physician account has been created successfully."

                    model.addLogEntry(LogEntry("Admin %s created new Physician %s" % (user.usr_id, phy_id)))

                    continue

            elif (opt == "4"):

                #First get the patient's username
                patient = self.captureUsername("patient")

                if patient == None:
                    continue

                appcancel = self.captureAppointmentCancellation(patient)

                if appcancel == None:
                    msg = ""
                    continue

                msg = ""

                if user.adm_permlevel < 2:

                    # superadmin = self.captureUsername("admin")
                    #
                    # if superadmin == None:
                    #     continue
                    superadmin = model.retrieveUser(usr_login="admin")

                    msg = self.authorizationScr(targetuser=superadmin, requestinguser=user)

                if msg == "":
                    model.cancelAppointment(appcancel)
                    model.addLogEntry(LogEntry("Admin %s cancelled Appointment %s of Patient %s scheduled for %s with Physician %s" % (user.usr_id, appcancel.app_id, appcancel.patient.usr_id, appcancel.app_date, appcancel.physician.usr_id)))
                    msg = "The appointment was successfully cancelled"



            elif (opt == "10"):
                self.displayOTPRequests(user)

            elif (opt in ["5","6","7","8","9"]):
                msg = "This feature is not implemented in this demo version"

            elif opt == "q":
                model.addLogEntry(LogEntry("Admin %s logged out" % user.usr_id, ))
                return "You have successfully logged out"

            else:
                msg = "Error: Unknown option. Please select one of the options in the menu"


    def capturePhysicianDetails(self, phy):
        """Captures physician-specific attributes (see Physician class). Carries out validation on the physician specialization to limit to one of the accepted options.

         :param phy: Physician object of the Physician for which details are being captured

        :return: Updated Physician object
         """
        phy_practiceno = phy.phy_practiceno
        phy_specialization = phy.phy_specialization

        phy_practiceno_tmp = input("Practice No: ")


        lstspecialization = [it for it in SPECIALIZATION.keys()]

        phy_specialization_tmp = ""

        opt = -1
        msg = ""
        while True:

            if msg != "":
                print("** %s **" % (msg))
            print("\nBelow are the specializations: ")
            for ind,it in enumerate(lstspecialization):
                print("(%s) %s" % (ind+1,it))

            opt = input("\nPlease enter the option corresponding to your specialization: ")

            if opt == "":
                break

            if opt.isnumeric() == False or int(opt) < 1 or int(opt) > len(lstspecialization):
                msg = "Error: Unknown option. Please select one of the options in the menu"
                continue

            phy_specialization_tmp = lstspecialization[int(opt)-1]
            break

        #This stuff is used when the user is trying to edit their details
        #If the user enters "" for either field, just use the detail already in pat
        #Only if the user actually puts something in, replace them
        if phy_practiceno_tmp != "":
            phy_practiceno = phy_practiceno_tmp

        if phy_specialization_tmp != "":
            phy_specialization = phy_specialization_tmp

        phy.setPhysicianDetails(phy_practiceno, phy_specialization)

        return phy

    def displayConsultedAppointments(self, phy):
        """Displays today's Appointments assigned to a specific Physician that have already been consulted i.e. have entries in the Consultation table.

         :param phy: Physician object of the Physician associated with the Appointments
         """
        appointmentslist = model.getPhysicianAppointments(phy)

        consultedlist = [app for app in appointmentslist if app.consulted==1]


        todaydate = datetime.datetime.today().strftime("%Y-%m-%d")

        self.clearScr()
        print("-" * 80)
        print("Appointments that you've already consulted today:")
        print("Date: %s" % (todaydate))
        print("-" * 80)

        for ind,app in enumerate(consultedlist):
            print("%s. %s %s" % (ind+1, app.patient.usr_fname, app.patient.usr_lname))

        input("\nPress the Enter key to return to the menu...")


    def displayPatientConsultations(self, patient):
        """Displays all Consultations (prescriptions and notes) of a specific patient.

         :param patient: Patient object of the Patient whose Consultations are to be displayed
         """

        patientconsults = model.getPatientConsultations(patient)

        self.clearScr()
        print("-" * 80)
        print("Patient Consultation Notes")
        print("-" * 80)

        for ind,consult in enumerate(patientconsults):
            print("%s:\nNotes: %s\nPrescription:%s\n" % (consult.cons_datetime, consult.cons_notes, consult.cons_prescription))

        input("\nPress the Enter key to return to the menu...")


    def captureConsultationInfo(self, app):
        """Reads in consultation-specific attributes (see Consultation class) pertaining to a given Appointment and saves it to the database

         :param app: Appointment
             The Appointment for which Consultation information is being captured.
         """
        self.clearScr()
        print("-" * 80)
        print("Patient Consultation Notes")
        print("-" * 80)
        print("Please enter the following information pertaining to this consultation:\n")

        cons_prescription = input("Prescription information: ")
        cons_notes = input("Consultation notes: ")

        cons_datetime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")

        cons = Consultation(cons_datetime=cons_datetime, appointment=app, cons_notes=cons_notes, cons_prescription=cons_prescription)

        model.addConsultationInfo(cons)

    def authorizationScr(self, targetuser, requestinguser):

        """A screen that generates and validates an OTP from a User requesting access from another User (e.g. Physician requesting Consultation information access from a Patient). The OTP is registered in the database so that the target user can access it. The OTP is checked for validity and expiry.

         :param targetuser: User
            User from whom access is requested
         :param requestinguser: User
            User who is requesting access
        :return: str message to be sent back to the previous screen; either "" if successful or an error message if not successful
         """

        #Generate intial otp
        otp = totp.now()
        auth_id = model.registerOTP(targetuser,requestinguser,otp)

        msg = ""
        while True:

            self.clearScr()
            print("-" * 80)
            print("Access Confirmation")
            print("-" * 80)
            if (msg != ""):
                print("** " + msg + " **\n")
                msg = ""

            print("A One-Time-Pin (OTP) has been sent to the patient to consent to access.")
            print("The OTP expires after 30 seconds and if it expires, you will need to")
            print(" go back to the previous menu and attempt access again.\n")
            print("Please enter the OTP to obtain access (or 'q' to go back): ")

            otp_try = input("OTP: ").lower()

            if (otp_try == "q"):
                model.deregisterOTP(auth_id)
                return "Access request was cancelled."

            if (totp.now() != otp):
                model.deregisterOTP(auth_id)
                return "OTP for access request expired. Try again."

            if (totp.verify(otp_try) == True):
                model.deregisterOTP(auth_id)
                return ""

            msg = "Invalid OTP. Try again..."




    def appointmentsScr(self, phy):

        """Displays a screen for appointment management functions i.e. lists available (pending) Appointments and allows selection; for a selected Appointment, it allows viewing the previous Consultation notes of the relevant patient (to give the Physician context if need be) and/or insert Consultation notes for the current Appointment.

         :param phy: Physician object pertaining to the presiding logged in Physician

        :return: str message to be sent back to the previous screen
         """

        appointmentslist = model.getPhysicianAppointments(phy)

        notconsultedlist = [app for app in appointmentslist if app.consulted==0]


        todaydate = datetime.datetime.today().strftime("%Y-%m-%d")

        while True:

            opt = -1
            msg = ""

            while True:

                self.clearScr()
                print("-" * 80)
                print("Pending Appointments")
                print("Date: %s" % (todaydate))
                print("-" * 80)
                if (msg != ""):
                    print("** " + msg + " **\n")
                    msg = ""

                print("\nAppointments that are pending consultation:")

                for ind,app in enumerate(notconsultedlist):
                    print("(%s) %s %s" % (ind+1, app.patient.usr_fname, app.patient.usr_lname))

                print("(q) Back to previous menu\n")
                opt = input("Please enter a menu option: ").lower()

                if opt == "q":
                    return ""

                if opt.isdigit() != True or int(opt) < 1 or int(opt) > len(notconsultedlist):
                    msg = "Error: Unknown option. Please select one of the options in the menu"
                    continue

                app_index = int(opt) - 1
                break

            opt = -1
            msg = ""

            while True:

                self.clearScr()
                print("-" * 80)
                print("Consult Appointment")
                print("Appointment for: %s %s" % (notconsultedlist[app_index].patient.usr_fname, notconsultedlist[app_index].patient.usr_lname))
                print("-" * 80)
                if (msg != ""):
                    print("** " + msg + " **\n")
                    msg = ""

                print("\nOptions:")

                print("(1) View patient consultation notes history (requires patient OTP)")
                print("(2) Add consultation note and prescription and finalize (go back to previous menu)")
                print("(q) Go back to previous menu without finalizing")

                print("")
                opt = input("Please enter an option: ").lower()


                if opt == "q":
                    break

                elif opt == "1":
                    msg = self.authorizationScr(targetuser=notconsultedlist[app_index].patient,requestinguser=phy)
                    if msg == "":
                        self.displayPatientConsultations(notconsultedlist[app_index].patient)
                        model.addLogEntry(LogEntry("Physician %s viewed the Consultation notes of Patient %s" % (phy.usr_id, notconsultedlist[app_index].patient.usr_id)))
                    continue


                elif opt == "2":
                    self.captureConsultationInfo(notconsultedlist[app_index])
                    model.addLogEntry(LogEntry("Physician %s captured Consultation notes for Appointment %s" % (
                    phy.usr_id, notconsultedlist[app_index].app_id)))
                    return "Consultation has been recorded and finalized"

                else:
                    msg = "Error: Unknown option. Please select one of the options in the menu"
                    continue


    def captureAppointmentCancellation(self, patient):

        """Displays a list of pending Appointments for a patient, allows the user to select one, and returns that Appointment object.

         :param patient: Patient object of the patient whose appointments are being listed

        :return: Appointment object or None if operation is cancelled by user
         """

        appointmentslist = model.getPatientAppointments(patient)

        notconsultedlist = [app for app in appointmentslist if app.consulted==0]


        todaydate = datetime.datetime.today().strftime("%Y-%m-%d")

        app_index = -1


        opt = -1
        msg = ""

        while True:

            self.clearScr()
            print("-" * 80)
            print("Appointment Cancellation")
            print("For Patient: %s %s" % (patient.usr_fname, patient.usr_lname))
            print("-" * 80)
            if (msg != ""):
                print("** " + msg + " **\n")
                msg = ""

            print("\nAppointments that are pending consultation for this patient:")

            for ind,app in enumerate(notconsultedlist):
                print("(%s) %s with Dr %s %s" % (ind+1, app.app_date, app.physician.usr_fname, app.physician.usr_lname))

            print("(q) Back to previous menu\n")
            opt = input("Please enter a menu option of the appointment to cancel: ").lower()

            if opt == "q":
                return None

            if opt.isdigit() != True or int(opt) < 1 or int(opt) > len(notconsultedlist):
                msg = "Error: Unknown option. Please select one of the options in the menu"
                continue

            app_index = int(opt) - 1
            break


        return notconsultedlist[app_index]

    def captureUsername(self, usr_type):
 
        """Allows the capture of a login username and checks if the username exists. This is used in various places in the program e.g. when a Physician wants to view the consultation notes of a Patient, this screen allows the Physician to specify the Patient by specifying the Patient's login username. The usr_type specifies what type of user is being retrieved. If successful the User is obtained and returned as an Admin/Physician/Patient object

         :param usr_type: Type of the user that is being queried

        :return: Admin or Physician or Patient object of the user
         """

        msg = ""

        user_type_camelcase = usr_type.capitalize()

        while True:
            self.clearScr()
            print("-" * 80)
            print("%s Username" % user_type_camelcase)
            print("-" * 80)
            if (msg != ""):
                print("** " + msg + " **\n")
                msg = ""
            print("Type in the %s's login username or 'q' to go back" % usr_type)

            usr_login = input("%s Login: " % user_type_camelcase).lower()

            if usr_login == 'q':
                return None

            if model.checkUsernameExists(usr_login) == False:
                msg = "Invalid %s username" % usr_type
                continue

            user = model.retrieveUser(usr_login)

            if user.usr_type != usr_type:
                msg = "Invalid %s username" % usr_type
                continue

            if user.usr_type == "admin" and user.adm_permlevel != 2:
                msg = "Invalid super admin username"
                continue

            return user


    def physicianMenuScr(self, user):
        """Displays the Physician main menu and handles all Physician actions.

         :param user: User object containing to the logged in Physician

        :return: str message to be sent back to the previous screen
         """
        model = self.model

        opt = -1
        msg = ""

        while True:
            self.clearScr()
            print("-" * 80)
            print("Physician Menu")
            print("User: %s" % (user.usr_login))
            print("Dr %s %s" % (user.usr_fname, user.usr_lname))
            print("-" * 80)
            if (msg != ""):
                print("** " + msg + " **\n")
                msg = ""

            print("Below are your current options:\n")

            print("(1) View my details")
            print("(2) Update my details")
            print("(3) View today's appointments that have already been consulted")
            print("(4) View today's appointments that are pending consultation")
            print("(5) Display patient consultation notes")
            print("")
            print("(q) Logout")

            opt = input("Please enter an option to continue: ").lower()

            if (opt == "1"):
                self.clearScr()
                self.displayUserDetail(user)
                input("\nPress the Enter key to return to the menu...")
                model.addLogEntry(LogEntry("Physician %s viewed their own details" % (user.usr_id,)))


            elif (opt == "2"):
                user = self.updateUserDetails(user)
                user = self.capturePhysicianDetails(user)
                model.updateUser(user)
                msg = "Your details have been successfully changed"

                model.addLogEntry(LogEntry("Physician %s updated their own details" % (user.usr_id,)))


            elif (opt == "3"):
                self.displayConsultedAppointments(user)




            elif (opt == "4"):
                msg = self.appointmentsScr(user)

            elif (opt == "5"):
                patient = self.captureUsername("patient")

                if patient == None:
                    continue

                msg = self.authorizationScr(targetuser=patient,requestinguser=user)
                if msg == "":
                    self.displayPatientConsultations(patient)
                    model.addLogEntry(LogEntry("Physician %s viewed the Consultation notes of Patient %s" % (user.usr_id, patient.usr_id)))
                continue


            elif (opt == "q"):
                model.addLogEntry(LogEntry("Physician %s logged out" % (user.usr_id, )))
                return "You have successfully logged out"

            else:
                msg = "Error: Unknown option. Please select one of the options in the menu"

    def userMenuScr(self, user):
        """Function that links to the relevant User menu screen depending on the type of User.

         :param user: User object containing to the logged in User

        :return: str message to be sent back to the previous screen from each relevant User screen
         """

        if isinstance(user,Admin):
            model.addLogEntry(LogEntry("Admin %s logged in" % (user.usr_id,)))
            return self.adminMenuScr(user)
        if isinstance(user,Patient):
            model.addLogEntry(LogEntry("Patient %s logged in" % (user.usr_id,)))
            return self.patientMenuScr(user)
        if isinstance(user,Physician):
            model.addLogEntry(LogEntry("Physician %s logged in" % (user.usr_id,)))
            return self.physicianMenuScr(user)


    def captureUserDetails(self):
        """Function that reads in user attribute information (see User object), carries out validation on the password and username (checks for existence), and returns a User object.

         :return: User object with captured information in it
         """
        model = self.model

        #Note: For this demo, there is no built-in way to get out of this procedure once in

        #These are all the details of a patient that need to be captured
        usr_login = ""
        usr_pass = ""
        usr_fname = ""
        usr_lname = ""

        self.clearScr()
        print("-" * 80)
        print("User Registration")
        print("-" * 80)
        print("Please provide the following information:\n")

        while True:
            usr_login = input("Desired login username: ")
            exists = model.checkUsernameExists(usr_login)

            if exists == False:
                print("This login username is available.")
                break

            print("This login username already exists. Please select another.")

        print("Note: For security purposes, your desired password should meet the following criteria:")
        print("Min 8 and max 16 characters, contain at least: 1 uppercase letter, 1 lowercase letter,")
        print("  1 special character, and 1 number (good luck :D)\n")

        while True:
            usr_pass = input("Desired password: ")
            success = passvalid.validate(usr_pass)

            if success == True:
                break

            print("**Invalid password**")
            print("For security purposes, your desired password should meet the following criteria:")
            print("Min 8 and max 16 characters, contain at least: 1 uppercase letter, 1 lowercase letter,")
            print("  1 special character, and 1 number (good luck :D)\n")


        print("")
        #No user validation done on these fields for this demo
        usr_fname = input("First Name: ")
        usr_lname = input("Last Name: ")

        user = User(usr_login,usr_pass)
        user.setUserDetails(usr_fname,usr_lname)

        return user


    def loginScr(self):
        """Function that displays a login screen. Allows the user to type in user login and password, and validates the login.

         :return: User object with the logged in User
        """
        model = self.model

        msg = ""

        while True:
            self.clearScr()
            print("-" * 80)
            print("User Login")
            print("-" * 80)
            if (msg != ""):
                print("** " + msg + " **")
                msg = ""
            print("Please provide your login credentials:\n")
            usr_login = input("User login: ")
            usr_pass = input("User password: ")

            userexists = model.checkUsernameExists(usr_login)

            if userexists == False:
                #Don't inform the user that the username was invalid;
                #This provides added security against username dictionary/brute force attacks
                msg = "Username or password is invalid"
                continue

            passisvalid = model.checkPasswordValid(usr_login, usr_pass)

            if passisvalid == False:
                # Don't inform the user that the username was invalid;
                # This provides added security against username dictionary/brute force attacks
                msg = "Username or password is invalid"
                continue

            #Ok username existed and password was valid. Logged in now
            break

        return model.retrieveUser(usr_login)




    def mainMenuScr(self):
        """Main menu screen that is initially displayed to all users as soon as the ASMIS is started up. Allows user to either login or register (as a patient).

         """
        model = self.model

        opt = -1
        msg = ""

        while True:

            self.clearScr()
            print("-" * 80)
            print("Welcome to the Queen's community ASMIS")
            print("-" * 80)
            print("Note: If you are a Physician requiring initial registration,")
            print("please contact an Admin to register you.")
            print("-" * 80 + "\n")
            print("Below are the current options:\n")
            print("(1) Login with existing credentials")
            print("(2) Register as a new patient\n")
            print("(q) Quit")
            print("-" * 80)
            if (msg != ""):
                print("** " + msg + " **")
                msg = ""
            opt = input("Please enter an option to continue: ").lower()

            if (opt == "1"):
                user = self.loginScr()
                msg = view.userMenuScr(user)

            elif (opt == "2"):
                user = self.captureUserDetails()
                pat = Patient()
                pat.createFromUser(user)
                pat = self.capturePatientDetails(pat)
                pat_id = model.addUser(pat)
                msg = "Your patient account has been created successfully.\nPlease proceed to login."
                model.addLogEntry(LogEntry("New Patient account %s created via registration screen" % (pat_id, )))


            elif (opt == "q"):
                print("Thanks for using the Queen's community ASMIS. Quiting...")
                break


            else:
                msg = "Error: Unknown option. Please select one of the options in the menu"


#Create a connection to the database
model = Model()

view = View(model)

view.mainMenuScr()


# model.resetUsers()


model.closeModel()

