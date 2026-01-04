import os
import sys
from google import genai
from google.genai import types
from PIL import Image
import io

# Check for API key
if "GEMINI_API_KEY" not in os.environ:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_image(prompt, model="gemini-3-pro-image-preview", output_file="output.png"):
    """
    Generates an image using the specified Gemini model.
    """
    print(f"Generating image with {model}...")
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="image/png"
            )
        )

        # Handle the response based on the SDK version and response structure
        # This is a generalized way to handle image data
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    image = Image.open(io.BytesIO(image_data))
                    image.save(output_file)
                    print(f"Image saved to {output_file}")
                    return True

        print("No image data found in response.")
        return False

    except Exception as e:
        print(f"Error generating image: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    prompt = "A futuristic city with neon signs saying 'Gemini 3' and 'Banana Pro'"

    # Try Nano Banana Pro (Gemini 3 Pro Image)
    generate_image(prompt, model="gemini-3-pro-image-preview", output_file="gemini_3_pro.png")

    # Try Nano Banana (Gemini 2.5 Flash Image)
    generate_image(prompt, model="gemini-2.5-flash-image", output_file="gemini_2_5_flash.png")
