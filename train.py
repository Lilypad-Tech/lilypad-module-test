import argparse
import os
import subprocess
import shutil
from datetime import datetime

def main(args):
    start_time = datetime.now()
    
    if not args.prompt:
        print("PROMPT is not set. Exiting.")
        exit(1)

    # Create directory if it does not exist
    os.makedirs(os.path.expanduser('~/.cache/huggingface/accelerate'), exist_ok=True)

    # Copy the pre-configured default_config.yaml
    shutil.copy('./default_config.yaml', os.path.expanduser('~/.cache/huggingface/accelerate/default_config.yaml'))

    # Change working directory
    os.chdir('./diffusers/examples/dreambooth')

    # Train dreambooth_lora_sdxl with the provided arguments
    cmd = [
        "accelerate", "launch", "train_dreambooth_lora_sdxl.py",
        "--pretrained_model_name_or_path=/app/models",
        "--instance_data_dir", args.input,
        "--output_dir", args.output,
        "--instance_prompt", args.prompt,
        "--resolution", "1024",
        "--gradient_checkpointing",
        "--gradient_accumulation_steps", "1",
        "--train_batch_size", "1",
        "--learning_rate", "1e-4",
        "--lr_scheduler", "constant",
        "--lr_warmup_steps", "0",
        "--max_train_steps", str(args.steps),
        "--seed", "0",
        "--use_8bit_adam",
        # "--enable_xformers_memory_efficient_attention"
    ]
    
    # Run the command and capture the output
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    print(f"stdout: \n\n{stdout}")
    print(f"stderr: \n\n{stderr}")

    # Calculate and print the elapsed time
    elapsed_time = datetime.now() - start_time
    print(f"Time elapsed since start of script: {elapsed_time.seconds} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to train Dreambooth model')
    parser.add_argument('--prompt', type=str, help='Prompt for the instance')
    parser.add_argument('--input', type=str, default="/inputs", help='Path to input directory with instance data')
    parser.add_argument('--output', type=str, default="/outputs", help='Path to output directory to save trained model')
    parser.add_argument('--steps', type=int, default=500, help='Number of training steps (default: 500)')
    
    args = parser.parse_args()
    
    main(args)
