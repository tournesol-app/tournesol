from PIL import Image, ImageDraw, ImageFont


def generate_analytics_preview(thumbnail_file_path: str, target_file_path: str):
    tournesol_footer = Image.new("RGBA", (320, 60), (255, 200, 0, 255))
    fnt = ImageFont.truetype("../../frontend/public/fonts/Poppins-Bold.ttf", 40)
    tournesol_footer_draw = ImageDraw.Draw(tournesol_footer)
    tournesol_footer_draw.text((10, 0), "by", font=fnt, fill=(29, 26, 20, 255))
    tournesol_footer_draw.text((80, 0), "Tournesol", font=fnt, fill=(29, 26, 20, 255))

    # TODO double check that this should be always 320x180.
    youtube_thumbnail = Image.open(thumbnail_file_path).convert("RGBA") 

    # Merges the two images into one
    preview_image = Image.new("RGBA", (320, 240), (255, 255, 255, 0))
    preview_image.paste(youtube_thumbnail)
    preview_image.paste(tournesol_footer, box=(0, 180))
    preview_image.save(target_file_path)

    youtube_thumbnail.close()
    return preview_image

def generate_comparison_preview(thumbnail_file_path_left: str, thumbnail_file_path_right: str, target_file_path: str):
    tournesol_footer = Image.new("RGBA", (320, 60), (255, 200, 0, 255))
    fnt = ImageFont.truetype("../../frontend/public/fonts/Poppins-Bold.ttf", 40)
    tournesol_footer_draw = ImageDraw.Draw(tournesol_footer)
    tournesol_footer_draw.text((10, 0), "by", font=fnt, fill=(29, 26, 20, 255))
    tournesol_footer_draw.text((80, 0), "Tournesol", font=fnt, fill=(29, 26, 20, 255))

    # TODO double check that this should be always 320x180.
    youtube_thumbnail_left = Image.open(thumbnail_file_path_left).convert("RGBA") 
    youtube_thumbnail_right = Image.open(thumbnail_file_path_right).convert("RGBA") 

    youtube_thumbnail_left.resize((160, 90))
    youtube_thumbnail_right.resize((160, 90))

    # Merges the two images into one
    preview_image = Image.new("RGBA", (320, 150), (255, 255, 255, 0))
    preview_image.paste(youtube_thumbnail_left.resize((160, 90)))
    preview_image.paste(youtube_thumbnail_right.resize((160, 90)), box=(160, 0))
    preview_image.paste(tournesol_footer, box=(0, 90))
    preview_image.save(target_file_path)

    youtube_thumbnail_left.close()
    youtube_thumbnail_right.close()
    return preview_image


img = generate_analytics_preview("veritasium.jpeg", "preview_analytics_veristasium.png")
img.show()

img = generate_comparison_preview("veritasium.jpeg", "veritasium.jpeg", "preview_comparison_veristasium.png")
img.show()
