"""
app.py - Main Streamlit Application for CineBook
Pure Python | No HTML/CSS/JavaScript | Beginner-Friendly
"""

import streamlit as st
import pandas as pd
import datetime
import random
import io
import os
import database

# QR code library check
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


st.set_page_config(
    page_title="CineBook - Online Movie Ticket Booking",
    page_icon="🎬",
    layout="wide"
)



# Initialize database
database.init_db()

# Session State
if "user_email" not in st.session_state:
    st.session_state["user_email"] = "demo@cinebook.com"
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "Demo User"
if "user_phone" not in st.session_state:
    st.session_state["user_phone"] = "9876543210"
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = True
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "selected_movie_title" not in st.session_state:
    st.session_state["selected_movie_title"] = "Interstellar"
if "recent_booking" not in st.session_state:
    st.session_state["recent_booking"] = None

# Sidebar Navigation
st.sidebar.title("🎬 CineBook")
st.sidebar.caption("Your Seat. Your Movie. Your Moment.")

nav_options = [
    "🏠 Home",
    "🎬 Movies",
    "🏢 Theatres",
    "🎟 Book Tickets",
    "📋 My Bookings",
    "🎯 Smart Picks",
    "🎁 Offers",
    "👤 Profile",
    "🛠 Admin Dashboard",
    "ℹ About"
]

menu = st.sidebar.radio("Navigation", nav_options)
st.sidebar.divider()

if st.session_state["is_logged_in"]:
    st.sidebar.success(f"Logged in as: **{st.session_state['user_name']}**")
    if st.sidebar.button("Logout"):
        st.session_state["is_logged_in"] = False
        st.session_state["user_name"] = ""
        st.session_state["user_email"] = ""
        st.session_state["user_phone"] = ""
        st.session_state["is_admin"] = False
        st.rerun()

# ==========================================
# 1. HOME PAGE
# ==========================================
if menu == "🏠 Home":
    st.title("🎬 CineBook")
    st.subheader("Your Seat. Your Movie. Your Moment.")
    st.write("Welcome to **CineBook**, the fast, simple, and reliable online movie ticket booking platform.")
    
    search_term = st.text_input("🔍 Search movies by title, director, or actor:", placeholder="e.g. Nolan, Inception, Action...")
    movies = database.get_all_movies(search_query=search_term)
    
    st.markdown("### 🔥 Now Showing in Theatres")
    if not movies:
        st.warning("No movies found matching your search query.")
    else:
        cols = st.columns(4)
        for i, movie in enumerate(movies):
            with cols[i % 4]:
                st.image(movie["poster"], use_container_width=True)
                st.markdown(f"**{movie['title']}**")
                st.caption(f"⭐ {movie['rating']} | {movie['genre']} | {movie['language']}")
                if st.button(f"Book '{movie['title']}'", key=f"home_book_{movie['id']}"):
                    st.session_state["selected_movie_title"] = movie["title"]
                    st.info(f"Selected **{movie['title']}**. Please open '🎟 Book Tickets' in the sidebar!")
        
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚀 Coming Soon")
        st.info("🎟 **Dune: Part Three** — Directed by Denis Villeneuve")
        st.info("🎟 **Spider-Man: Beyond the Multiverse** — Animated Wonder")
    with col2:
        st.markdown("### 💡 Why CineBook?")
        st.write("✔️ Real-time seat reservation")
        st.write("✔️ Instant QR code digital tickets")
        st.write("✔️ Easy online ticket cancellation")
        st.write("✔️ Pure Python & SQLite architecture")

# ==========================================
# 2. MOVIES CATALOGUE
# ==========================================
elif menu == "🎬 Movies":
    st.title("🎬 Movie Catalogue")
    c1, c2 = st.columns(2)
    with c1:
        genre_choice = st.selectbox("Filter by Genre", ["All", "Sci-Fi", "Action", "Comedy", "Romance", "Animation", "Thriller"])
    with c2:
        lang_choice = st.selectbox("Filter by Language", ["All", "English", "Japanese"])
        
    movies = database.get_all_movies(genre_filter=genre_choice, lang_filter=lang_choice)
    for movie in movies:
        with st.expander(f"🎬 {movie['title']} ({movie['genre']}) — Rating: ⭐ {movie['rating']}", expanded=True):
            m_col1, m_col2 = st.columns([1, 2])
            with m_col1:
                st.image(movie["poster"], width=240)
            with m_col2:
                st.subheader(movie["title"])
                st.write(f"**Genre:** {movie['genre']} | **Language:** {movie['language']} | **Duration:** {movie['duration']}")
                st.write(f"**Rating:** ⭐ {movie['rating']}/10 | **Release Date:** {movie['release_date']}")
                st.write(f"**Director:** {movie['director']}")
                st.write(f"**Cast:** {movie['cast']}")
                st.write(f"**Synopsis:** {movie['description']}")
                if st.button("🎟 Select This Movie for Booking", key=f"cat_book_{movie['id']}"):
                    st.session_state["selected_movie_title"] = movie["title"]
                    st.success(f"Selected **{movie['title']}**! Go to '🎟 Book Tickets' to continue.")

# ==========================================
# 3. THEATRES
# ==========================================
elif menu == "🏢 Theatres":
    st.title("🏢 Our Partner Theatres")
    theatres = database.get_all_theatres()
    for t in theatres:
        st.subheader(f"📍 {t['name']}")
        st.write(f"**Location:** {t['location']}")
        st.write(f"**Amenities:** {t['facilities']}")
        st.divider()

# ==========================================
# 4. BOOK TICKETS (SEAT SELECTION & DEMO PAYMENT)
# ==========================================
elif menu == "🎟 Book Tickets":
    st.title("🎟 Reserve Your Seats")
    
    # Step 1: Movie & Showtime
    st.subheader("Step 1: Choose Movie, Theatre & Showtime")
    all_movies = database.get_all_movies()
    movie_titles = [m["title"] for m in all_movies]
    
    def_idx = 0
    if st.session_state["selected_movie_title"] in movie_titles:
        def_idx = movie_titles.index(st.session_state["selected_movie_title"])
        
    c1, c2 = st.columns(2)
    with c1:
        chosen_movie = st.selectbox("Select Movie", movie_titles, index=def_idx)
    with c2:
        theatres = database.get_all_theatres()
        theatre_names = [t["name"] for t in theatres]
        chosen_theatre = st.selectbox("Select Theatre", theatre_names)
        
    c3, c4 = st.columns(2)
    with c3:
        today = datetime.date.today()
        dates = [
            f"Today ({today.strftime('%d %b')})",
            f"Tomorrow ({(today + datetime.timedelta(days=1)).strftime('%d %b')})",
            f"Day After ({(today + datetime.timedelta(days=2)).strftime('%d %b')})"
        ]
        chosen_date = st.selectbox("Select Date", dates)
    with c4:
        showtimes = ["10:00 AM", "01:00 PM", "04:00 PM", "07:00 PM", "10:00 PM"]
        chosen_time = st.selectbox("Select Showtime", showtimes)
        
    st.divider()
    
    # Step 2: Interactive Seat Grid
    st.subheader("Step 2: Select Your Seats")
    st.info("💺 **Regular Seats (Rows A, B, C):** ₹150 | **Premium Seats (Rows D, E):** ₹200")
    
    occupied_seats = database.get_occupied_seats(chosen_movie, chosen_theatre, chosen_date, chosen_time)
    st.caption("🔴 Disabled = Occupied | ⚪ Checkbox = Available")
    
    selected_seats = []
    rows = ["A", "B", "C", "D", "E"]
    
    for row in rows:
        row_cols = st.columns(6)
        for num in range(1, 7):
            seat_code = f"{row}{num}"
            with row_cols[num - 1]:
                if seat_code in occupied_seats:
                    st.button(f"❌ {seat_code}", key=f"seat_{seat_code}", disabled=True)
                else:
                    if st.checkbox(f"{seat_code}", key=f"cb_{chosen_movie}_{chosen_theatre}_{seat_code}"):
                        selected_seats.append(seat_code)
                        
    st.divider()
    
    # Step 3: Price Calculation
    st.subheader("Step 3: Price Summary")
    if not selected_seats:
        st.warning("Please select at least one seat to proceed.")
        total_price = 0
    else:
        seat_cost = sum(150 if s.startswith(("A", "B", "C")) else 200 for s in selected_seats)
        convenience_fee = 30
        total_price = seat_cost + convenience_fee
        
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Selected Seats", ", ".join(selected_seats))
        sc2.metric("Tickets Subtotal", f"₹{seat_cost}")
        sc3.metric("Final Total (incl. ₹30 fee)", f"₹{total_price}")
        
    st.divider()
    
    # Step 4: Customer Details & Demo Payment
    st.subheader("Step 4: Customer Details & Demo Payment")
    cust_col1, cust_col2, cust_col3 = st.columns(3)
    with cust_col1:
        cust_name = st.text_input("Full Name", value=st.session_state["user_name"])
    with cust_col2:
        cust_email = st.text_input("Email Address", value=st.session_state["user_email"])
    with cust_col3:
        cust_phone = st.text_input("Phone Number", value=st.session_state["user_phone"])
        
    payment_method = st.radio(
        "Select Demo Payment Method",
        ["UPI (GPay / PhonePe / Paytm)", "Credit Card", "Debit Card", "Net Banking"],
        horizontal=True
    )
    st.info("⚠️ **DEMO PAYMENT:** No real money will be charged. This is an academic simulation.")
    
    if st.button("💳 Pay & Confirm Booking", type="primary"):
        if not selected_seats:
            st.error("Please select at least one seat before proceeding.")
        elif not cust_name.strip() or not cust_email.strip() or not cust_phone.strip():
            st.error("Please fill in all customer details (Name, Email, Phone).")
        else:
            booking_id = f"CB2026{random.randint(1000, 9999)}"
            database.save_booking(
                booking_id=booking_id,
                name=cust_name.strip(),
                email=cust_email.strip(),
                phone=cust_phone.strip(),
                movie=chosen_movie,
                theatre=chosen_theatre,
                date=chosen_date,
                time=chosen_time,
                seats_list=selected_seats,
                amount=total_price
            )
            
            st.session_state["recent_booking"] = {
                "booking_id": booking_id,
                "name": cust_name.strip(),
                "email": cust_email.strip(),
                "phone": cust_phone.strip(),
                "movie": chosen_movie,
                "theatre": chosen_theatre,
                "date": chosen_date,
                "time": chosen_time,
                "seats": ", ".join(selected_seats),
                "amount": total_price
            }
            st.success("🎉 Payment Simulated Successfully! Booking Confirmed.")
            st.balloons()
            
    # Step 5: Digital Ticket with QR Code
    if st.session_state["recent_booking"]:
        b = st.session_state["recent_booking"]
        st.divider()
        st.markdown(f"## 🎉 Booking Confirmed! Ticket ID: `{b['booking_id']}`")
        
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            st.write(f"**Movie:** {b['movie']}")
            st.write(f"**Theatre:** {b['theatre']}")
            st.write(f"**Date & Time:** {b['date']} at {b['time']}")
            st.write(f"**Seat(s):** {b['seats']}")
            st.write(f"**Customer:** {b['name']} ({b['phone']})")
            st.write(f"**Total Amount Paid:** ₹{b['amount']}")
            st.success("Status: **CONFIRMED**")
            
        with t_col2:
            if QR_AVAILABLE:
                qr = qrcode.QRCode(box_size=6, border=2)
                qr.add_data(f"CineBook Ticket | ID: {b['booking_id']} | Movie: {b['movie']} | Seats: {b['seats']}")
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="Scan for Entry Verification", width=180)
            else:
                st.info(f"Verification Code: {b['booking_id']}")
                
        ticket_text = f"""=====================================
          CINEBOOK DIGITAL TICKET
=====================================
Booking ID : {b['booking_id']}
Movie      : {b['movie']}
Theatre    : {b['theatre']}
Date       : {b['date']}
Showtime   : {b['time']}
Seats      : {b['seats']}
Name       : {b['name']}
Phone      : {b['phone']}
Total Paid : INR {b['amount']}
Status     : CONFIRMED
=====================================
Thank you for booking with CineBook!
"""
        st.download_button(
            label="📥 Download Digital Ticket (.txt)",
            data=ticket_text,
            file_name=f"CineBook_Ticket_{b['booking_id']}.txt",
            mime="text/plain"
        )

# ==========================================
# 5. MY BOOKINGS
# ==========================================
elif menu == "📋 My Bookings":
    st.title("📋 My Bookings")
    user_email = st.text_input("Enter your booking email:", value=st.session_state["user_email"])
    
    if st.button("Search Bookings") or user_email:
        bookings = database.get_bookings_by_email(user_email.strip())
        if not bookings:
            st.info(f"No bookings found for `{user_email}`.")
        else:
            for b in bookings:
                status_icon = "🟢" if b["status"] == "CONFIRMED" else "🔴"
                with st.expander(f"{status_icon} Ticket {b['booking_id']} — {b['movie']} ({b['date']} {b['time']})", expanded=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**Theatre:** {b['theatre']}")
                        st.write(f"**Seats:** {b['seats']}")
                        st.write(f"**Amount:** ₹{b['amount']}")
                        st.write(f"**Status:** `{b['status']}`")
                    with c2:
                        if b["status"] == "CONFIRMED":
                            if st.button(f"Cancel Ticket {b['booking_id']}", key=f"cancel_{b['booking_id']}"):
                                database.cancel_booking_by_id(b["booking_id"])
                                st.success(f"Booking `{b['booking_id']}` has been CANCELLED. Seats are now released!")
                                st.rerun()
                        else:
                            st.warning("Booking is Cancelled.")

# ==========================================
# 6. SMART PICKS
# ==========================================
elif menu == "🎯 Smart Picks":
    st.title("🎯 CineBook Smart Picks")
    st.write("A transparent **rule-based recommendation algorithm** matching films to your preferred genre.")
    fav_genre = st.selectbox("What genre are you in the mood for?", ["Sci-Fi", "Action", "Comedy", "Romance", "Animation", "Thriller"])
    recommended = database.get_all_movies(genre_filter=fav_genre)
    
    if recommended:
        cols = st.columns(len(recommended))
        for i, m in enumerate(recommended):
            with cols[i]:
                st.image(m["poster"], use_container_width=True)
                st.markdown(f"**{m['title']}**")
                st.caption(f"⭐ {m['rating']}/10 | {m['duration']}")
    else:
        st.info("No recommendations found for this genre.")

# ==========================================
# 7. OFFERS
# ==========================================
elif menu == "🎁 Offers":
    st.title("🎁 Special Offers & Discounts")
    st.caption("All offers shown below are simulated for demonstration purposes.")
    o1, o2, o3 = st.columns(3)
    with o1:
        st.subheader("🎓 Student Offer")
        st.write("Get **10% OFF** on weekday matinee shows! Valid with any college student ID card.")
        st.code("PROMO: CINESTUDENT10")
    with o2:
        st.subheader("👥 Group Booking")
        st.write("Booking 4 or more tickets? Get **complimentary popcorn vouchers** at the theatre counter.")
        st.code("PROMO: CINEGROUP4")
    with o3:
        st.subheader("🍿 Weekend Night")
        st.write("Flat **₹50 Cashback** on Sunday evening shows booked via CineBook.")
        st.code("PROMO: WEEKEND50")

# ==========================================
# 8. PROFILE / LOGIN
# ==========================================
elif menu == "👤 Profile":
    st.title("👤 User Profile & Login")
    tab1, tab2 = st.tabs(["Login", "Update Profile"])
    
    with tab1:
        st.subheader("Demo Login")
        login_email = st.text_input("Email", value="demo@cinebook.com")
        login_pass = st.text_input("Password", type="password", value="Demo123")
        if st.button("Login"):
            if login_email == "demo@cinebook.com" and login_pass == "Demo123":
                st.session_state["is_logged_in"] = True
                st.session_state["user_email"] = "demo@cinebook.com"
                st.session_state["user_name"] = "Demo User"
                st.session_state["user_phone"] = "9876543210"
                st.success("Successfully logged in as Demo User!")
            elif login_email == "admin@cinebook.com" and login_pass == "admin123":
                st.session_state["is_logged_in"] = True
                st.session_state["is_admin"] = True
                st.session_state["user_name"] = "Administrator"
                st.success("Logged in as Admin! You can access the 🛠 Admin Dashboard.")
            else:
                st.error("Invalid credentials. Try demo@cinebook.com / Demo123")
                
    with tab2:
        st.subheader("Current Profile Information")
        new_name = st.text_input("Full Name", value=st.session_state["user_name"])
        new_phone = st.text_input("Phone Number", value=st.session_state["user_phone"])
        if st.button("Save Profile"):
            st.session_state["user_name"] = new_name
            st.session_state["user_phone"] = new_phone
            st.success("Profile updated!")

# ==========================================
# 9. ADMIN DASHBOARD
# ==========================================
elif menu == "🛠 Admin Dashboard":
    st.title("🛠 Admin Management Portal")
    admin_user = st.text_input("Admin Username", value="admin")
    admin_pass = st.text_input("Admin Password", type="password", value="admin123")
    
    if admin_user == "admin" and admin_pass == "admin123":
        st.success("Admin Verified!")
        metrics = database.get_admin_metrics()
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Movies", metrics["movies"])
        m2.metric("Theatres", metrics["theatres"])
        m3.metric("Registered Users", metrics["users"])
        m4.metric("Active Bookings", metrics["bookings"])
        m5.metric("Total Revenue", f"₹{metrics['revenue']}")
        
        st.divider()
        atab1, atab2, atab3 = st.tabs(["Add Movie", "View All Bookings", "Registered Users"])
        
        with atab1:
            with st.form("add_movie_form"):
                n_title = st.text_input("Movie Title")
                n_genre = st.selectbox("Genre", ["Action", "Sci-Fi", "Comedy", "Drama", "Romance", "Horror", "Animation", "Thriller"])
                n_lang = st.selectbox("Language", ["English", "Hindi", "Tamil", "Telugu", "Japanese"])
                n_duration = st.text_input("Duration", value="140 min")
                n_rating = st.number_input("Rating (0-10)", min_value=0.0, max_value=10.0, value=8.5, step=0.1)
                n_release = st.text_input("Release Date", value="2026-10-15")
                n_director = st.text_input("Director")
                n_cast = st.text_input("Cast (comma separated)")
                n_poster = st.text_input("Poster Image Path or URL", value="posters/interstellar.png")
                n_desc = st.text_area("Description")
                
                if st.form_submit_button("Save Movie"):
                    if n_title.strip() and n_desc.strip():
                        database.add_new_movie(n_title, n_genre, n_lang, n_duration, n_rating, n_release, n_desc, n_director, n_cast, n_poster)
                        st.success(f"Movie '{n_title}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Please provide at least a title and description.")
                        
        with atab2:
            all_b = database.get_all_bookings()
            if all_b:
                st.dataframe(pd.DataFrame(all_b), use_container_width=True)
            else:
                st.info("No bookings recorded yet.")
                
        with atab3:
            st.dataframe(pd.DataFrame(database.get_all_users()), use_container_width=True)
    else:
        st.error("Incorrect admin credentials. Use admin / admin123")

# ==========================================
# 10. ABOUT
# ==========================================
elif menu == "ℹ About":
    st.title("ℹ About CineBook")
    st.markdown("""
    ### Online Movie Ticket Booking System
    **CineBook** is an academic project built to demonstrate full-stack principles using pure Python, Streamlit, and SQLite.
    
    #### Core Architectural Highlights:
    * **Frontend:** Native Streamlit interactive elements (radio buttons, columns, checkboxes, metrics).
    * **Backend:** Python business logic and input sanitization.
    * **Database:** SQLite relational engine storing movies, theatres, and bookings.
    * **Verification:** Algorithmic QR code generation with downloadable plain-text receipts.
    """)
# ==========================================

