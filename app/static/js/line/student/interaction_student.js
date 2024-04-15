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
    fetch(
      `/check_register_in${contraturno ? "_contraturno" : ""}` +
        generate_url_dict(data),
      {
        method: "GET",
      }
    )
      .then((response) => response.json())
      .then((response) => {
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

function register_in_point_fixed() {
  const data = return_data_route();
  const popup_point = local_popup.querySelector("#config_rel_point_route");
  data.type = extract_info(popup_point, "tipo");
  data.name_point = extract_info(popup_point, "nome");

  popup_button_load("confirm_register_in_point");
  fetch("/create_pass_fixed", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        create_popup(response.title, response.text, "Ok", "success");
        close_popup("confirm_register_in_point");
        loadInterfaceRoutes(data.name_line);
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        document
          .getElementById("config_rel_point_route_cadastrar")
          .classList.add("inactive");
        document
          .getElementById("config_rel_point_route_sair")
          .classList.remove("inactive");
      } else {
        create_popup(response.title, response.text);
        popup_button_load("confirm_register_in_point", "Confirmar");
      }
    });
}

function del_myPoint_fixed() {
  const name_line = document.getElementById("interface_nome").textContent;
  const type = extract_info(
    local_popup.querySelector("#config_rel_point_route"),
    "tipo"
  );

  popup_button_load("confirm_del_mypoint");
  fetch("/del_myPoint_fixed/" + encodeURIComponent(type), { method: "DELETE" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        document
          .getElementById("config_rel_point_route_cadastrar")
          .classList.remove("inactive");
        document
          .getElementById("config_rel_point_route_sair")
          .classList.add("inactive");

        create_popup(response.title, response.text, "Ok", "success");
        close_popup("confirm_del_mypoint");
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        loadInterfaceRoutes(name_line);
      } else {
        create_popup(response.title, response.text);
        popup_button_load("confirm_del_mypoint", "Confirmar");
      }
    });
}

function register_in_point_contraturno() {
  const popup = local_popup.querySelector("#options_contraturno");
  const data = return_data_route();
  let execute = true;

  const option = popup.querySelector('[id*="nome"][class*="selected"]');
  if (option) {
    data.type = option.id.includes("partida") ? "partida" : "retorno";
    data.name_point = option.textContent;
  } else {
    execute = false;
  }

  if (execute) {
    popup_button_load("confirm_register_contraturno");
    fetch("/create_pass_contraturno", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((response) => {
        if (!response.error) {
          local_popup.removeChild(
            local_popup.querySelector("#options_contraturno")
          );
          close_popup("confirm_register_contraturno");
          create_popup(response.title, response.text, "Ok", "success");

          loadInterfaceRoutes(data.name_line);
          config_popup_route(
            null,
            return_data_route(null, (format_dict_url = true))
          );
        } else {
          create_popup(response.title, response.text);
          popup_button_load("confirm_register_contraturno", "Confirmar");
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

function del_myPoint_contraturno() {
  const name_line = document.getElementById("interface_nome").textContent;
  popup_button_load("confirm_del_mycontraturno");

  fetch("/del_myPoint_contraturno", { method: "DELETE" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        create_popup(response.title, response.text, "Ok", "success");
        close_popup("confirm_del_mycontraturno");
        config_popup_route(
          null,
          return_data_route(null, (format_dict_url = true))
        );
        loadInterfaceRoutes(name_line);
      } else {
        create_popup(response.title, response.text);
        popup_button_load("confirm_del_mycontraturno", "Confirmar");
      }
    });
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
