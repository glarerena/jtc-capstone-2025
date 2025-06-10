from setuptools import setup, find_packages

setup(
    name="hero-chatbot",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "langchain",
        "langchain-community",
        "langchain-huggingface",
        "langchain-ollama",
        "faiss-cpu",
        "deep-translator",
        "pydantic",
        "aiofiles",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "hero-chatbot=app.main:app",
        ],
    },
)
