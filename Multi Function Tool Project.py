#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk
from tkinter import messagebox, ttk, filedialog, scrolledtext
import cv2
import boto3
from botocore.exceptions import NoCredentialsError
from email.message import EmailMessage
import ssl
import smtplib
import socket
import requests
from googlesearch import search

# AWS Configurations (Replace with your actual credentials)
aws_access_key_id = 'Aaws access key'
aws_secret_access_key = 'secret access key'
region_name = 'ap-south-1'

# Mappls API key (Replace with your actual Mappls API key)
API_KEY = "1api key"

# Initialize Boto3 clients
ec2 = boto3.client(
    'ec2',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

def open_camera():
    """ Opens a camera feed using OpenCV. """
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Unable to read frame.")
            break
        cv2.imshow('Original', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def apply_sketch(frame):
    """ Applies a sketch effect to a video frame. """
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    inverted_gray_frame = 255 - gray_frame
    blurred_frame = cv2.GaussianBlur(inverted_gray_frame, (21, 21), 0)
    inverted_blurred_frame = 255 - blurred_frame
    sketch = cv2.divide(gray_frame, inverted_blurred_frame, scale=256.0)
    return sketch

def open_camera_with_sketch():
    """ Opens a camera feed with a sketch effect using OpenCV. """
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Unable to read frame.")
            break
        sketch = apply_sketch(frame)
        cv2.imshow('Sketch Effect', sketch)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def update_instance_status():
    """ Updates the status of EC2 instances and displays control buttons. """
    instances = ec2.describe_instances()
    for widget in ec2_frame.winfo_children():
        widget.destroy()

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_state = instance['State']['Name']
            row = tk.Frame(ec2_frame)
            row.pack(fill='x')
            tk.Label(row, text=f"{instance_id} - {instance_state}", width=30).pack(side='left')
            if instance_state == "running":
                action_button = tk.Button(row, text="Stop", command=lambda id=instance_id: stop_instance(id))
                action_button.pack(side='right')
            else:
                action_button = tk.Button(row, text="Start", command=lambda id=instance_id: start_instance(id))
                action_button.pack(side='right')

def start_instance(instance_id):
    """ Starts an EC2 instance by instance ID. """
    ec2.start_instances(InstanceIds=[instance_id])
    messagebox.showinfo("Instance Starting", f"Instance {instance_id} is being started.")
    update_instance_status()

def stop_instance(instance_id):
    """ Stops an EC2 instance by instance ID. """
    ec2.stop_instances(InstanceIds=[instance_id])
    messagebox.showinfo("Instance Stopping", f"Instance {instance_id} is being stopped.")
    update_instance_status()

def list_buckets():
    """ Lists all S3 buckets in the AWS account. """
    buckets = s3.list_buckets()
    bucket_listbox.delete(0, tk.END)
    for bucket in buckets['Buckets']:
        bucket_listbox.insert(tk.END, bucket['Name'])

def list_files():
    """ Lists files in the selected S3 bucket. """
    selected_bucket = bucket_listbox.get(tk.ANCHOR)
    if selected_bucket:
        objects = s3.list_objects(Bucket=selected_bucket)
        file_listbox.delete(0, tk.END)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                file_listbox.insert(tk.END, obj['Key'])

def upload_file():
    """ Uploads a file to the selected S3 bucket. """
    selected_bucket = bucket_listbox.get(tk.ANCHOR)
    if selected_bucket:
        filepath = filedialog.askopenfilename()
        if filepath:
            filename = filepath.split('/')[-1]
            with open(filepath, 'rb') as file_data:
                s3.upload_fileobj(file_data, selected_bucket, filename)
            list_files()
            messagebox.showinfo("Upload Successful", f"Uploaded {filename} to {selected_bucket}")

def delete_file():
    """ Deletes a file from the selected S3 bucket. """
    selected_bucket = bucket_listbox.get(tk.ANCHOR)
    selected_file = file_listbox.get(tk.ANCHOR)
    if selected_bucket and selected_file:
        s3.delete_object(Bucket=selected_bucket, Key=selected_file)
        list_files()
        messagebox.showinfo("Delete Successful", f"Deleted {selected_file} from {selected_bucket}")

def get_current_location():
    """ Retrieves the current location using geolocation API. """
    try:
        response = requests.get("https://api.geolocation.com/v1/location")
        location_data = response.json()
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        return latitude, longitude
    except Exception as e:
        messagebox.showerror("Error", f"Error getting location: {e}")
        return None, None

def reverse_geocode(latitude, longitude):
    """ Reverse geocodes the coordinates to get address using Mappls API. """
    url = f"https://apis.mappls.com/advancedmaps/v1/{API_KEY}/rev_geocode?lat={latitude}&lng={longitude}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        address = data.get("results")[0].get("formatted_address")
        return address
    else:
        messagebox.showerror("Error", f"Error getting address: {response.text}")
        return None

def get_location():
    """ Retrieves and displays the current location. """
    latitude, longitude = get_current_location()
    if latitude and longitude:
        address = reverse_geocode(latitude, longitude)
        if address:
            location_label.config(text=f"Your current location is: {address}")
        else:
            location_label.config(text="Failed to get address from Mappls API")
    else:
        location_label.config(text="Failed to get current location")

def send_email():
    """ Sends an email using SMTP. """
    try:
        email_sender = sender_entry.get()
        email_password = password_entry.get()
        email_receiver = receiver_entry.get()
        subject = subject_entry.get()
        body = body_text.get("1.0", tk.END)

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        
        messagebox.showinfo("Success", "Email sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {str(e)}")

def check_server(ip_address, port):
    """ Checks if a server is running on the specified IP address and port. """
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect((ip_address, port))
        return True
    except socket.error:
        return False
    finally:
        s.close()

def check_ports(ip_address):
    """ Checks common ports on a specified IP address. """
    ports = [80, 443, 22, 21, 25, 53, 110, 143, 3306]
    results = []
    for port in ports:
        if check_server(ip_address, port):
            results.append(f"Server is running on {ip_address}:{port}")
        else:
            results.append(f"Server is NOT running on {ip_address}:{port}")
    return results

def check_server_status():
    """ Retrieves server status for a specified IP address. """
    ip_address = ip_entry.get()
    if not ip_address:
        messagebox.showwarning("Warning", "Please enter an IP address.")
        return
    
    results = check_ports(ip_address)
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    for result in results:
        result_text.insert(tk.END, result + "\n")
    result_text.config(state=tk.DISABLED)

def get_wikipedia_summary(search_term):
    """ Fetches the summary of a Wikipedia page for a given search term. """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": search_term,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return "Error: Unable to fetch data from Wikipedia."
    
    data = response.json()
    
    pages = data["query"]["pages"]
    for page_id, page in pages.items():
        if page_id == "-1":
            return "No page found for the given search term."
        if "extract" in page:
            return page["extract"]
        else:
            return "No summary available for this page."

def search_google(search_term):
    """ Fetches the top 5 Google search results for a given search term. """
    results = []
    try:
        for result in search(search_term, num=5, stop=5):
            results.append(result)
    except Exception as e:
        results.append(f"Error: {str(e)}")
    return results

def search_wikipedia_and_google():
    """ Performs a Wikipedia search and displays the summary and Google search results. """
    search_term = search_entry.get()
    
    # Fetch Wikipedia summary
    summary = get_wikipedia_summary(search_term)
    wiki_result.config(state=tk.NORMAL)
    wiki_result.delete(1.0, tk.END)
    wiki_result.insert(tk.END, summary)
    wiki_result.config(state=tk.DISABLED)
    
    # Fetch Google top results
    google_results = search_google(search_term)
    top_results_text.config(state=tk.NORMAL)
    top_results_text.delete(1.0, tk.END)
    for result in google_results:
        top_results_text.insert(tk.END, result + "\n\n")
    top_results_text.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("Multi-Function Tool")

# Set up tabs for different functionalities
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Tab 1: AWS S3 Operations
s3_frame = ttk.Frame(notebook)
notebook.add(s3_frame, text='AWS S3')

bucket_frame = tk.LabelFrame(s3_frame, text="Buckets")
bucket_frame.pack(padx=10, pady=5, fill="both", expand=True)
bucket_listbox = tk.Listbox(bucket_frame)
bucket_listbox.pack(padx=5, pady=5, fill="both", expand=True)

file_frame = tk.LabelFrame(s3_frame, text="Files in Selected Bucket")
file_frame.pack(padx=10, pady=5, fill="both", expand=True)
file_listbox = tk.Listbox(file_frame)
file_listbox.pack(padx=5, pady=5, fill="both", expand=True)

button_frame_s3 = tk.Frame(s3_frame)
button_frame_s3.pack(padx=10, pady=5, fill="x", expand=True)
list_bucket_button = tk.Button(button_frame_s3, text="List Buckets", command=list_buckets)
list_bucket_button.pack(side="left", expand=True)
upload_button = tk.Button(button_frame_s3, text="Upload File", command=upload_file)
upload_button.pack(side="left", expand=True)
delete_button = tk.Button(button_frame_s3, text="Delete File", command=delete_file)
delete_button.pack(side="left", expand=True)

# Tab 2: Server Status Check
server_frame = ttk.Frame(notebook)
notebook.add(server_frame, text='Server Status')

ip_label = tk.Label(server_frame, text="Enter IP Address:")
ip_label.pack(pady=5)
ip_entry = tk.Entry(server_frame, width=50)
ip_entry.pack(pady=5)

check_button = tk.Button(server_frame, text="Check Server", command=check_server_status)
check_button.pack(pady=10)

result_text = tk.Text(server_frame, height=10, width=60, state=tk.DISABLED)
result_text.pack(pady=10)

# Tab 3: Location Finder
location_frame = ttk.Frame(notebook)
notebook.add(location_frame, text='Location')

location_label = tk.Label(location_frame, text="Click the button to get your current location")
location_label.pack(pady=20)

get_location_button = tk.Button(location_frame, text="Get Location", command=get_location)
get_location_button.pack(pady=10)

# Tab 4: Email Sender
email_frame = ttk.Frame(notebook)
notebook.add(email_frame, text='Email Sender')

sender_label = tk.Label(email_frame, text="Sender Email:")
sender_label.pack(pady=5)
sender_entry = tk.Entry(email_frame, width=50)
sender_entry.pack(pady=5)

password_label = tk.Label(email_frame, text="Sender Password:")
password_label.pack(pady=5)
password_entry = tk.Entry(email_frame, show='*', width=50)
password_entry.pack(pady=5)

receiver_label = tk.Label(email_frame, text="Receiver Email:")
receiver_label.pack(pady=5)
receiver_entry = tk.Entry(email_frame, width=50)
receiver_entry.pack(pady=5)

subject_label = tk.Label(email_frame, text="Subject:")
subject_label.pack(pady=5)
subject_entry = tk.Entry(email_frame, width=50)
subject_entry.pack(pady=5)

body_label = tk.Label(email_frame, text="Body:")
body_label.pack(pady=5)
body_text = tk.Text(email_frame, height=10, width=50)
body_text.pack(pady=5)

send_button = tk.Button(email_frame, text="Send Email", command=send_email)
send_button.pack(pady=10)

# Tab 5: Wikipedia and Google Search
search_frame = ttk.Frame(notebook)
notebook.add(search_frame, text='Search')

input_frame = tk.Frame(search_frame, padx=20, pady=20)
input_frame.pack(side=tk.TOP, fill=tk.X)

tk.Label(input_frame, text="Enter a search term:", font=("Arial", 14)).pack(side=tk.LEFT, padx=10)
search_entry = tk.Entry(input_frame, width=50, font=("Arial", 14))
search_entry.pack(side=tk.LEFT, padx=10)
search_button = tk.Button(input_frame, text="Search", command=search_wikipedia_and_google, font=("Arial", 14))
search_button.pack(side=tk.LEFT, padx=10)

top_results_frame = tk.Frame(search_frame, padx=20, pady=20)
top_results_frame.pack(side=tk.TOP, fill=tk.X)

tk.Label(top_results_frame, text="Top Google Results:", font=("Arial", 14)).pack(pady=10)
top_results_text = scrolledtext.ScrolledText(top_results_frame, wrap=tk.WORD, font=("Arial", 12), height=10, state=tk.DISABLED)
top_results_text.pack(pady=10, fill=tk.X)

wiki_result_frame = tk.Frame(search_frame, padx=20, pady=20)
wiki_result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

tk.Label(wiki_result_frame, text="Wikipedia Summary:", font=("Arial", 14)).pack(pady=10)
wiki_result = scrolledtext.ScrolledText(wiki_result_frame, wrap=tk.WORD, font=("Arial", 12), state=tk.DISABLED)
wiki_result.pack(pady=10, fill=tk.BOTH, expand=True)

# Tab 6: OpenCV Camera
camera_frame = ttk.Frame(notebook)
notebook.add(camera_frame, text='Camera')

camera_button_frame = tk.Frame(camera_frame)
camera_button_frame.pack(pady=10)

open_camera_button = tk.Button(camera_button_frame, text="Open Camera", command=open_camera)
open_camera_button.pack(side=tk.LEFT, padx=10)

sketch_camera_button = tk.Button(camera_button_frame, text="Open Camera with Sketch", command=open_camera_with_sketch)
sketch_camera_button.pack(side=tk.LEFT, padx=10)

# Tab 7: EC2 Instances
ec2_frame = ttk.Frame(notebook)
notebook.add(ec2_frame, text='EC2 Instances')

update_instance_status()

# Run the application
root.mainloop()


# In[ ]:


#FIRST BUTTON

import cv2
import tkinter as tk
from tkinter import messagebox

# Function to apply sketch effect to the frame
def apply_sketch(frame):
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Invert the grayscale frame
    inverted_gray_frame = 255 - gray_frame
    # Apply Gaussian blur to the inverted grayscale frame
    blurred_frame = cv2.GaussianBlur(inverted_gray_frame, (21, 21), 0)
    # Invert the blurred frame
    inverted_blurred_frame = 255 - blurred_frame
    # Create the sketch effect by performing image subtraction
    sketch = cv2.divide(gray_frame, inverted_blurred_frame, scale=256.0)
    return sketch

# Function to open the camera normally
def open_camera():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Unable to read frame.")
            break
        cv2.imshow('Original', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Function to open the camera with sketch effect
def open_camera_with_sketch():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Unable to read frame.")
            break
        sketch = apply_sketch(frame)
        cv2.imshow('Sketch Effect', sketch)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Create the main window
root = tk.Tk()
root.title("Camera App")

# Create a button to open the camera normally
open_camera_button = tk.Button(root, text="Open Camera", command=open_camera)
open_camera_button.pack(pady=10)

# Create a button to open the camera with sketch effect
open_sketch_button = tk.Button(root, text="Open Camera with Sketch", command=open_camera_with_sketch)
open_sketch_button.pack(pady=10)

# Run the application
root.mainloop()

