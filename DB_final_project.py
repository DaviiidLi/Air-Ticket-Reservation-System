from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

# Initialize the app from Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='Air_Ticket_Reservation_System',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.config["SECRET_KEY"] = "have a guess"


# Define a route to hello function
@app.route('/')
def home():
    username = session.get('username')
    return render_template('home.html',
                           username=username)


# Define a route to show login function
@app.route('/login')
def login():
    return render_template('login.html')


# Define route for customer register
@app.route('/register_customer')
def c_register():
    return render_template('register_customer.html')


# Define route for booking agent register
@app.route('/register_booking_agent')
def ba_register():
    return render_template('register_booking_agent.html')


# Define route for airline staff register
@app.route('/register_airline_staff')
def as_register():
    all_airline = []
    query_for_airline = "select * from airline"
    cursor = conn.cursor()
    cursor.execute(query_for_airline)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        all_airline.append(each)
    cursor.close()
    return render_template('register_airline_staff.html',
                           all_airline=all_airline)


# Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['uname']
    password = request.form['psw']
    identification = request.form['identification']

    # verify user's identification
    if identification == 'Customer':
        query = 'SELECT * FROM customer WHERE email = %s and password = %s'
    elif identification == 'Booking agent':
        query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s'
    elif identification == 'Airline Staff':
        query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    cursor.execute(query, (username, password))
    # stores the results in a variable
    data = cursor.fetchone()
    if data:
        # creates a session for the the user
        # session is a built in
        session['identification'] = identification
        session['username'] = username

        if identification == 'Airline Staff':
            query_for_permission = 'select permission_type ' \
                                   'from permission ' \
                                   'where username = "{}"'.format(username)
            cursor.execute(query_for_permission)
            session['permission'] = cursor.fetchone()["permission_type"]

        cursor.close()
        return redirect(url_for('home'))
    else:
        # try whether username exists
        and_position = query.find("and")
        query = query[:and_position - 1]
        # executes query
        cursor.execute(query, username)
        # stores the results in a variable
        data = cursor.fetchone()
        # use fetchall() if you are expecting more than 1 data row
        cursor.close()
        # username exists, but password is wrong
        if data:
            # returns an error message to the html page
            error = 'Wrong password'
            return render_template('login.html',
                                   error=error)
        # invalid username
        else:
            # returns an error message to the html page
            if identification == 'Airline Staff':
                error = 'Invalid username'
            else:
                error = 'Invalid email'
            return render_template('login.html',
                                   error=error)


# Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form['uname']
    password = request.form['psw']
    confirmpassword = request.form['confirmpsw']
    identification = request.form['identification']

    # cursor used to send queries
    cursor = conn.cursor()

    # get query based on user type
    if identification == 'Customer':
        page = 'register_customer.html'
        query = 'SELECT * FROM customer WHERE email = %s'
    elif identification == 'Booking agent':
        page = 'register_booking_agent.html'
        query = 'SELECT * FROM booking_agent WHERE email = %s'
    elif identification == 'Airline Staff':
        page = 'register_airline_staff.html'
        query = 'SELECT * FROM airline_staff WHERE username = %s'

    # check password consistency
    if password != confirmpassword:
        error = "Password inconsistent. Please check your password"
        return render_template(page,
                               error=error)

    # executes query
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template(page,
                               error=error)
    else:
        try:
            # get query based on user type
            if identification == 'Customer':
                name = request.form['name']
                building_number = request.form['buildingn']
                street = request.form['street']
                city = request.form['city']
                state = request.form['state']
                phone_number = request.form['phonen']
                passport_number = request.form['passportn']
                passport_expiration = request.form['passporte']
                passport_country = request.form['passportc']
                date_of_birth = request.form['dob']
                query = 'INSERT INTO `customer` (`email`, `name`, `password`, `building_number`,' \
                        ' `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`,' \
                        ' `passport_country`, `date_of_birth`) VALUE ("{}", "{}", "{}", "{}", "{}", "{}",' \
                        ' "{}", {}, "{}", "{}", "{}", "{}")'.format(username, name, password, building_number,
                                                                    street, city, state, phone_number, passport_number,
                                                                    passport_expiration, passport_country, date_of_birth)
                cursor.execute(query)
                conn.commit()
            elif identification == 'Booking agent':
                query_for_booking_agent_id = 'select max(booking_agent_id) ' \
                                             'from booking_agent'
                cursor.execute(query_for_booking_agent_id)
                booking_agent_id = cursor.fetchone()['max(booking_agent_id)'] + 1

                query = 'INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`) ' \
                        'VALUE ("{}", "{}", {})'.format(username, password, booking_agent_id)
                cursor.execute(query)
                conn.commit()
            elif identification == 'Airline Staff':
                first_name = request.form['firstn']
                last_name = request.form['lastn']
                date_of_birth = request.form['dob']
                airline_name = request.form['airlinen']
                query = 'INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`,' \
                        ' `date_of_birth`, `airline_name`) VALUE ("{}", "{}", "{}", "{}", "{}",' \
                        ' "{}")'.format(username, password, first_name, last_name, date_of_birth, airline_name)
                cursor.execute(query)

                query_for__insert_permission = 'insert into `permission` (`username`, `permission_type`) ' \
                                               'value ("{}", "None")'.format(username)
                cursor.execute(query_for__insert_permission)
                conn.commit()

        except:
            error = "Please check your input!"
            return render_template(page,
                                   error=error)

        cursor.close()
        return redirect(url_for('home'))


# search by filter page
@app.route('/search_by_filter', methods=['GET', 'POST'])
def searchbyfilter():
    username = session.get('username')
    identification = session.get('identification')
    source_city = []
    query_for_source_city = "select distinct airport_city from airport"
    cursor = conn.cursor()
    cursor.execute(query_for_source_city)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        source_city.append(each)
    return render_template("search_by_filter.html",
                           source_city=source_city,
                           username = username,
                           identification = identification)


# search by filter result page
@app.route('/search_by_filter_result', methods=['GET', 'POST'])
def searchbyfilterresult():
    username = session.get('username')
    identification = session.get('identification')
    flights_after_search = []
    chosen_source_city = request.form['sourcec']
    chosen_destination_city = request.form['destinationc']
    date = request.form['date']
    selected_departure_airport = request.form.getlist("mycheckbox")
    selected_arrival_airport = request.form.getlist("mycheckbox_1")
    purchase = request.form.getlist("purchase")

    cursor = conn.cursor()

    # get city list
    source_city = []
    query_for_source_city = "select distinct airport_city from airport"
    cursor.execute(query_for_source_city)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        source_city.append(each)

    # get selected departure_airport
    departure_airport = []
    query_for_departure_airport = "select airport_name from airport where airport_city = '{}'".format(
        chosen_source_city)
    cursor.execute(query_for_departure_airport)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        departure_airport.append(each["airport_name"])

    # get selected arrival_airport
    arrival_airport = []
    query_for_arrival_airport = "select airport_name from airport where airport_city = '{}'".format(
        chosen_destination_city)
    cursor.execute(query_for_arrival_airport)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        arrival_airport.append(each["airport_name"])

    # arrival airport is selected
    if selected_arrival_airport != []:
        query_for_selected_arrival_airport = ''
        for each in selected_arrival_airport:
            query_for_selected_arrival_airport += ("'{}', ").format(each)
        query_for_selected_arrival_airport = '(' + query_for_selected_arrival_airport[:-2] + ')'

        # departure airport is selected
        if selected_departure_airport != []:
            query_for_selected_departure_airport = ''
            for each in selected_departure_airport:
                query_for_selected_departure_airport += ("'{}', ").format(each)
            query_for_selected_departure_airport = '(' + query_for_selected_departure_airport[:-2] + ')'
            query_for_flights = "select * from flight " \
                                "where arrival_airport in {} " \
                                "and departure_airport in {}" \
                                "   and departure_time like '{}%' " \
                                "and status = 'upcoming'".format(query_for_selected_arrival_airport,
                                                                          query_for_selected_departure_airport, date)

        # departure airport is not selected
        else:
            query_for_flights = "select * from flight " \
                                "where arrival_airport in {}" \
                                "   and departure_airport in (select airport_name" \
                                "                           from airport" \
                                "                           where airport_city = '{}')" \
                                "   and departure_time like '{}%' " \
                                "   and status = 'upcoming'".format(query_for_selected_arrival_airport,
                                                                          chosen_source_city, date)

    # arrival airport is not selected
    else:

        # departure airport is selected
        if selected_departure_airport != []:
            query_for_selected_departure_airport = ''
            for each in selected_departure_airport:
                query_for_selected_departure_airport += ("'{}', ").format(each)
            query_for_selected_departure_airport = '(' + query_for_selected_departure_airport[:-2] + ')'
            query_for_flights = "select * from flight " \
                                "where departure_airport in {}" \
                                "   and arrival_airport in (select airport_name" \
                                "                           from airport" \
                                "                           where airport_city = '{}')" \
                                "   and departure_time like '{}%' " \
                                "   and status = 'upcoming'".format(query_for_selected_departure_airport,
                                                                          chosen_destination_city, date)

        # departure airport is not selected
        else:
            query_for_flights = "select * from flight " \
                                "where departure_airport in (select airport_name" \
                                "                           from airport" \
                                "                           where airport_city = '{}')" \
                                "   and arrival_airport in (select airport_name" \
                                "                           from airport" \
                                "                           where airport_city = '{}')" \
                                "   and departure_time like '{}%' " \
                                "   and status = 'upcoming'".format(chosen_source_city, chosen_destination_city,
                                                                          date)

    # execute query
    cursor.execute(query_for_flights)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        flights_after_search.append(each)
    cursor.close()
    return render_template("search_by_filter_result.html",
                           date=date,
                           source_city=source_city,
                           chosen_source_city=chosen_source_city,
                           chosen_destination_city=chosen_destination_city,
                           flights_after_search=flights_after_search,
                           departure_airport=departure_airport,
                           arrival_airport=arrival_airport,
                           selected_departure_airport=selected_departure_airport,
                           selected_arrival_airport=selected_arrival_airport,
                           username = username,
                           identification = identification,
                           purchase = purchase)


# search by flight number page
@app.route('/search_by_flight_number', methods=['GET', 'POST'])
def searchbyflightnumber():
    username = session.get('username')
    return render_template("search_by_flight_number.html",
                           username = username)


# function used to process purchase
@app.route('/process_purchase', methods=['GET', 'POST'])
def process_purchase():
    username = session.get('username')
    identification = session.get('identification')
    flight_info = request.form["flightinfo"].split(',')
    airline_name = flight_info[0]
    flight_num = flight_info[1]
    tickets = []

    cursor = conn.cursor()

    query_for_chosen_flight = 'select * ' \
                              'from flight ' \
                              'where airline_name = "{}" and flight_num = "{}"'.format(airline_name, flight_num)
    # execute query
    cursor.execute(query_for_chosen_flight)
    chosen_flight = cursor.fetchone()

    query_for_ticket_id = 'select ticket_id ' \
                          'from ticket ' \
                          'where airline_name = "{}" and flight_num = "{}" ' \
                          'and ticket_id not in (select ticket_id ' \
                          '                     from purchases)'.format(airline_name, flight_num)

    # execute query
    cursor.execute(query_for_ticket_id)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        tickets.append(each)

    if identification == "Customer":
        cursor.close()
        return render_template('purchase_customer.html',
                               username = username,
                               tickets = tickets,
                               chosen_flight = chosen_flight)

    elif identification == "Booking agent":
        error = None
        query_for_booking_agent_airline = 'select airline_name ' \
                                          'from booking_agent_work_for ' \
                                          'where email = "{}"'.format(username)
        # execute query
        cursor.execute(query_for_booking_agent_airline)
        if airline_name != cursor.fetchone()['airline_name']:
            error = "You can not purchase tickets from an airline that you don't work for."

        customers = []
        query_for_customers = 'select email ' \
                              'from customer'
        # execute query
        cursor.execute(query_for_customers)
        while True:
            # fetch each line of data and collect them
            each = cursor.fetchone()
            # get all the data
            if each is None:
                break
            customers.append(each["email"])
        cursor.close()

        return render_template('purchase_booking_agent.html',
                               username = username,
                               tickets = tickets,
                               chosen_flight = chosen_flight,
                               error = error,
                               customers = customers)


# function used to complete purchase
@app.route('/complete_purchase', methods=['GET', 'POST'])
def complete_purchase():
    ticket = request.form["ticket"]
    date = datetime.today().strftime('%Y-%m-%d')
    email = session.get('username')
    identification = session.get('identification')

    cursor = conn.cursor()

    if identification == 'Customer':
        query_for_customer = 'insert into `purchases` (`ticket_id`, `customer_email`, `purchase_date`) values' \
                             '({}, "{}", "{}")'.format(ticket, email, date)

        cursor.execute(query_for_customer)

    elif identification == 'Booking agent':
        customer_email = request.form["customer"]

        query_for_booking_agent_id = 'select booking_agent_id ' \
                                     'from booking_agent ' \
                                     'where email = "{}"'.format(email)
        cursor.execute(query_for_booking_agent_id)
        booking_agent_id = cursor.fetchone()["booking_agent_id"]

        query_for_booking_agent = 'insert into `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, ' \
                                  '`purchase_date`) values ({}, "{}", {}, "{}")'\
                                    .format(ticket, customer_email, booking_agent_id, date)
        cursor.execute(query_for_booking_agent)

    conn.commit()
    cursor.close()
    return redirect(url_for('home'))


# search by flight number result page
@app.route('/search_by_flight_number_result', methods=['GET', 'POST'])
def searchbyflightnumberresult():
    username = session.get('username')
    identification = session.get('identification')
    flights_after_search = []
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']

    cursor = conn.cursor()

    if arrival_date != '':
        query_for_flights = 'select * ' \
                            'from flight ' \
                            'where flight_num = "{}" ' \
                            'and departure_time like "{}%" ' \
                            'and arrival_time like "{}%"'.format(flight_number, departure_date, arrival_date)
    else:
        query_for_flights = 'select * ' \
                            'from flight ' \
                            'where flight_num = "{}" ' \
                            'and departure_time like "{}%"'.format(flight_number, departure_date)

    # execute query
    cursor.execute(query_for_flights)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        flights_after_search.append(each)
    cursor.close()
    return render_template("search_by_flight_number_result.html",
                           flights_after_search=flights_after_search,
                           flight_number=flight_number,
                           departure_date=departure_date,
                           arrival_date=arrival_date,
                           username = username,
                           identification = identification)


# action center my flights function
@app.route('/action_center_my_flights', methods=['GET', 'POST'])
def action_center_my_flights():
    username = session.get('username')
    identification = session.get('identification')
    flights_after_search = []
    fromdate = None
    todate = None

    cursor = conn.cursor()

    # customer identification
    if identification == 'Customer':
        try:
            submit_type = request.form['search']
            status = request.form['status']
            fromdate = request.form['fromdate']
            todate = request.form['todate']
            fromtime = fromdate + ' 00:00:00'
            totime = todate + ' 23:59:59'

            # submit by status
            if submit_type == "submitbystatus":
                fromdate = None
                todate = None

                if status == "upcoming":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and status = "upcoming"'.format(username)
                elif status == "all":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}"'.format(username)
                elif status == "delayed":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and status = "delayed"'.format(username)
                elif status == "completed":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and status = "completed"'.format(username)
                elif status == "in progress":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and status = "in progress"'.format(username)

            # submit by search
            else:
                if status == "upcoming":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and status = "upcoming" ' \
                                        'and departure_time between "{}" and "{}"'.format(username, fromtime, totime)
                elif status == "all":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and departure_time between "{}" and "{}"'\
                                        .format(username, fromtime, totime)
                elif status == "delayed":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and status = "delayed" ' \
                                        'and departure_time between "{}" and "{}"'.format(username, fromtime, totime)
                elif status == "completed":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and status = "completed" ' \
                                        'and departure_time between "{}" and "{}"'.format(username, fromtime, totime)
                elif status == "in progress":
                    query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, status ' \
                                        'from flight natural join purchases natural join ticket ' \
                                        'where customer_email = "{}" and status = "in progress" ' \
                                        'and departure_time between "{}" and "{}"'.format(username, fromtime, totime)

        except:
            status = "upcoming"
            query_for_flights = 'select ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                'departure_time, arrival_airport, arrival_time, price, status ' \
                                'from flight natural join purchases natural join ticket ' \
                                'where customer_email = "{}" and status = "upcoming"'.format(username)

    # booking agent identification
    elif identification == "Booking agent":
        try:
            submit_type = request.form['search']
            status = request.form['status']
            fromdate = request.form['fromdate']
            todate = request.form['todate']
            fromtime = fromdate + ' 00:00:00'
            totime = todate + ' 23:59:59'

            # submit by status
            if submit_type == "submitbystatus":
                fromdate = None
                todate = None

                if status == "upcoming":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and status = "upcoming"'.format(username)
                elif status == "all":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}"'.format(username)
                elif status == "delayed":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and status = "delayed"'.format(username)
                elif status == "completed":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and status = "completed"'.format(username)
                elif status == "in progress":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and status = "in progress"'.format(username)

            # submit by search
            else:
                if status == "upcoming":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and status = "upcoming" ' \
                                        'and departure_time between "{}" and "{}"'.format(username, fromtime, totime)
                elif status == "all":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and departure_time between "{}" and "{}"' \
                                        .format(username, fromtime, totime)
                elif status == "delayed":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and status = "delayed" ' \
                                        'and departure_time between "{}" and "{}"'.format(username, fromtime, totime)
                if status == "completed":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and status = "completed" ' \
                                        'and departure_time between "{}" and "{}"'.format(username, fromtime, totime)
                if status == "in progress":
                    query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                        'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                        'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                        'where email = "{}" and status = "in progress" ' \
                                        'and departure_time between "{}" and "{}"'.format(username, fromtime, totime)

        except:
            status = "upcoming"
            query_for_flights = 'select customer_email, ticket_id, purchase_date, airline_name, flight_num, airplane_id, departure_airport, ' \
                                'departure_time, arrival_airport, arrival_time, price, price*0.1 as commission, status ' \
                                'from flight natural join purchases natural join ticket natural join booking_agent ' \
                                'where email = "{}" and status = "upcoming"'.format(username)

    # airline staff identification
    elif identification == "Airline Staff":
        permission = session.get('permission')
        chosen_source_city = None
        chosen_destination_city = None
        selected_departure_airport = None
        selected_arrival_airport = None
        departure_airport = None
        arrival_airport = None
        error = None
        status = 'upcoming'

        # default date range
        fromdate = datetime.now().strftime("%Y-%m-%d")
        todate = (datetime.now().date() + relativedelta(days=30)).strftime("%Y-%m-%d")
        fromtime = fromdate + ' 00:00:00'
        totime = todate + ' 23:59:59'

        # get city list
        source_city = []
        query_for_source_city = "select distinct airport_city from airport"
        cursor.execute(query_for_source_city)
        while True:
            # fetch each line of data and collect them
            each = cursor.fetchone()
            # get all the data
            if each is None:
                break
            source_city.append(each)

        # get airline working for
        query_for_airline_working_for = 'select airline_name ' \
                                        'from airline_staff ' \
                                        'where username = "{}"'.format(username)
        cursor.execute(query_for_airline_working_for)
        airline_working_for = cursor.fetchone()["airline_name"]

        try:
            status = request.form['status']
            chosen_source_city = request.form['sourcec']
            chosen_destination_city = request.form['destinationc']
            fromdate = request.form['fromdate']
            todate = request.form['todate']
            selected_departure_airport = request.form.getlist("mycheckbox")
            selected_arrival_airport = request.form.getlist("mycheckbox_1")
            fromtime = fromdate + ' 00:00:00'
            totime = todate + ' 23:59:59'

            if (chosen_source_city != '' and chosen_destination_city == '') or (chosen_source_city == '' and chosen_destination_city != ''):
                error = "Choose source city and destination city at the same time or not."
                query_for_flights = 'select * ' \
                                    'from flight ' \
                                    'where airline_name = "{}" ' \
                                    'and departure_time between "{}" and "{}"' \
                    .format(airline_working_for, fromtime, totime)

            elif chosen_source_city == '' and chosen_destination_city == '':
                if status == "upcoming":
                    query_for_flights = "select * from flight " \
                                        "where departure_time between '{}' and '{}' " \
                                        "and airline_name = '{}' and status = 'upcoming'"\
                                        .format(fromtime, totime, airline_working_for)
                elif status == "all":
                    query_for_flights = "select * from flight " \
                                        "where departure_time between '{}' and '{}' " \
                                        "and airline_name = '{}'" \
                        .format(fromtime, totime, airline_working_for)
                elif status == "delayed":
                    query_for_flights = "select * from flight " \
                                        "where departure_time between '{}' and '{}' " \
                                        "and airline_name = '{}' and status = 'delayed'" \
                        .format(fromtime, totime, airline_working_for)
                elif status == "completed":
                    query_for_flights = "select * from flight " \
                                        "where departure_time between '{}' and '{}' " \
                                        "and airline_name = '{}' and status = 'completed'" \
                        .format(fromtime, totime, airline_working_for)
                elif status == "in progress":
                    query_for_flights = "select * from flight " \
                                        "where departure_time between '{}' and '{}' " \
                                        "and airline_name = '{}' and status = 'in progress'" \
                        .format(fromtime, totime, airline_working_for)

            else:
                # get selected departure_airport
                departure_airport = []
                query_for_departure_airport = "select airport_name from airport where airport_city = '{}'".format(
                    chosen_source_city)
                cursor.execute(query_for_departure_airport)
                while True:
                    # fetch each line of data and collect them
                    each = cursor.fetchone()
                    # get all the data
                    if each is None:
                        break
                    departure_airport.append(each["airport_name"])

                # get selected arrival_airport
                arrival_airport = []
                query_for_arrival_airport = "select airport_name from airport where airport_city = '{}'".format(
                    chosen_destination_city)
                cursor.execute(query_for_arrival_airport)
                while True:
                    # fetch each line of data and collect them
                    each = cursor.fetchone()
                    # get all the data
                    if each is None:
                        break
                    arrival_airport.append(each["airport_name"])

                # arrival airport is selected
                if selected_arrival_airport != []:
                    query_for_selected_arrival_airport = ''
                    for each in selected_arrival_airport:
                        query_for_selected_arrival_airport += ("'{}', ").format(each)
                    query_for_selected_arrival_airport = '(' + query_for_selected_arrival_airport[:-2] + ')'

                    # departure airport is selected
                    if selected_departure_airport != []:
                        query_for_selected_departure_airport = ''
                        for each in selected_departure_airport:
                            query_for_selected_departure_airport += ("'{}', ").format(each)
                        query_for_selected_departure_airport = '(' + query_for_selected_departure_airport[:-2] + ')'

                        if status == "upcoming":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {} " \
                                                "and departure_airport in {}" \
                                                "and departure_time between '{}' and '{}' " \
                                                "and airline_name = '{}' and status = 'upcoming'".format(query_for_selected_arrival_airport,
                                                                                          query_for_selected_departure_airport,
                                                                                          fromtime, totime, airline_working_for)
                        elif status == "all":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {} " \
                                                "and departure_airport in {}" \
                                                "and departure_time between '{}' and '{}' " \
                                                "and airline_name = '{}'".format(
                                query_for_selected_arrival_airport,
                                query_for_selected_departure_airport,
                                fromtime, totime, airline_working_for)
                        elif status == "delayed":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {} " \
                                                "and departure_airport in {}" \
                                                "and departure_time between '{}' and '{}' " \
                                                "and airline_name = '{}' and status = 'delayed'".format(
                                query_for_selected_arrival_airport,
                                query_for_selected_departure_airport,
                                fromtime, totime, airline_working_for)
                        elif status == "completed":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {} " \
                                                "and departure_airport in {}" \
                                                "and departure_time between '{}' and '{}' " \
                                                "and airline_name = '{}' and status = 'completed'".format(
                                query_for_selected_arrival_airport,
                                query_for_selected_departure_airport,
                                fromtime, totime, airline_working_for)
                        elif status == "in progress":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {} " \
                                                "and departure_airport in {}" \
                                                "and departure_time between '{}' and '{}' " \
                                                "and airline_name = '{}' and status = 'in progress'".format(
                                query_for_selected_arrival_airport,
                                query_for_selected_departure_airport,
                                fromtime, totime, airline_working_for)

                    # departure airport is not selected
                    else:
                        if status == "upcoming":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {}" \
                                                "   and departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'upcoming'".format(query_for_selected_arrival_airport,
                                                                                          chosen_source_city, fromtime, totime, airline_working_for)
                        elif status == "all":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {}" \
                                                "   and departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}'".format(
                                query_for_selected_arrival_airport,
                                chosen_source_city, fromtime, totime, airline_working_for)
                        elif status == "delayed":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {}" \
                                                "   and departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'delayed'".format(
                                query_for_selected_arrival_airport,
                                chosen_source_city, fromtime, totime, airline_working_for)
                        elif status == "completed":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {}" \
                                                "   and departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'completed'".format(
                                query_for_selected_arrival_airport,
                                chosen_source_city, fromtime, totime, airline_working_for)
                        elif status == "in progress":
                            query_for_flights = "select * from flight " \
                                                "where arrival_airport in {}" \
                                                "   and departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'in progress'".format(
                                query_for_selected_arrival_airport,
                                chosen_source_city, fromtime, totime, airline_working_for)

                # arrival airport is not selected
                else:

                    # departure airport is selected
                    if selected_departure_airport != []:
                        query_for_selected_departure_airport = ''
                        for each in selected_departure_airport:
                            query_for_selected_departure_airport += ("'{}', ").format(each)
                        query_for_selected_departure_airport = '(' + query_for_selected_departure_airport[:-2] + ')'

                        if status == "upcoming":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in {}" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'upcoming'".format(query_for_selected_departure_airport,
                                                                                          chosen_destination_city, fromtime, totime, airline_working_for)
                        elif status == "all":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in {}" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}'".format(query_for_selected_departure_airport,
                                                chosen_destination_city, fromtime, totime, airline_working_for)
                        elif status == "delayed":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in {}" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'delayed'".format(
                                query_for_selected_departure_airport,
                                chosen_destination_city, fromtime, totime, airline_working_for)
                        elif status == "completed":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in {}" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'completed'".format(
                                query_for_selected_departure_airport,
                                chosen_destination_city, fromtime, totime, airline_working_for)
                        elif status == "in progress":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in {}" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'in progress'".format(
                                query_for_selected_departure_airport,
                                chosen_destination_city, fromtime, totime, airline_working_for)

                    # departure airport is not selected
                    else:
                        if status == "upcoming":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'upcoming'".format(chosen_source_city,
                                                                                          chosen_destination_city,
                                                                                          fromtime, totime, airline_working_for)
                        elif status == "all":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}'".format(
                                chosen_source_city,
                                chosen_destination_city,
                                fromtime, totime, airline_working_for)
                        elif status == "delayed":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'delayed'".format(
                                chosen_source_city,
                                chosen_destination_city,
                                fromtime, totime, airline_working_for)
                        elif status == "completed":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'completed'".format(
                                chosen_source_city,
                                chosen_destination_city,
                                fromtime, totime, airline_working_for)
                        elif status == "in progress":
                            query_for_flights = "select * from flight " \
                                                "where departure_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and arrival_airport in (select airport_name" \
                                                "                           from airport" \
                                                "                           where airport_city = '{}')" \
                                                "   and departure_time between '{}' and '{}' " \
                                                "   and airline_name = '{}' and status = 'in progress'".format(
                                chosen_source_city,
                                chosen_destination_city,
                                fromtime, totime, airline_working_for)

        except:
            try:
                fromdate = request.form['fromdate']
                todate = request.form['todate']
                fromtime = fromdate + ' 00:00:00'
                totime = todate + ' 23:59:59'

            finally:
                query_for_flights = 'select * ' \
                                    'from flight ' \
                                    'where airline_name = "{}" ' \
                                    'and departure_time between "{}" and "{}"'\
                                    .format(airline_working_for, fromtime, totime)

        finally:
            # execute query
            cursor.execute(query_for_flights)
            while True:
                # fetch each line of data and collect them
                each = cursor.fetchone()
                # get all the data
                if each is None:
                    break
                flights_after_search.append(each)
            cursor.close()
            return render_template("action_center_my_flights.html",
                                   fromdate=fromdate,
                                   todate=todate,
                                   source_city=source_city,
                                   chosen_source_city=chosen_source_city,
                                   chosen_destination_city=chosen_destination_city,
                                   flights_after_search=flights_after_search,
                                   departure_airport=departure_airport,
                                   arrival_airport=arrival_airport,
                                   selected_departure_airport=selected_departure_airport,
                                   selected_arrival_airport=selected_arrival_airport,
                                   username=username,
                                   identification=identification,
                                   status=status,
                                   permission=permission,
                                   error=error)

    # execute query
    cursor.execute(query_for_flights)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        flights_after_search.append(each)
    cursor.close()
    return render_template('action_center_my_flights.html',
                           username=username,
                           identification = identification,
                           flights_after_search = flights_after_search,
                           status = status,
                           fromdate = fromdate,
                           todate = todate)


# action center track my spending function
@app.route('/action_center_track_my_spending', methods=['GET', 'POST'])
def action_center_track_my_spending():
    username = session.get('username')
    identification = session.get('identification')
    month_format = [None, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    months = []
    money = []

    try:
        # selected month range
        fromdate = request.form['frommonth']
        strfromdate = request.form['frommonth'].split('-')
        intfromdate = [int(each) for each in strfromdate]
        fromyear = intfromdate[0]
        frommonth = intfromdate[1]

        todate = request.form['tomonth']
        strtodate = request.form['tomonth'].split('-')
        inttodate = [int(each) for each in strtodate]
        toyear = inttodate[0]
        tomonth = inttodate[1]

        if fromyear > toyear or fromyear == toyear and frommonth > tomonth:
            error = 'Error! To Date exceeds From Date.'
            return render_template('action_center_track_my_spending.html',
                           username = username,
                           identification = identification,
                           error = error,
                           fromdate = fromdate,
                           todate = todate)

        while fromyear != toyear or frommonth != tomonth:
            temp = []
            temp.append(str(fromyear))
            temp.append(month_format[frommonth])
            months.append('-'.join(temp))

            if frommonth + 1 > 12:
                frommonth = 1
                fromyear += 1
            else:
                frommonth += 1
        temp = []
        temp.append(str(toyear))
        temp.append(month_format[tomonth])
        months.append('-'.join(temp))

    except:
        # default month range
        todate = datetime.today().strftime('%Y-%m')
        strdate = todate.split('-')
        intdate = [int(each) for each in strdate]
        toyear = intdate[0]
        tomonth = intdate[1]

        for i in range(6):
            temp = []
            if tomonth - i >= 1:
                temp.append(str(toyear))
                temp.append(month_format[tomonth - i])
            else:
                temp.append(str(toyear - 1))
                temp.append(month_format[12 - (i - tomonth)])
            months.append('-'.join(temp))

        months = months[::-1]

        fromdate = months[0]
    finally:
        cursor = conn.cursor()

        for month in months:
            query = 'select sum(price) ' \
                    'from flight natural join purchases natural join ticket ' \
                    'where customer_email = "{}" and purchase_date like "{}%"'.format(username, month)
            # execute query
            cursor.execute(query)
            each = cursor.fetchone()['sum(price)']
            if each is None:
                money.append(0)
            else:
                money.append(each)

        cursor.close()
    return render_template('action_center_track_my_spending.html',
                           username = username,
                           identification = identification,
                           months = months,
                           money = money,
                           fromdate = fromdate,
                           todate = todate)


# action center view my commission function
@app.route('/action_center_view_my_commission', methods=['GET', 'POST'])
def action_center_view_my_commission():
    username = session.get('username')
    identification = session.get('identification')

    cursor = conn.cursor()

    query_for_booking_agent_id = 'select booking_agent_id ' \
                                 'from booking_agent ' \
                                 'where email = "{}"'.format(username)
    cursor.execute(query_for_booking_agent_id)
    booking_agent_id = cursor.fetchone()["booking_agent_id"]

    try:
        # selected date range
        fromdate = request.form['fromdate']
        todate = request.form['todate']

        try:
            pd.date_range(fromdate, todate, freq='D')[0]

        except:
            error = 'Error! To Date exceeds From Date.'
            return render_template('action_center_view_my_commission.html',
                                   username=username,
                                   identification=identification,
                                   error=error,
                                   fromdate=fromdate,
                                   todate=todate)

    except:
        # default date range
        todate = str(datetime.today()).split(' ')[0]
        fromdate = str(datetime.today() - timedelta(days=30)).split(' ')[0]

    finally:
        query_for_total_commission = 'select sum(0.1 * price) as commission ' \
                'from flight natural join purchases natural join ticket ' \
                'where booking_agent_id = "{}" and purchase_date between "{}" and "{}"'.format(booking_agent_id, fromdate, todate)

        query_for_total_tickets = 'select count(ticket_id) as ticket_num ' \
                                  'from flight natural join purchases natural join ticket ' \
                                  'where booking_agent_id = "{}" and purchase_date between "{}" and "{}"'.format(booking_agent_id, fromdate, todate)

        # execute query
        cursor.execute(query_for_total_tickets)
        ticket_num = cursor.fetchone()['ticket_num']

        # execute query
        cursor.execute(query_for_total_commission)
        each = cursor.fetchone()['commission']
        if each is None:
            total_commission = 0
            avg_commission = 0
        else:
            total_commission = each
            avg_commission = round(total_commission / ticket_num, 2)

        cursor.close()
    return render_template('action_center_view_my_commission.html',
                           username = username,
                           identification = identification,
                           total_commission = total_commission,
                           avg_commission = avg_commission,
                           ticket_num = ticket_num,
                           fromdate = fromdate,
                           todate = todate)


# action center view top customers function
@app.route('/action_center_view_top_customers', methods=['GET', 'POST'])
def action_center_view_top_customers():
    username = session.get('username')
    identification = session.get('identification')
    top_5_customer_email_by_ticket = []
    top_5_customer_email_by_commission = []
    num_of_tickets = []
    amount_of_commission = []

    cursor = conn.cursor()

    query_for_booking_agent_id = 'select booking_agent_id ' \
                                 'from booking_agent ' \
                                 'where email = "{}"'.format(username)
    cursor.execute(query_for_booking_agent_id)
    booking_agent_id = cursor.fetchone()["booking_agent_id"]

    # date range
    todate = datetime.now().strftime("%Y-%m-%d")
    fromdate_for_ticket = (datetime.now().date() - relativedelta(months=6)).strftime("%Y-%m-%d")
    fromdate_for_commission = (datetime.now().date() - relativedelta(years=1)).strftime("%Y-%m-%d")

    query_for_customer_email_by_ticket = 'select customer_email, count(ticket_id) ' \
                                         'from purchases ' \
                                         'where booking_agent_id = "{}" ' \
                                         '  and purchase_date between "{}" and "{}" ' \
                                         'group by customer_email ' \
                                         'order by count(ticket_id) desc limit 5'\
                                         .format(booking_agent_id, fromdate_for_ticket, todate)

    # execute query
    cursor.execute(query_for_customer_email_by_ticket)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        top_5_customer_email_by_ticket.append(each['customer_email'])
        num_of_tickets.append(each['count(ticket_id)'])

    query_for_customer_email_by_commission = 'select customer_email, sum(0.1 * price)' \
                                             'from purchases natural join ticket natural join flight ' \
                                             'where booking_agent_id = "{}" ' \
                                             '  and purchase_date between "{}" and "{}" ' \
                                             'group by customer_email ' \
                                             'order by sum(0.1 * price) desc limit 5'\
                                             .format(booking_agent_id, fromdate_for_commission, todate)

    # execute query
    cursor.execute(query_for_customer_email_by_commission)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        top_5_customer_email_by_commission.append(each['customer_email'])
        amount_of_commission.append(each['sum(0.1 * price)'])

    cursor.close()
    return render_template('action_center_view_top_customers.html',
                           username = username,
                           identification = identification,
                           top_5_customer_email_by_ticket = top_5_customer_email_by_ticket,
                           num_of_tickets = num_of_tickets,
                           top_5_customer_email_by_commission = top_5_customer_email_by_commission,
                           amount_of_commission = amount_of_commission)


# action center view customers of a flight function
@app.route('/action_center_my_flights_view_customers', methods=['GET', 'POST'])
def action_center_my_flights_view_customers():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    flight_info = request.form["flightinfo"].split(',')
    airline_name = flight_info[0]
    flight_num = flight_info[1]
    customers_info = []

    cursor = conn.cursor()

    query_for_chosen_flight = 'select * ' \
                              'from flight ' \
                              'where airline_name = "{}" and flight_num = "{}"'.format(airline_name, flight_num)
    # execute query
    cursor.execute(query_for_chosen_flight)
    chosen_flight = cursor.fetchone()

    query_for_customers = 'select customer_email, ticket_id, booking_agent_id, purchase_date ' \
                          'from purchases natural join ticket ' \
                          'where airline_name = "{}" and flight_num = "{}"'.format(airline_name, flight_num)
    # execute query
    cursor.execute(query_for_customers)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        customers_info.append(each)

    cursor.close()
    return render_template('action_center_my_flights_view_customers.html',
                           username = username,
                           identification = identification,
                           permission = permission,
                           chosen_flight = chosen_flight,
                           customers_info = customers_info)


# action center view customers of a flight function
@app.route('/action_center_create_new_flights', methods=['GET', 'POST'])
def action_center_create_new_flights():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    airport_list = []
    error = None
    succeed = None
    flight_num = None
    departure_airport = None
    departure_time = None
    arrival_airport = None
    arrival_time = None
    price = None
    airplane_id = None

    cursor = conn.cursor()

    # get airline name
    query_for_airline_name = 'select airline_name from airline_staff where username = "{}"'.format(username)
    cursor.execute(query_for_airline_name)
    airline_name = cursor.fetchone()["airline_name"]

    # get airport list
    query_for_airport_list = 'select airport_name from airport'
    # execute query
    cursor.execute(query_for_airport_list)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        airport_list.append(each)

    # get airplane_id list
    airplane_id_list = []
    query_for_airplane_id_list = 'select airplane_id from airplane where airline_name = "{}"'.format(airline_name)
    # execute query
    cursor.execute(query_for_airplane_id_list)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        airplane_id_list.append(each)

    try:
        flight_num = request.form['flight_num']
        airplane_id = request.form['airplane_id']
        departure_time = request.form['departure_time']
        departure_time = ' '.join(departure_time.split('T'))
        departure_time += ':00'
        departure_airport = request.form['departure_airport']
        arrival_airport = request.form['arrival_airport']
        arrival_time = request.form['arrival_time']
        arrival_time = ' '.join(arrival_time.split('T'))
        arrival_time += ':00'
        price = request.form['price']
        existed_flight_num = []

        # get existed flight num
        query_for_existed_flight_num = 'select flight_num ' \
                                       'from flight ' \
                                       'where airline_name = "{}"'.format(airline_name)
        # execute query
        cursor.execute(query_for_existed_flight_num)
        while True:
            # fetch each line of data and collect them
            each = cursor.fetchone()
            # get all the data
            if each is None:
                break
            existed_flight_num.append(str(each['flight_num']))

        timenow = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        if departure_time < timenow:
            error = "Can't choose a past time!"
        elif departure_time > arrival_time:
            error = "Departure time cannot exceed arrival time!"
        elif flight_num in existed_flight_num:
            error = "Flight number already exists!"
        else:
            try:
                query_for_new_flight = 'INSERT INTO `flight` (`airline_name`, `flight_num`, `departure_airport`, ' \
                                       '`departure_time`, `arrival_airport`, `arrival_time`, `price`, `status`, ' \
                                       '`airplane_id`) VALUES ("{}", {}, "{}", "{}", "{}", "{}", {}, "upcoming", {})'\
                                        .format(airline_name, flight_num, departure_airport, departure_time, arrival_airport,
                                                arrival_time, price, airplane_id)
                cursor.execute(query_for_new_flight)
                conn.commit()
                succeed = 'Successfully created!'
            except:
                error = 'Please check your input!'

    finally:
        cursor.close()
        return render_template('action_center_create_new_flights.html',
                               username=username,
                               identification=identification,
                               permission=permission,
                               error = error,
                               succeed = succeed,
                               flight_num = flight_num,
                               departure_airport = departure_airport,
                               departure_time = departure_time,
                               arrival_airport = arrival_airport,
                               arrival_time = arrival_time,
                               price = price,
                               airplane_id = airplane_id,
                               airplane_id_list = airplane_id_list,
                               airport_list = airport_list)


# action center change status of flights function
@app.route('/action_center_change_status_of_flights', methods=['GET', 'POST'])
def action_center_change_status_of_flights():
    username = session.get('username')
    identification = session.get('identification')
    flights_after_search = []

    cursor = conn.cursor()

    permission = session.get('permission')
    chosen_source_city = None
    chosen_destination_city = None
    selected_departure_airport = None
    selected_arrival_airport = None
    departure_airport = None
    arrival_airport = None
    error = None
    change_error = None
    status_for_change_submit = "No"
    status = 'upcoming'

    # default date range
    fromdate = datetime.now().strftime("%Y-%m-%d")
    todate = (datetime.now().date() + relativedelta(days=30)).strftime("%Y-%m-%d")
    fromtime = fromdate + ' 00:00:00'
    totime = todate + ' 23:59:59'

    # get city list
    source_city = []
    query_for_source_city = "select distinct airport_city from airport"
    cursor.execute(query_for_source_city)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        source_city.append(each)

    # get airline working for
    query_for_airline_working_for = 'select airline_name ' \
                                    'from airline_staff ' \
                                    'where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    try:
        status = request.form['status']
        chosen_source_city = request.form['sourcec']
        chosen_destination_city = request.form['destinationc']
        fromdate = request.form['fromdate']
        todate = request.form['todate']
        selected_departure_airport = request.form.getlist("mycheckbox")
        selected_arrival_airport = request.form.getlist("mycheckbox_1")
        fromtime = fromdate + ' 00:00:00'
        totime = todate + ' 23:59:59'

        if (chosen_source_city != '' and chosen_destination_city == '') or (
                chosen_source_city == '' and chosen_destination_city != ''):
            error = "Choose source city and destination city at the same time or not."
            query_for_flights = 'select * ' \
                                'from flight ' \
                                'where airline_name = "{}" ' \
                                'and departure_time between "{}" and "{}"' \
                .format(airline_working_for, fromtime, totime)

        elif chosen_source_city == '' and chosen_destination_city == '':
            if status == "upcoming":
                query_for_flights = "select * from flight " \
                                    "where departure_time between '{}' and '{}' " \
                                    "and airline_name = '{}' and status = 'upcoming'" \
                    .format(fromtime, totime, airline_working_for)
            elif status == "all":
                query_for_flights = "select * from flight " \
                                    "where departure_time between '{}' and '{}' " \
                                    "and airline_name = '{}'" \
                    .format(fromtime, totime, airline_working_for)
            elif status == "delayed":
                query_for_flights = "select * from flight " \
                                    "where departure_time between '{}' and '{}' " \
                                    "and airline_name = '{}' and status = 'delayed'" \
                    .format(fromtime, totime, airline_working_for)
            elif status == "completed":
                query_for_flights = "select * from flight " \
                                    "where departure_time between '{}' and '{}' " \
                                    "and airline_name = '{}' and status = 'completed'" \
                    .format(fromtime, totime, airline_working_for)
            elif status == "in progress":
                query_for_flights = "select * from flight " \
                                    "where departure_time between '{}' and '{}' " \
                                    "and airline_name = '{}' and status = 'in progress'" \
                    .format(fromtime, totime, airline_working_for)

        else:
            # get selected departure_airport
            departure_airport = []
            query_for_departure_airport = "select airport_name from airport where airport_city = '{}'".format(
                chosen_source_city)
            cursor.execute(query_for_departure_airport)
            while True:
                # fetch each line of data and collect them
                each = cursor.fetchone()
                # get all the data
                if each is None:
                    break
                departure_airport.append(each["airport_name"])

            # get selected arrival_airport
            arrival_airport = []
            query_for_arrival_airport = "select airport_name from airport where airport_city = '{}'".format(
                chosen_destination_city)
            cursor.execute(query_for_arrival_airport)
            while True:
                # fetch each line of data and collect them
                each = cursor.fetchone()
                # get all the data
                if each is None:
                    break
                arrival_airport.append(each["airport_name"])

            # arrival airport is selected
            if selected_arrival_airport != []:
                query_for_selected_arrival_airport = ''
                for each in selected_arrival_airport:
                    query_for_selected_arrival_airport += ("'{}', ").format(each)
                query_for_selected_arrival_airport = '(' + query_for_selected_arrival_airport[:-2] + ')'

                # departure airport is selected
                if selected_departure_airport != []:
                    query_for_selected_departure_airport = ''
                    for each in selected_departure_airport:
                        query_for_selected_departure_airport += ("'{}', ").format(each)
                    query_for_selected_departure_airport = '(' + query_for_selected_departure_airport[:-2] + ')'

                    if status == "upcoming":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {} " \
                                            "and departure_airport in {}" \
                                            "and departure_time between '{}' and '{}' " \
                                            "and airline_name = '{}' and status = 'upcoming'".format(
                            query_for_selected_arrival_airport,
                            query_for_selected_departure_airport,
                            fromtime, totime, airline_working_for)
                    elif status == "all":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {} " \
                                            "and departure_airport in {}" \
                                            "and departure_time between '{}' and '{}' " \
                                            "and airline_name = '{}'".format(
                            query_for_selected_arrival_airport,
                            query_for_selected_departure_airport,
                            fromtime, totime, airline_working_for)
                    elif status == "delayed":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {} " \
                                            "and departure_airport in {}" \
                                            "and departure_time between '{}' and '{}' " \
                                            "and airline_name = '{}' and status = 'delayed'".format(
                            query_for_selected_arrival_airport,
                            query_for_selected_departure_airport,
                            fromtime, totime, airline_working_for)
                    elif status == "completed":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {} " \
                                            "and departure_airport in {}" \
                                            "and departure_time between '{}' and '{}' " \
                                            "and airline_name = '{}' and status = 'completed'".format(
                            query_for_selected_arrival_airport,
                            query_for_selected_departure_airport,
                            fromtime, totime, airline_working_for)
                    elif status == "in progress":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {} " \
                                            "and departure_airport in {}" \
                                            "and departure_time between '{}' and '{}' " \
                                            "and airline_name = '{}' and status = 'in progress'".format(
                            query_for_selected_arrival_airport,
                            query_for_selected_departure_airport,
                            fromtime, totime, airline_working_for)

                # departure airport is not selected
                else:
                    if status == "upcoming":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {}" \
                                            "   and departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'upcoming'".format(
                            query_for_selected_arrival_airport,
                            chosen_source_city, fromtime, totime, airline_working_for)
                    elif status == "all":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {}" \
                                            "   and departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}'".format(
                            query_for_selected_arrival_airport,
                            chosen_source_city, fromtime, totime, airline_working_for)
                    elif status == "delayed":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {}" \
                                            "   and departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'delayed'".format(
                            query_for_selected_arrival_airport,
                            chosen_source_city, fromtime, totime, airline_working_for)
                    elif status == "completed":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {}" \
                                            "   and departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'completed'".format(
                            query_for_selected_arrival_airport,
                            chosen_source_city, fromtime, totime, airline_working_for)
                    elif status == "in progress":
                        query_for_flights = "select * from flight " \
                                            "where arrival_airport in {}" \
                                            "   and departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'in progress'".format(
                            query_for_selected_arrival_airport,
                            chosen_source_city, fromtime, totime, airline_working_for)

            # arrival airport is not selected
            else:

                # departure airport is selected
                if selected_departure_airport != []:
                    query_for_selected_departure_airport = ''
                    for each in selected_departure_airport:
                        query_for_selected_departure_airport += ("'{}', ").format(each)
                    query_for_selected_departure_airport = '(' + query_for_selected_departure_airport[:-2] + ')'

                    if status == "upcoming":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in {}" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'upcoming'".format(
                            query_for_selected_departure_airport,
                            chosen_destination_city, fromtime, totime, airline_working_for)
                    elif status == "all":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in {}" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}'".format(query_for_selected_departure_airport,
                                                                                chosen_destination_city, fromtime,
                                                                                totime, airline_working_for)
                    elif status == "delayed":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in {}" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'delayed'".format(
                            query_for_selected_departure_airport,
                            chosen_destination_city, fromtime, totime, airline_working_for)
                    elif status == "completed":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in {}" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'completed'".format(
                            query_for_selected_departure_airport,
                            chosen_destination_city, fromtime, totime, airline_working_for)
                    elif status == "in progress":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in {}" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'in progress'".format(
                            query_for_selected_departure_airport,
                            chosen_destination_city, fromtime, totime, airline_working_for)

                # departure airport is not selected
                else:
                    if status == "upcoming":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'upcoming'".format(
                            chosen_source_city,
                            chosen_destination_city,
                            fromtime, totime, airline_working_for)
                    elif status == "all":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}'".format(
                            chosen_source_city,
                            chosen_destination_city,
                            fromtime, totime, airline_working_for)
                    elif status == "delayed":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'delayed'".format(
                            chosen_source_city,
                            chosen_destination_city,
                            fromtime, totime, airline_working_for)
                    elif status == "completed":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'completed'".format(
                            chosen_source_city,
                            chosen_destination_city,
                            fromtime, totime, airline_working_for)
                    elif status == "in progress":
                        query_for_flights = "select * from flight " \
                                            "where departure_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and arrival_airport in (select airport_name" \
                                            "                           from airport" \
                                            "                           where airport_city = '{}')" \
                                            "   and departure_time between '{}' and '{}' " \
                                            "   and airline_name = '{}' and status = 'in progress'".format(
                            chosen_source_city,
                            chosen_destination_city,
                            fromtime, totime, airline_working_for)

    except:
        try:
            fromdate = request.form['fromdate']
            todate = request.form['todate']
            fromtime = fromdate + ' 00:00:00'
            totime = todate + ' 23:59:59'

        finally:
            query_for_flights = 'select * ' \
                                'from flight ' \
                                'where airline_name = "{}" ' \
                                'and departure_time between "{}" and "{}"' \
                .format(airline_working_for, fromtime, totime)

    finally:
        # execute query
        cursor.execute(query_for_flights)
        while True:
            # fetch each line of data and collect them
            each = cursor.fetchone()
            # get all the data
            if each is None:
                break
            flights_after_search.append(each)

        try:
            flight_info = request.form['viewinfo']
            flight_into = flight_info.split(',')
            chosen_airline = flight_into[0]
            chosen_flight_num = flight_into[1]
            chosen_status = flight_into[2]
            status_for_change = request.form['status_for_change']
            status_for_change_submit = "Yes"

            if chosen_status == status_for_change:
                change_error = "Same status. Don't have to change!"
            else:
                query_for_change_status = 'update flight ' \
                                          'set status = "{}" ' \
                                          'where airline_name = "{}" and flight_num = {}'\
                                            .format(status_for_change, chosen_airline, chosen_flight_num)

                cursor.execute(query_for_change_status)
                conn.commit()

        finally:
            cursor.close()
            return render_template("action_center_change_status_of_flights.html",
                                   fromdate=fromdate,
                                   todate=todate,
                                   source_city=source_city,
                                   chosen_source_city=chosen_source_city,
                                   chosen_destination_city=chosen_destination_city,
                                   flights_after_search=flights_after_search,
                                   departure_airport=departure_airport,
                                   arrival_airport=arrival_airport,
                                   selected_departure_airport=selected_departure_airport,
                                   selected_arrival_airport=selected_arrival_airport,
                                   username=username,
                                   identification=identification,
                                   status=status,
                                   permission=permission,
                                   error=error,
                                   change_error=change_error,
                                   status_for_change_submit=status_for_change_submit)


# action center add airplane in the system function
@app.route('/action_center_add_airplane_in_the_system', methods=['GET', 'POST'])
def action_center_add_airplane_in_the_system():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    airplane_for_same_airline = []
    airplane_id = None
    num_of_seats = None
    error = None
    succeed = None

    cursor = conn.cursor()

    # get airline
    query_for_airline_working_for = 'select airline_name from airline_staff where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    # get airplanes
    query_for_airplane = 'select * from airplane where airline_name = "{}"'.format(airline_working_for)
    cursor.execute(query_for_airplane)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        airplane_for_same_airline.append(each)

    all_airplane = []
    for each in airplane_for_same_airline:
        all_airplane.append(each['airplane_id'])

    try:
        airplane_id = request.form['airplane_id']
        num_of_seats = request.form['num_of_seats']
        try:
            if int(airplane_id) in all_airplane:
                error = "Can't add existed airplane!"
            else:
                query_for_add_airplane = 'insert into `airplane` (`airline_name`, `airplane_id`, `seats`) ' \
                                         'value ("{}", {}, {})'.format(airline_working_for, airplane_id, num_of_seats)
                cursor.execute(query_for_add_airplane)
                conn.commit()
                succeed = "Airplane successfully added!"
        except:
            error = "Please check your input!"

    finally:
        cursor.close()
        return render_template('action_center_add_airplane_in_the_system.html',
                               username=username,
                               identification=identification,
                               permission=permission,
                               airplane_for_same_airline=airplane_for_same_airline,
                               error=error,
                               succeed=succeed,
                               airplane_id=airplane_id,
                               num_of_seats=num_of_seats)


# action center add new airport in the system function
@app.route('/action_center_add_new_airport_in_the_system', methods=['GET', 'POST'])
def action_center_add_new_airport_in_the_system():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    all_airport_info = []
    all_airport = []
    airport_name = None
    airport_city = None
    error = None
    succeed = None

    cursor = conn.cursor()

    # get airports
    query_for_airports = 'select * from airport'
    cursor.execute(query_for_airports)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        all_airport_info.append(each)

    for each in all_airport_info:
        all_airport.append(each['airport_name'])

    try:
        airport_name = request.form['airport_name']
        airport_city = request.form['airport_city']
        if airport_name in all_airport:
            error = "Can't add existed airport!"
        else:
            try:
                query_for_add_airplane = 'insert into `airport` (`airport_name`, `airport_city`) ' \
                                         'value ("{}", "{}")'.format(airport_name, airport_city)
                cursor.execute(query_for_add_airplane)
                conn.commit()
                succeed = "Airport successfully added!"
            except:
                error = "Please check your input!"

    finally:
        cursor.close()
        return render_template('action_center_add_new_airport_in_the_system.html',
                               username=username,
                               identification=identification,
                               permission=permission,
                               error=error,
                               succeed=succeed,
                               airport_name=airport_name,
                               airport_city=airport_city,
                               all_airport_info=all_airport_info)


# action center view all the booking agents function
@app.route('/action_center_view_all_the_booking_agents', methods=['GET', 'POST'])
def action_center_view_all_the_booking_agents():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    booking_agents_for_1_month_ticket = []
    booking_agents_for_1_year_ticket = []
    booking_agents_for_1_year_commission = []
    num_of_tickets_for_1_month = []
    num_of_tickets_for_1_year = []
    amount_of_commission_for_1_year = []
    all_booking_agent = []

    cursor = conn.cursor()

    # get airline working for
    query_for_airline_working_for = 'select airline_name ' \
                                    'from airline_staff ' \
                                    'where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    # date range
    todate = datetime.now().strftime("%Y-%m-%d")
    todate += ' 23:59:59'
    fromdate_for_1_months = (datetime.now().date() - relativedelta(months=1)).strftime("%Y-%m-%d")
    fromdate_for_1_months += ' 00:00:00'
    fromdate_for_1_year = (datetime.now().date() - relativedelta(years=1)).strftime("%Y-%m-%d")
    fromdate_for_1_year += ' 00:00:00'

    query_for_all_booking_agent = 'select airline_name, email, booking_agent_id ' \
                                  'from booking_agent natural join booking_agent_work_for ' \
                                  'where airline_name = "{}"'.format(airline_working_for)
    # execute query
    cursor.execute(query_for_all_booking_agent)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        all_booking_agent.append(each)

    query_for_booking_agent_tickets_for_1_month = 'select email, count(ticket_id) ' \
                                                   'from booking_agent natural join booking_agent_work_for natural join purchases ' \
                                                   'where airline_name = "{}" and purchase_date between "{}" and "{}" ' \
                                                   'group by booking_agent_id ' \
                                                   'order by count(ticket_id) desc'\
                                                    .format(airline_working_for, fromdate_for_1_months, todate)
    # execute query
    cursor.execute(query_for_booking_agent_tickets_for_1_month)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        booking_agents_for_1_month_ticket.append(each['email'])
        num_of_tickets_for_1_month.append(each['count(ticket_id)'])

    query_for_booking_agent_tickets_for_1_year = 'select email, count(ticket_id) ' \
                                                  'from booking_agent natural join booking_agent_work_for natural join purchases ' \
                                                  'where airline_name = "{}" and purchase_date between "{}" and "{}" ' \
                                                  'group by booking_agent_id ' \
                                                  'order by count(ticket_id) desc' \
                                                    .format(airline_working_for, fromdate_for_1_year, todate)
    # execute query
    cursor.execute(query_for_booking_agent_tickets_for_1_year)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        booking_agents_for_1_year_ticket.append(each['email'])
        num_of_tickets_for_1_year.append(each['count(ticket_id)'])

    query_for_booking_agent_commission_for_1_year = 'select email, sum(price * 0.1) ' \
                                                    'from booking_agent natural join booking_agent_work_for natural join purchases natural join ticket natural join flight ' \
                                                    'where airline_name = "{}" and purchase_date between "{}" and "{}" ' \
                                                    'group by booking_agent_id ' \
                                                    'order by sum(price * 0.1) desc'.format(airline_working_for, fromdate_for_1_year, todate)
    # execute query
    cursor.execute(query_for_booking_agent_commission_for_1_year)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        booking_agents_for_1_year_commission.append(each['email'])
        amount_of_commission_for_1_year.append(each['sum(price * 0.1)'])

    cursor.close()
    return render_template('action_center_view_all_the_booking_agents.html',
                           username=username,
                           identification=identification,
                           permission=permission,
                           booking_agents_for_1_month_ticket=booking_agents_for_1_month_ticket,
                           booking_agents_for_1_year_ticket=booking_agents_for_1_year_ticket,
                           booking_agents_for_1_year_commission=booking_agents_for_1_year_commission,
                           num_of_tickets_for_1_month=num_of_tickets_for_1_month,
                           num_of_tickets_for_1_year=num_of_tickets_for_1_year,
                           amount_of_commission_for_1_year=amount_of_commission_for_1_year,
                           all_booking_agent=all_booking_agent)


# action center view frequent customers function
@app.route('/action_center_view_frequent_customers', methods=['GET', 'POST'])
def action_center_view_frequent_customers():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    customer_frequency = []

    cursor = conn.cursor()

    # date range
    todate = datetime.now().strftime("%Y-%m-%d")
    todate += ' 23:59:59'
    fromdate_for_1_year = (datetime.now().date() - relativedelta(years=1)).strftime("%Y-%m-%d")
    fromdate_for_1_year += ' 00:00:00'

    # get airline
    query_for_airline_working_for = 'select airline_name from airline_staff where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    # get customer info
    query_for_customer_frequency = 'select customer_email as email, count(ticket_id) as num ' \
                                   'from purchases natural join ticket natural join flight ' \
                                   'where airline_name = "{}" and status = "completed" ' \
                                   'and departure_time between "{}" and "{}" ' \
                                   'group by customer_email ' \
                                   'order by count(ticket_id) desc'.format(airline_working_for, fromdate_for_1_year, todate)
    cursor.execute(query_for_customer_frequency)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        customer_frequency.append(each)

    cursor.close()
    return render_template('action_center_view_frequent_customers.html',
                           username=username,
                           identification=identification,
                           permission=permission,
                           customer_frequency=customer_frequency)


# action center view frequent customers detail function
@app.route('/action_center_view_frequent_customers_detail', methods=['GET', 'POST'])
def action_center_view_frequent_customers_detail():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    customer_info = request.form["viewinfo"]
    flight_list = []

    cursor = conn.cursor()

    # get airline
    query_for_airline_working_for = 'select airline_name from airline_staff where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    query_for_flight_list = 'select customer_email, airline_name, flight_num, airplane_id, departure_time, departure_airport, arrival_airport, arrival_time, price, status ' \
                            'from purchases natural join ticket natural join flight ' \
                            'where customer_email = "{}" and status = "completed" ' \
                            'and airline_name = "{}"'.format(customer_info, airline_working_for)
    cursor.execute(query_for_flight_list)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        flight_list.append(each)

    cursor.close()
    return render_template('action_center_view_frequent_customers_detail.html',
                           username=username,
                           identification=identification,
                           permission=permission,
                           flight_list=flight_list)


# action center view reports function
@app.route('/action_center_view_reports', methods=['GET', 'POST'])
def action_center_view_reports():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    month_format = [None, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    months = []
    num_of_ticket = []

    cursor = conn.cursor()

    # get airline working for
    query_for_airline_working_for = 'select airline_name ' \
                                    'from airline_staff ' \
                                    'where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    try:
        # selected month range
        fromdate = request.form['frommonth']
        strfromdate = request.form['frommonth'].split('-')
        intfromdate = [int(each) for each in strfromdate]
        fromyear = intfromdate[0]
        frommonth = intfromdate[1]

        todate = request.form['tomonth']
        strtodate = request.form['tomonth'].split('-')
        inttodate = [int(each) for each in strtodate]
        toyear = inttodate[0]
        tomonth = inttodate[1]

        if fromyear > toyear or fromyear == toyear and frommonth > tomonth:
            error = 'Error! To Date exceeds From Date.'
            return render_template('action_center_track_my_spending.html',
                                   username=username,
                                   identification=identification,
                                   permission=permission,
                                   error=error,
                                   fromdate=fromdate,
                                   todate=todate)

        while fromyear != toyear or frommonth != tomonth:
            temp = []
            temp.append(str(fromyear))
            temp.append(month_format[frommonth])
            months.append('-'.join(temp))

            if frommonth + 1 > 12:
                frommonth = 1
                fromyear += 1
            else:
                frommonth += 1
        temp = []
        temp.append(str(toyear))
        temp.append(month_format[tomonth])
        months.append('-'.join(temp))

    except:
        # default month range
        todate = datetime.today().strftime('%Y-%m')
        strdate = todate.split('-')
        intdate = [int(each) for each in strdate]
        toyear = intdate[0]
        tomonth = intdate[1]

        for i in range(6):
            temp = []
            if tomonth - i >= 1:
                temp.append(str(toyear))
                temp.append(month_format[tomonth - i])
            else:
                temp.append(str(toyear - 1))
                temp.append(month_format[12 - (i - tomonth)])
            months.append('-'.join(temp))

        months = months[::-1]

        fromdate = months[0]
    finally:

        for month in months:
            query = 'select count(ticket_id) ' \
                    'from flight natural join purchases natural join ticket ' \
                    'where airline_name = "{}" and purchase_date like "{}%"'.format(airline_working_for, month)
            # execute query
            cursor.execute(query)
            each = cursor.fetchone()['count(ticket_id)']
            if each is None:
                num_of_ticket.append(0)
            else:
                num_of_ticket.append(each)

        cursor.close()
    return render_template('action_center_view_reports.html',
                           username=username,
                           identification=identification,
                           permission=permission,
                           months=months,
                           num_of_ticket=num_of_ticket,
                           fromdate=fromdate,
                           todate=todate)


# action center comparison of revenue earned function
@app.route('/action_center_comparison_of_revenue_earned', methods=['GET', 'POST'])
def action_center_comparison_of_revenue_earned():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    revenue_for_1_month = []
    revenue_for_1_year = []
    way_of_revenue = ["Revenue without Booking Agent", "Revenue with Booking Agent"]

    cursor = conn.cursor()

    # get airline working for
    query_for_airline_working_for = 'select airline_name ' \
                                    'from airline_staff ' \
                                    'where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    # date range
    todate = datetime.now().strftime("%Y-%m-%d")
    todate += ' 23:59:59'
    fromdate_for_1_months = (datetime.now().date() - relativedelta(months=1)).strftime("%Y-%m-%d")
    fromdate_for_1_months += ' 00:00:00'
    fromdate_for_1_year = (datetime.now().date() - relativedelta(years=1)).strftime("%Y-%m-%d")
    fromdate_for_1_year += ' 00:00:00'

    query_for_revenue_withput_booking_agent_for_1_month = 'select sum(price) ' \
                                                          'from ticket t, purchases p, flight f ' \
                                                          'where p.ticket_id = t.ticket_id and t.airline_name = f.airline_name and t.flight_num = f.flight_num and p.booking_agent_id is null and f.airline_name = "{}" ' \
                                                          'and p.purchase_date between "{}" and "{}"'\
                                                            .format(airline_working_for, fromdate_for_1_months, todate)
    # execute query
    cursor.execute(query_for_revenue_withput_booking_agent_for_1_month)
    each = cursor.fetchone()
    if each is None:
        revenue_for_1_month.append(0)
    else:
        revenue_for_1_month.append(each['sum(price)'])

    query_for_revenue_withput_booking_agent_for_1_year = 'select sum(price) ' \
                                                          'from ticket t, purchases p, flight f ' \
                                                          'where p.ticket_id = t.ticket_id and t.airline_name = f.airline_name and t.flight_num = f.flight_num and p.booking_agent_id is null and f.airline_name = "{}" ' \
                                                          'and p.purchase_date between "{}" and "{}"'\
                                                            .format(airline_working_for, fromdate_for_1_year, todate)
    # execute query
    cursor.execute(query_for_revenue_withput_booking_agent_for_1_year)
    each = cursor.fetchone()
    if each is None:
        revenue_for_1_year.append(0)
    else:
        revenue_for_1_year.append(each['sum(price)'])

    query_for_revenue_with_booking_agent_for_1_month = 'select sum(0.9 * price) ' \
                                                          'from ticket natural join purchases natural join flight natural join booking_agent natural join booking_agent_work_for ' \
                                                          'where airline_name = "{}" ' \
                                                          'and purchase_date between "{}" and "{}"' \
                                                        .format(airline_working_for, fromdate_for_1_months, todate)
    # execute query
    cursor.execute(query_for_revenue_with_booking_agent_for_1_month)
    each = cursor.fetchone()
    if each is None:
        revenue_for_1_month.append(0)
    else:
        revenue_for_1_month.append(each['sum(0.9 * price)'])

    query_for_revenue_with_booking_agent_for_1_year = 'select sum(0.9 * price) ' \
                                                       'from ticket natural join purchases natural join flight natural join booking_agent natural join booking_agent_work_for ' \
                                                       'where airline_name = "{}" ' \
                                                       'and purchase_date between "{}" and "{}"' \
                                                        .format(airline_working_for, fromdate_for_1_year, todate)
    # execute query
    cursor.execute(query_for_revenue_with_booking_agent_for_1_year)
    each = cursor.fetchone()
    if each is None:
        revenue_for_1_year.append(0)
    else:
        revenue_for_1_year.append(each['sum(0.9 * price)'])

    cursor.close()
    return render_template('action_center_comparison_of_revenue_earned.html',
                           username=username,
                           identification=identification,
                           permission=permission,
                           revenue_for_1_month=revenue_for_1_month,
                           revenue_for_1_year=revenue_for_1_year,
                           way_of_revenue=way_of_revenue)


# action center view top destinations function
@app.route('/action_center_view_top_destinations', methods=['GET', 'POST'])
def action_center_view_top_destinations():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    all_destinations_for_3_months = []
    all_destinations_for_1_year = []
    visit_frequency_for_3_months = []
    visit_frequency_for_1_year = []

    cursor = conn.cursor()

    # get airline working for
    query_for_airline_working_for = 'select airline_name ' \
                                    'from airline_staff ' \
                                    'where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    # date range
    todate = datetime.now().strftime("%Y-%m-%d")
    todate += ' 23:59:59'
    fromdate_for_3_months = (datetime.now().date() - relativedelta(months=3)).strftime("%Y-%m-%d")
    fromdate_for_3_months += ' 00:00:00'
    fromdate_for_1_year = (datetime.now().date() - relativedelta(years=1)).strftime("%Y-%m-%d")
    fromdate_for_1_year += ' 00:00:00'

    query_for_destination_frequency_for_3_months = 'select a.airport_city as city, count(p.ticket_id) as num ' \
                                      'from ticket t, purchases p, flight f, airport a ' \
                                      'where p.ticket_id = t.ticket_id and t.airline_name = f.airline_name ' \
                                      'and t.flight_num = f.flight_num and f.arrival_airport = a.airport_name ' \
                                      'and f.arrival_time between "{}" and "{}" and f.airline_name = "{}" '\
                                      'group by a.airport_city ' \
                                      'order by count(p.ticket_id) desc'.format(fromdate_for_3_months, todate, airline_working_for)
    # execute query
    cursor.execute(query_for_destination_frequency_for_3_months)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        all_destinations_for_3_months.append(each['city'])
        visit_frequency_for_3_months.append(each['num'])

    query_for_destination_frequency_for_1_year = 'select a.airport_city as city, count(p.ticket_id) as num ' \
                                                   'from ticket t, purchases p, flight f, airport a ' \
                                                   'where p.ticket_id = t.ticket_id and t.airline_name = f.airline_name ' \
                                                   'and t.flight_num = f.flight_num and f.arrival_airport = a.airport_name ' \
                                                   'and f.arrival_time between "{}" and "{}" and f.airline_name = "{}" ' \
                                                   'group by a.airport_city ' \
                                                   'order by count(p.ticket_id) desc'.format(fromdate_for_1_year, todate, airline_working_for)

    # execute query
    cursor.execute(query_for_destination_frequency_for_1_year)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        all_destinations_for_1_year.append(each['city'])
        visit_frequency_for_1_year.append(each['num'])

    cursor.close()
    return render_template('action_center_view_top_destinations.html',
                           username=username,
                           identification=identification,
                           permission=permission,
                           all_destinations_for_3_months=all_destinations_for_3_months,
                           visit_frequency_for_3_months=visit_frequency_for_3_months,
                           all_destinations_for_1_year=all_destinations_for_1_year,
                           visit_frequency_for_1_year=visit_frequency_for_1_year)


# action center grant new permissions function
@app.route('/action_center_grant_new_permissions', methods=['GET', 'POST'])
def action_center_grant_new_permissions():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    staff_work_for_same_airline = []
    submit = "No"
    error = None

    cursor = conn.cursor()

    query_for_airline_name = 'select airline_name from airline_staff where username = "{}"'.format(username)
    cursor.execute(query_for_airline_name)
    airline_name = cursor.fetchone()["airline_name"]

    query_for_airline_staff = 'select airline_name, username, permission_type ' \
                              'from permission natural join airline_staff ' \
                              'where airline_name = "{}"'.format(airline_name)
    # execute query
    cursor.execute(query_for_airline_staff)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        staff_work_for_same_airline.append(each)

    try:
        grant_info = request.form['grant'].split(',')
        chosen_staff = grant_info[0]
        existed_permission = grant_info[1]
        tried_permission = request.form['permission_type']
        submit = "Yes"

        if tried_permission == existed_permission:
            error = 'Permission type already exists!'
        else:
            if chosen_staff == username:
                session["permission"] = tried_permission
                permission = session.get("permission")

            query_for_permission = 'update permission ' \
                                   'set permission_type = "{}" ' \
                                   'where username = "{}"'.format(tried_permission, chosen_staff)
            cursor.execute(query_for_permission)
            conn.commit()

    finally:
        cursor.close()
        return render_template('action_center_grant_new_permissions.html',
                               username=username,
                               identification=identification,
                               permission=permission,
                               staff_work_for_same_airline=staff_work_for_same_airline,
                               error = error,
                               submit = submit)


# action center add booking agents function
@app.route('/action_center_add_booking_agents', methods=['GET', 'POST'])
def action_center_add_booking_agents():
    username = session.get('username')
    identification = session.get('identification')
    permission = session.get('permission')
    independent_booking_agent = []
    submit = "No"
    error = None

    cursor = conn.cursor()

    # get airline working for
    query_for_airline_working_for = 'select airline_name ' \
                                    'from airline_staff ' \
                                    'where username = "{}"'.format(username)
    cursor.execute(query_for_airline_working_for)
    airline_working_for = cursor.fetchone()["airline_name"]

    # get independent booking agent
    query_for_independent_booking_agent = 'select email, booking_agent_id ' \
                                          'from booking_agent ' \
                                          'where email not in (select email ' \
                                          '                     from booking_agent_work_for)'
    cursor.execute(query_for_independent_booking_agent)
    while True:
        # fetch each line of data and collect them
        each = cursor.fetchone()
        # get all the data
        if each is None:
            break
        independent_booking_agent.append(each)

    try:
        chosen_booking_agent = request.form['grant']
        submit = "Yes"
        query_for_add = 'insert into `booking_agent_work_for` (`email`, `airline_name`) ' \
                        'value ("{}", "{}")'.format(chosen_booking_agent, airline_working_for)

        cursor.execute(query_for_add)
        conn.commit()

    finally:
        cursor.close()
        return render_template('action_center_add_booking_agents.html',
                               username=username,
                               identification=identification,
                               permission=permission,
                               independent_booking_agent=independent_booking_agent,
                               error=error,
                               submit=submit)


# logout function
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    identification = session.get("identification")
    if identification == "Airline Staff":
        session.pop('username')
        session.pop('identification')
        session.pop('permission')
    else:
        session.pop('username')
        session.pop('identification')
    return redirect(url_for('home'))


# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
