import streamlit as st
import pandas as pd
import pickle
import re

# Load the exported data
jobs = pickle.load(open('jobs_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


# Function to preprocess text
def preprocess_text(text):
    text = str(text).lower()
    text = re.sub('<.*?>', '', text)  # Remove HTML tags
    text = re.sub('[^a-z\s]', '', text)  # Remove special characters and digits
    return text


# Improved recommend function
def recommend(job_title, location, top_n=5):
    job_title = preprocess_text(job_title)  # Preprocess the input job title
    location = preprocess_text(location)  # Preprocess the input location

    matching_jobs = jobs[(jobs['title'].str.contains(job_title, case=False, na=False)) &
                         (jobs['location'].str.contains(location, case=False, na=False))]

    if matching_jobs.empty:
        # If no exact matches found, try partial matching for location
        matching_jobs = jobs[(jobs['title'].str.contains(job_title, case=False, na=False)) &
                             (jobs['location'].apply(lambda x: location in preprocess_text(x)))]

    if matching_jobs.empty:
        return None

    job_indices = matching_jobs.index
    distances = sorted([(i, similarity[i][job_indices].mean()) for i in job_indices], reverse=True, key=lambda x: x[1])

    recommended_jobs = []
    recommended_urls = set()
    for i, _ in distances:
        job = matching_jobs.loc[i]
        if job['job_posting_url'] not in recommended_urls:
            recommended_jobs.append({
                'Title': job['title'],
                'Company': job['company_name'],
                'Location': job['location'],
                'URL': job['job_posting_url']
            })
            recommended_urls.add(job['job_posting_url'])

        if len(recommended_jobs) == top_n:
            break

    return recommended_jobs


# Streamlit app
def main():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            body {
                font-family: 'Roboto', sans-serif;
            }
        </style>
        """, unsafe_allow_html=True)
    st.markdown(f"<style>{open('style.css').read()}</style>", unsafe_allow_html=True)

    st.image("logo.png", width=200)
    st.title("Job Recommendation System")

    # User input
    job_title = st.sidebar.text_input("Enter job title")
    location = st.sidebar.text_input("Enter location")
    top_n = st.sidebar.slider("Number of recommendations", min_value=1, max_value=10, value=5)

    if st.sidebar.button("Get Recommendations"):
        if job_title and location:
            recommendations = recommend(job_title, location, top_n)

            if recommendations:
                st.subheader(f"Recommendations for '{job_title}' in '{location}':")
                for i, job in enumerate(recommendations, 1):
                    with st.expander(f"Recommendation {i}"):
                        st.write(f"**Title:** {job['Title']}")
                        st.write(f"**Company:** {job['Company']}")
                        st.write(f"**Location:** {job['Location']}")
                        st.write(f"**URL:** {job['URL']}")
            else:
                st.warning("No matching jobs found for the given job title and location.")
        else:
            st.warning("Please enter both job title and location.")

    st.markdown("---")
    st.markdown(
        "Created by PRATHAM MINDA | [GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)")


if __name__ == '__main__':
    main()