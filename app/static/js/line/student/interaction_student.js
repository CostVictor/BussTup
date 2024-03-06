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
  } else if ("vehicle_utilities_routes") {
    const surname_vehicle = extract_info(obj_click, "surname");
    document.getElementById("vehicle_utilities_routes_surname").textContent =
      surname_vehicle;
    config_popup_routes_vehicle(surname_vehicle);
  }
}

const local = document.getElementById("popup_local");
function check_help() {
  const popups = local.querySelectorAll('section[id*="help_me_cadastro"]');
  if (popups.length) {
    return true;
  }
  return false;
}

function close_help() {
  const popups = local.querySelectorAll('section[id*="help_me_cadastro"]');
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
            if (!local.querySelector(`#${popup_id}`)) {
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
                  op_1.textContent = '~> ' + shift_1[shift_1.length - 1];
                  criar_rota(data[shifts[0]], op_1_container, true);

                  shift_2 = shifts[1].split(" ");
                  op_2.textContent = '~> ' + shift_2[shift_2.length - 1];
                  criar_rota(data[shifts[1]], op_2_container, true);

                  op_1.classList.remove('inactive')
                  op_1_container.classList.remove('inactive')
                  op_2.classList.remove('inactive')
                  op_2_container.classList.remove('inactive')
                } else {
                  shift_1 = shifts[0].split(" ");
                  op_1.textContent = '~> ' + shift_1[shift_1.length - 1];
                  criar_rota(data[shifts[0]], op_1_container, true);

                  op_1.classList.remove('inactive')
                  op_1_container.classList.remove('inactive')
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
                "<> Prontinho! Você já fez todas as configurações necessárias. Agora, aproveite ao máximo os nossos recursos!",
                "Ok",
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

function confirm_register_in() {
  const popup = local.querySelector("#config_rel_point_route");
  const name_line = document.getElementById("interface_nome").textContent;
  data = {
    principal: [name_line, extract_info(popup, "tipo")],
  };
  fetch("/check_register_in" + generate_url_dict(data), {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const id = "confirm_register_in_point";
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
}

function register_in_point_fixed() {
  const data = return_data_route();
  const popup_point = local_popup.querySelector("#config_rel_point_route");
  data.type = extract_info(popup_point, "tipo");
  data.name_point = extract_info(popup_point, "nome");

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
      }
    });
}

function del_myPoint_fixed() {
  const name_line = document.getElementById("interface_nome").textContent;
  const type = extract_info(
    local_popup.querySelector("#config_rel_point_route"),
    "tipo"
  );

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
      }
    });
}
