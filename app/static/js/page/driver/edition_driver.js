function create_line(obj_form, event) {
    event.preventDefault()
    let execute = true
    let data = {'paga': true}
    
    const options_gratuidade = document.getElementById('options_gratuidade').querySelectorAll('div')
    options_gratuidade.forEach(element => {
        const text = element.querySelector('p').textContent
        const icon = element.querySelector('i')

        if (text === 'Sim') {
            if (!icon.className.includes('selected')) {
                data['paga'] = false
            }
        }
    })

    for (let index = 0; index < obj_form.length; index++) {
        var campo = obj_form.elements[index]

        if (campo.name) {
            if (data.paga && !campo.name.includes('nome') && !campo.name.includes('cidade')) {
                const value = parseFloat(campo.value)
                if (!value || value <= 0) {
                    var erro_title = 'Valor inválido'
                    var erro_text = `O ${campo.name} deve ser maior que 0.`
                    execute = false; break
                } else {
                    const nome_campo = `${campo.name.includes('cartela')? 'valor_cartela' : 'valor_diaria'}`
                    data[nome_campo] = value
                }
            } else if (!campo.name.includes('preço')) {
                data[campo.name.trim()] = campo.value.trim()
            }
        }
    }

    if (execute) {
        fetch("/create_line", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'data': data})
        })
        .then(response => response.json())
        .then(response => {
            if (response.error) {
                create_popup(response.title, response.text, 'Voltar', 'warning', '', false)
            } else {
                close_popup('create_line')
                create_popup(response.title, response.text, 'Ok', 'success')
                loadLines()
            }
        })
    } else {
        campo.classList.add('input_error')
        create_popup(erro_title, erro_text, 'Voltar', 'error', '', false)
    }
}
