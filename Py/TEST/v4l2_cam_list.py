import subprocess

def check_and_install_v4l_utils():
    # v4l2-ctl 명령어가 시스템에 존재하는지 확인
    v4l2_ctl_exists = subprocess.run(["which", "v4l2-ctl"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # v4l2-ctl 명령어가 없다면 v4l-utils 설치
    if v4l2_ctl_exists.returncode != 0:
        print("v4l-utils가 설치되어 있지 않습니다. 설치를 시작합니다.")
        install_command = "sudo apt-get install v4l-utils -y"
        subprocess.run(install_command, shell=True, check=True)
        print("v4l-utils 설치가 완료되었습니다.")
    else:
        print("v4l-utils가 이미 설치되어 있습니다.")

def list_cameras():
    # 연결된 카메라 리스트 출력
    command = "v4l2-ctl --list-devices"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    print(result.stdout)

# v4l-utils 설치 확인 및 설치
check_and_install_v4l_utils()
# 카메라 리스트 출력
list_cameras()
