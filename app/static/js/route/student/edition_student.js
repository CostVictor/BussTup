function request_wait() {
  const data = return_data_route();
  data.type = return_path_selected();

  const btn_espera = document
    .getElementById("btn_solicitar_espera")
    .querySelector("p");
  btn_espera.textContent = "Aguarde...";

  fetch("/request_wait", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      btn_espera.textContent = "Solicitar espera ao motorista";
      if (!response.error) {
        create_popup(response.title, response.text, "Ok", "success");
      } else {
        create_popup(response.title, response.text);
      }
    });
}

function dell_request_wait() {
  const data = {
    principal: Object.values(return_data_route()),
  };
  data.principal.push(return_path_selected());

  fetch("/dell_request_wait" + generate_url_dict(data), { method: "GET" })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        reload_data_stop()
      } else {
        create_popup(response.title, response.text);
      }
    });
}
