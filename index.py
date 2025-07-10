import streamlit as st
from openai import OpenAI
import requests
from dotenv import load_dotenv
import os
import json
import ast


load_dotenv()
print("IMGBB Key:", os.getenv("IMGBB_API_KEY"))

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("💄 AI Foundation & Concealer Recommender")
st.write("Upload your selfie, and let AI analyze your skin tone, undertone, and skin type to recommend the best foundation product for you.")

uploaded_file = st.file_uploader("Upload a clear selfie (jpg/png)", type=["jpg", "jpeg", "png"])

def upload_to_imgbb(image_bytes):
    """Upload image to ImgBB for a temporary public URL (free, easy testing)."""
    API_KEY = os.getenv("IMGBB_API_KEY")
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": API_KEY},
        files={"image": image_bytes}
    )
    if response.status_code == 200:
        st.success("Image uploaded successfully.")
        return response.json()["data"]["url"]
    else:
        st.error(f"Failed to upload image. Status code: {response.status_code}. Response: {response.text}")
        st.stop()

if uploaded_file:
    if uploaded_file.type not in ["image/jpeg", "image/png"]:
        st.error("Unsupported image format. Please upload a JPEG or PNG image.")
        st.stop()

    # Upload image to get a public URL
    image_url = upload_to_imgbb(uploaded_file)

    with st.spinner("Analyzing your skin and finding the best foundation and concealer for you..."):
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional AI beauty assistant specializing in analyzing selfies to recommend foundation and concealer. "
                        "You will detect the user's skin tone, undertone, and skin type. "
                        "You will then recommend the best foundation and concealer based on these detected values, following these rules: "
                        "- Concealer should be 1-2 shades lighter than the foundation shade. "
                        "- Concealer should match the same undertone as the foundation. "
                        "- Concealer formula should match the user's skin type (hydrating for dry, matte for oily/combination). "
                        "Always respond ONLY with strict JSON in the format: "
                        "{\"skin_tone_detected\": \"\", \"undertone_detected\": \"\", \"skin_type_detected\": \"\", "
                        "\"recommended_foundation\": \"\", \"why_foundation_is_recommended\": \"\", "
                        "\"recommended_concealer\": \"\", \"why_concealer_is_recommended\": \"\"} without any explanation."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this selfie and recommend the best foundation and concealer based on my skin tone, undertone, and skin type."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        )
        
        result = completion.choices[0].message.content

    try:
        # Strip leading/trailing whitespace
        cleaned_result = result.strip()

        # Attempt standard JSON parsing
        parsed = json.loads(cleaned_result)
        st.success("Recommendation generated!")
        st.json(parsed)

    except json.JSONDecodeError:
        try:
            # Fallback: use ast.literal_eval for valid Python dict strings
            parsed = ast.literal_eval(cleaned_result)
            st.success("Recommendation generated!")
            st.json(parsed)
        except Exception:
            st.error("The AI did not return JSON. Displaying raw output:")
            st.code(result, language='json')
