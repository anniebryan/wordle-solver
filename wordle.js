document.getElementById('wordle-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const inputs = Array.from(document.querySelectorAll('.wordle-input input'));
    const word = inputs.map(input => input.value).join('');

    if (word.length === 5) {
        alert(`You entered: ${word}`);
    } else {
        alert('Please fill out all the boxes.');
    }
});
