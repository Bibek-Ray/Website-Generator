# backend/main.py
from dotenv import load_dotenv
import sys
from generator import generate_frontend_site, save_generated_site
load_dotenv()

def main():
    # Example usage:
    user_prompt = """I need a vibrant, colorful website to sell kid's toys. The website should evoke fun, creativity, and playfulness that appeals to both children and their parents. The design should incorporate bright colors like red, blue, yellow, and green, and feature cartoon-like illustrations, playful typography, and engaging visuals.

The purpose of the website is to showcase and sell a wide range of high-quality, safe, and educational toys. It should make it easy for parents to browse through different toy categories and help capture the attention of young visitors.

Please design the website with the following sections in mind:
- **Hero:** A visually engaging introduction with a catchy tagline and inviting imagery.
- **Products:** A section that highlights various toy categories (e.g., featured toys, bestsellers) with images, short descriptions, and prices.
- **Testimonials:** A space to display customer reviews and feedback from satisfied parents.
- **About Us:** Information about the brand, its mission, and its commitment to quality and safety.
- **Contact:** A section for inquiries and customer support, including a simple contact form.
- **Footer:** Additional links, social media icons, and perhaps a newsletter signup area.

The overall design should be energetic and easy to navigate, with clear call-to-action buttons that guide users toward making a purchase.
"""

    html, css = generate_frontend_site(user_prompt)
    site_dir = save_generated_site("001", html, css)
    print(f"Site generated at: {site_dir}")

if __name__ == "__main__":
    main()