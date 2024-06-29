function validationLogin(event) {
  event.preventDefault();

  const btn_entrar = document.getElementById("btn_entrar");
  btn_entrar.value = "Aguarde...";

  const form = document.getElementById("formulario_login");
  const usuario = form.elements.user.value.trim();
  const senha = form.elements.password.value.trim();

  fetch("/authenticate_user", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ login: usuario, password: senha }),
  })
    .then((response) => response.json())
    .then((response) => {
      if (response.error) {
        create_popup(response.title, response.text, "Ok");
        btn_entrar.value = "Entrar";
      } else {
        closeInterface("login", response.redirect);
      }
    });
}

function recoverAccount(event) {
  event.preventDefault();
  const options = document.getElementById("popup_recover_options");
  const option_selected = return_text_bool_selected(options);
  const email = document.getElementById("popup_recover_email").value;
  const data = {
    recover: option_selected,
    email: email,
  };

  popup_button_load("popup_recover");
  fetch("/schedule_recover", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((response) => {
      if (!response.error) {
        close_popup("popup_recover");
        create_popup(response.title, response.text, "Ok", "success");
      } else {
        create_popup(response.title, response.text, "Voltar");
        popup_button_load("popup_recover", "Solicitar");
      }
    });
}
