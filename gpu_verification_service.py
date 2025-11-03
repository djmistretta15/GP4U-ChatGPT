"""
GPU verification and benchmarking service.

This service provides methods to verify ownership of a GPU and to
benchmark its performance.  In a real deployment these operations
would be performed over SSH on the host machine where the GPU
resides, and the service would run commands like ``nvidia-smi`` or
PyTorch/TensorFlow benchmarks to gather data.  Here we provide a
mock implementation that demonstrates the intended API while avoiding
remote dependencies or heavy computation.

The methods are asynchronous to allow integration with async HTTP
frameworks such as FastAPI.  If paramiko is installed, the service
will attempt to open an SSH connection; otherwise it falls back to
returning simulated results.  Extending this service to run real
benchmarks can be done by replacing the simulated code paths with
actual command execution.
"""

from __future__ import annotations

import asyncio
from typing import Dict, Optional

try:
    import paramiko  # type: ignore
except ImportError:
    # ``paramiko`` is optional.  If it's not installed we operate in a
    # simulated mode that returns hard‑coded results.  This makes it
    # easier to develop and test the service without requiring SSH
    # connectivity or GPU hardware.
    paramiko = None  # type: ignore


class GPUVerificationService:
    """Service for verifying GPU ownership and benchmarking performance."""

    async def verify_gpu_ownership(self, host: str, ssh_key: Optional[str] = None) -> Dict[str, str]:
        """Verify GPU ownership via SSH.

        Connect to the given host using SSH and run ``nvidia-smi`` to
        retrieve GPU information.  The caller can optionally provide an
        SSH private key as a string.  If no key is provided the
        service will attempt to use the default SSH key configured on
        the server.  If the ``paramiko`` library is not available or
        the connection fails, a simulated result is returned.

        Parameters
        ----------
        host: str
            The hostname or IP address of the machine to verify.
        ssh_key: Optional[str]
            An optional SSH private key (PEM format) for authentication.

        Returns
        -------
        Dict[str, str]
            A dictionary containing GPU model name and total memory.
        """
        # If paramiko isn't available we return simulated data.  This
        # branch also serves as a fallback on connection errors to
        # preserve a consistent API.
        if paramiko is None:
            await asyncio.sleep(0.1)
            return {"name": "Simulated GPU", "memory": "16 GB"}

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # Attempt to connect using either an explicit key or the
            # default SSH key configured on the machine.  The username
            # is hard‑coded to ``root`` for demonstration; in a real
            # system you'd accept a username parameter or derive it from
            # the provider's configuration.
            if ssh_key:
                # ``ssh_key`` may be a path to a file or the key
                # contents themselves.  ``paramiko`` handles file
                # loading automatically when passed a filename; if a
                # string beginning with ``-----BEGIN`` is provided we
                # treat it as a key body.
                if ssh_key.startswith("-----BEGIN"):
                    from io import StringIO

                    key_obj = paramiko.RSAKey.from_private_key(StringIO(ssh_key))
                else:
                    key_obj = paramiko.RSAKey.from_private_key_file(ssh_key)
                client.connect(hostname=host, username="root", pkey=key_obj, timeout=10)
            else:
                client.connect(hostname=host, username="root", timeout=10)
            # Run ``nvidia-smi`` to get model name and memory in MiB.  We
            # strip units and convert to GB for presentation.
            stdin, stdout, stderr = client.exec_command(
                "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits"
            )
            output = stdout.read().decode().strip()
            if not output:
                raise RuntimeError("Failed to retrieve GPU info")
            name, memory_mib = output.split(",")
            # Convert memory from MiB to GB, rounding to the nearest
            # whole number for simplicity
            try:
                memory_gb = int(int(memory_mib.strip()) / 1024)
            except Exception:
                memory_gb = memory_mib.strip()
            return {"name": name.strip(), "memory": f"{memory_gb} GB"}
        except Exception:
            # On any error, return a minimal response indicating
            # verification failed.  We do not propagate exceptions to
            # avoid leaking host details or stack traces to callers.
            return {"name": "Unknown GPU", "memory": "Unknown"}
        finally:
            client.close()

    async def benchmark_gpu(self, gpu_id: str, host: str) -> Dict[str, float]:
        """Run synthetic benchmarks on the GPU and return performance metrics.

        A real implementation would run ML frameworks or compute kernels
        (e.g. PyTorch/TF benchmarks) to measure throughput and latency.
        Here we simulate the results with deterministic values based on
        the ``gpu_id`` so that repeated calls return consistent values.

        Parameters
        ----------
        gpu_id: str
            An identifier for the GPU.  In a real system this might
            correspond to the device index reported by ``nvidia-smi``.
        host: str
            The hostname or IP address where the GPU resides (unused in
            this simulation).

        Returns
        -------
        Dict[str, float]
            Benchmark results including FLOPS and memory bandwidth.
        """
        # Use a simple hash of the gpu_id to derive reproducible numbers
        seed = sum(ord(c) for c in gpu_id)
        flops = 10.0 + (seed % 10)  # e.g. 10–19 TFLOPS
        bandwidth = 200.0 + (seed % 50)  # e.g. 200–249 GB/s
        # Simulate asynchronous work
        await asyncio.sleep(0.1)
        return {"tflops": round(flops, 2), "bandwidth_gbps": round(bandwidth, 2)}