document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const editMode = urlParams.get('edit') === '1';

    if (!editMode) return;

    console.log('🛠️ Editor ACTIVATED!');

    document.querySelectorAll('.editor-element').forEach((el, index) => {
        const elementId = el.dataset.elementId;
        const hasChildren = el.dataset.hasChildren === 'true';

        el.classList.add(`editor-el-${index}`);

        // Border
        const border = document.createElement('div');
        border.className = `editor-border ${hasChildren ? 'non-leaf' : 'leaf'}`;
        el.appendChild(border);

        // Controls с НОВЫМИ иконками
        const controls = document.createElement('div');
        controls.className = 'editor-controls';
        if (hasChildren) {
            controls.innerHTML = '';
        } else {
            controls.innerHTML = `
            <div class="editor-control editor-edit" title="Edit content" data-action="edit" data-id="${elementId}">
                📝
            </div>
            `;
        }
        controls.innerHTML += `<div class="editor-control editor-config" title="Configure" data-action="config" data-id="${elementId}">
                ⚙️
            </div>
            <div class="editor-control editor-delete" title="Delete" data-action="delete" data-id="${elementId}">
                🗑️
            </div>
        `;
        el.appendChild(controls);

        controls.addEventListener('click', (e) => {
            e.stopPropagation();
            const btn = e.target.closest('.editor-control');
            const action = btn.dataset.action;
            const id = btn.dataset.id;

            console.log(`🚀 ${action} #${id}`);

            switch(action) {
                case 'edit':
                    editContent(id, el);
                    break;
                case 'config':
                    openConfig(id);
                    break;
                case 'delete':
                    deleteElement(id);
                    break;
            }
        });
    });
});

// 📝 Edit content
function editContent(elementId, element) {
    fetch(`/landing/api/element/${elementId}/has-content/`)
        .then(res => res.json())
        .then(data => {
            if (data.has_content) {
                showInlineEdit(elementId, element, data.content);
            } else {
                alert('No editable content found');
            }
        });
}

function showInlineEdit(elementId, element, content) {
    const inputContainer = document.createElement('div');
    inputContainer.className = 'editor-inline-edit';
    inputContainer.style.cssText = `
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: white; z-index: 10002; display: flex; flex-direction: column;
        padding: 12px; box-sizing: border-box;
    `;

    inputContainer.innerHTML = `
        <textarea class="editor-inline-input" placeholder="Edit content..." style="flex: 1; resize: vertical; min-height: 60px;">${content}</textarea>
        <div class="editor-inline-buttons" style="margin-top: 12px; display: flex; gap: 8px; justify-content: flex-end;">
            <button onclick="saveInlineEdit(${elementId}, this)" style="padding: 8px 16px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer;">✅ Save</button>
            <button onclick="cancelInlineEdit(this)" style="padding: 8px 16px; background: #6b7280; color: white; border: none; border-radius: 4px; cursor: pointer;">❌ Cancel</button>
        </div>
    `;

    element.appendChild(inputContainer);
    inputContainer.querySelector('.editor-inline-input').focus();
}

window.saveInlineEdit = function(elementId, btn) {
    const inputContainer = btn.closest('.editor-inline-edit');
    const newContent = inputContainer.querySelector('.editor-inline-input').value;

    fetch(`/landing/api/element/${elementId}/update-content/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ content: newContent })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
};

window.cancelInlineEdit = function(btn) {
    btn.closest('.editor-inline-edit').remove();
};

// ⚙️ Configure modal
function openConfig(elementId) {
    fetch(`/landing/api/element/${elementId}/config/`)
        .then(res => res.json())
        .then(data => {
            showConfigModal(data);
        });
}

function showConfigModal(data) {
    document.body.insertAdjacentHTML('beforeend', `
        <div class="editor-modal" onclick="this.remove()">
            <div class="editor-modal-content" onclick="event.stopPropagation()">
                <div class="editor-modal-header">
                    <h3>⚙️ Configure Element #${data.id}</h3>
                    <button onclick="this.closest('.editor-modal').remove()" style="background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
                </div>
                <form id="config-form-${data.id}">
                    ${data.form_html || '<p>Configuration coming soon...</p>'}
                    <div style="margin-top: 20px; text-align: right;">
                        <button type="button" onclick="this.closest('.editor-modal').remove()" style="margin-right: 10px; padding: 8px 16px;">Cancel</button>
                        <button type="submit" style="background: #3b82f6; color: white; padding: 8px 16px; border: none; border-radius: 4px;">Save</button>
                    </div>
                </form>
            </div>
        </div>
    `);

    document.getElementById(`config-form-${data.id}`).addEventListener('submit', (e) => {
        e.preventDefault();
        // Пока заглушка
        console.log('💾 Config save:', new FormData(e.target));
        e.target.closest('.editor-modal').remove();
    });
}

// 🗑️ Delete
function deleteElement(elementId) {
    if (confirm('🗑️ Delete this element? This cannot be undone.')) {
        fetch(`/landing/api/element/${elementId}/delete/`, {
            method: 'POST',
            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value}
        })
        .then(() => location.reload());
    }
}