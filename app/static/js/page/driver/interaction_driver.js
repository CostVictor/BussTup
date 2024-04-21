function action_popup(popup, card, id, obj_click) {
  if (id === "summary_route") {
    const name_line = extract_info(obj_click, "line");
    const shift = extract_info(obj_click, "turno");
    const hr_par = extract_info(obj_click, "horario_partida");
    const hr_ret = extract_info(obj_click, "horario_retorno");
    const surname = extract_info(obj_click, "apelido");
    const driver = extract_info(obj_click, "motorista");

    popup.querySelector("#summary_route_span_turno").textContent = shift;
    popup.querySelector("#summary_route_span_partida").textContent = hr_par;
    popup.querySelector("#summary_route_span_retorno").textContent = hr_ret;

    popup.querySelector("#summary_route_linha").textContent = name_line;
    popup.querySelector("#summary_route_motorista").textContent = driver;
    popup.querySelector("#summary_route_veiculo").textContent = surname;
    popup.querySelector(
      "#summary_route_horarios"
    ).textContent = `${shift} > ${hr_par} ~ ${hr_ret}`;
    load_popup_route(popup);
  } else if (id === "summary_line") {
    const name_line = extract_info(obj_click, "nome");
    document.getElementById("summary_line_nome").textContent = name_line;
    load_popup_line(card, name_line);
  }
}

function loadSchedule() {}
