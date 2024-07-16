document.addEventListener('DOMContentLoaded', function() {
    let chart = '';
    const form = document.getElementById('flowchartForm');
    const inputField = document.getElementById('inputField');
    const submitButton = document.getElementById('submitButton');
    const templateSelect = document.getElementById('templateSelect');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const chartDiv = document.getElementById('chart');
    const initialContent = document.getElementById('initialContent');
    const exportOptions = document.getElementById('exportOptions');
    const llmProviderSelect = document.getElementById('llmProvider');
    const llmModelSelect = document.getElementById('llmModel');
    const modelSelection = document.getElementById('modelSelection');
    const manualModelInput = document.getElementById('manualModelInput');
    const manualModelField = document.getElementById('manualModel');

    llmProviderSelect.addEventListener('change', async () => {
        const provider = llmProviderSelect.value;
        if (['huggingface-openai', 'huggingface-text', 'ollama'].includes(provider)) {
            modelSelection.style.display = 'none';
            manualModelInput.style.display = 'block';
            manualModelField.value = '';
            manualModelField.placeholder = provider.startsWith('huggingface') ? 'Enter Hugging Face model name' : 'Enter Ollama model name';
        } else {
            modelSelection.style.display = 'block';
            manualModelInput.style.display = 'none';
            if (provider) {
                const response = await fetch(`/api/models?provider=${provider}`);
                const models = await response.json();
                llmModelSelect.innerHTML = '<option value="">Select Model</option>' + 
                    models.map(model => `<option value="${model.value}">${model.label}</option>`).join('');
                llmModelSelect.disabled = false;
            } else {
                llmModelSelect.innerHTML = '<option value="">Select Model</option>';
                llmModelSelect.disabled = true;
            }
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

    // Gather form data
    const input = document.getElementById('inputField').value;
    const selectedTemplate = document.getElementById('templateSelect').value;
    const provider = document.getElementById('llmProvider').value;
    const model = getSelectedModel();
    const apiKey = document.getElementById('apiKey').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens = parseInt(document.getElementById('maxTokens').value);

    if (!input || !provider || !model) {
    showToast('error', 'Validation Error', 'Please fill in all required fields.');
    return;
    }

    loadingIndicator.classList.remove('hidden');
    chartDiv.classList.add('hidden');
    initialContent.classList.add('hidden');
    exportOptions.classList.add('hidden');
    submitButton.disabled = true;
    submitButton.classList.add('opacity-50');

    try {
    const response = await axios.post('/api/ask', {
        input,
        selectedTemplate,
        provider,
        model,
        apiKey,
        temperature,
        maxTokens
    });

    if (response.data.text) {
        chart = response.data.text;
        // Clear previous content
        chartDiv.innerHTML = '';
        // Create a new div for Mermaid
        const mermaidDiv = document.createElement('div');
        mermaidDiv.className = 'mermaid';
        mermaidDiv.textContent = chart;
        chartDiv.appendChild(mermaidDiv);
        // Re-run Mermaid rendering
        mermaid.init(undefined, mermaidDiv);
        chartDiv.classList.remove('hidden');
        exportOptions.classList.remove('hidden');
    } else {
        throw new Error('No chart data received from the server');
    }
    } catch (error) {
    console.error('Error:', error);
    let errorMessage = 'An unexpected error occurred';
    let errorTitle = 'Error';

    if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (typeof error.response.data === 'string') {
            errorMessage = error.response.data;
        } else if (error.response.data && error.response.data.error) {
            errorMessage = error.response.data.error;
        }
        errorTitle = `Error ${error.response.status}`;
    } else if (error.request) {
        // The request was made but no response was received
        errorMessage = 'No response received from the server';
    } else {
        // Something happened in setting up the request that triggered an Error
        errorMessage = error.message;
    }

    // Check for specific error messages
    if (errorMessage.includes('API key not valid') || errorMessage.includes('Invalid API token')) {
        errorTitle = 'API Key Error';
        errorMessage = 'Invalid API key. Please check your API key and try again.';
    }

    showToast('error', errorTitle, errorMessage);
    initialContent.classList.remove('hidden');
    } finally {
    loadingIndicator.classList.add('hidden');
    submitButton.disabled = false;
    submitButton.classList.remove('opacity-50');
    }
    });

        function getSelectedModel() {
            const provider = document.getElementById('llmProvider').value;
            if (['huggingface-openai', 'huggingface-text', 'ollama'].includes(provider)) {
                return document.getElementById('manualModel').value.trim();
            } else {
                return document.getElementById('llmModel').value;
            }
        }
    });

    function exportSvg() {
        const svgElement = document.querySelector('svg');
        if (!svgElement) {
            showToast('warning', 'Warning', 'No SVG found to export');
            return;
        }

        const serializer = new XMLSerializer();
        let svgContent = serializer.serializeToString(svgElement); // Correctly assign serialized SVG to svgContent

        // Optionally, adjust the SVG size here if needed
        const newWidth = '1600px';
        const newHeight = '1200px';
        svgContent = svgContent.replace(/width="[^"]*"/, `width="${newWidth}"`).replace(/height="[^"]*"/, `height="${newHeight}"`);

        const svgBlob = new Blob([svgContent], {type: 'image/svg+xml;charset=utf-8'});
        const url = URL.createObjectURL(svgBlob);

        let baseName = 'diagram_chart';
        let timestamp = new Date().toISOString().replace(/[:.-]/g, '_');
        let fileName = `${baseName}_${timestamp}.svg`;

        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link); // Clean up
    }

    async function copyMermaidCode() {
        try {
            await navigator.clipboard.writeText(chart);
            showToast('success', 'Success', "Mermaid code copied to clipboard!");
        } catch (error) {
            showToast('warning', 'Warning', error);
            alert('Error copying Mermaid code');
        }
    }

    function showToast(type, title, message) {
    const toastPanel = document.getElementById('toastPanel');
    if (!toastPanel) {
    console.error('Toast panel not found!');
    return;
    }

    // Check for existing toasts with the same message
    const existingToasts = toastPanel.querySelectorAll('.toast-item');
    for (let existingToast of existingToasts) {
    if (existingToast.querySelector('p').textContent === message) {
        return; // Don't show duplicate toast
    }
    }

    const toastItem = document.createElement('div');
    toastItem.className = `toast-item ${type}`;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const closeBtn = document.createElement('div');
    closeBtn.className = 'close';
    closeBtn.onclick = function() {
    toastItem.classList.remove('show');
    setTimeout(() => toastItem.remove(), 300);
    };

    const toastTitle = document.createElement('h3');
    toastTitle.textContent = title;

    const toastMessage = document.createElement('p');
    toastMessage.textContent = message;

    toast.appendChild(closeBtn);
    toast.appendChild(toastTitle);
    toast.appendChild(toastMessage);
    toastItem.appendChild(toast);

    // Append the new toast to the panel
    toastPanel.appendChild(toastItem);

    // Force reflow
    toastItem.offsetHeight;

    // Add the 'show' class to trigger the animation
    toastItem.classList.add('show');

    setTimeout(() => {
    closeBtn.click();
    }, 5000);
    }

