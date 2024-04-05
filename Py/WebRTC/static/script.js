let mediaRecorder;
let recordedBlobs;

async function startWebRTC() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    document.getElementById('video').srcObject = stream;
    startRecording(stream);
}

function startRecording(stream) {
    recordedBlobs = [];
    let options = { mimeType: 'video/webm; codecs=vp9' };
    try {
        mediaRecorder = new MediaRecorder(stream, options);
    } catch (e) {
        console.error('Exception while creating MediaRecorder:', e);
        return;
    }

    mediaRecorder.onstop = (event) => {
        const blob = new Blob(recordedBlobs, { type: 'video/webm' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'recorded.webm';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 100);
    };

    mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
            recordedBlobs.push(event.data);
        }
    };

    mediaRecorder.start();
    console.log('MediaRecorder started', mediaRecorder);
}

document.getElementById('startRecording').addEventListener('click', () => {
    startWebRTC(); // 스트림을 시작하고 녹화를 시작합니다.
});

document.getElementById('stopRecording').addEventListener('click', () => {
    mediaRecorder.stop(); // 녹화를 중지합니다.
});
