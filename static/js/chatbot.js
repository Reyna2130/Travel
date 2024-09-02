import { GoogleGenerativeAI } from "@google/generative-ai";

// Fetch your API_KEY
const API_KEY = "AIzaSyDV7AWgfuD1f3kke1aKDrGG-vRWlLr4Zzs";

const genAI = new GoogleGenerativeAI(API_KEY);

const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

document.getElementById("send-btn").addEventListener("click", sendMessage);
document
  .getElementById("speak-btn")
  .addEventListener("click", startRecognition);
document.getElementById("stop-btn").addEventListener("click", stopSpeech);
document
  .getElementById("user-input")
  .addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

const synth = window.speechSynthesis;
const recognition = new (window.SpeechRecognition ||
  window.webkitSpeechRecognition)();
recognition.lang = "en-US";
recognition.interimResults = false;
recognition.maxAlternatives = 1;

let stopBot = false;

function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  if (!userInput.trim()) return;

  appendMessage("User", userInput);
  document.getElementById("user-input").value = "";
  speak(userInput);

  fetchReply(userInput);
}

function appendMessage(sender, message) {
  const chatBox = document.getElementById("chat-box");
  const messageElement = document.createElement("div");
  messageElement.className = "chat-message";

  let styledMessage = "";

  if (sender === "Bot" && message.includes("* ")) {
    const listItems = message
      .split("* ")
      .filter((item) => item.trim() !== "")
      .map((item) => `<li>${item.trim()}</li>`)
      .join("");

    styledMessage = `<strong>${sender}:</strong> <ul>${listItems}</ul>`;
  } else {
    // Otherwise, display the message as usual
    styledMessage = `<strong>${sender}:</strong> <span class="preformatted">${message}</span>`;
  }

  messageElement.innerHTML = styledMessage;
  chatBox.appendChild(messageElement);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function speak(text) {
  if (synth.speaking) {
    console.error("SpeechSynthesisUtterance.voice is speaking");
    return;
  }
  const utterThis = new SpeechSynthesisUtterance(text);
  utterThis.onend = function (event) {
    console.log("SpeechSynthesisUtterance.onend");
    if (stopBot) {
      stopBot = false;
      return;
    }
    fetchReply("");
  };
  utterThis.onerror = function (event) {
    console.error("SpeechSynthesisUtterance.onerror");
  };

  const voices = synth.getVoices();
  const gowriVoice = voices.find(
    (voice) => voice.name === "Google UK English Female"
  );
  if (gowriVoice) {
    utterThis.voice = gowriVoice;
  }

  synth.speak(utterThis);
}

function stopSpeech() {
  synth.cancel();
  stopBot = true;
}


async function fetchReply(userInput) {
  try {
    let desiredText;

    // Check if the user's input is a greeting
    const lowerInput = userInput.trim().toLowerCase();
    if (lowerInput === "hi" || lowerInput === "hello" || lowerInput === "hii") {
      desiredText = "How can I help you today?"; // Respond only with this message

      // Display and speak the response, then return early
      appendMessage("Bot", desiredText);
      speak(desiredText);
      return; // Stop further processing
    }

    // Generate a response from the AI model for other inputs
    const result = await model.generateContent(userInput);
    const response = await result.response;
    desiredText = await response.text();

    // Display and speak the response
    appendMessage("Bot", desiredText);
    speak(desiredText);

  } catch (error) {
    const errorMessage = "Sorry, I am having trouble connecting to the server.";
    appendMessage("Bot", errorMessage);
    speak(errorMessage);
    console.error("Error:", error);
  }
}




function startRecognition() {
  recognition.start();
  recognition.onresult = function (event) {
    const speechResult = event.results[0][0].transcript;
    document.getElementById("user-input").value = speechResult;
    sendMessage();
  };
  recognition.onerror = function (event) {
    console.error("Recognition error:", event.error);
  };
}


