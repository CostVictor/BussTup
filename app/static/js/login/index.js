function validationLogin(event) {
    event.preventDefault()

    const form = document.getElementById('formulario_login')
    const usuario = form.elements.user.value.trim()
    const senha = form.elements.password.value.trim()

    fetch('/authenticate_user', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'login': usuario, 'password': senha})
    })
    .then(response => response.json())
    .then(response => {
        if (response.error) {
            create_popup(response.title, response.text, 'Ok')
        } else {closeInterface('login', response.redirect)}
    })
}
