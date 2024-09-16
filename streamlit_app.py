import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Initialize session state variables
if 'entries' not in st.session_state:
    st.session_state.entries = pd.DataFrame(columns=['date', 'title', 'content'])
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'timer_duration' not in st.session_state:
    st.session_state.timer_duration = 5

def save_entry(date, title, content):
    new_entry = pd.DataFrame({'date': [date], 'title': [title], 'content': [content]})
    st.session_state.entries = pd.concat([st.session_state.entries, new_entry], ignore_index=True)

def update_entry(index, date, title, content):
    st.session_state.entries.loc[index] = [date, title, content]

def delete_entry(index):
    st.session_state.entries = st.session_state.entries.drop(index).reset_index(drop=True)

def start_timer():
    st.session_state.timer_running = True
    st.session_state.start_time = time.time()

def stop_timer():
    st.session_state.timer_running = False
    st.session_state.start_time = None

st.title("💭 ThoughtStream Journal")

# Sidebar for creating and editing entries
with st.sidebar:
    st.header("Create/Edit Entry")
    date = st.date_input("Date", datetime.now().date())
    title = st.text_input("Title")
    content = st.text_area("Content", height=200)
    
    # Timer feature
    st.header("Timer")
    st.session_state.timer_duration = st.number_input("Set timer (minutes)", min_value=1, max_value=60, value=st.session_state.timer_duration)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Timer"):
            start_timer()
    with col2:
        if st.button("Stop Timer"):
            stop_timer()
    
    # Create placeholders for the timer display
    progress_bar = st.empty()
    timer_display = st.empty()

    if st.session_state.editing_index is None:
        if st.button("Add Entry"):
            save_entry(date, title, content)
            st.success("Entry added successfully!")
    else:
        if st.button("Update Entry"):
            update_entry(st.session_state.editing_index, date, title, content)
            st.session_state.editing_index = None
            st.success("Entry updated successfully!")
        if st.button("Cancel Edit"):
            st.session_state.editing_index = None

# Main area for displaying entries
st.header("Journal Entries")

for index, entry in st.session_state.entries.iterrows():
    with st.expander(f"{entry['date']} - {entry['title']}"):
        st.write(entry['content'])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Edit", key=f"edit_{index}"):
                st.session_state.editing_index = index
                st.sidebar.date_input("Date", entry['date'])
                st.sidebar.text_input("Title", entry['title'])
                st.sidebar.text_area("Content", entry['content'])
        with col2:
            if st.button("Delete", key=f"delete_{index}"):
                delete_entry(index)
                st.success("Entry deleted successfully!")
                st.rerun()

# Timer update function
def update_timer():
    while st.session_state.timer_running:
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = max(st.session_state.timer_duration * 60 - elapsed_time, 0)
        
        mins, secs = divmod(int(remaining_time), 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        
        progress_bar.progress(1 - remaining_time / (st.session_state.timer_duration * 60))
        timer_display.header(f"Time remaining: {time_format}")
        
        if remaining_time <= 0:
            timer_display.success("Time's up!")
            stop_timer()
        
        time.sleep(0.1)  # Update every 0.1 seconds

# Run the timer update function
if st.session_state.timer_running:
    update_timer()