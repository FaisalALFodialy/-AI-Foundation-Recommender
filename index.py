import streamlit as st
from openai import OpenAI
import base64
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("💄 AI Foundation Recommender")

uploaded_file = st.file_uploader("Upload your clear selfie (jpg/png). Image stays private.", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Read and encode image
    image_bytes = uploaded_file.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    with st.spinner("Analyzing your skin securely..."):
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional AI beauty assistant specializing in analyzing selfies to recommend the best foundation and concealer. "
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
                            "type": "image_data",
                            "image_data": {
                                "b64_json": encoded_image
                            }
                        }
                    ]
                }
            ]
        )

        result = response.choices[0].message.content.strip()

    st.success("Analysis complete. Here is your recommendation:")
    st.json(result)
