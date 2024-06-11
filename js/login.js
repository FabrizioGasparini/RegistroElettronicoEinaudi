const usernameInput = document.getElementById('uid-input')
const passwordInput = document.getElementById('pwd-input')
const submitButton = document.getElementById('submit')

const errorMessage = document.getElementById('error-message')


submitButton.addEventListener('click', () => {
    if (usernameInput.value.length > 0 && passwordInput.value.length > 0)
    {
        response = fetch('https://registroelettronicoeinaudi.pythonanywhere.com/api/login', {
            body: {
                "uid": "***",
                "pwd": "***"
            },
            method: "POST"
        })

        console.log(response)
    }
})

fetch('https://registroelettronicoeinaudi.pythonanywhere.com/api/login', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        uid: 'username_inserito',
        pwd: 'password_inserita',
    })
})
.then(response => response.json())
.then(data => {
    // Gestisci la risposta del server Flask qui
    if (data.token) {
        // Salva il token nei cookie o nell'archiviazione locale
        // Esempio con i cookie:
        document.cookie = `token=${data.token}`;
    } else {
        // Gestisci errore di login
        console.error('Credenziali non valide');
    }
})
.catch(error => {
    // Gestisci eventuali errori di connessione al server
    console.error('Errore nella richiesta API:', error);
});
