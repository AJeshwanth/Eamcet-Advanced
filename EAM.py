import streamlit as st
import pymongo

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Adjust your connection string
db = client["EAMCET"]  # Replace with your database name
collection = db["EAMCET2022"]  # Replace with your collection name

# Page configuration with custom title and layout
st.set_page_config(page_title="🎓 Student Search Portal", page_icon="📚", layout="wide")

# Add custom CSS for enhanced UI

st.markdown("""
    <style>
    /* General App Background */
    .stApp {
        # background-color: #f0f4f8;
    }
    .st-bp{
            cursor: pointer;
    }
    .fixi{  
        position: fixed;
    }
    .search-container {
        padding: 10px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #d1d8e0;
        margin-bottom: 20px;
    }

    .search-container h3 {
        color: #2980b9;
        font-size: 1.8em;
        text-align: center;
        font-weight: bold;
    }

    .search-container label {
        font-weight: bold;
        font-size: 1.2em;
        color: #2c3e50;
        margin-bottom: 8px;
        display: block;
    }

    /* Styling for input fields */
    input[type="text"] {
        width: 100%;
        font-size: 1.1em;
        border: 1px solid #bdc3c7;
            
    }

    /* Dropdown styling */
    .search-container select {
        width: 100%;
        padding: 15px;
        font-size: 1.1em;
        border: 1px solid #bdc3c7;
    }

    /* Styling for Search Button */
    .search-btn {
        background-color: #2980b9;
        color: white;
        font-size: 18px;
        padding: 14px;
        border-radius: 10px;
        width: 100%;
        border: none;
    }

    .search-btn:hover {
        background-color: #3498db;
    }

    /* Styling the Results Section */
    .results-container {
        padding: 20px;
    }
    .st-emotion-cache-15hul6a {
            float: right;
    }
    .student-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    .student-card h4 {
        font-size: 1.5em;
        color: #2c3e50;
        margin-bottom: 10px;
        font-weight: bold;
    }

    .student-card p {
        font-size: 1.1em;
        color: #34495e;
    }
    #fixed{
            position: fixed;}
    /* Empty Result Styling */
    .empty-result {
        text-align: center;
        padding: 20px;
        background-color: #e74c3c;
        color: white;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 5])
with st.container():
    st.markdown("<div class='fixi'>", unsafe_allow_html=True)
    with col1:
        st.markdown("<div class='search-container'><h3>🔍 Search Filters</h3>", unsafe_allow_html=True)
        student_name = st.text_input("Search by Student Name:", "")
        colleges = collection.distinct("colleges.college_name")
        selected_college = st.selectbox("Filter by College:", ["All Colleges"] + colleges)
        branches = collection.distinct("colleges.branches.branch_name")
        selected_branch = st.selectbox("Filter by Branch:", ["All Branches"] + branches)
        years = ["2020", "2021", "2022", "2023"]
        selected_year = st.selectbox("Select Year:", years, index=years.index("2023"))
        st.markdown("</div>", unsafe_allow_html=True)
        collection = db[f"EAMCET{selected_year}"]
        search_button = st.button("🔎 Search", help="Click to search for students matching the criteria.")
    st.markdown("</div>", unsafe_allow_html=True)
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'results_per_page' not in st.session_state:
    st.session_state.results_per_page = 50  
if 'student_data' not in st.session_state:
    st.session_state.student_data = [] 
with col2:
    st.title("🎓 Student Search Results")

    if search_button:
        st.session_state.current_page = 0  
        st.session_state.student_data = []  

        query = {}
        if student_name:
            query["colleges.branches.students.candidate_name"] = {"$regex": student_name, "$options": "i"}
        if selected_college != "All Colleges":
            query["colleges.college_name"] = selected_college
        if selected_branch != "All Branches":
            query["colleges.branches.branch_name"] = selected_branch
        pipeline = [
            { "$unwind": "$colleges" },
            { "$unwind": "$colleges.branches" },
            { "$unwind": "$colleges.branches.students" },
            { "$match": query },
            {
                "$project": {
                    "_id": 0,
                    "college": "$colleges.college_name",
                    "branch": "$colleges.branches.branch_name",
                    "candidate_name": "$colleges.branches.students.candidate_name",
                    "rank": "$colleges.branches.students.rank",
                    "gender": "$colleges.branches.students.gender",
                    "region": "$colleges.branches.students.region",
                    "category": "$colleges.branches.students.category",
                    "seat_category": "$colleges.branches.students.seat_category"
                }
            }
        ]

        st.session_state.student_data = list(collection.aggregate(pipeline))  
    if st.session_state.student_data:
        total_results = len(st.session_state.student_data)
        total_pages = (total_results + st.session_state.results_per_page - 1) // st.session_state.results_per_page
        start_idx = st.session_state.current_page * st.session_state.results_per_page
        end_idx = start_idx + st.session_state.results_per_page
        current_page_data = st.session_state.student_data[start_idx:end_idx]

        st.subheader(f"Search Results ({total_results} found):")

        for student in current_page_data:
            with st.expander(student['candidate_name']):
                st.markdown(f"""
                    <p><strong>College:</strong> {student['college']}<br>
                    <strong>Branch:</strong> {student['branch']}<br>
                    <strong>Rank:</strong> {student['rank']}<br>
                    <strong>Gender:</strong> {student['gender']}<br>
                    <strong>Region:</strong> {student['region']}<br>
                    <strong>Category:</strong> {student['category']}<br>
                    <strong>Seat Category:</strong> {student['seat_category']}</p>
                """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.current_page > 0:
                if st.button("◀️ Previous"):
                    st.session_state.current_page -= 1

        with col2:
            if st.session_state.current_page < total_pages-1:
                if st.button("Next ▶️"):
                    st.session_state.current_page += 1
    else:
        st.markdown("<div class='empty-result'><p>No students found matching the search criteria.</p></div>", unsafe_allow_html=True)
