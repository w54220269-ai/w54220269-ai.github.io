import subprocess
import os
import zipfile
import shutil

class ADBHelper:
    @staticmethod
    def run_command(cmd):
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", str(e)

    @classmethod
    def get_installed_packages(cls):
        stdout, _ = cls.run_command("adb shell pm list packages -3")
        packages = []
        for line in stdout.splitlines():
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        return packages

    @classmethod
    def get_package_paths(cls, package_name):
        stdout, _ = cls.run_command(f"adb shell pm path {package_name}")
        paths = []
        for line in stdout.splitlines():
            if line.startswith("package:"):
                paths.append(line.replace("package:", "").strip())
        return paths

    @classmethod
    def extract_package(cls, package_name, output_dir):
        paths = cls.get_package_paths(package_name)
        if not paths:
            return None, "التطبيق غير موجود أو متعذر الوصول إليه"

        pkg_folder = os.path.join(output_dir, package_name)
        os.makedirs(pkg_folder, exist_ok=True)
        pulled_files = []

        for idx, remote_path in enumerate(paths):
            local_apk = os.path.join(pkg_folder, f"base_{idx}.apk" if len(paths) > 1 else f"{package_name}.apk")
            out, err = cls.run_command(f"adb pull \"{remote_path}\" \"{local_apk}\"")
            if os.path.exists(local_apk):
                pulled_files.append(local_apk)

        if not pulled_files:
            return None, "فشل استخراج ملفات APK عبر ADB"

        if len(pulled_files) > 1:
            zip_path = os.path.join(output_dir, f"{package_name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for f in pulled_files:
                    zipf.write(f, os.path.basename(f))
            shutil.rmtree(pkg_folder)
            return zip_path, None
        else:
            final_apk = os.path.join(output_dir, f"{package_name}.apk")
            os.rename(pulled_files[0], final_apk)
            shutil.rmtree(pkg_folder)
            return final_apk, None
