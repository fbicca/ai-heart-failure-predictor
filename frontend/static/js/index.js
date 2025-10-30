let chat = document.querySelector("#chat");
let input = document.querySelector("#input");
let botaoEnviar = document.querySelector("#botao-enviar");

async function enviarMensagem() {
  if (input.value == "" || input.value == null) return;
  let mensagem = input.value;
  const type_conversation = document.querySelector("#type_conversation").value;
  input.value = "";

  let novaBolha = criaBolhaUsuario();
  novaBolha.innerHTML = mensagem;
  chat.appendChild(novaBolha);

  let novaBolhaBot = criaBolhaBot();
  chat.appendChild(novaBolhaBot);
  vaiParaFinalDoChat();
  novaBolhaBot.innerHTML = "Analisando ...";

  // Envia requisição com a mensagem para a API do ChatBot
  const resposta = await fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      msg: mensagem,
      type_conversation: type_conversation,
    }),
  });
  const dadosResposta = await resposta.json();
  console.log(dadosResposta);
  const textoDaResposta = dadosResposta.msg;
  document.querySelector("#type_conversation").value =
    dadosResposta.type_conversation;
  console.log(textoDaResposta);
  novaBolhaBot.innerHTML = textoDaResposta.replace(/\n/g, "<br>");
  vaiParaFinalDoChat();
}

function criaBolhaUsuario() {
  let bolha = document.createElement("p");
  bolha.classList = "chat__bolha chat__bolha--usuario";
  return bolha;
}

function criaBolhaBot() {
  let bolha = document.createElement("p");
  bolha.classList = "chat__bolha chat__bolha--bot";
  return bolha;
}

function vaiParaFinalDoChat() {
  chat.scrollTop = chat.scrollHeight;
}

botaoEnviar.addEventListener("click", enviarMensagem);
input.addEventListener("keyup", function (event) {
  event.preventDefault();
  if (event.keyCode === 13) {
    botaoEnviar.click();
  }
});
