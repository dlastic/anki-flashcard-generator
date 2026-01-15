import argparse
import sys

from dotenv import load_dotenv
from loguru import logger


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Language description")
    parser.add_argument(
        "-s",
        "--source",
        default="EN",
        type=str.upper,
        help="Source language (default: EN)",
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        type=str.upper,
        help="Target language (required)",
    )
    parser.add_argument(
        "-c",
        "--count",
        default=5,
        type=int,
        help="Maximum number of sentences to translate (default: 5)",
    )
    parser.add_argument(
        "-a",
        "--api",
        default="gemini",
        type=str.lower,
        choices=["gemini", "openai"],
        help="LLM API to use: 'gemini' or 'openai' (default: gemini)",
    )
    return parser


def setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )


def load_environment() -> None:
    load_dotenv()
