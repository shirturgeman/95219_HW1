document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData();
    let fileField = document.querySelector('input[type="file"]');
    let questionField = document.getElementById('question');

    formData.append('file', fileField.files[0]);
    formData.append('question', questionField.value);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerText = data.message + " - " + data.result;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});