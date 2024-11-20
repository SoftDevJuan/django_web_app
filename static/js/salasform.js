document.addEventListener('DOMContentLoaded', function() {
    const addRoomButton = document.getElementById('add-room');
    const modal = document.getElementById('modal');
    const closeModalButton = document.getElementById('close-modal');

    addRoomButton.addEventListener('click', () => {
        modal.classList.remove('hidden');
    });

    closeModalButton.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    // Optional: Close modal when clicking outside of the modal content
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.add('hidden');
        }
    });
});
