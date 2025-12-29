document.addEventListener('DOMContentLoaded', () => {
    const downloadBtn = document.getElementById('download-btn');
    const videoUrlInput = document.getElementById('video-url');
    const qualitySelect = document.getElementById('quality');
    const historyList = document.getElementById('history-list');

    const loadHistory = () => {
        const history = JSON.parse(localStorage.getItem('downloadHistory')) || [];
        historyList.innerHTML = '';
        history.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            historyList.appendChild(li);
        });
    };

    const addToHistory = (url) => {
        let history = JSON.parse(localStorage.getItem('downloadHistory')) || [];
        if (!history.includes(url)) {
            history.push(url);
            localStorage.setItem('downloadHistory', JSON.stringify(history));
        }
        loadHistory();
    };

    downloadBtn.addEventListener('click', () => {
        const videoUrl = videoUrlInput.value.trim();
        const quality = qualitySelect.value;

        if (!videoUrl) {
            alert('Please enter a video URL');
            return;
        }

        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: videoUrl, quality: quality })
        })
        .then(response => response.json())
        .then(data => {
            if (data.download_url) {
                const a = document.createElement('a');
                a.href = data.download_url;
                a.download = '';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                addToHistory(videoUrl);
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while trying to download the video.');
        });
    });

    loadHistory();
});
