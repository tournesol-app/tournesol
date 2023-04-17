

from django.conf import settings
from PIL import Image, ImageDraw

BASE_DIR = settings.BASE_DIR


class PreviewDrawer():
    def draw_text_center(self, image: Image, text, font, text_color):
        draw = ImageDraw.Draw(image)
        text_size = draw.textsize(
            text,
            font
        )
        text_pos = ((image.size[0] - text_size[0]) / 2, (image.size[1] - text_size[1]) / 2)
        draw.text(
            text_pos,
            text,
            font=font,
            fill=text_color,
        )

    def get_ts_logo(self, size: tuple):
        return (
            Image.open(BASE_DIR / "tournesol/resources/Logo64.png")
            .convert("RGBA")
            .resize(size)
        )

    def draw_tournesol_score_box(self, recommendation, image: Image, fnt_config, upscale_ratio):

        ts_score_box = Image.new(
            "RGBA", (200 * upscale_ratio, 20 * upscale_ratio), 'white'
        )
        ts_score_box_draw = ImageDraw.Draw(ts_score_box)

        ts_logo_size = (12 * upscale_ratio, 12 * upscale_ratio)
        ts_logo = self.get_ts_logo(ts_logo_size)
        ts_score_box.alpha_composite(
                ts_logo,
                dest=(0, 0),
            )

        score = str(round(recommendation.tournesol_score))
        comparisons = str(recommendation.rating_n_ratings) + ' comparisons by '
        contributors = str(recommendation.rating_n_contributors) + ' contributors'

        score_size = ts_score_box_draw.textsize(score, fnt_config["entity_title"])
        comparisons_size = ts_score_box_draw.textsize(
            comparisons,
            fnt_config["recommendations_rating"]
            )

        score_x_gap = ts_logo_size[0]
        comparisons_x_gap = score_x_gap + score_size[0] + 2 * upscale_ratio
        contributors_x_gap = comparisons_x_gap + comparisons_size[0]

        ts_score_box_draw.text(
            (score_x_gap, -4 * upscale_ratio),
            score,
            font=fnt_config["entity_title"],
            fill=(29, 26, 20, 255),
        )

        ts_score_box_draw.text(
            (comparisons_x_gap, 2 * upscale_ratio),
            comparisons,
            font=fnt_config["recommendations_rating"],
            fill=(160, 155, 135, 255),
        )

        ts_score_box_draw.text(
            (contributors_x_gap, 2 * upscale_ratio),
            contributors,
            font=fnt_config["recommendations_rating"],
            fill="#B38B00",
        )

        image.paste(ts_score_box, (110 * upscale_ratio, 25 * upscale_ratio))
