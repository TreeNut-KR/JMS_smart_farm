def check_libraries():
    libraries = {
        "fastapi": "0.108.0",
        "pydantic": "2.5.3",
        "uvicorn": "0.25.0",
        "python-dotenv": "1.0.1",
        "opencv-python": "4.9.0.80",
        "serial": "0.0.97",
        "typing_extensions": "4.9.0",
        "google-auth-oauthlib": "1.2.0",
        "google-api-python-client": "2.122.0",
        "google-api-core": "2.17.1",
    }

    for lib, expected_version in libraries.items():
        try:
            module = __import__(lib.replace("-", "_"))
            if hasattr(module, '__version__'):
                version = module.__version__
            elif lib == "python_dotenv":
                # python-dotenv 패키지는 __version__을 직접 제공하지 않으므로 다른 방식으로 버전을 확인해야 합니다.
                from dotenv import find_dotenv
                find_dotenv
                version = "버전 정보 없음; 설치된 것으로 간주"
            else:
                version = "버전 정보 없음"

            print(f"{lib}: 설치됨, 버전 {version} (예상 버전: {expected_version})")
        except ImportError:
            print(f"{lib}: 설치되지 않음")

if __name__ == "__main__":
    check_libraries()
