import gc
import logging
import sys
import threading
import time
from pathlib import Path

import mlx.core.metal as metal
from mflux import Config, Flux1, ModelConfig, StopImageGenerationException

from mflux_fasthtml.app.storage import gens

logger = logging.getLogger(__name__)


def mlx_cleanup():
    """Cleanup any memory hogging by the prior run."""
    ops = []
    if metal.is_available():
        ops.append(metal.clear_cache)
        ops.append(metal.reset_peak_memory)
    ops.append(gc.collect)
    for cleanup_op in ops:
        try:
            cleanup_op()
        except (RuntimeError, MemoryError, SystemError) as e:
            logging.exception(e)


# Create a global event to signal stopping
stop_event = threading.Event()


def background_worker(empty_pause_interval_seconds=5):
    """Continuously check for queued image generation and execute it."""
    if stop_event.is_set():
        return

    while True:
        try:
            next_gen = gens(where="completed_at IS NULL", limit=1)[0]
        except IndexError:
            # where-clause returned empty
            time.sleep(empty_pause_interval_seconds)
            continue

        if next_gen.output_path.exists():
            # a prior job already completed
            gens.update({"completed_at": int(time.time())}, pk_values=[next_gen.uid])
        else:
            try:
                if generate_image(next_gen):
                    gens.update(
                        {"completed_at": int(time.time())}, pk_values=[next_gen.uid]
                    )
            except (RuntimeError, MemoryError, SystemError) as e:
                mlx_cleanup()
                logging.exception(e)


def generate_image(gen):
    if stop_event.is_set():
        return False

    flux = Flux1(
        model_config=ModelConfig.from_alias(gen.model),
        quantize=gen.quantize,
        lora_paths=gen.lora_paths,
        lora_scales=gen.lora_scales,
    )
    try:
        # Generate an image
        image = flux.generate_image(
            seed=int(time.time()) if gen.seed is None else gen.seed,
            prompt=gen.prompt,
            stepwise_output_dir=Path(gen.stepwise_image_output_dir),
            config=Config(
                num_inference_steps=gen.steps,
                height=gen.height,
                width=gen.width,
                guidance=gen.guidance,
                init_image_path=gen.init_image_path,
                init_image_strength=gen.init_image_strength,
            ),
        )

        # Save the image
        image.save(path=gen.output, export_json_metadata=gen.metadata)
        del image
        return True
    except StopImageGenerationException as stop_exc:
        return False
        print(stop_exc)
    finally:
        try:
            del flux
        except NameError:
            pass
        mlx_cleanup()


image_generator_thread = threading.Thread(target=background_worker, daemon=True)
