import sqlite3

DB = "patients.db"

patients = [
    ("James","Anderson","B","1982-04-15","123-45-6001","(555)201-0001","12 Maple St","Hartford","CT","06101","james.anderson@email.com","DOC1"),
    ("Maria","Garcia","L","1990-08-22","123-45-6002","(555)201-0002","45 Oak Ave","Boston","MA","02101","maria.garcia@email.com","DOC2"),
    ("Robert","Martinez","A","1975-11-30","123-45-6003","(555)201-0003","78 Pine Rd","New York","NY","10001","robert.martinez@email.com","DOC1"),
    ("Linda","Wilson","M","1988-02-14","123-45-6004","(555)201-0004","90 Elm St","Chicago","IL","60601","linda.wilson@email.com","DOC3"),
    ("Michael","Taylor","J","1965-06-05","123-45-6005","(555)201-0005","33 Cedar Ln","Houston","TX","77001","michael.taylor@email.com","DOC2"),
    ("Patricia","Thomas","R","1993-09-18","123-45-6006","(555)201-0006","21 Birch Blvd","Phoenix","AZ","85001","patricia.thomas@email.com","DOC1"),
    ("David","Hernandez","E","1980-12-25","123-45-6007","(555)201-0007","56 Spruce Way","Philadelphia","PA","19101","david.hernandez@email.com","DOC3"),
    ("Barbara","Moore","C","1971-03-08","123-45-6008","(555)201-0008","14 Walnut Dr","San Antonio","TX","78201","barbara.moore@email.com","DOC2"),
    ("Richard","Jackson","T","1987-07-19","123-45-6009","(555)201-0009","67 Willow Ct","San Diego","CA","92101","richard.jackson@email.com","DOC1"),
    ("Susan","White","N","1995-01-28","123-45-6010","(555)201-0010","38 Chestnut Pl","Dallas","TX","75201","susan.white@email.com","DOC2"),
    ("Joseph","Harris","P","1969-05-11","123-45-6011","(555)201-0011","82 Poplar St","San Jose","CA","95101","joseph.harris@email.com","DOC3"),
    ("Karen","Martin","F","1983-10-02","123-45-6012","(555)201-0012","29 Ash Ave","Austin","TX","73301","karen.martin@email.com","DOC1"),
    ("Thomas","Thompson","G","1978-08-16","123-45-6013","(555)201-0013","51 Hickory Ln","Jacksonville","FL","32099","thomas.thompson@email.com","DOC2"),
    ("Nancy","Garcia","H","1991-04-23","123-45-6014","(555)201-0014","17 Magnolia Rd","Fort Worth","TX","76101","nancy.garcia@email.com","DOC3"),
    ("Charles","Martinez","K","1974-02-07","123-45-6015","(555)201-0015","43 Cypress Dr","Columbus","OH","43085","charles.martinez@email.com","DOC1"),
    ("Betty","Robinson","V","1986-06-30","123-45-6016","(555)201-0016","65 Redwood Blvd","Charlotte","NC","28201","betty.robinson@email.com","DOC2"),
    ("Christopher","Clark","W","1998-11-14","123-45-6017","(555)201-0017","11 Juniper Way","Indianapolis","IN","46201","christopher.clark@email.com","DOC3"),
    ("Dorothy","Rodriguez","S","1967-09-03","123-45-6018","(555)201-0018","74 Dogwood Ct","San Francisco","CA","94101","dorothy.rodriguez@email.com","DOC1"),
    ("Daniel","Lewis","Q","1984-03-21","123-45-6019","(555)201-0019","36 Sycamore Pl","Seattle","WA","98101","daniel.lewis@email.com","DOC2"),
    ("Margaret","Lee","U","1992-07-09","123-45-6020","(555)201-0020","58 Mulberry St","Denver","CO","80201","margaret.lee@email.com","DOC3"),
    ("Paul","Walker","D","1973-01-17","123-45-6021","(555)201-0021","22 Linden Ave","Nashville","TN","37201","paul.walker@email.com","DOC1"),
    ("Lisa","Hall","I","1989-05-26","123-45-6022","(555)201-0022","47 Hawthorn Rd","Oklahoma City","OK","73101","lisa.hall@email.com","DOC2"),
    ("Mark","Allen","O","1977-08-04","123-45-6023","(555)201-0023","83 Cottonwood Ln","El Paso","TX","79901","mark.allen@email.com","DOC3"),
    ("Donna","Young","Z","1994-12-12","123-45-6024","(555)201-0024","15 Aspen Blvd","Washington","DC","20001","donna.young@email.com","DOC1"),
    ("Donald","Hernandez","X","1968-04-29","123-45-6025","(555)201-0025","61 Beech Dr","Las Vegas","NV","89101","donald.hernandez@email.com","DOC2"),
    ("Sandra","King","Y","1981-10-08","123-45-6026","(555)201-0026","28 Locust Way","Louisville","KY","40201","sandra.king@email.com","DOC3"),
    ("George","Wright","B","1996-02-20","123-45-6027","(555)201-0027","54 Pecan Ct","Baltimore","MD","21201","george.wright@email.com","DOC1"),
    ("Ashley","Scott","C","1985-06-13","123-45-6028","(555)201-0028","39 Acacia Pl","Milwaukee","WI","53201","ashley.scott@email.com","DOC2"),
    ("Kenneth","Torres","D","1972-09-27","123-45-6029","(555)201-0029","76 Olive St","Albuquerque","NM","87101","kenneth.torres@email.com","DOC3"),
    ("Jessica","Nguyen","E","1997-01-05","123-45-6030","(555)201-0030","13 Palm Ave","Tucson","AZ","85701","jessica.nguyen@email.com","DOC1"),
    ("Steven","Hill","F","1979-07-16","123-45-6031","(555)201-0031","49 Bamboo Rd","Fresno","CA","93701","steven.hill@email.com","DOC2"),
    ("Ruth","Flores","G","1963-03-31","123-45-6032","(555)201-0032","87 Fern Ln","Sacramento","CA","94201","ruth.flores@email.com","DOC3"),
    ("Edward","Green","H","1991-11-22","123-45-6033","(555)201-0033","25 Ivy Blvd","Mesa","AZ","85201","edward.green@email.com","DOC1"),
    ("Kimberly","Adams","I","1986-05-09","123-45-6034","(555)201-0034","63 Holly Dr","Kansas City","MO","64101","kimberly.adams@email.com","DOC2"),
    ("Brian","Nelson","J","1970-08-18","123-45-6035","(555)201-0035","31 Laurel Way","Atlanta","GA","30301","brian.nelson@email.com","DOC3"),
    ("Sharon","Baker","K","1993-02-03","123-45-6036","(555)201-0036","77 Moss Ct","Omaha","NE","68101","sharon.baker@email.com","DOC1"),
    ("Ronald","Carter","L","1976-06-25","123-45-6037","(555)201-0037","19 Clover Pl","Colorado Springs","CO","80901","ronald.carter@email.com","DOC2"),
    ("Michelle","Mitchell","M","1988-10-14","123-45-6038","(555)201-0038","55 Daisy St","Raleigh","NC","27601","michelle.mitchell@email.com","DOC3"),
    ("Kevin","Perez","N","1964-04-07","123-45-6039","(555)201-0039","42 Violet Ave","Virginia Beach","VA","23450","kevin.perez@email.com","DOC1"),
    ("Laura","Roberts","O","1999-12-19","123-45-6040","(555)201-0040","88 Jasmine Rd","Minneapolis","MN","55401","laura.roberts@email.com","DOC2"),
    ("Timothy","Turner","P","1982-07-01","123-45-6041","(555)201-0041","26 Lilac Ln","Tulsa","OK","74101","timothy.turner@email.com","DOC3"),
    ("Sarah","Phillips","Q","1975-03-15","123-45-6042","(555)201-0042","64 Rose Blvd","Arlington","TX","76001","sarah.phillips@email.com","DOC1"),
    ("Jason","Campbell","R","1990-09-28","123-45-6043","(555)201-0043","37 Orchid Dr","New Orleans","LA","70112","jason.campbell@email.com","DOC2"),
    ("Deborah","Parker","S","1967-01-11","123-45-6044","(555)201-0044","71 Sunflower Way","Wichita","KS","67201","deborah.parker@email.com","DOC3"),
    ("Jeffrey","Evans","T","1984-05-24","123-45-6045","(555)201-0045","18 Tulip Ct","Cleveland","OH","44101","jeffrey.evans@email.com","DOC1"),
    ("Stephanie","Edwards","U","1997-09-06","123-45-6046","(555)201-0046","53 Marigold Pl","Tampa","FL","33601","stephanie.edwards@email.com","DOC2"),
    ("Ryan","Collins","V","1971-12-30","123-45-6047","(555)201-0047","84 Carnation St","Bakersfield","CA","93301","ryan.collins@email.com","DOC3"),
    ("Rebecca","Stewart","W","1985-04-17","123-45-6048","(555)201-0048","27 Blossom Ave","Aurora","CO","80010","rebecca.stewart@email.com","DOC1"),
    ("Gary","Sanchez","X","1994-08-08","123-45-6049","(555)201-0049","66 Garden Rd","Anaheim","CA","92801","gary.sanchez@email.com","DOC2"),
    ("Amy","Morris","Y","1978-02-22","123-45-6050","(555)201-0050","41 Meadow Ln","Santa Ana","CA","92701","amy.morris@email.com","DOC3"),
]

with sqlite3.connect(DB) as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            PatNum INTEGER PRIMARY KEY AUTOINCREMENT,
            FName TEXT, LName TEXT, MiddleI TEXT,
            Birthdate TEXT, SSN TEXT, HmPhone TEXT,
            Address TEXT, City TEXT, State TEXT, Zip TEXT,
            Email TEXT, priProvAbbr TEXT,
            PatStatus TEXT DEFAULT 'Patient',
            BillingType TEXT DEFAULT 'Standard Account'
        )
    """)
    con.execute("DELETE FROM patients")
    con.executemany(
        "INSERT INTO patients (FName,LName,MiddleI,Birthdate,SSN,HmPhone,Address,City,State,Zip,Email,priProvAbbr) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        patients
    )
    print(f"✓ Inserted {len(patients)} patients into {DB}")