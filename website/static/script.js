document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData();
    let fileField = document.querySelector('input[type="file"]');
    let questionField = document.getElementById('question');

    formData.append('image', fileField.files[0]);
    formData.append('question', questionField.value);

    fetch('/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('result').innerText = data.error.message;
        } else {
            document.getElementById('result').innerText = JSON.stringify(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
