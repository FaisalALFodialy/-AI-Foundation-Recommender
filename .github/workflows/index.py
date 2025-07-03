import streamlit as st
from openai import OpenAI
import requests
from dotenv import load_dotenv
import os
import json


load_dotenv()
print("IMGBB Key:", os.getenv("IMGBB_API_KEY"))

# Initialize OpenAI client
client = OpenAI(api_key="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")

st.title("💄 AI Foundation Recommender")
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

    with st.spinner("Analyzing your skin and finding the best foundation product for you..."):
        completion = client.chat.completions.create(
            model="gpt-4-turbo",  # if only this is available,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional AI beauty assistant specializing in analyzing selfies and recommending the best foundation product using the skin level dataset provided internally. Always respond in JSON with fields: skin_tone_detected, undertone_detected, skin_type_detected, recommended_product, why_this_product_is_recommended."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this selfie and recommend the best foundation product based on my skin tone, undertone, and skin type."
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
        parsed = json.loads(result)
        st.success("Recommendation generated!")
        st.json(parsed)
    except json.JSONDecodeError:
        st.error("The AI did not return JSON. Displaying raw output:")
        st.write(result)
