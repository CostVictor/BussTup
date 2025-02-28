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
  } else if (id === "aparence_vehicle") {
    const surname_vehicle = extract_info(obj_click, "surname");
    document.getElementById("aparence_vehicle_surname").textContent =
      surname_vehicle;
    config_popup_aparence(surname_vehicle);
  } else if (id === "vehicle_utilities_routes") {
    const surname_vehicle = extract_info(obj_click, "surname");
    document.getElementById("vehicle_utilities_routes_surname").textContent =
      surname_vehicle;
    config_popup_routes_vehicle(surname_vehicle);
  } else if (id === "options_contraturno") {
    config_popup_contraturno();
  } else if (id === "sched_daily") {
    config_popup_sched();
  } else if (id === 'confirm_del_daily') {
    const date = obj_click.parentNode.parentNode.querySelector('h1').textContent.split(' ')
    const info = obj_click.parentNode.querySelector('p').textContent.split(' ~> ')
    document.getElementById('confirm_del_daily_date').textContent = date[date.length - 1]
    document.getElementById('confirm_del_daily_type').textContent = info[0]
    document.getElementById('confirm_del_daily_name_point').textContent = info[1]
  }
}

function check_help() {
  const popups = local_popup.querySelectorAll(
    'section[id*="help_me_cadastro"]'
  );
  if (popups.length) {
    return true;
  }
  return false;
}

function close_help() {
  const popups = local_popup.querySelectorAll(
    'section[id*="help_me_cadastro"]'
  );
  popups.forEach((popup) => {
    close_popup(popup.id);
  });
}

function check_state(init = false, check = true) {
  if (check ? check_help() : true) {
    const name_line = document.getElementById("interface_nome").textContent;
    fetch(`/help_student/${encodeURIComponent(name_line)}`, {
      method: "GET",
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          const data = response.data;
          const type = response.popup;

          if (!response.finished) {
            let popup_id = `help_me_cadastro_${type}`;
            if (!local_popup.querySelector(`#${popup_id}`)) {
              close_help();
              open_popup(popup_id);
            } else {
              document
                .getElementById(popup_id + "_msg")
                .classList.add("inactive");
              document
                .getElementById(popup_id + "_msg_reload")
                .classList.remove("inactive");
            }

            if (type !== "contraturno") {
              const container = document.getElementById(
                popup_id + "_container"
              );
              criar_rota(data, container, true);
            } else {
              shifts = Object.keys(data);
              const op_1 = document.getElementById("op_1");
              const op_1_container = document.getElementById("op_1_container");

              const op_2 = document.getElementById("op_2");
              const op_2_container = document.getElementById("op_2_container");

              if (shifts.length) {
                if (shifts.length > 1) {
                  shift_1 = shifts[0].split(" ");
                  op_1.textContent = "~> " + shift_1[shift_1.length - 1];
                  criar_rota(data[shifts[0]], op_1_container, true);

                  shift_2 = shifts[1].split(" ");
                  op_2.textContent = "~> " + shift_2[shift_2.length - 1];
                  criar_rota(data[shifts[1]], op_2_container, true);

                  op_1.classList.remove("inactive");
                  op_1_container.classList.remove("inactive");
                  op_2.classList.remove("inactive");
                  op_2_container.classList.remove("inactive");
                } else {
                  shift_1 = shifts[0].split(" ");
                  op_1.textContent = "~> " + shift_1[shift_1.length - 1];
                  criar_rota(data[shifts[0]], op_1_container, true);

                  op_1.classList.remove("inactive");
                  op_1_container.classList.remove("inactive");
                }
              }
            }
          } else {
            close_help();
            if (init) {
              create_popup(
                "Assistente",
                "<> Você já fez todas as configurações necessárias!",
                "Ok",
                "success"
              );
            } else {
              create_popup(
                "Assistente",
                "<> Prontinho! Você já fez todas as configurações necessárias. Agora, aproveite ao máximo os nossos recursos.",
                "Claro!!",
                "success"
              );
            }
          }
        } else {
          close_help();
          create_popup(response.title, response.text);
        }
      });

    if (init) {
      const msg_help = document.getElementById("interface_line_enter");
      msg_help.classList.add("inactive");
    } else {
      close_popup("config_route");
    }
  } else {
    close_popup("config_route");
  }
}

function confirm_register_in(contraturno = false) {
  const name_line = document.getElementById("interface_nome").textContent;
  let execute = true;
  let data = {};

  if (contraturno) {
    const popup = local_popup.querySelector("#options_contraturno");
    if (!popup.querySelector('[class*="selected"]')) {
      execute = false;
    }

    data = {
      principal: [name_line],
    };
  } else {
    const popup = local_popup.querySelector("#config_rel_point_route");
    data = {
      principal: [name_line, extract_info(popup, "tipo")],
    };
  }

  if (execute) {
    popup_button_load("config_rel_point_route");
    fetch(
      `/check_register_in${contraturno ? "_contraturno" : ""}` +
        generate_url_dict(data),
      {
        method: "GET",
      }
    )
      .then((response) => response.json())
      .then((response) => {
        popup_button_load("config_rel_point_route", "Fechar");
        if (!response.error) {
          const id = contraturno
            ? "confirm_register_contraturno"
            : "confirm_register_in_point";
          open_popup(id);

          if (response.change) {
            if (response.new_line) {
              document
                .getElementById(id + "_new_line")
                .classList.remove("inactive");
            } else {
              document
                .getElementById(id + "_change")
                .classList.remove("inactive");
            }
          } else {
            document.getElementById(id + "_msg").classList.remove("inactive");
          }
        } else {
          create_popup(response.title, response.text);
        }
      });
  } else {
    create_popup(
      "Nenhuma opção selecionada",
      "Selecione uma opção de ponto disponível.",
      "Voltar"
    );
  }
}

function config_popup_contraturno() {
  const data = return_data_route(null, (format_dict_url = true));
  const model_option = models.querySelector("#interface_model_option_headli");

  fetch("/get_interface-option_point_contraturno" + generate_url_dict(data), {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        for (shift in data) {
          const local = document.getElementById(
            `options_contraturno_container_${shift}`
          );
          const container = local.querySelector("div");

          const local_reverse = document.getElementById(
            `options_contraturno_container_${
              shift === "partida" ? "retorno" : "partida"
            }`
          );
          const container_reverse = local_reverse.querySelector("div");

          local.classList.remove("inactive");
          container.innerHTML = "";

          const options = data[shift];
          for (index in options) {
            const option = model_option.cloneNode(true);
            option.id = local.id + `-ponto_${index}`;

            ids = option.querySelectorAll(`[id*="${model_option.id}"]`);
            ids.forEach((value) => {
              value.id = value.id.replace(model_option.id, option.id);
            });

            for (dado in options[index]) {
              const info = options[index][dado];
              option.querySelector(`[id*="${dado}"]`).textContent = info;
            }

            option.removeAttribute("onclick");
            option.onclick = function () {
              popup_selectOption_span(this, [container_reverse]);
            };

            option.classList.remove("inactive");
            container.appendChild(option);
          }
        }
      } else {
        create_popup(response.title, response.text);
      }
    });
}

function config_popup_sched() {
  const data = return_data_route(null, (format_dict_url = true));
  fetch("/get_stops_route" + generate_url_dict(data), {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const data = response.data;
        const model = models.querySelector("#model_option");

        for (type in data) {
          const container = document.getElementById(
            `sched_daily_op_${type}_container`
          );
          const list = data[type];

          if (list.length) {
            for (index in list) {
              const option = model.cloneNode(true);
              option.id = `${container.id}-option_${index}`;
              option.querySelector("p").textContent = `${
                parseInt(index) + 1
              } - ${list[index]}`;

              option.classList.remove("inactive");
              container.appendChild(option);
            }
          } else {
            const nenhum = document.createElement('p');
            nenhum.textContent = "Nenhum disponível";
            nenhum.className = 'text secundario fundo cinza justify'
            container.appendChild(nenhum);
          }
        }
      } else {
        create_popup(response.title, response.text);
      }
    });
}
