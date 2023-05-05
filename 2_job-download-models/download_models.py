import subprocess

print(subprocess.run(["sh 2_job-download-models/download_models.sh"], shell=True))