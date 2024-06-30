// Define initial x and y coordinates
var chatbotPositionX = 100;
var chatbotPositionY = 100;

lastScrapeDate = "October 23, 2023"
messageHistory = [{"role": "system", "content": "You are a tool that cleans up questions and prompts given, such that they are easier to understand and more clear in its meaning, for use with OpenAI Embeddings. Only provide the refactored question in your answer, do not say anything else. Use the message history (if applicable) to provide context to the question."}];
qaHistory = [{"role": "system", "content": "You are a informational chatbot designed to help answer questions about the City of Clyde Hill. A prompt and a text will be provided. Briefly answer the prompt using the texts as accurately and concisely as possible. Limit your response to about 100 words unless specified to be any longer. In your answer, do not mention the text or say the word 'text' in your answer. Do not say, 'Based on the texts...', 'The texts...', or anything similar to that. Make sure your answer makes sense without the context of the text. Keep in mind, the texts were last updated on " + lastScrapeDate + ". Try to maintain relevance to the current date: " + new Date().toJSON().slice(0,10)}];

function handleKeyPress(event) {
    if (event.keyCode === 13) {
        clearInputAndSend();
    }
}

function clearInputAndSend() {
    const micIcon = document.getElementById('micIcon');
    micIcon.classList.remove("recording");
    
    var userInput = document.getElementById("userInput").value;
    if (userInput !== "") {
        document.getElementById("userInput").value = "";
        sendMessage(userInput)
    }
}
function sendMessage(message) {
    displayMessage(message, "user-message", null);

    getBotResponse(message, function(response, sources) {
        displayMessage(response, "bot-message", sources);
    });
    
}
function truncateString(str) {
    if (str.length > 40) {
        return str.slice(0, 40) + "…"; // Adding ellipsis to indicate truncation
    }
    return str;
    
}

function displayMessage(message, className, sources) {
    var chatContainer = document.getElementById("box");
    var messageElement = document.createElement("div");
    messageElement.classList.add("item");
    messageElement.classList.add(className);


    if (className == "bot-message") {
        var messageIconDiv = document.createElement("div");
        messageIconDiv.classList.add("icon");
        var messageIcon = document.createElement("i");
        messageIcon.classList.add("fa");
        messageIcon.classList.add("fa-user");
        messageIconDiv.appendChild(messageIcon);
        messageElement.appendChild(messageIconDiv);
    }

    var messageContent = document.createElement("div");
    messageContent.classList.add("msg");
    messageContent.innerHTML = message;

    // Add timestamp
    var timestamp = document.createElement("div");
    timestamp.classList.add("timestamp");
    timestamp.innerText = getCurrentTimestamp(); // Call the function to get the current timestamp
    messageContent.appendChild(timestamp);

    // Convert sources into buttons
    if (sources) {
        for (var i = 0; i < sources.length; i++) {
            var sourceLinkButton = document.createElement("button");
            sourceLinkButton.classList.add("source-button");

            if (sources[i]["url"] != "") {
                sourceLinkButton.innerText = truncateString(sources[i]["title"]);
                sourceLinkButton.addEventListener("click", createButtonClickListener(sources[i]["url"]));

                messageContent.appendChild(sourceLinkButton);
            }
        }
    }

    messageElement.appendChild(messageContent);
    chatContainer.appendChild(messageElement);

    scrollToBottom();
}

function getCurrentTimestamp() {
    var now = new Date();
    var hours = now.getHours() % 12 || 12;
    var minutes = now.getMinutes();
    var ampm = now.getHours() >= 12 ? "PM" : "AM";

    return hours + ":" + (minutes < 10 ? "0" : "") + minutes + " " + ampm;
}

function createButtonClickListener(url) {
    return function () {
        window.open(url, "_blank");
    };
}



// Function to generate a bot response based on user input
function getBotResponse(userInput, callback) {
    var loadingBar = document.getElementById("loading-bar");
    
    var data = {message: userInput, 
        messageHistory: messageHistory, 
        qaHistory: qaHistory, 
        curOrg: "City of Clyde Hill",
        websiteTitleSuffix: " - City of Clyde Hill"};

    //console.log(data)
    //console.log(userInput)
    console.log(messageHistory);
    console.log(qaHistory);

    
    loadingBar.style.display = "block";
    fetch('https://api.mindflow.ai/api/chroma', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        loadingBar.style.display = "none";
        return response.text();
    })
    .then(result => {
        //console.log(result)
        result_json = JSON.parse(result);
        messageHistory = result_json.messageHistory;
        qaHistory = result_json.qaHistory;
        console.log(messageHistory);
        console.log(qaHistory);
        
        callback(result_json.response, result_json.sources); // Call the callback function with the response
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

/*
function regenMessage(curMessageId, curMessage) {
    //console.log(curMessageId-2);
    //console.log(messageCount);

    for (var i = curMessageId-2; i < messageCount; i++) {
        var messageElement = document.querySelector('[data-message-id="message-' + i + '"]');
        if (messageElement) {
            messageElement.remove();
        }
    }
    sendMessage(curMessage);
    
}*/

//document.getElementById("scrollToBottomBtn").addEventListener("click", scrollToBottom);

function scrollToBottom() {
    var chatContent = document.getElementById("box");
    chatContent.scrollTop = chatContent.scrollHeight;
}

var isFirstTimeOpen = true;

function openChat() {
    const wrapper = document.querySelector('.wrapper');
    
    if (isFirstTimeOpen) {
        displayMessage("Hello! I'm your virtual assistant. Feel free to ask me anything.", "bot-message", null);
        isFirstTimeOpen = false;
    }

    wrapper.style.left = chatbotPositionX + 'px';
    wrapper.style.top = chatbotPositionY + 'px';
    
    wrapper.style.display = 'block';
    
    const userInput = document.getElementById("userInput");
    userInput.focus();
}



function closeChat() {
    const wrapper = document.querySelector('.wrapper');
    wrapper.style.display = 'none';
}

if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  
    const textInput = document.getElementById('userInput');
    const voiceButton = document.getElementById('voice-button');
    const micIcon = document.getElementById('micIcon');

    recognition.continuous = false;
    recognition.interimResults = false;
  
    let isRecognizing = false;

    recognition.onresult = function(event) {
        const result = event.results[0][0].transcript;
        textInput.value = result;
    };

    voiceButton.addEventListener('click', function() {
        if (isRecognizing) {
            console.log("Stopping recording");
            micIcon.classList.remove("recording");
            recognition.stop();
        } else {
            console.log("Starting recording");
            micIcon.classList.add("recording");
            recognition.start();
        }
    
        isRecognizing = !isRecognizing;
    });
} else {
    console.log('Web Speech API is not supported in this browser.');
}
