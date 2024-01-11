const header = document.getElementById('header_page')
const content = document.getElementById('content_page')
const nav = document.getElementById('nav_page')

const divs = content.querySelectorAll('div.page__container--aba')
const btns = nav.querySelectorAll('i.page__icon--btn')
let aba_atual = nav.querySelector('i.btn_selected').id

header.style.opacity = 0
observer_header = createObserver(null)
observer_header.observe(header)


// ~~ SSE ~~ //


// ~~ Página ~~ //

function loadLinha() {
    function create_lines(local, list_datas, list_minha_linha = false) {
        for (index_linha in list_datas) {
            const model_linha = document.getElementById('model_line')
            const linha = model_linha.cloneNode(true)
            linha.id = `${local.id}-linha_${index_linha}`

            const dados = list_datas[index_linha]
            for (data in dados) {
                const value = dados[data]

                if (data === 'particular') {
                    const pago = linha.querySelector('h1#model_line_pago')
                    const gratuito = linha.querySelector('h1#model_line_gratuito')
                    pago.id = pago.id.replace('model_line', linha.id)
                    gratuito.id = gratuito.id.replace('model_line', linha.id)

                    if (!value) {
                        pago.classList.add('inactive')
                        gratuito.classList.remove('inactive')
                    }
                } else if (data === 'ferias') {
                    const ferias = linha.querySelector('h1#model_line_ferias')
                    ferias.id = ferias.id.replace('model_line', linha.id)

                    if (value) {ferias.classList.remove('inactive')}
                } else {
                    const info = linha.querySelector(`[id*="${data}"]`)
                    info.id = linha.id + '_' + data
                    info.textContent = value
                }
                linha.classList.remove('inactive')

                if (list_minha_linha) {
                    for (minha_linha in list_minha_linha) {
                        if (list_minha_linha[minha_linha]['nome'] === dados['nome']) {
                            linha.classList.add('selected')
                        }
                    }
                }
            }
            local.appendChild(linha)
        }
    }

    fetch("/get_linhas", { method: "GET" })
    .then(response => response.json())
    .then(response => {
        if (response['identify']) {
            const local_linhas = document.getElementById('local_linhas')
            const minha_linha_area = document.getElementById('minha_linha_area')
            if (minha_linha_area) {minha_linha_area.innerHTML = ''}
            local_linhas.innerHTML = ''

            for (cidade in response['cidades']) {
                if (!local_linhas.querySelector(`div#${cidade}`)) {
                    const model_regiao = document.getElementById('model_regiao')
                    var regiao = model_regiao.cloneNode(true)
                    regiao.id = cidade

                    regiao.querySelector('h2').textContent = cidade
                    regiao.classList.remove('inactive')
                    regiao.classList.add('enter')
                    local_linhas.appendChild(regiao)
                }
                create_lines(regiao, response['cidades'][cidade], response['minha_linha'])
            }
            if (minha_linha_area) {
                create_lines(minha_linha_area, response['minha_linha'])
            }
            const elements = divs[2].querySelectorAll('[class*="enter"]')
            animate_itens(elements, 'fadeDown', 0.7, 0)
        }


        if (response['role'] === 'motorista') {
            const container_msg = document.getElementById('msg_criar_linha')
            const texts_msg = container_msg.querySelectorAll('p')
            const text_solicitar = document.getElementById('msg_solicitar_entrada')

            if (!response['minha_linha'].length) {
                text_solicitar.classList.remove('inactive')
                texts_msg.forEach(msg => {
                    msg.classList.remove('inactive')
                })
            } else {
                text_solicitar.classList.add('inactive')
                texts_msg.forEach(msg => {
                    msg.classList.add('inactive')
                })
            }
        }
    })
}


function loadInterfaceLinha(obj_linha, nome_linha = false) {
    if (nome_linha) {
        name_reference = nome_linha
    } else {
        name_reference = obj_linha.querySelector('[id*="nome"]').textContent
    }
    fetch("/get_interface-linha", {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'nome_linha': name_reference})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            let adm = false

            if (response['role'] === 'motorista') {
                const config_linha = document.getElementById('interface_config')
                config_linha.classList.add('inactive')

                if (response['relacao'] === 'dono') {
                    config_linha.classList.remove('inactive')
                    adm = true
                } else if (response['relacao'] === 'adm') {
                    adm = true
                }
            }

            for (dado in response['data']) {
                if (dado === 'particular') {
                    const area_precos = document.getElementById('area_precos')
                    if (!response['data'][dado]) {
                        area_precos.classList.add('inactive')
                    } else {area_precos.classList.remove('inactive')}

                } else if (dado === 'ferias') {
                    const info_ferias = document.getElementById('interface_ferias')
                    if (!response['data'][dado]) {
                        info_ferias.classList.add('inactive')
                    } else {info_ferias.classList.remove('inactive')}

                } else {
                    const info = document.getElementById(`interface_${dado}`)
                    const edit = document.getElementById(info.id.replace('interface', 'edit'))
                    info.textContent = response['data'][dado]

                    if (edit) {
                        if (adm) {
                            edit.classList.remove('inactive')
                        } else {edit.classList.add('inactive')}
                    }
                }
            }

        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
    setTimeout(() => {
        loadMotoristaInterface(name_reference)
    }, 100)
}


function loadMotoristaInterface(nome_linha) {
    fetch("/get_interface-motorista", {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'nome_linha': nome_linha})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            const data = response['data']
            const local_motorista = document.getElementById('area_motoristas')
            const elements_remove = Array.from(local_motorista.children)
            elements_remove.forEach(element => {
                if (element.id.includes('motorista')) {
                    local_motorista.removeChild(element)
                }
            })

            for (tipo in data) {
                for (pos in data[tipo]) {
                    const model_motorista = document.getElementById('model_motorista')
                    const motorista = model_motorista.cloneNode(true)
                    motorista.id = `motorista_${tipo}_${pos}`
                    
                    const elements = motorista.querySelectorAll('[id*="model_motorista"]')
                    elements.forEach(element => {
                        element.id = element.id.replace('model_motorista', motorista.id)
                    })

                    for (info in data[tipo][pos]) {
                        const tag = motorista.querySelector(`[id*="${info}"]`)
                        tag.textContent = data[tipo][pos][info]
                    }

                    const dono = motorista.querySelector('[id*="dono"]')
                    const adm = motorista.querySelector('[id*="adm"]')
                    if (response['role'] === 'motorista' && response['relacao'] === 'dono' && tipo !== 'dono') {
                        const btn_config = motorista.querySelector('[id*="btn"]')
                        btn_config.classList.remove('inactive')
                    }
                    if (tipo === 'dono') {
                        dono.classList.remove('inactive')
                        adm.classList.remove('inactive')
                    } else if (tipo === 'adm') {
                        adm.classList.remove('inactive')
                    }

                    motorista.classList.remove('inactive')
                    local_motorista.appendChild(motorista)
                }
            }
        } else {create_popup(response['title'], response['text'], 'Voltar', 'error')}
    })
}


function loadVeiculoInterface(nome_linha) {
    fetch("/get_interface-veiculo", {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'nome_linha': nome_linha})
    })
    .then(response => response.json())
    .then(response => {
        if (!response['error']) {
            
        }
    })
}


function enterPage() {
    content.classList.remove('content_noBorder')

    setTimeout(() => {
        header.classList.remove('header_hidden')
    }, 180)

    setTimeout(() => {
        header.removeAttribute('style')
        nav.classList.remove('nav_hidden')
    }, 500)

    setTimeout(() => {
        divs.forEach(element => {
            itens = element.querySelectorAll('[class*="enter"]')
            animate_itens(itens, 'fadeDown', 0.7, 0)
        })
    }, 600)
}


function closePage() {
    const aba = document.getElementById(`aba_${aba_atual}`)
    const itens = aba.querySelectorAll('[class*="enter"]')
    header.style.opacity = 0

    setTimeout(() => {
        animate_itens(itens, 'outUp', 0.5, 0, 0.03, 1)
    }, 100)

    setTimeout(() => {
        header.classList.add('header_hidden')
        nav.classList.add('nav_hidden')
    }, 150)

    setTimeout(() => {
        content.classList.add('content_noBorder')
    }, 400)
}


// ~~ Animação de rolamento ~~ //

let update_aba = false
function ajustAba(index_atual) {
    const abas = document.querySelectorAll('[id*="area"].page__container.column')
    abas.forEach((aba, index_aba) => {
        if (index_aba === index_atual) {
            checkLine()
        } else {
            aba.classList.add('inactive')
        }
    })
    update_aba = false
}


let isScrolling
content.addEventListener('scroll', function() {
    if (update_aba) {
        clearTimeout(isScrolling)
        isScrolling = setTimeout(function() {
            const larguraDiv = content.scrollWidth / divs.length;
            const index = Math.floor(content.scrollLeft / larguraDiv)
          
            btns.forEach((btn) => {
                btn.classList.remove('btn_selected')
            })
            btns[index].classList.add('btn_selected')
            aba_atual = btns[index].id
            ajustAba(index)
        }, 40)
    }
  })


function replaceAba(btn_click) {
    btns.forEach((element, index) => {
        if (element === btn_click) {
            const divAlvo = divs[index]
            content.scrollLeft = divAlvo.offsetLeft
            element.classList.add('btn_selected')
        } else {
            element.classList.remove('btn_selected')
        }
    })
    update_aba = true
}

set_observerScroll(document.querySelectorAll('div.scroll_horizontal'))
set_observerScroll(document.querySelectorAll('div.scroll_vertical'))


// ~~ Interações na aba ~~ //

function checkLine() {
    fetch("/checar_linha", { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        const aviso = document.getElementById(`not_line_${aba_atual}`)
        const area = document.getElementById(`area_${aba_atual}`)

        if (!response['conf'] && aba_atual !== 'linhas') {
            area.classList.add('inactive')
            aviso.classList.remove('inactive')
        } else {
            if (area) {area.classList.remove('inactive')}
            if (aviso) {aviso.classList.add('inactive')}

            if (aba_atual === 'agenda') {

            } else if (aba_atual === 'rota') {
                
            } else if (aba_atual === 'linhas') {
                loadLinha()
            }
        }
    })
}


function validationLine(obj_form, event) {
    event.preventDefault()
    let execute = true
    let data = {'particular': true}
    
    const options_gratuidade = document.getElementById('options_gratuidade').querySelectorAll('div')
    options_gratuidade.forEach(element => {
        const text = element.querySelector('p').textContent
        const icon = element.querySelector('i')

        if (text === 'Sim') {
            if (!icon.className.includes('selected')) {
                data['particular'] = false
            }
        }
    })

    for (let index = 0; index < obj_form.length; index++) {
        var campo = obj_form.elements[index]

        if (campo.name) {
            if (data['particular'] && !campo.name.includes('nome') && !campo.name.includes('cidade')) {
                const value = parseFloat(campo.value)
                if (!value || value <= 0) {
                    var erro_titulo = 'Valor inválido'
                    var erro_texto = `O ${campo.name} deve ser maior que 0.`
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
        fetch("/create_linha", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'data': data})
        })
        .then(response => response.json())
        .then(response => {
            if (response['error']) {
                create_popup(response['title'], response['text'], 'Voltar', 'error', '', false)
            } else {
                cancel_popup_edit('create_line')
                loadLinha()
                create_popup(response['title'], response['text'], 'Ok', 'success')
            }
        })
    } else {
        campo.classList.add('input_error')
        create_popup(erro_titulo, erro_texto, 'Voltar', 'error', '', false)
    }
}
