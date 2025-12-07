from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# Load environment variables from .env file (assuming GOOGLE_API_KEY is defined there)
load_dotenv()

# Configure the Gemini API client
# The GOOGLE_API_KEY is retrieved from the environment variables loaded above.
# NOTE: This API key is required to use the Google Generative AI service.
headers = {
    "authorization": st.secrets["AUTH key"],
    "content-type": "application/json"
}

def get_gemini_response(input_prompt, image_parts):
    """
    Sends the user's prompt and image data to the Gemini 1.5 Pro model for detailed analysis.
    """
    # Using gemini-1.5-pro for its high-quality vision and reasoning capabilities
    model = genai.GenerativeModel('gemini-2.5-flash')
    # The image_parts list contains the image data. We combine the text prompt and the first image part.
    response = model.generate_content([input_prompt, image_parts[0]])
    return response.text

def input_image_setup(uploaded_file, captured_image_bytes):
    """
    Prepare the uploaded file or captured image bytes for the Gemini API call.
    Returns a list of image parts in the required format for the API.
    """
    bytes_data = None
    mime_type = None
    
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        mime_type = uploaded_file.type
    elif captured_image_bytes is not None:
        bytes_data = captured_image_bytes
        # Assuming camera input returns a JPEG image
        mime_type = "image/jpeg"
    else:
        # This should ideally be caught before calling this function
        raise FileNotFoundError("No file uploaded or image captured.")
    
    image_parts = [
        {
            "mime_type": mime_type,
            "data": bytes_data
        }
    ]
    return image_parts

# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Plant Disease Detector")
st.header("AI Plant Disease Detector 🌿🔬")
st.markdown("Upload an image of a leaf to get an expert diagnosis, symptom analysis, and treatment plan.")

# --- Image Input Section ---
st.subheader("Leaf Image Input")
source = st.radio("Choose image source:", ("Upload an image", "Take a picture"))

uploaded_file = None
captured_image_bytes = None

if source == "Upload an image":
    uploaded_file = st.file_uploader("Choose a leaf image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Leaf Image.", use_column_width=True)
        except Exception as e:
            st.error(f"Error loading image: {e}")
else:  # Take a picture
    captured_image = st.camera_input("Take a picture of the plant leaf")
    if captured_image:
        captured_image_bytes = captured_image.getvalue()
        # Optionally display the captured image
        st.image(captured_image, caption="Captured Leaf Image.", use_column_width=True)
    
submit = st.button("Analyze Leaf Disease")

# --- Processing Logic ---
if submit:
    if uploaded_file is None and captured_image_bytes is None:
        st.warning("Please upload a leaf image or take a picture to proceed with the analysis.")
    else:
        try:
            # Prepare image data for the API call
            image_data = input_image_setup(uploaded_file, captured_image_bytes)

            # Customized prompt for plant pathology analysis
            input_prompt = """
            You are an expert agricultural scientist and certified plant pathologist. Your task is to analyze the provided image of a plant leaf and give a complete, detailed diagnosis and recommendation.

            Structure your response into the following three sections using markdown headings:

            ### 1. Plant & Disease Identification
            - **Plant Species (if identifiable):** [Identify the specific plant/crop]
            - **Diagnosis:** [Identify the most probable disease, pest, or deficiency (e.g., Late Blight, Spider Mites, Iron Deficiency)]
            - **Cause Type:** [e.g., Fungal, Bacterial, Viral, Insect Pest, Nutrient Deficiency, Environmental Stress]

            ### 2. Symptom Analysis
            - Describe the specific visual symptoms observed in the image (e.g., presence of chlorosis, necrosis, lesions, mold, wilting pattern).
            - Explain what these symptoms indicate about the health of the plant and the progression of the issue.

            ### 3. Recommended Treatment & Prevention
            - **Immediate Treatment:** Provide specific, actionable steps to treat the identified issue (e.g., suggested fungicide/pesticide type, proper pruning, isolation).
            - **Long-term Prevention:** Suggest strategies for preventing recurrence, including optimal soil management, watering schedules, and proper environmental conditions.

            Maintain a professional, informative, and easy-to-understand tone suitable for a gardener or farmer.
            """

            # Call the Gemini API with the specialized prompt and image data
            with st.spinner("Analyzing the leaf image and generating the plant health report... 🧪🌱"):
                response = get_gemini_response(input_prompt, image_data)

            st.subheader("🔬 Plant Health Report and Treatment Plan")
            # Display the detailed, structured response
            st.markdown(response)

        except FileNotFoundError as fnfe:
            st.error(f"File Error: {fnfe}")

        except Exception as e:
            # Provide a general error message if the API call or processing fails

            st.error(f"An unexpected error occurred during analysis: {e}")


