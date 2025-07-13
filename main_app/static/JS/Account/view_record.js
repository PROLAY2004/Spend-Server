document.addEventListener('DOMContentLoaded', function () {
    // Existing note dialog
    const noteButtons = document.querySelectorAll('.note-btn');
    const noteDialog = document.getElementById('note-dialog');
    const noteText = document.getElementById('note-dialog-text');
    const noteClose = document.querySelector('.note-dialog-close');

    noteButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const note = this.getAttribute('data-note') || 'No note provided.';
            noteText.textContent = note;
            noteDialog.classList.add('active');
        });
    });

    noteClose.addEventListener('click', function () {
        noteDialog.classList.remove('active');
    });

    noteDialog.addEventListener('click', function (e) {
        if (e.target === noteDialog) {
            noteDialog.classList.remove('active');
        }
    });

    // 🚨 NEW: Delete dialog logic
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const deleteDialog = document.getElementById('delete-dialog');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const deleteCloseButtons = document.querySelectorAll('.delete-dialog-close');

    let deleteUrl = "";

    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            deleteUrl = this.getAttribute('data-delete-url');
            deleteDialog.classList.add('active');
        });
    });

    confirmDeleteBtn.addEventListener('click', function () {
        if (deleteUrl) {
            window.location.href = deleteUrl;
        }
    });

    deleteCloseButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            deleteDialog.classList.remove('active');
        });
    });

    deleteDialog.addEventListener('click', function (e) {
        if (e.target === deleteDialog) {
            deleteDialog.classList.remove('active');
        }
    });
});



document.addEventListener("DOMContentLoaded", function () {
    const filterType = document.getElementById("filter-type");
    const filterInput = document.getElementById("filter-input");
    const filterStatus = document.getElementById("filter-status");
    const rows = document.querySelectorAll("tbody tr");

    function filterTable() {
        const type = filterType.value;
        let keyword = "";

        if (type === "status") {
            keyword = filterStatus.value.trim();
        } else {
            keyword = filterInput.value.trim().toLowerCase();
        }

        rows.forEach(row => {
            let match = false;

            if (type === "date") {
                match = row.children[0].textContent.toLowerCase().includes(keyword);
            } else if (type === "description") {
                match = row.children[1].textContent.toLowerCase().includes(keyword);
            } else if (type === "due_from") {
                match = row.children[4].textContent.toLowerCase().includes(keyword);
            } else if (type === "status") {
                match = row.children[6].textContent.trim() === keyword;
            }

            row.style.display = match || !type || !keyword ? "" : "none";
        });
    }

    // Show relevant input based on filter type
    filterType.addEventListener("change", function () {
        const selected = filterType.value;
        filterInput.style.display = selected && selected !== "status" ? "inline-block" : "none";
        filterStatus.style.display = selected === "status" ? "inline-block" : "none";

        // Reset both fields on type change
        filterInput.value = "";
        filterStatus.value = "";
        filterTable();
    });

    filterInput.addEventListener("input", filterTable);
    filterStatus.addEventListener("change", filterTable);
});
