import argparse
from waifu2x import run

def upscale_image(input_file, output_file):
    # model_path = "models/anime_style_art_rgb"  # default model for waifu2x-chainer
    # waifu2x = Waifu2x(model_path=model_path)

    # call waifu2x.upscale() to upscale images
    run(input_file, output_file, scale_ratio=4.0)  # magnify by 2x

    # waifu2x.upscale(input_file, output_file, mag=2)  # magnify by 2x

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upscale images using waifu2x.')
    parser.add_argument('--input', type=str, help='Path to the input image.')
    parser.add_argument('--output', type=str, help='Path to save the upscaled image.')

    args = parser.parse_args()
    
    upscale_image(args.input, args.output)
