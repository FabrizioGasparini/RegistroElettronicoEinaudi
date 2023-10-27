const LOGIN_URL = 'https://web.spaggiari.eu/rest/v1/auth/login'

async function login(data) {
    const response = await fetch(LOGIN_URL, {
        method: 'POST',
        withCredentials: true,
        headers: {
            "User-Agent": "CVVS/std/4.1.7 Android/12",
            "Content-Type": "application/json",
            "Z-Dev-ApiKey": "Tg1NWEwNGIgIC0K"
        },
        body: {
            "pass": "gasparini",
            "uid": "abcd"
        }
    }).then(response => response.json()).then(response => console.log(JSON.stringify(response)))
}

login('12', '34')