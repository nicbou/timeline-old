from pathlib import Path

from django.conf import settings
import logging
import subprocess


logger = logging.getLogger(__name__)


class SSHCredentialsError(ConnectionError):
    pass


class SSHTimeoutError(ConnectionError):
    pass


KEY_EXCHANGE_SSH_COPY_ID = 'ssh-copy-id'
KEY_EXCHANGE_HETZNER = 'hetzner'
KEY_EXCHANGE_METHODS = (
    KEY_EXCHANGE_HETZNER,
    KEY_EXCHANGE_SSH_COPY_ID,
)


def copy_ssh_keys(host, port, user, password, key_exchange_method=KEY_EXCHANGE_SSH_COPY_ID):
    """
    Copies SSH keys to a remote host without user input
    """
    try:
        ssh_private_key_path: Path = settings.SSH_DIR / 'id_rsa'
        ssh_public_key_path: Path = settings.SSH_DIR / 'id_rsa.pub'
        if not ssh_private_key_path.exists():
            # Don't regenerate an existing key, or it will break every connection that relies on it
            subprocess.check_call(['ssh-keygen', '-b', '2048', '-t', 'rsa', '-f', ssh_private_key_path, '-q', '-N', '',])

        if key_exchange_method == KEY_EXCHANGE_SSH_COPY_ID:
            subprocess.check_call([
                'sshpass', '-p', password,
                'ssh-copy-id',
                '-o', 'StrictHostKeyChecking=no',
                '-p', str(port),
                '-i', ssh_private_key_path,
                f'{user}@{host}',
            ], timeout=10)
        elif key_exchange_method == KEY_EXCHANGE_HETZNER:
            # Hetzner storage boxes don't support ssh-copy-id or shell commands, so we upload an authorized_keys file.

            # Remove and recreate remote .ssh dir. Fails silently (for example if the directory exists).
            mk_dir_command = subprocess.Popen(['echo', 'mkdir', '.ssh'], stdout=subprocess.PIPE)
            subprocess.check_call(['sshpass', '-p', password, 'sftp', f'{user}@{host}'], stdin=mk_dir_command.stdout)

            # Upload authorized_keys file
            subprocess.check_call([
                'sshpass', '-p', password,
                'scp', str(ssh_public_key_path), f'{user}@{host}:.ssh/authorized_keys'
            ])
        else:
            raise Exception(f"Unexpected key exchange method: {key_exchange_method}")
    except subprocess.TimeoutExpired:
        raise SSHTimeoutError(f"Failed to copy keys to {host}. Request timed out.")
    except subprocess.CalledProcessError as exc:
        raise SSHCredentialsError(f"Failed to copy keys to {host}. Command returned exit code {exc.returncode}")
    except:
        raise Exception(f"Failed to copy keys to {host}")