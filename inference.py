import os
import torch
import logging
import argparse
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline, DiffusionPipeline


def inference(args):
    try:
        generator = torch.Generator(device="cpu").manual_seed(args.seed)

        pipe = DiffusionPipeline.from_pretrained(
            "/app/models",
            use_safetensors=True,
            torch_dtype=torch.float16, 
            variant="fp16", 
        )
        pipe.load_lora_weights(f"{args.lora_model}/pytorch_lora_weights.safetensors")

        _ = pipe.to("cuda")

        image = pipe(
            prompt=args.prompt, 
            num_inference_steps=args.num_inf_steps,
            generator=generator).images[0]

 
        image.save(f"{args.output}/image_{args.seed}.png")

    except Exception as err:
        logging.error(f"Error: {err}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to infer Dreambooth LORA model')

    # prompt
    parser.add_argument('--prompt', type=str, help='Prompt for the instance')
    parser.add_argument('--num_inf_steps', type=int, default=50, help='Number of inference steps')
    parser.add_argument('--lora_model', type=str, default="/inputs", help="Path to lora model")
    parser.add_argument('--output', type=str, default='/outputs', help='Output path')
    parser.add_argument('--seed', type=int, default=42, help='Seed for inference')
    args = parser.parse_args()

    inference(args=args)