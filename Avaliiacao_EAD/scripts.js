document.addEventListener('DOMContentLoaded', function() {
    loadFila();

    document.getElementById('addClienteForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const nome = document.getElementById('nome').value;
        const tipo = document.getElementById('tipo').value;

        fetch('http://127.0.0.1:8000/fila', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ nome: nome, tipo: tipo })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(error => { throw new Error(error.detail) });
            }
            return response.json();
        })
        .then(data => {
            alert('Cliente adicionado com sucesso!');
            loadFila();
        })
        .catch(error => {
            alert(`Erro: ${error.message}`);
        });
    });
});

function loadFila() {
    fetch('http://127.0.0.1:8000/fila')
        .then(response => response.json())
        .then(data => {
            const filaDiv = document.getElementById('fila');
            filaDiv.innerHTML = '';
            if (data.length === 0) {
                filaDiv.innerHTML = '<p>Ninguém na fila</p>';
            } else {
                data.forEach(cliente => {
                    const clienteDiv = document.createElement('div');
                    clienteDiv.className = 'cliente';
                    clienteDiv.innerHTML = `
                        <p>ID: ${cliente.id}</p>
                        <p>Nome: ${cliente.nome}</p>
                        <p>Data de Chegada: ${new Date(cliente.data_de_chegada).toLocaleString()}</p>
                        <button onclick="removerCliente(${cliente.id})">Remover</button>
                        <button onclick="atenderCliente(${cliente.id})">Atendido</button>
                    `;
                    filaDiv.appendChild(clienteDiv);
                });
            }
        });
}

function removerCliente(id) {
    fetch(`http://127.0.0.1:8000/fila/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(error => { throw new Error(error.detail) });
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        loadFila();
    })
    .catch(error => {
        alert(`Erro: ${error.message}`);
    });
}

function atenderCliente(id) {
    fetch(`http://127.0.0.1:8000/fila/atendido/${id}`, {
        method: 'PUT'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(error => { throw new Error(error.detail) });
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        loadFila();
    })
    .catch(error => {
        alert(`Erro: ${error.message}`);
    });
}

function atualizarFila() {
    fetch('http://127.0.0.1:8000/fila', {
        method: 'PUT'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(error => { throw new Error(error.detail) });
        }
        return response.json();
    })
    .then(data => {
        alert('Fila atualizada!');
        loadFila();
    })
    .catch(error => {
        alert(`Erro: ${error.message}`);
    });
}
