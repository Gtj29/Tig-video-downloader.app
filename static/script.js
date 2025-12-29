document.addEventListener('DOMContentLoaded', () => {
    const downloadBtn = document.getElementById('download-btn');
    const videoUrlInput = document.getElementById('video-url');
    const qualitySelect = document.getElementById('quality');
    const historyList = document.getElementById('history-list');
    const statusEl = document.getElementById('status');
    const spinner = document.getElementById('spinner');

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

    const setLoading = (loading) => {
        downloadBtn.disabled = loading;
        if (loading) {
            spinner.style.display = 'inline-block';
            statusEl.textContent = 'Processing... this may take a while for large videos.';
        } else {
            spinner.style.display = 'none';
        }
    };

    downloadBtn.addEventListener('click', () => {
        const videoUrl = videoUrlInput.value.trim();
        const quality = qualitySelect.value;

        if (!videoUrl) {
            alert('Please enter a video URL');
            return;
        }

        setLoading(true);
        statusEl.textContent = '';

        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: videoUrl, quality: quality })
        })
        .then(async (response) => {
            const contentType = response.headers.get('content-type') || '';
            let data;
            if (contentType.includes('application/json')) {
                data = await response.json();
            } else {
                // Fallback: try to read as text
                const text = await response.text();
                try {
                    data = JSON.parse(text);
                } catch (e) {
                    data = { error: text || 'Unknown server response' };
                }
            }

            if (!response.ok) {
                throw new Error(data.error || `Server responded with status ${response.status}`);
            }

            return data;
        })
        .then(data => {
            if (data.download_url) {
                // Show a visible link for the downloaded file so user can cancel and use it
                const linkContainer = document.getElementById('download-link');
                linkContainer.innerHTML = '';
                const a = document.createElement('a');
                a.href = data.download_url;
                a.textContent = data.filename ? `Download ${data.filename}` : 'Download file';
                a.setAttribute('download', '');
                a.className = 'download-ready';
                linkContainer.appendChild(a);

                // Trigger native download
                a.click();

                addToHistory(videoUrl);
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while trying to download the video: ' + (error.message || error));
        })
        .finally(() => {
            setLoading(false);
        });
    });

    loadHistory();
});
