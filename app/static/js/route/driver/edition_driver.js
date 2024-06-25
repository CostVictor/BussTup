function action_popup(popup, card, id, obj_click) {
  if (id === "confirmar_passou") {
    const btn_confirm = document.getElementById("confirmar_passou_btn_follow");
    const ponto_atual = document
      .getElementById("route_stop_path_local")
      .textContent.trim();
    if (ponto_atual === return_stop_path("ultimo")) {
      btn_confirm.textContent = "Finalizar";
    }
  }
}

function confirm_star_path() {
  open_popup("confirmar_iniciar_trajeto");
  const text_info = document.getElementById("confirmar_iniciar_trajeto_info");
  const btn_cancell = document.getElementById(
    "confirmar_iniciar_trajeto_btn_cancell"
  );
  const btn_confirm = document.getElementById(
    "confirmar_iniciar_trajeto_btn_confirm"
  );

  const data = {
    principal: Object.values(return_data_route()),
  };
  data.principal.push(return_path_selected());

  fetch("/confirm_start_path" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        text_info.textContent = response.aviso;
        btn_cancell.classList.add("cancel");
        btn_confirm.classList.remove("inactive");
      } else {
        close_popup("confirmar_iniciar_trajeto");
        create_popup(response.title, response.text);
      }
    });
}

function start_path() {
  const data = return_data_route();
  data.type = return_path_selected();
  const stops_path = Array.from(
    document.getElementById(`route_container_${data.type}`).children
  );

  popup_button_load("confirmar_iniciar_trajeto");
  fetch("/start_path", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      close_popup("confirmar_iniciar_trajeto");
      if (!response.error) {
        reload_data_path();
        if (stops_path.length) {
          open_stop_path(stops_path[0]);
        }
      } else {
        create_popup(response.title, response.text);
      }
    });
}

function follow_path() {
  const container_students = document.getElementById(
    "route_stop_path_container_students"
  );
  const count_students = container_students.querySelectorAll("div").length;

  const btn_follow = document.getElementById("confirmar_passou_btn_follow");
  const text_btn_follow = btn_follow.textContent
  btn_follow.onclick = null;


  const data = return_data_route();
  data.type = return_path_selected();
  data.qnt = count_students;

  popup_button_load("confirmar_passou");
  fetch("/follow_path", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        const local_popup = document.getElementById("popup_local");
        local_popup.removeChild(local_popup.querySelector("#route_stop_path"));
        close_popup("confirmar_passou");

        const proximo = return_stop_path("proximo", true);
        if (proximo) {
          setTimeout(() => {
            open_stop_path(proximo);
          }, 250);
        }

        if (response.ultimo) {
          reload_data_path();
          create_popup("Trajeto Finalizado", "", "Ok", "success");
        }
      } else {
        popup_button_load("confirmar_passou", text_btn_follow);
        btn_follow.onclick = function () {
          follow_path();
        };
      }
    });
}
