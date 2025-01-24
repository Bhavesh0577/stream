import streamlit as st
from streamlit_ace import st_ace
import matplotlib.pyplot as plt
import time

# Function to execute the provided code
def execute_code(user_code, input_data):
    global_vars = {}
    local_vars = {"input_data": input_data}
    try:
        exec(user_code, global_vars, local_vars)
        return local_vars.get("result", None), None
    except Exception as e:
        return None, str(e)

# Function to visualize the algorithm
def visualize_execution(data):
    fig, ax = plt.subplots()
    ax.bar(range(len(data)), data, color="skyblue")
    ax.set_title("Algorithm Execution Visualization")
    ax.set_xlabel("Index")
    ax.set_ylabel("Value")
    st.pyplot(fig)

# Streamlit UI
st.title("DSA Visualizer with Code Execution")

st.sidebar.title("Settings")
ide_theme = st.sidebar.selectbox("Select IDE Theme", ["github", "monokai", "dracula"], index=0)
st.sidebar.info("Write your DSA code in Python. Use 'input_data' for input and assign the result to 'result' for visualization.")

# Code editor
st.subheader("Code Editor")
default_code = '''# Example: Bubble Sort
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

result = bubble_sort(input_data)
'''
user_code = st_ace(value=default_code, language="python", theme=ide_theme, height=300)

# Input for the algorithm
st.subheader("Input Data")
input_data = st.text_input("Enter a list of numbers (comma-separated):", "5, 3, 8, 6, 2")

try:
    input_data = [int(x.strip()) for x in input_data.split(",")]
except ValueError:
    st.error("Invalid input! Please enter comma-separated numbers.")
    input_data = []

# Execute and visualize
if st.button("Run and Visualize"):
    if user_code and input_data:
        with st.spinner("Executing your code..."):
            result, error = execute_code(user_code, input_data)
            time.sleep(1)  # Simulate execution time
            if error:
                st.error(f"Error in execution: {error}")
            else:
                st.success("Code executed successfully!")
                st.write("Output:", result)
                visualize_execution(result if result else input_data)
    else:
        st.warning("Please provide valid code and input data.")
