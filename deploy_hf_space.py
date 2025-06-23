
from huggingface_hub import HfApi

api = HfApi()
repo_id = "corentinm7/IMPatienT"

api.add_space_secret(repo_id=repo_id, key="SECRET_KEY", value="XXXXXX")
api.add_space_secret(repo_id=repo_id, key="MAIL_SERVER", value="XXXXXX")
api.add_space_secret(repo_id=repo_id, key="MAIL_PORT", value="25")
api.add_space_secret(repo_id=repo_id, key="MAIL_USERNAME", value="XXXXXX")
api.add_space_secret(repo_id=repo_id, key="MAIL_PASSWORD", value="XXXXXX")
api.add_space_secret(repo_id=repo_id, key="ADMINS_EMAIL", value="XXXXXX")

api.upload_folder(
    folder_path=".",
    repo_id=repo_id,
    repo_type="space",
    allow_patterns=[
        "data",
        "docker",
        "src",
        ".flaskenv",
        ".gitattributes",
        ".gitignore",
        ".python-version",
        "deploy_hf_space.py",
        "requirements.txt",
        "README.md",
        "pyproject.toml",
        "uv.lock",
        "dev_boot.sh",
        "Dockerfile",
        "LICENSE",
        "*.demo",
        "*.js",
        "*.css",
        "*.html",
        "*.py",
        "*.sh",
        "*.json",
        "*.jpg",
        "*.png",
        "*.pkl",
        "*.json",
        "*.npy",
        "*.txt",
        "*.md",
        "*.ini",
        "*.mako",
        "README",
        ".gitkeep",
    ],
    ignore_patterns=[
        ".venv",
        ".github",
        "dpcs",
        "flask_session",
        "joblib_cache",
        "logs",
        "notebooks",
        "tests",
        "libcairo.2.dylib",
        "ontology.json",
    ],
)
