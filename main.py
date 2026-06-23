# Kevin Cox
# CS 341
# 9/23/25
# Chicago traffic camera data program
# Helps find intersections, red light camera, speed camera, streets
# Helps compare data for all the things stated above

import sqlite3
import matplotlib.pyplot as plt

##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    # total red cams
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Cameras:", f"{row[0]:,}")
    # total speed cams
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Speed Cameras:", f"{row[0]:,}")
    #total red violations
    dbCursor.execute("SELECT COUNT(*) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Camera Violation Entries:", f"{row[0]:,}")
    #total speed violations
    dbCursor.execute("SELECT COUNT(*) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Speed Camera Violation Entries:", f"{row[0]:,}")
    # Date ranges
    dbCursor.execute("""
        SELECT MIN(d), MAX(d)
        FROM (
            SELECT Violation_Date AS d FROM RedViolations
            UNION ALL
            SELECT Violation_Date AS d FROM SpeedViolations
            );
    """)
    mind, maxd = dbCursor.fetchone()
    if mind is None or maxd is None:
        print("  Range of Dates in the Database: N/A - N/A")
    else:
        print(f"  Range of Dates in the Database: {mind} - { maxd}") 
    #total red cam violation in date
    dbCursor.execute("SELECT COALESCE(SUM(Num_Violations), 0 ) FROM RedViolations")
    row = dbCursor.fetchone()
    print("  Total Number of Red Light Camera Violations:", f"{row[0]:,}")
    # total speed cam violation in date
    dbCursor.execute("SELECT COALESCE(SUM(Num_Violations), 0 ) FROM SpeedViolations")
    row = dbCursor.fetchone()
    print("  Total Number of Speed Camera Violations:", f"{row[0]:,}")

    

# Find an intersection by name
def command1(dbConn):
    dbCursor = dbConn.cursor()

    intersection_name = input("\nEnter the name of the intersection to find (wildcards _ and % allowed): ").strip()
    
    dbCursor.execute("""
        SELECT Intersection_ID, Intersection
        FROM Intersections
        WHERE Intersection LIKE ? 
        ORDER BY Intersection ASC;
        """,(intersection_name,))
    
    results = dbCursor.fetchall()

    if not results:
        print("No intersections matching that name were found.")
    else:
        for intersection_id, intersection in results:
            print(f"{intersection_id} : {intersection}")

# find all the cameras at an intersection
def command2(dbConn):
    dbCursor = dbConn.cursor()

    all_camera = input("\nEnter the name of the intersection (no wildcards allowed): ").strip()

    dbCursor.execute("""
        SELECT Intersection_ID
        FROM Intersections
        WHERE Intersection = ?
        """, (all_camera,))
    
    intersection = dbCursor.fetchone()

    if not intersection:
        print("\nNo red light cameras found at that intersection.")
        print("\nNo speed cameras found at that intersection.")
        print()
        return
    
    intersection_id = intersection[0]
    
    dbCursor.execute("""
        SELECT Camera_ID, Address
        FROM RedCameras
        WHERE Intersection_ID = ?
        ORDER BY Camera_ID ASC
        """, (intersection_id,))
    red_cameras = dbCursor.fetchall()

    dbCursor.execute("""
        SELECT Camera_ID, Address
        FROM SpeedCameras
        WHERE Intersection_ID = ?
        ORDER BY Camera_ID ASC
        """, (intersection_id,))
    speed_cameras = dbCursor.fetchall()

    if red_cameras:
        print("\nRed Light Cameras:")
        for camera_id, address in red_cameras:
            print(f"   {camera_id} : {address}")
    else:
        print("\nNo red light cameras found at that intersection.")
    
    if speed_cameras:
        print("\nSpeed Cameras:")
        for camera_id, address in speed_cameras:
            print(f"   {camera_id} : {address}")
    else:
        print("\nNo speed cameras found at that intersection.")
# find the precentage of violations on a date
def command3(dbConn):
    dbCursor = dbConn.cursor()

    date_input = input("\nEnter the date that you would like to look at (format should be YYYY-MM-DD): ").strip()

    dbCursor.execute("""
        SELECT SUM(Num_Violations)
        FROM RedViolations
        WHERE Violation_Date = ?
        """, (date_input,))
    red_violations = dbCursor.fetchone()[0] or 0
    

    dbCursor.execute("""
        SELECT SUM(Num_Violations)
        FROM SpeedViolations
        WHERE Violation_Date = ?
        """, (date_input,))
    speed_violations = dbCursor.fetchone()[0] or 0
    
    total = red_violations + speed_violations

    if total == 0:
        print("No violations on record for that date.")
        return
    
    red_percent = (red_violations / total) * 100
    speed_percent = (speed_violations / total) * 100

    print(f"Number of Red Light Violations: {red_violations:,} ({red_percent:.3f}%)")
    print(f"Number of Speed Violations: {speed_violations:,} ({speed_percent:.3f}%)")
    print(f"Total Number of Violations: {total:,}")

# Find the number of cameras at an intersection
def command4(dbConn):
    dbCursor = dbConn.cursor()

    dbCursor.execute("""
        SELECT COUNT(*)
        FROM RedCameras
        """)
    total_red = dbCursor.fetchone()[0]

    dbCursor.execute("""
        SELECT COUNT(*)
        FROM SpeedCameras
        """)
    total_speed = dbCursor.fetchone()[0]

    dbCursor.execute("""
        SELECT Intersections.Intersection, Intersections.Intersection_ID, COUNT(RedCameras.Camera_ID)
        FROM Intersections
        JOIN RedCameras ON Intersections.Intersection_ID = RedCameras.Intersection_ID
        GROUP BY Intersections.Intersection_ID
        ORDER BY COUNT(RedCameras.Camera_ID) DESC
        """)
    red_results = dbCursor.fetchall()

    dbCursor.execute("""
        SELECT Intersections.Intersection, Intersections.Intersection_ID, COUNT(SpeedCameras.Camera_ID)
        FROM Intersections
        JOIN SpeedCameras ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
        GROUP BY Intersections.Intersection_ID
        ORDER BY COUNT(SpeedCameras.Camera_ID) DESC
        """)
    speed_results = dbCursor.fetchall()

    print("\nNumber of Red Light Cameras at Each Intersection")
    for intersection, intersection_id, count in red_results:
        percentage = (count / total_red) * 100
        print(f"  {intersection} ({intersection_id}) : {count} ({percentage:.3f}%)")

    print("\nNumber of Speed Cameras at Each Intersection")
    for intersection, intersection_id, count in speed_results:
        percentage = (count / total_speed) * 100
        print(f"  {intersection} ({intersection_id}) : {count} ({percentage:.3f}%)")
# find the number of volations at an intersection in a certain year
def command5(dbConn):
    dbCursor = dbConn.cursor()

    year = input("\nEnter the year that you would like to analyze: ").strip()

    dbCursor.execute("""
        SELECT SUM(Num_Violations)
        FROM RedViolations
        WHERE strftime('%Y', Violation_Date) = ?
    """, (year,))
    total_red = dbCursor.fetchone()[0] or 0

    dbCursor.execute("""
        SELECT SUM(Num_Violations)
        FROM SpeedViolations
        WHERE strftime('%Y', Violation_Date) = ?
    """, (year,))
    total_speed = dbCursor.fetchone()[0] or 0

    dbCursor.execute("""
        SELECT Intersections.Intersection, Intersections.Intersection_ID, SUM(RedViolations.Num_Violations)
        FROM Intersections
        JOIN RedCameras ON Intersections.Intersection_ID = RedCameras.Intersection_ID
        JOIN RedViolations ON RedCameras.Camera_ID = RedViolations.Camera_ID
        WHERE strftime('%Y', RedViolations.Violation_Date) = ?
        GROUP BY Intersections.Intersection_ID
        ORDER BY SUM(RedViolations.Num_Violations) DESC
    """, (year,))
    red_results = dbCursor.fetchall()

    dbCursor.execute("""
        SELECT Intersections.Intersection, Intersections.Intersection_ID, SUM(SpeedViolations.Num_Violations)
        FROM Intersections
        JOIN SpeedCameras ON Intersections.Intersection_ID = SpeedCameras.Intersection_ID
        JOIN SpeedViolations ON SpeedCameras.Camera_ID = SpeedViolations.Camera_ID
        WHERE strftime('%Y', SpeedViolations.Violation_Date) = ?
        GROUP BY Intersections.Intersection_ID
        ORDER BY SUM(SpeedViolations.Num_Violations) DESC
    """, (year,))
    speed_results = dbCursor.fetchall()

    print(f"\nNumber of Red Light Violations at Each Intersection for {year}")
    if not red_results:
        print("No red light violations on record for that year.")
    else:
        for intersection, intersection_id, count in red_results:
            percentage = (count / total_red) * 100
            print(f"  {intersection} ({intersection_id}) : {count:,} ({percentage:.3f}%)")

        print(f"Total Red Light Violations in {year} : {total_red:,}")

    print(f"\nNumber of Speed Violations at Each Intersection for {year}")
    if not speed_results:
        print("No speed violations on record for that year.")
    else:
        for intersection, intersection_id, count in speed_results:
            percentage = (count / total_speed) * 100
            print(f"  {intersection} ({intersection_id}) : {count:,} ({percentage:.3f}%)")

        print(f"Total Speed Violations in {year} : {total_speed:,}")

# find the number of violations by year at a camera id
def command6(dbConn):
    dbCursor = dbConn.cursor()

    camera_id = input("\nEnter a camera ID: ").strip()

    dbCursor.execute("""
        SELECT Camera_ID
        FROM RedCameras
        WHERE Camera_ID = ?
        """,(camera_id,))
    is_red = dbCursor.fetchone() is not None

    dbCursor.execute("""
        SELECT Camera_ID
        FROM SpeedCameras
        WHERE Camera_ID = ?
        """,(camera_id,))
    is_speed = dbCursor.fetchone() is not None

    if not is_red and not is_speed:
        print("No cameras matching that ID were found in the database.\n")
        return
    
    if is_red:
        dbCursor.execute("""
        SELECT strftime('%Y', Violation_Date) AS Year, SUM(Num_Violations)
        FROM RedViolations
        WHERE Camera_ID = ?
        GROUP BY Year
        ORDER BY Year ASC
        """,(camera_id,))
        camera_type = "Red Light"
        color = "red"
    else:
        dbCursor.execute("""
        SELECT strftime('%Y', Violation_Date) AS Year, SUM(Num_Violations)
        FROM SpeedViolations
        WHERE Camera_ID = ?
        GROUP BY Year
        ORDER BY Year ASC
        """,(camera_id,))
        camera_type = "Speed"
        color = "orange"

    violations = dbCursor.fetchall()

    if not violations:
        print(f"No violations found for Camera {camera_id}.")
        return
    
    print(f"Yearly Violations for Camera {camera_id}")
    years = []
    counts = []
    for year, count in violations:
        print(f"{year} : {count:,}")
        years.append(year)
        counts.append(count)

    plot_choice = input("\nPlot? (y/n) \n").strip().lower()
    if plot_choice == 'y':
        plt.figure(figsize=(8, 5))
        plt.plot(years, counts, marker='o', linestyle='-', color=color)
        plt.xlabel("Year")
        plt.ylabel("Number of Violations")
        plt.title(f"Violations by Year for Camera {camera_id}")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.show()

# find the number of violations in a month at a certian camera id and year
def command7(dbConn):
    dbCursor = dbConn.cursor()

    camera_id = input("\nEnter a camera ID: ").strip()

    dbCursor.execute("""
        SELECT Camera_ID 
        FROM RedCameras 
        WHERE Camera_ID = ?
        """, (camera_id,))
    is_red = dbCursor.fetchone() is not None

    dbCursor.execute("""
        SELECT Camera_ID
        FROM SpeedCameras 
        WHERE Camera_ID = ?
        """, (camera_id,))
    is_speed = dbCursor.fetchone() is not None

   
    if not is_red and not is_speed:
        print("No cameras matching that ID were found in the database.\n")
        return

    
    year_input = input("Enter a year: ").strip()

    
    if is_red:
        dbCursor.execute("""
            SELECT strftime('%m', Violation_Date) AS Month, SUM(Num_Violations)
            FROM RedViolations
            WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
            GROUP BY Month
            ORDER BY Month ASC
        """, (camera_id, year_input))
        camera_type = "Red Light"
        color = "red"
    else:  
        dbCursor.execute("""
            SELECT strftime('%m', Violation_Date) AS Month, SUM(Num_Violations)
            FROM SpeedViolations
            WHERE Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
            GROUP BY Month
            ORDER BY Month ASC
        """, (camera_id, year_input))
        camera_type = "Speed"
        color = "orange"

    violations = dbCursor.fetchall()


    
    print(f"Monthly Violations for Camera {camera_id} in {year_input}")
    months = []
    counts = []
    

    for month, count in violations:
        month_year = f"{month}/{year_input}"  
        print(f"{month_year} : {count:,}")
        months.append(month_year)
        counts.append(count)

   
    plot_choice = input("\nPlot? (y/n) \n").strip().lower()
    if plot_choice == 'y':
        plt.figure(figsize=(8, 5))
        plt.plot(months, counts, marker='o', linestyle='-', color=color)
        plt.xlabel("Month/Year")
        plt.ylabel("Number of Violations")
        plt.title(f"Violations by Month for {camera_type} Camera {camera_id} in {year_input}")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.show()

# compare the number of red light to speed camera violations in a given year
def command8(dbConn):
    dbCursor = dbConn.cursor()

    
    year_input = input("\nEnter a year: ").strip()

    dbCursor.execute("""
        SELECT Violation_Date, SUM(Num_Violations)
        FROM RedViolations
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY Violation_Date
        ORDER BY Violation_Date ASC
    """, (year_input,))
    red_violations = dbCursor.fetchall()

    dbCursor.execute("""
        SELECT Violation_Date, SUM(Num_Violations)
        FROM SpeedViolations
        WHERE strftime('%Y', Violation_Date) = ?
        GROUP BY Violation_Date
        ORDER BY Violation_Date ASC
    """, (year_input,))
    speed_violations = dbCursor.fetchall()


    # helper function to help command 8 print easier
    def command_8_print(title, data):
        print(f"{title}:")
        if not data:
            print()
        elif len(data) <= 10:
            for date, count in data:
                print(f"{date} {count:,}")
        else:
            for date, count in data[:5]: 
                print(f"{date} {count}")
            for date, count in data[-5:]:
                print(f"{date} {count}")

    command_8_print("Red Light Violations", red_violations)
    command_8_print("Speed Violations", speed_violations)

    plot_choice = input("\nPlot? (y/n) \n").strip().lower()
    if plot_choice == 'y':
        red_dates, red_counts = zip(*red_violations) if red_violations else ([], [])
        speed_dates, speed_counts = zip(*speed_violations) if speed_violations else ([], [])

        plt.figure(figsize=(10, 5))
        
        if red_dates:
            plt.plot(red_dates, red_counts, marker='o', linestyle='-', color='red', label="Red Light Violations")
        if speed_dates:
            plt.plot(speed_dates, speed_counts, marker='o', linestyle='-', color='orange', label="Speed Violations")

        plt.xlabel("Day")
        plt.ylabel("Number of Violations")
        plt.title(f"Violations Each Day of {year_input}")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.show()

# helper function for command9 in order to fix the decimals under the cap
def fix_coords(v):
    s = f"{float(v):.8f}"      # cap at 8 decimals
    return s.rstrip('0').rstrip('.')

# find all cameras on a given street
def command9(dbConn):
    dbCursor = dbConn.cursor()

    street = input("\nEnter a street name: ").strip()
    
    like = street if ('%' in street or '_' in street) else f"%{street}%"

    dbCursor.execute("""
        SELECT Camera_ID, Address, Latitude, Longitude
        FROM RedCameras
        WHERE Address LIKE ? COLLATE NOCASE
        ORDER BY Camera_ID ASC;
    """, (like,))
    red_cams = dbCursor.fetchall()

    dbCursor.execute("""
        SELECT Camera_ID, Address, Latitude, Longitude
        FROM SpeedCameras
        WHERE Address LIKE ? COLLATE NOCASE
        ORDER BY Camera_ID ASC;
    """, (like,))
    speed_cams = dbCursor.fetchall()

    if not red_cams and not speed_cams:
        print("There are no cameras located on that street.")
        return
    
    print(f"\nList of Cameras Located on Street: {street}")

    print("  Red Light Cameras:")
    if red_cams:
        for cid, addr, lat, lon in red_cams:
            print(f"     {cid} : {addr} ({fix_coords(lat)}, {fix_coords(lon)})")

    print("  Speed Cameras:")
    if speed_cams:
        for cid, addr, lat, lon in speed_cams:
            print(f"     {cid} : {addr} ({fix_coords(lat)}, {fix_coords(lon)})")

    plot_choice = input("\nPlot? (y/n) \n").strip().lower()
    if plot_choice != 'y':
        return
    
    x_red   = [float(lon) for _, _, _, lon in red_cams]
    y_red   = [float(lat) for _, _, lat, _ in red_cams]
    x_speed = [float(lon) for _, _, _, lon in speed_cams]
    y_speed = [float(lat) for _, _, lat, _ in speed_cams]

    plt.figure(figsize=(8, 5))

    # Try to draw the background map first
    try:
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]  # [xmin, xmax, ymin, ymax]
        plt.imshow(image, extent=xydims)
    except Exception:
        # If the image isn't present, still plot the points and frame the axes
        pass

    # Plot with your style: line + markers (red for red light, orange for speed)
    if x_red:
        plt.plot(x_red, y_red, marker='o', linestyle='-', color='red')
        for (cid, _, lat, lon) in red_cams:
            plt.annotate(str(cid), (float(lon), float(lat)))

    if x_speed:
        plt.plot(x_speed, y_speed, marker='o', linestyle='-', color='orange')
        for (cid, _, lat, lon) in speed_cams:
            plt.annotate(str(cid), (float(lon), float(lat)))

    # Match the Chicagoland frame even if the image didn't load
    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(f"Cameras on {street}")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

##################################################################  
#
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')

print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Fall 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()

def choices():
    print("Select a menu option: ")
    print("  1. Find an intersection by name")
    print("  2. Find all cameras at an intersection")
    print("  3. Percentage of violations for a specific date")
    print("  4. Number of cameras at each intersection")
    print("  5. Number of violations at each intersection, given a year")
    print("  6. Number of violations by year, given a camera ID")
    print("  7. Number of violations by month, given a camera ID and year")
    print("  8. Compare the number of red light and speed violations, given a year")
    print("  9. Find cameras located on a street")
    print("or x to exit the program.")

# loop to get the users input which runs to there is an x inputed
while True:
    choices()

    selection = input("Your choice --> ").strip()

    #only way to leave the program
    if selection == "x":
        print("Exiting program.")
        break
    # looks for 1-9 and matched it to the right command
    elif selection == "1":
        command1(dbConn)
    elif selection == "2":
        command2(dbConn)
    elif selection == "3":
        command3(dbConn)
    elif selection == "4":
        command4(dbConn)
    elif selection == "5":
        command5(dbConn)
    elif selection == "6":
        command6(dbConn)
    elif selection == "7":
        command7(dbConn)
    elif selection == "8":
        command8(dbConn)
    elif selection == "9":
        command9(dbConn)
    else:
        print("Error, unknown command, try again...\n") # gives and error if not an x or 1-9 and lets the user try again
#
# done
#