document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchForm = document.getElementById('searchForm');
    const queryInput = document.getElementById('queryInput');
    const searchBtn = document.getElementById('searchBtn');
    const searchIcon = document.getElementById('searchIcon');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const topKInput = document.getElementById('topKInput');
    const topKValue = document.getElementById('topKValue');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorMsg = document.getElementById('errorMsg');
    const noResults = document.getElementById('noResults');

    // Difficulty Mapping
    const DIFFICULTY_LEVELS = {
        1: { label: 'سهل', class: 'diff-1' },
        2: { label: 'متوسط', class: 'diff-2' },
        3: { label: 'متقدم', class: 'diff-3' },
        4: { label: 'متقدم جداً', class: 'diff-4' }
    };

    // Update Slider Value
    topKInput.addEventListener('input', (e) => {
        topKValue.textContent = e.target.value;
    });

    // Form Submit
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = queryInput.value.trim();
        if (!query) return;

        const topK = parseInt(topKInput.value);

        // UI Loading State
        setLoading(true);
        hideElements([errorMsg, noResults]);
        resultsContainer.innerHTML = '';

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query, top_k: topK })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'حدث خطأ أثناء الاتصال بالخادم');
            }

            const data = await response.json();
            const results = data.results || [];

            if (results.length === 0) {
                noResults.classList.remove('hidden');
            } else {
                renderResults(results);
            }

        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    });

    function renderResults(results) {
        results.forEach((result, index) => {
            const diffConfig = DIFFICULTY_LEVELS[result.difficulty] || DIFFICULTY_LEVELS[2];
            const delay = index * 0.1; // Staggered animation
            
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.animationDelay = `${delay}s`;

            card.innerHTML = `
                <div class="result-header">
                    <span class="result-book">${result.resource_name || 'تفسير غير معروف'}</span>
                    <span class="badge badge-ayah">الآية ${result.verses_keys || ''}</span>
                    <span class="badge ${diffConfig.class}">مستوى الصعوبة: ${result.difficulty} (${diffConfig.label})</span>
                    <span class="badge-rank">#${result.rank || (index + 1)}</span>
                </div>
                <div class="result-text">${highlightQuery(result.text, queryInput.value)}</div>
            `;
            resultsContainer.appendChild(card);
        });
    }

    // Basic highlighter for UX (optional enhancement)
    function highlightQuery(text, query) {
        if (!text) return '';
        // Very basic escaping text to prevent XSS
        let safeText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        return safeText;
    }

    function setLoading(isLoading) {
        if (isLoading) {
            searchBtn.disabled = true;
            searchIcon.classList.add('hidden');
            loadingSpinner.classList.remove('hidden');
        } else {
            searchBtn.disabled = false;
            loadingSpinner.classList.add('hidden');
            searchIcon.classList.remove('hidden');
        }
    }

    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
    }

    function hideElements(elements) {
        elements.forEach(el => el.classList.add('hidden'));
    }
});
