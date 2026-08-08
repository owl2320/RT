let conversationId = null;
let isStreaming = false;


async function sendMessage() {
    if (isStreaming) return;

    const input = document.getElementById("message-input");
    const message = input.value.trim();

    if (!message) return;

    isStreaming = true;

    addMessage("You", message);
    input.value = "";

    try {
        const response = await fetch("/chat/stream", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });


        if (response.status === 401) {
            addMessage("System","Session expired. Redirecting to login...");
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            addMessage("System",`Server error (${response.status})`);
            return;
        }

        const aiContent = addMessage("AI", "");
        await readStream(response,aiContent);
    }
    catch(error) {
        addMessage("System","Couldn't reach server.");
        console.error(error);
    }
    finally {
        isStreaming = false;
    }
}

async function readStream(response, aiContent) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";

    while(true) {
        const {value, done} = await reader.read();
        if(done) break;

        buffer += decoder.decode(value, {stream:true});
        const events = buffer.split("\n\n");
        buffer = events.pop();


        for(const eventString of events) {
            if(!eventString.startsWith("data:")) continue;

            const raw = eventString.slice(6);
            let event;
            try {
                event = JSON.parse(raw);
            }
            catch {
                continue;
            }


            switch(event.type) {
                case "conversation":
                    conversationId = event.id;
                    break;

                case "token":
                    console.log(event.content); //re,move later
                    aiContent.textContent += event.content;
                    break;

                case "error":
                    aiContent.textContent +=
                        "\n[Error] " + event.message;
                    break;

                case "done":
                    console.log("done");
                    return;
            }
        }
    }
}



function addMessage(sender,text) {
    const chatBox = document.getElementById("chat-box");

    const message = document.createElement("p");
    const label = document.createElement("b");
    label.textContent = `${sender}: `;
    const content = document.createElement("span");
    content.textContent = text;

    message.appendChild(label);
    message.appendChild(content);
    chatBox.appendChild(message);

    chatBox.scrollTop = chatBox.scrollHeight;

    return content;
}

document.getElementById("message-input").addEventListener(
    "keydown",
    (event)=>{
        if(event.key==="Enter" && !event.shiftKey){
            event.preventDefault();
            sendMessage();
        }

    }
);

document.getElementById("logout-button").addEventListener("click", async () => {
        await fetch("/auth/logout", {
            method: "POST",
            credentials: "include"
        });

        window.location.href = "/login";
    });