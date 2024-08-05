document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById("modal");
    const btn = document.getElementById("configure-defaults-btn");
    const span = document.getElementsByClassName("close")[0];

    // When the user clicks the button, open the modal 
    btn.onclick = function() {
        modal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside the modal, close it
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }

});

document.addEventListener('DOMContentLoaded', function () {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const saveButton = document.getElementById('save-button');
    const formFields = document.querySelectorAll('input, select, textarea');

    // Function to validate the form
    function validateForm() {
        let isValid = true;
        formFields.forEach(field => {
            if (field.required && !field.value) {
                isValid = false;
            }
        });
        saveButton.disabled = !isValid;
    }

    // Initial validation check
    validateForm();

    // Add event listeners to form fields for real-time validation
    formFields.forEach(field => {
        field.addEventListener('input', validateForm);
    });

    // Add event listener for file input (if applicable)
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            saveButton.disabled = !fileInput.files.length;
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            if (confirm('Are you sure you want to delete this file?')) {
                form.submit();
            }
        });
    });
});

document.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'deleteConfirmModal .modal-body') {
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        const deleteUrl = evt.detail.requestConfig.path.replace('/confirm-delete', '/delete');

        confirmDeleteBtn.onclick = async function() {
            const response = await fetch(deleteUrl, { method: 'DELETE' });
            if (response.ok) {
                const data = await response.json();
                const defaultsTable = document.getElementById('defaultsTable');
                defaultsTable.innerHTML = data.remaining_defaults;
                const deleteConfirmModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
                deleteConfirmModal.hide();
            }
        };
    }
});