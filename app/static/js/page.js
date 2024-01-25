const header = document.getElementById('header_page')
const content = document.getElementById('content_page')
const nav = document.getElementById('nav_page')

const divs = content.querySelectorAll('section.page__container--aba')
const btns = nav.querySelectorAll('i.page__icon--btn')
let aba_atual = nav.querySelector('i.btn_selected').id

header.style.opacity = 0
observer_header = createObserver(null)
observer_header.observe(header)


// ~~ SSE ~~ //


// ~~ Página ~~ //

function loadLines() {
    function create_lines(local, list_datas, minha_linha = false) {
        const model_linha = document.getElementById('model_line')
        for (index_linha in list_datas) {
            const linha = model_linha.cloneNode(true)
            linha.id = `${local.id}-linha_${index_linha}`

            const dados = list_datas[index_linha]
            for (data in dados) {
                const value = dados[data]

                if (data === 'paga') {
                    const pago = linha.querySelector('h1#model_line_paga')
                    const gratuito = linha.querySelector('h1#model_line_gratuita')
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

                if (minha_linha) {
                    if (Array.isArray(minha_linha)) {
                        for (element in minha_linha) {
                            if (minha_linha[element]['nome'] === dados['nome']) {
                                linha.classList.add('selected')
                            }
                        }
                    } else {
                        if (dados['nome'] === minha_linha) {
                            linha.classList.add('selected')
                        }
                    }
                }
            }
            local.appendChild(linha)
        }
    }

    fetch("/get_lines", { method: "GET" })
    .then(response => response.json())
    .then(response => {
        if (response['identify']) {
            const local_linhas = document.getElementById('local_linhas')
            const minha_linha_area = document.getElementById('minha_linha_area')
            if (minha_linha_area) {minha_linha_area.innerHTML = ''}
            local_linhas.innerHTML = ''

            const model_regiao = document.getElementById('model_regiao')
            for (cidade in response['cidades']) {
                if (!local_linhas.querySelector(`div#${cidade}`)) {
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
        if (aba_atual === 'linhas') {
            loadLines()
        } else {
            divs.forEach(element => {
                itens = element.querySelectorAll('[class*="enter"]')
                animate_itens(itens, 'fadeDown', 0.7, 0)
            })
        }
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

function ajustAba(index_atual) {
    const abas = document.querySelectorAll('[id*="area"].page__container.column')
    abas.forEach((aba, index_aba) => {
        if (index_aba === index_atual) {
            checkLine()
        } else {
            aba.classList.add('inactive')
        }
    })
}


let isScrolling
content.addEventListener('scroll', function() {
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
}

set_observerScroll(document.querySelectorAll('div.scroll_horizontal'))
set_observerScroll(document.querySelectorAll('div.scroll_vertical'))


// ~~ Interações na aba ~~ //

function checkLine() {
    fetch("/get_association", { method: 'GET' })
    .then(response => response.json())
    .then(response => {
        const aviso = document.getElementById(`not_line_${aba_atual}`)
        const area = document.getElementById(`area_${aba_atual}`)

        if (!response['conf'] && aba_atual !== 'linhas') {
            area.classList.add('inactive')
            aviso.classList.remove('inactive')
        } else {
            if (area) {
                area.classList.remove('inactive')
            }
            if (aviso) {aviso.classList.add('inactive')}

            if (aba_atual === 'agenda') {

            } else if (aba_atual === 'rota') {
                
            } else if (aba_atual === 'linhas') {
                loadLines()
            }
        }
    })
}


function validationLine(obj_form, event) {
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
            if (data['paga'] && !campo.name.includes('nome') && !campo.name.includes('cidade')) {
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
            if (response['error']) {
                create_popup(response['title'], response['text'], 'Voltar', 'error', '', false)
            } else {
                cancel_popup_edit('create_line')
                create_popup(response['title'], response['text'], 'Ok', 'success')
                loadLines()
            }
        })
    } else {
        campo.classList.add('input_error')
        create_popup(erro_title, erro_text, 'Voltar', 'error', '', false)
    }
}
