document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const results = document.getElementById('results');
    const reportLink = document.getElementById('report-link');

    // Add drag and drop functionality
    document.querySelectorAll('.upload-box').forEach((box, index) => {
        box.addEventListener('dragover', (e) => {
            e.preventDefault();
            box.classList.add('drag-over');
        });

        box.addEventListener('dragleave', (e) => {
            e.preventDefault();
            box.classList.remove('drag-over');
        });

        box.addEventListener('drop', (e) => {
            e.preventDefault();
            box.classList.remove('drag-over');
            const fileInput = document.getElementById(`file${index + 1}`);
            const file = e.dataTransfer.files[0];
            if (file && file.type === 'application/pdf') {
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;
                box.querySelector('.upload-text').textContent = file.name;
            }
        });
    });

    // Handle file input changes
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const box = e.target.previousElementSibling;
                box.querySelector('.upload-text').textContent = file.name;
            }
        });
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.textContent = 'Analyzing...';
        submitButton.disabled = true;

        try {
            const formData = new FormData(form);
            const response = await fetch('/compare', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'An error occurred');
            }

            const data = await response.json();
            
            // Update results
            if (data.text_similarity !== undefined) {
                document.getElementById('text-similarity').textContent = 
                    (data.text_similarity * 100).toFixed(1) + '%';
            }
            
            if (data.handwriting_similarity !== undefined) {
                document.getElementById('handwriting-similarity').textContent = 
                    (data.handwriting_similarity * 100).toFixed(1) + '%';
            }
            
            if (data.similarity_index !== undefined) {
                document.getElementById('similarity-index').textContent = 
                    (data.similarity_index * 100).toFixed(1) + '%';
            }
            
            // Update report link
            if (data.report_url) {
                reportLink.href = data.report_url;
                reportLink.style.display = 'block';
            }
            
            // Show results
            results.style.display = 'block';
            
            // Scroll to results
            results.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'An error occurred during analysis');
        } finally {
            // Reset button state
            submitButton.textContent = originalButtonText;
            submitButton.disabled = false;
        }
    });

    // Add slider progress handling
    const slider = document.getElementById('weight-text');
    
    function updateSliderProgress(value) {
        const progress = (value * 100);
        slider.style.background = `linear-gradient(to right, 
            var(--accent-color) ${progress}%, 
            #e5e5e5 ${progress}%)`;
    }

    // Initialize slider progress
    if (slider) {
        updateSliderProgress(slider.value);

        // Update on slider change
        slider.addEventListener('input', (e) => {
            updateSliderProgress(e.target.value);
        });
    }
}); 