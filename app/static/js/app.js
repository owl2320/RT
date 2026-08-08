let conversationId = localStorage.getItem("conversation_id");
let isstreaming = false;

async function sendMessage() {
    if(isstreaming)  return;
    isstreaming = true;

    const input = document.getElementById("message-input");
    const message = input.value.trim();

    if (!message) return;

    addMessage("You", message);
    input.value = "";

    let response;
    try{
        try {
            response = await fetch("/chat/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId
                })
            });
        } catch (err) {
            addMessage("System", "Couldn't reach the server — check your connection.");
            return;
        }

        if (!response.ok) {
            addMessage("System", `Something went wrong (status ${response.status}).`);
            return;
        }

        // Create ONE bubble for the AI's reply, and keep a reference to its
        // content span — every incoming token gets appended into this same
        // element instead of creating a new paragraph each time.
        const aiContent = addMessage("AI", "");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop(); // keep any incomplete chunk for the next read

            for (const line of lines) {
                if (!line.startsWith("data:")) continue;

                // "data: " is 6 characters — this strips the prefix correctly
                const raw = line.slice(6);

                let event;
                try {
                    event = JSON.parse(raw);
                } catch (err) {
                    continue; // skip malformed/partial event, don't crash the stream
                }

                if (event.type === "conversation") {
                    conversationId = event.id;
                    localStorage.setItem("conversation_id", conversationId);
                }

                if (event.type === "token") {
                    console.log(event.content);
                    aiContent.textContent += event.content;
                }

                if (event.type === "error") {
                   aiContent.textContent += "\n[Error]: " + event.message;
                }

                if (event.type === "done") {
                    console.log("done");
                    return; // stream finished — exit the function entirely,
                            // not just the inner for-loop
                }
            }
        }
    }
    catch (err){
        addMessage("System","Couldn't reach Server");
    }
    finally{
        isstreaming = false;
    }
}


// Sends the message on Enter (without Shift, so Shift+Enter still allows
// multi-line input if you ever switch to a textarea).
document.getElementById("message-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function addMessage(sender, text) {
    const chatBox = document.getElementById("chat-box");
    const message = document.createElement("p");

    const label = document.createElement("b");
    label.textContent = `${sender}: `;
    message.appendChild(label);

    const content = document.createElement("span");
    content.textContent = text;
    message.appendChild(content);

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;

    return content; // caller can keep this to append streamed tokens into it
}