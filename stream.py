import streamlit as st
import torch
import numpy as np
from transformers import pipeline
from diffusers import StableDiffusionControlNetImg2ImgPipeline, ControlNetModel, UniPCMultistepScheduler
from diffusers.utils import load_image, make_image_grid
from PIL import Image
import requests
from io import BytesIO

# Initialize the depth estimator
depth_estimator = pipeline("depth-estimation")

# Function to load an image from a URL
def load_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

# Function to get depth map
def get_depth_map(image, depth_estimator):
    image = depth_estimator(image)["depth"]
    image = np.array(image)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    detected_map = torch.from_numpy(image).float() / 255.0
    depth_map = detected_map.permute(2, 0, 1)
    return depth_map

# Streamlit UI
st.title("Image Modification with ControlNet and Stable Diffusion")

# User inputs
image_url = st.text_input("Enter the URL of a farm image:", "")
prompt = st.text_input("Enter your prompt:", "vineyard agrotourism service on the farm")

if st.button("Generate"):
    if image_url:
        # Load the image
        farm_image = load_image_from_url(image_url)
        
        # Process image for depth map
        depth_map = get_depth_map(farm_image, depth_estimator).unsqueeze(0).half().to("cuda")

        # Load the ControlNet model and the StableDiffusionControlNetImg2ImgPipeline
        controlnet = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-normal", torch_dtype=torch.float16, use_safetensors=True)
        pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=torch.float16,
            use_safetensors=True
        ).to("cuda")
        pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
        pipe.enable_model_cpu_offload()

        # Generate the image
        output = pipe(
            prompt,
            image=farm_image,
            control_image=depth_map,
        ).images[0]

        # Convert PIL images to display in Streamlit
        st.image(farm_image, caption="Original Image")
        st.image(output, caption="Generated Image")
    else:
        st.write("Please enter an image URL.")
