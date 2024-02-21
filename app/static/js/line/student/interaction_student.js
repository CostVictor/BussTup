var templates = document.getElementById("templates_model");
var models = document.importNode(templates.content, true);

function action_popup(popup, card, id, obj_click) {
  if (id === "config_route") {
    config_popup_route(obj_click);
    document.getElementById("config_route_pos").textContent =
      obj_click.querySelector("span").textContent;
  } else if (id === "config_relacao_ponto_rota") {
    card.querySelector(`p#${popup.id}_nome`).textContent = extract_info(
      obj_click,
      "nome"
    );
    card.querySelector(`p#${popup.id}_ordem`).textContent = extract_info(
      obj_click,
      "number"
    );
    card.querySelector(`p#${popup.id}_horario`).textContent = extract_info(
      obj_click,
      "horario"
    );
  } else if (id === "config_rel_point_route") {
    const data = return_data_route(null, (format_dict_url = true));
    data.principal.push(
      obj_click.id.includes("partida") ? "partida" : "retorno"
    );
    data.principal.push(extract_info(obj_click, "nome"));
    document.getElementById("config_rel_point_route_ordem").textContent =
      extract_info(obj_click, "number");
    config_popup_relationship(data);
  }
}

function check_state() {
  close_popup("config_route");
}
