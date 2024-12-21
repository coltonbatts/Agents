// WebSocket connection
let ws;
let agents = [];

// Initialize the application
async function init() {
    await fetchAgents();
    setupWebSocket();
    updateAgentSelects();
}

// Fetch available agents from the API
async function fetchAgents() {
    const response = await fetch('/api/agents');
    const data = await response.json();
    agents = data.agents;
    
    // Display agents in the grid
    const agentsList = document.getElementById('agents-list');
    agentsList.innerHTML = agents.map(agent => `
        <div class="agent-card">
            <h3>${agent.name}</h3>
            <p>${agent.description}</p>
            <p><strong>Capabilities:</strong></p>
            <ul>
                ${agent.capabilities.map(cap => `<li>${cap}</li>`).join('')}
            </ul>
        </div>
    `).join('');
}

// Setup WebSocket connection
function setupWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        appendOutput(JSON.stringify(data, null, 2));
    };
    
    ws.onerror = function(error) {
        appendOutput('WebSocket Error: ' + error);
    };
    
    ws.onclose = function() {
        appendOutput('WebSocket Connection Closed');
        // Try to reconnect after 5 seconds
        setTimeout(setupWebSocket, 5000);
    };
}

// Add a new workflow step
function addWorkflowStep() {
    const template = document.getElementById('workflow-step-template');
    const workflowSteps = document.getElementById('workflow-steps');
    const clone = template.content.cloneNode(true);
    
    // Update agent options
    const select = clone.querySelector('.agent-select');
    agents.forEach(agent => {
        const option = document.createElement('option');
        option.value = agent.name;
        option.textContent = agent.name;
        select.appendChild(option);
    });
    
    workflowSteps.appendChild(clone);
}

// Remove a workflow step
function removeStep(button) {
    button.closest('.workflow-step').remove();
}

// Update all agent select dropdowns
function updateAgentSelects() {
    document.querySelectorAll('.agent-select').forEach(select => {
        if (select.options.length <= 1) {
            agents.forEach(agent => {
                const option = document.createElement('option');
                option.value = agent.name;
                option.textContent = agent.name;
                select.appendChild(option);
            });
        }
    });
}

// Execute the workflow
function executeWorkflow() {
    const steps = Array.from(document.querySelectorAll('.workflow-step')).map(step => ({
        agent: step.querySelector('.agent-select').value,
        input: step.querySelector('.step-input').value,
        type: 'process'
    }));
    
    if (steps.length === 0) {
        appendOutput('Please add at least one step to the workflow');
        return;
    }
    
    if (steps.some(step => !step.agent || !step.input)) {
        appendOutput('Please fill in all workflow steps');
        return;
    }
    
    ws.send(JSON.stringify({ steps }));
}

// Append output to the terminal
function appendOutput(text) {
    const output = document.getElementById('output');
    output.textContent += '\n' + text;
    output.scrollTop = output.scrollHeight;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
