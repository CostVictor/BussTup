var templates = document.getElementById('templates_model')
var models = document.importNode(templates.content, true)

function action_popup(popup, card, id, obj_click) {
    if (id === 'config_route') {
       config_popup_route(obj_click)
       
   } else if (id === 'config_relacao_ponto_rota') {
       card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(obj_click, 'nome')
       card.querySelector(`p#${popup.id}_ordem`).textContent = extract_info(obj_click, 'number')
       card.querySelector(`p#${popup.id}_horario`).textContent = extract_info(obj_click, 'horario')
   }
}
