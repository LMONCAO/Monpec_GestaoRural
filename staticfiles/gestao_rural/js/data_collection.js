(() => {
    const page = document.querySelector('[data-page="data-collection"]');
    if (!page) return;

    const actionMap = {
        'aparte': 'aparte',
        'consultar-animal': 'consultar-animal',
        'cadastros': 'cadastros'
    };

    const body = document.body;
    const modals = new Map();
    page.querySelectorAll('[data-classic-modal]').forEach((modal) => {
        modals.set(modal.dataset.classicModal, modal);
    });

    function openModal(key) {
        const modal = modals.get(key);
        if (!modal) return;
        modal.removeAttribute('hidden');
        body.classList.add('show-classic-modal');
    }

    function closeModal(modal) {
        modal.setAttribute('hidden', '');
        if (![...modals.values()].some((m) => !m.hasAttribute('hidden'))) {
            body.classList.remove('show-classic-modal');
        }
    }

    page.addEventListener('click', (event) => {
        const button = event.target.closest('[data-classic-action]');
        if (button) {
            const action = button.dataset.classicAction;
            if (actionMap[action]) {
                event.preventDefault();
                openModal(actionMap[action]);
            }
        }

        const dismiss = event.target.closest('[data-classic-dismiss]');
        if (dismiss) {
            const modal = dismiss.closest('[data-classic-modal]');
            if (modal) {
                event.preventDefault();
                closeModal(modal);
            }
        }
    });

    modals.forEach((modal) => {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });

    const tabs = page.querySelectorAll('[data-classic-tab]');
    tabs.forEach((tabButton) => {
        tabButton.addEventListener('click', (event) => {
            const button = event.currentTarget;
            const target = button.dataset.classicTab;
            const container = button.closest('.classic-tabs');
            if (!container) return;

            container.querySelectorAll('[data-classic-tab]').forEach((btn) => btn.classList.remove('is-active'));
            button.classList.add('is-active');

            container.querySelectorAll('[data-classic-tab-panel]').forEach((panel) => {
                panel.classList.toggle('is-active', panel.dataset.classicTabPanel === target);
            });
        });
    });
})();
(() => {
    const page = document.querySelector('[data-page="data-collection"]');
    if (!page) {
        return;
    }

    const filters = {
        periodo: document.getElementById('dcFilterPeriodo'),
        lote: document.getElementById('dcFilterLote'),
        status: document.getElementById('dcFilterStatus'),
        busca: document.getElementById('dcFilterBusca')
    };

    const listeners = [];
    const eventsTable = page.querySelector('.dc-table tbody');

    function dispatchFilterChange() {
        const detail = {
            periodo: filters.periodo?.value || null,
            lote: filters.lote?.value || null,
            status: filters.status?.value || null,
            busca: filters.busca?.value?.trim() || null
        };
        page.dispatchEvent(new CustomEvent('dc:filters:change', { detail }));
    }

    function handleRowClick(event) {
        const row = event.target.closest('tr[data-evento-id]');
        if (!row) return;
        const eventoId = row.getAttribute('data-evento-id');
        page.dispatchEvent(new CustomEvent('dc:event:show', { detail: { id: eventoId } }));
        row.classList.add('is-active');
        setTimeout(() => row.classList.remove('is-active'), 350);
    }

    Object.values(filters).forEach((input) => {
        if (!input) return;
        const type = input.tagName === 'SELECT' ? 'change' : 'input';
        const listener = () => dispatchFilterChange();
        input.addEventListener(type, listener);
        listeners.push({ input, type, listener });
    });

    if (eventsTable) {
        eventsTable.addEventListener('click', handleRowClick);
        listeners.push({ input: eventsTable, type: 'click', listener: handleRowClick });
    }

    // Exponibiliza uma pequena API global opcional para integração posterior
    window.MonpecDataCollection = {
        updateTable(rowsHtml) {
            if (!eventsTable) return;
            eventsTable.innerHTML = rowsHtml;
        },
        destroy() {
            listeners.forEach(({ input, type, listener }) => input.removeEventListener(type, listener));
        }
    };
})();

