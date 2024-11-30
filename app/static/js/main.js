document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const results = document.getElementById('results');

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
            document.getElementById('text-similarity').textContent = 
                (data.text_similarity * 100).toFixed(1) + '%';
            document.getElementById('handwriting-similarity').textContent = 
                (data.handwriting_similarity * 100).toFixed(1) + '%';
            document.getElementById('similarity-index').textContent = 
                (data.similarity_index * 100).toFixed(1) + '%';
            
            // Update report download link
            document.getElementById('report-link').href = data.report_url;
            
            // Show results
            results.style.display = 'block';
            
            // Scroll to results
            results.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            alert(error.message);
        } finally {
            // Reset button state
            submitButton.textContent = originalButtonText;
            submitButton.disabled = false;
        }
    });
}); 