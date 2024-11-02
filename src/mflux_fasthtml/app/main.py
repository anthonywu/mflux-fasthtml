# noqa: F405
import logging
import os
import time
from pathlib import Path

from fasthtml.common import *  # noqa: F403
from uuid_extensions import uuid7str

from mflux_fasthtml.app import worker
from mflux_fasthtml.app.storage import Generation, gens
from mflux_fasthtml.app.utils import safe_cast

tailwind_cdn = Script(src="https://cdn.tailwindcss.com")


async def startup():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    print("Starting the background worker...")
    worker.mlx_cleanup()
    worker.image_generator_thread.start()


async def shutdown():
    print("Stopping the background worker...")
    worker.stop_event.set()
    worker.image_generator_thread.join(timeout=30)
    worker.mlx_cleanup()
    print("Stopped the background worker...")


app, rt = fast_app(hdrs=(tailwind_cdn,), on_startup=[startup], on_shutdown=[shutdown])

reg_re_param("imgext", "ico|gif|GIF|heic|HEIC|jpg|JPG|jpeg|JPEG|png|PNG|webp|WEBP")
app.static_route_exts(prefix="/", static_path=Path(".").resolve(), exts="imgext")
setup_toasts(app)

DEFAULT_OUTPUT_DIR = Path(".").resolve()


# Main page
@app.get("/")
def home():
    # fmt: off
    generate_next = Form(
        Div(
            Fieldset(
                Legend("Model"),
                Label(Input("Schnell", name="model", type="radio", value="schnell", checked=True)),
                Label(Input("Dev", name="model", type="radio", value="dev")),
            ),
            Fieldset(
                Legend("Quantize"),
                Label(Input("No", name="quantize", type="radio", value="0", checked=True)),
                Label(Input("4", name="quantize", type="radio", value="4")),
                Label(Input("8", name="quantize", type="radio", value="8")),
            ),
            cls="grid"
        ),
        Hr(),
        Div(
            Div(
                Label(
                    "Width",
                    Input(
                        id="new-width",
                        name="width",
                        type="number",
                        step="16",
                        value="1024",
                    ),
                ),
                Label(
                    "Height",
                    Input(
                        id="new-height",
                        name="height",
                        type="number",
                        step="16",
                        value="1024",
                    ),
                ),
                cls="grid"
            ),
            Div(
                Label("Steps"),
                Input(
                    id="new-steps",
                    name="steps",
                    type="number",
                    min="2",
                    max="60",
                    step="1",
                    value="4",
                ),
            ),
            Div(
                Label("Guidance"),
                Input(
                    id="new-guidance",
                    name="guidance",
                    type="number",
                    step="0.1",
                    value="3.5",
                ),
            ),
            Div(
                Label("Seed"),
                Input(id="new-seed", name="seed", type="number", placeholder="random"),
            ),
            cls="grid"
        ),
        Div(
            Textarea(
                id="new-prompt",
                name="prompt",
                rows=20
            )("a quick brown fox jumped over the lazy dog."),
            cls="grid"
        ),
        Div(
            Label("Choose output Folder: "),
            Input(
                id="new-output-dir",
                name="output_dir",
                value=DEFAULT_OUTPUT_DIR,
            ),
        ),
        Div(Button("Generate")),
        hx_post="/generate",
        target_id="gen-list",
        hx_swap="afterbegin",
    )
    # fmt: on

    todo_gens = gens(where="completed_at IS NULL")
    todo_gen_containers = [
        generation_preview(g) for g in todo_gens[:10]
    ]  # Start with last 10
    gen_list = Div(*reversed(todo_gen_containers), id="gen-list", cls="overflow-x-auto")
    return Title("MFlux Image Generation"), Main(
        Hgroup(
            H1("MFlux Image Generation"),
            P("the web gui over MLX-powered Flux image generation"),
        ),
        Hr(),
        generate_next,
        Hr(),
        Div(B(len(todo_gens)), Span(" generations in the queue")),
        H2("Generations"),
        gen_list,
        Hr(),
        cls="container",
    )


# Show the image (if available) and prompt for a generation
def generation_preview(g):
    grid_cls = "box col-xs-12 col-sm-6 col-md-4 col-lg-3"
    if g.is_completed:
        return Div(
            Card(
                Img(
                    src=str(g.output_path.relative_to(Path(".").resolve())),
                    alt="Card image",
                    cls="card-img-top",
                ),
                Div(
                    P(B("Prompt: "), g.prompt, cls="card-text"),
                    P(B("Seed: "), g.seed, cls="card-text"),
                ),
                cls="card-body",
            ),
            cls=grid_cls,
            id=f"gen-{g.uid}",
        )

    return Div(
        P(f"Queued: {g.uid} with prompt {g.prompt} and seed {g.seed}", cls="card-text"),
        id=f"gen-{g.uid}",
        hx_get=f"/gens/{g.uid}",
        hx_trigger="every 10s",
        hx_swap="outerHTML",
        cls=grid_cls,
    )


# A pending preview keeps polling this route until we return the image preview
@app.get("/gens/{uid}")
def preview(uid: str):
    return generation_preview(gens.get(uid))


# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname: str, ext: str):
    return FileResponse(f"{fname}.{ext}")


# Generation route
@app.post("/generate")
def post(
    model: str,
    prompt: str,
    height: int,
    width: int,
    guidance: float,
    steps: int,
    seed: str,
    quantize: int | None,
    output_dir: str,
):
    os.makedirs(output_dir, exist_ok=True)
    g = gens.insert(
        Generation(
            uid=uuid7str(),
            model=model,
            prompt=prompt,
            height=height,
            width=width,
            guidance=guidance,
            quantize=safe_cast(quantize, int) if quantize > 0 else None,
            seed=safe_cast(seed, str) or int(time.time()),
            steps=steps,
            output_dir=output_dir,
        )
    )
    return generation_preview(g)

def run():
    serve()

serve()
