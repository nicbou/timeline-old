from pathlib import Path

from django.conf import settings
import logging
import subprocess


logger = logging.getLogger(__name__)


class SSHCredentialsError(ConnectionError):
    pass


class SSHTimeoutError(ConnectionError):
    pass


def copy_ssh_keys(host, port, user, password):
    """
    Copies SSH keys to a remote host without user input
    """
    try:
        ssh_key_path: Path = settings.SSH_DIR / 'id_rsa'
        if not ssh_key_path.exists():
            # Don't regenerate an existing key
            subprocess.check_call(['ssh-keygen', '-b', '2048', '-t', 'rsa', '-f', ssh_key_path, '-q', '-N', '',])

        subprocess.check_call([
            'sshpass',
            '-p', password,
            'ssh-copy-id',
            '-o', 'StrictHostKeyChecking=no',
            '-p', str(port),
            '-i', ssh_key_path,
            f'{user}@{host}',
        ], timeout=10)
    except subprocess.TimeoutExpired:
        raise SSHTimeoutError(f"Failed to copy keys to {host}. Request timed out.")
    except subprocess.CalledProcessError as exc:
        raise SSHCredentialsError(f"Failed to copy keys to {host}. Command returned exit code {exc.returncode}")
    except:
        raise Exception(f"Failed to copy keys to {host}")