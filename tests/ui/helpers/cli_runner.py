"""CLI runner for UI testing.

This module provides a CLI runner for UI testing.
"""

import os
import tempfile
from typing import List, Optional

import pexpect


class CLIResult:
    """Result of a CLI run.

    This class represents the result of a CLI run, including stdout, stderr, and exit code.
    """

    def __init__(self, stdout: str, exit_code: int):
        """Initialize the CLI result.

        Args:
            stdout: The standard output
            exit_code: The exit code
        """
        self.stdout = stdout
        self.exit_code = exit_code

    def __str__(self) -> str:
        """Return a string representation of the CLI result.

        Returns:
            A string representation of the CLI result
        """
        return f"CLIResult(exit_code={self.exit_code}, stdout={self.stdout!r})"


class CLIRunner:
    """CLI runner for UI testing.

    This class provides methods for running the CLI and interacting with it.
    """

    def __init__(
        self,
        command: str = "python -m fogis_reporter",
        timeout: int = 30,
        env: Optional[dict] = None,
    ):
        """Initialize the CLI runner.

        Args:
            command: The command to run
            timeout: The timeout in seconds
            env: Environment variables to set
        """
        self.command = command
        self.timeout = timeout
        self.env = env or {}

    def run_with_input(
        self, inputs: List[str], env: Optional[dict] = None
    ) -> CLIResult:
        """Run the CLI with the given inputs.

        Args:
            inputs: The inputs to provide to the CLI
            env: Environment variables to set

        Returns:
            A CLIResult instance
        """
        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(delete=False) as f:
            output_file = f.name

        try:
            # Set up environment variables
            if env is None:
                env = {}

            # Combine environment variables from constructor and method call
            combined_env = self.env.copy()
            combined_env.update(env)

            # Add environment variables to the current environment
            full_env = os.environ.copy()
            full_env.update(combined_env)

            # Start the process
            child = pexpect.spawn(
                self.command, env=full_env, timeout=self.timeout, encoding="utf-8"
            )

            # Set up logging to the temporary file
            with open(output_file, "w") as logfile:
                child.logfile = logfile

                # Provide inputs
                for input_str in inputs:
                    child.expect_exact([pexpect.EOF, pexpect.TIMEOUT, ">"])
                    child.sendline(input_str)

                # Wait for the process to finish
                child.expect(pexpect.EOF)
                child.close()

            # Read the output
            with open(output_file, "r") as f:
                stdout = f.read()

            return CLIResult(stdout=stdout, exit_code=child.exitstatus)
        finally:
            # Clean up the temporary file
            if os.path.exists(output_file):
                os.unlink(output_file)

    def run_with_args(self, args: List[str], env: Optional[dict] = None) -> CLIResult:
        """Run the CLI with the given arguments.

        Args:
            args: The arguments to provide to the CLI
            env: Environment variables to set

        Returns:
            A CLIResult instance
        """
        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(delete=False) as f:
            output_file = f.name

        try:
            # Set up environment variables
            if env is None:
                env = {}

            # Combine environment variables from constructor and method call
            combined_env = self.env.copy()
            combined_env.update(env)

            # Add environment variables to the current environment
            full_env = os.environ.copy()
            full_env.update(combined_env)

            # Start the process
            command = f"{self.command} {' '.join(args)}"
            child = pexpect.spawn(
                command, env=full_env, timeout=self.timeout, encoding="utf-8"
            )

            # Set up logging to the temporary file
            with open(output_file, "w") as logfile:
                child.logfile = logfile

                # Wait for the process to finish
                child.expect(pexpect.EOF)
                child.close()

            # Read the output
            with open(output_file, "r") as f:
                stdout = f.read()

            return CLIResult(stdout=stdout, exit_code=child.exitstatus)
        finally:
            # Clean up the temporary file
            if os.path.exists(output_file):
                os.unlink(output_file)
