#!/usr/bin/env python3
"""
Cross-platform .deb package builder in pure Python.
Generates Debian package archives without requiring dpkg-deb on host.
"""
import os
import shutil
import tarfile
import struct
import tempfile

VERSION = "1.0.0"
PACKAGE_NAME = "linux-eye"
ARCH = "all"

def create_ar_archive(ar_filename, members):
    """Create a standard Unix ar archive containing (name, data_bytes)."""
    with open(ar_filename, 'wb') as ar_file:
        ar_file.write(b"!<arch>\n")
        for filename, data in members:
            # ar header format:
            # File name (16 bytes), timestamp (12 bytes), owner id (6 bytes), group id (6 bytes),
            # file mode (8 bytes), file size (10 bytes), magic (\x60\x0a) (2 bytes)
            name_field = filename.ljust(16)[:16].encode('ascii')
            mtime_field = str(int(os.path.getmtime(ar_filename) if os.path.exists(ar_filename) else 0)).ljust(12)[:12].encode('ascii')
            owner_field = b"0     "
            group_field = b"0     "
            mode_field = b"100644  "
            size_field = str(len(data)).ljust(10)[:10].encode('ascii')
            magic_field = b"`\n"

            header = name_field + mtime_field + owner_field + group_field + mode_field + size_field + magic_field
            ar_file.write(header)
            ar_file.write(data)
            # 2-byte alignment padding
            if len(data) % 2 != 0:
                ar_file.write(b"\n")

def make_tar_gz(source_dir, output_tar_gz, base_path=""):
    """Archive directory into .tar.gz with normalized permissions."""
    with tarfile.open(output_tar_gz, "w:gz") as tar:
        for root, dirs, files in os.walk(source_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, source_dir)
                arcname = os.path.join(base_path, rel_path) if base_path else rel_path
                ti = tar.gettarinfo(full_path, arcname=arcname)
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "root"
                if f in ("postinst", "prerm", "postrm", "linux-eye") or full_path.endswith(".sh"):
                    ti.mode = 0o755
                else:
                    ti.mode = 0o644
                with open(full_path, "rb") as fp:
                    tar.addfile(ti, fp)

def build_deb():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "dist")
    os.makedirs(output_dir, exist_ok=True)
    deb_filepath = os.path.join(output_dir, f"{PACKAGE_NAME}_{VERSION}_{ARCH}.deb")

    with tempfile.TemporaryDirectory() as tmp_dir:
        debian_dir = os.path.join(tmp_dir, "DEBIAN")
        data_dir = os.path.join(tmp_dir, "data")
        os.makedirs(debian_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "opt", "linux-eye"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "etc", "systemd", "system"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "usr", "local", "bin"), exist_ok=True)

        # 1. Populate data payload
        opt_dir = os.path.join(data_dir, "opt", "linux-eye")
        shutil.copytree(os.path.join(base_dir, "linux_eye"), os.path.join(opt_dir, "linux_eye"))
        shutil.copytree(os.path.join(base_dir, "config"), os.path.join(opt_dir, "config"))
        shutil.copy(os.path.join(base_dir, "requirements.txt"), opt_dir)
        if os.path.exists(os.path.join(base_dir, "pyproject.toml")):
            shutil.copy(os.path.join(base_dir, "pyproject.toml"), opt_dir)

        shutil.copy(os.path.join(base_dir, "systemd", "linux-eye.service"), os.path.join(data_dir, "etc", "systemd", "system"))

        launcher_path = os.path.join(data_dir, "usr", "local", "bin", "linux-eye")
        with open(launcher_path, "w") as f:
            f.write("#!/usr/bin/env bash\ncd /opt/linux-eye && sudo /opt/linux-eye/.venv/bin/python -m linux_eye.main \"$@\"\n")
        os.chmod(launcher_path, 0o755)

        # 2. Control file
        with open(os.path.join(debian_dir, "control"), "w") as f:
            f.write(f"""Package: {PACKAGE_NAME}
Version: {VERSION}
Section: utils
Priority: optional
Architecture: {ARCH}
Maintainer: Amit Padhan <amitpadhan525@gmail.com>
Depends: python3, python3-venv, python3-pip, systemd
Description: Lightweight real-time Linux security monitor (EDR)
 LinuxEye monitors running processes, network connections, file changes
 in /etc, and authentication journals to flag suspicious behavior.
""")

        # 3. Post-installation script
        postinst = os.path.join(debian_dir, "postinst")
        with open(postinst, "w") as f:
            f.write("""#!/usr/bin/env bash
set -e
mkdir -p /opt/linux-eye/logs
python3 -m venv /opt/linux-eye/.venv
/opt/linux-eye/.venv/bin/pip install --upgrade pip --quiet
/opt/linux-eye/.venv/bin/pip install -r /opt/linux-eye/requirements.txt --quiet
systemctl daemon-reload
systemctl enable linux-eye.service
systemctl restart linux-eye.service || true
echo "LinuxEye service enabled and started."
""")
        os.chmod(postinst, 0o755)

        # 4. Pre-removal script
        prerm = os.path.join(debian_dir, "prerm")
        with open(prerm, "w") as f:
            f.write("""#!/usr/bin/env bash
set -e
systemctl stop linux-eye.service 2>/dev/null || true
systemctl disable linux-eye.service 2>/dev/null || true
""")
        os.chmod(prerm, 0o755)

        # 5. Pack control.tar.gz and data.tar.gz
        control_tar = os.path.join(tmp_dir, "control.tar.gz")
        data_tar = os.path.join(tmp_dir, "data.tar.gz")

        make_tar_gz(debian_dir, control_tar, base_path=".")
        make_tar_gz(data_dir, data_tar, base_path="")

        # 6. Assemble .deb archive
        with open(control_tar, "rb") as f:
            control_data = f.read()
        with open(data_tar, "rb") as f:
            data_data = f.read()

        members = [
            ("debian-binary", b"2.0\n"),
            ("control.tar.gz", control_data),
            ("data.tar.gz", data_data)
        ]

        create_ar_archive(deb_filepath, members)
        print(f"[+] Successfully built: {deb_filepath}")

if __name__ == "__main__":
    build_deb()
