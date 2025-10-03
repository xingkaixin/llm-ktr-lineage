import asyncio
import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from httpx import AsyncClient
from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.openai import OpenAIProvider
from tqdm import tqdm

# Configuration
load_dotenv()

# Setup logging
logger.add("app.log", rotation="10 MB", retention="7 days", level="INFO")
logger.add("error.log", rotation="10 MB", retention="30 days", level="ERROR")


class KTRProcessor:
    def __init__(self):
        self.api_endpoint = os.getenv("API_ENDPOINTS")
        self.api_token = os.getenv("API_TOKEN")
        self.system_prompt = os.getenv("SYSTEM_PROMPT")
        self.model_name = os.getenv("MODEL_NAME")
        self.provider = os.getenv("PROVIDER")

        if not all([self.api_endpoint, self.api_token, self.system_prompt]):
            raise ValueError("Missing required environment variables")

        # Initialize Pydantic AI agent
        if self.provider == "OpenAI":
            model = OpenAIChatModel(
                self.model_name,
                provider=OpenAIProvider(
                    base_url=self.api_endpoint, api_key=self.api_token
                ),
            )
        elif self.provider == "Anthropic":
            custom_http_client = AsyncClient(
                base_url=self.api_endpoint,
                headers={
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
            )
            model = AnthropicModel(
                self.model_name,
                provider=AnthropicProvider(
                    api_key=self.api_token, http_client=custom_http_client
                ),
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        self.agent = Agent(model, system_prompt=self.system_prompt)

        # Ensure directories exist
        Path("output").mkdir(exist_ok=True)

        # Track failed files
        self.failed_files: List[str] = []

    def find_ktr_files(self, sample_dir: str = "./sample") -> List[Path]:
        """Find all .ktr files in the sample directory"""
        sample_path = Path(sample_dir)
        if not sample_path.exists():
            logger.error(f"Sample directory {sample_dir} does not exist")
            return []

        ktr_files = list(sample_path.glob("*.ktr"))
        logger.info(f"Found {len(ktr_files)} KTR files in {sample_dir}")
        return ktr_files

    async def process_single_file(self, file_path: Path) -> Optional[str]:
        """Process a single KTR file and return the LLM response"""
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(f"Processing file: {file_path.name}")

            # Call LLM
            result = await self.agent.run(content)
            response = result.output

            logger.info(f"LLM usage: {result.usage()}")

            # Save response to output file
            output_path = Path("output") / f"{file_path.stem}.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(response)

            logger.info(f"Successfully processed {file_path.name} -> {output_path}")
            return response

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {str(e)}")
            self.failed_files.append(str(file_path))
            return None

    async def process_all_files(self):
        """Process all KTR files with progress bar"""
        ktr_files = self.find_ktr_files()

        if not ktr_files:
            logger.warning("No KTR files found to process")
            return

        logger.info(f"Starting to process {len(ktr_files)} files")

        # Process files with progress bar
        with tqdm(total=len(ktr_files), desc="Processing KTR files") as pbar:
            for file_path in ktr_files:
                await self.process_single_file(file_path)
                pbar.update(1)

        # Write failed files report if any
        if self.failed_files:
            self.write_failed_report()

        logger.info(
            f"Processing complete. Success: {len(ktr_files) - len(self.failed_files)}, Failed: {len(self.failed_files)}"
        )

    def write_failed_report(self):
        """Write a report of failed files"""
        try:
            with open("fail.md", "w", encoding="utf-8") as f:
                f.write("# Failed KTR Files Processing Report\n\n")
                f.write(f"Total failed files: {len(self.failed_files)}\n\n")
                f.write("## Failed Files:\n\n")
                for failed_file in self.failed_files:
                    f.write(f"- {failed_file}\n")

            logger.warning(
                f"Failed report written to fail.md with {len(self.failed_files)} files"
            )
        except Exception as e:
            logger.error(f"Error writing failed report: {str(e)}")


async def main():
    """Main entry point"""
    logger.info("Starting KTR file processor")

    try:
        processor = KTRProcessor()
        await processor.process_all_files()
        logger.info("KTR processing completed successfully")
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
